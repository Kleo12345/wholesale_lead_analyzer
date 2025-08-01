# wholesale_lead_analyzer/data_processing/cleaner.py

import pandas as pd
import re
import logging
from typing import Optional
from configs import settings # Import the settings module

logger = logging.getLogger(__name__)

class DataCleaner:
    """Cleans and prepares raw lead data for analysis."""

    def clean_contact_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize input data, with optional USA filtering."""
        logger.info("Starting data cleaning process...")
        data = raw_data.copy()

        # --- MODIFICATION START ---
        # Conditionally filter leads based on the target country setting
        if settings.TARGET_COUNTRY == "USA":
            logger.info(f"Filtering enabled for target country: {settings.TARGET_COUNTRY}")
            data = self._filter_usa_leads(data)
        else:
            logger.info("Country filtering is disabled in settings.")
        # --- MODIFICATION END ---

        data = data.drop_duplicates()
        data = data.drop_duplicates(subset=['username'], keep='first')

        if 'name' in data.columns:
            data['name'] = data['name'].astype(str).str.title().replace('Nan', None)

        if 'website' in data.columns:
            data['website'] = data['website'].apply(self._clean_website_url)

        if 'bio' in data.columns:
            data['bio'] = data['bio'].astype(str).replace('nan', '')
            data['phone_extracted'] = data['bio'].apply(self._extract_phone)
            data['email_extracted'] = data['bio'].apply(self._extract_email)

        if 'category' in data.columns:
            data['category'] = data['category'].astype(str).str.lower().replace('nan', '')

        logger.info(f"Data cleaning complete. {len(data)} records processed.")
        return data

    def _filter_usa_leads(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter leads to keep only USA-based ones. (Your logic is great, no changes needed here)"""
        initial_count = len(data)
        if initial_count == 0:
            return data

        # USA indicators patterns
        usa_patterns = [
            r'\b(USA|US|United States|America|American)\b',
            r'\b(AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY)\b',
            r'\b\d{5}(-\d{4})?\b',  # ZIP codes
            r'\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US phone format
            r'\b(California|Texas|Florida|New York|Illinois|Pennsylvania|Ohio|Georgia|North Carolina|Michigan)\b'
        ]
        usa_pattern = '|'.join(usa_patterns)

        # Check multiple columns for USA indicators
        text_columns = ['bio', 'category', 'name', 'website']
        usa_mask = pd.Series([False] * len(data), index=data.index)

        for col in text_columns:
            if col in data.columns:
                # Use .fillna('') to avoid errors on pure NaN columns
                usa_mask |= data[col].fillna('').astype(str).str.contains(
                    usa_pattern, case=False, na=False, regex=True
                )

        # If no clear indicators, assume leads are valid for the target country
        if not usa_mask.any():
            logger.warning("No specific USA indicators found in any leads - keeping all rows.")
            return data

        filtered_data = data[usa_mask].copy()
        final_count = len(filtered_data)
        dropped_count = initial_count - final_count

        logger.info(f"USA filtering: {initial_count} -> {final_count} leads retained ({dropped_count} dropped).")
        return filtered_data

    def _clean_website_url(self, url: str) -> Optional[str]:
        """Clean and validate website URLs."""
        if pd.isna(url) or str(url).lower() in ['nan', 'none', '']:
            return None
        url = str(url).strip()
        if not url:
            return None
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')

    def _extract_phone(self, bio: str) -> Optional[str]:
        """Extract USA phone number from bio."""
        if pd.isna(bio):
            return None
        # Enhanced USA phone patterns
        phone_patterns = [
            r'\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{10}',
        ]
        for pattern in phone_patterns:
            match = re.search(pattern, str(bio))
            if match:
                return match.group(0)
        return None

    def _extract_email(self, bio: str) -> Optional[str]:
        """Extract email from bio."""
        if pd.isna(bio):
            return None
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, str(bio))
        return match.group(0) if match else None