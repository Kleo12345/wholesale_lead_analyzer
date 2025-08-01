# wholesale_lead_analyzer/data_processing/scorer.py

import pandas as pd
from typing import Dict, List, Tuple

from configs import settings
from enrichment import email_validator, web_scraper, business_records, public_records
from enrichment.social_media import SocialMediaAnalyzer # Import the class
from utils.proxy_manager import ProxyManager # Import the class

class LeadScorer:
    """Calculates a comprehensive lead score by orchestrating various analysis modules."""

    def __init__(self, proxy_manager: ProxyManager, social_media_analyzer: SocialMediaAnalyzer):
        """
        Initializes the LeadScorer with required analysis tools.
        
        Args:
            proxy_manager: An instance of ProxyManager for web requests.
            social_media_analyzer: An instance of SocialMediaAnalyzer.
        """
        self.proxy_manager = proxy_manager
        self.social_media_analyzer = social_media_analyzer

    def analyze_bio(self, bio: str) -> Tuple[int, List[str]]:
        if pd.isna(bio) or not bio: return 0, []
        bio_lower = str(bio).lower()
        score, reasons = 0, []

        stress_score, stress_found = 0, []
        for keyword in settings.FINANCIAL_STRESS_KEYWORDS:
            if keyword in bio_lower:
                stress_score += 3
                stress_found.append(keyword)
        stress_score = min(stress_score, 20)
        if stress_found: reasons.append(f"Financial stress indicators: {', '.join(stress_found)}")

        property_score, property_found = 0, []
        for keyword in settings.PROPERTY_KEYWORDS:
            if keyword in bio_lower:
                property_score += 3
                property_found.append(keyword)
        property_score = min(property_score, 20)
        if property_found: reasons.append(f"Property ownership indicators: {', '.join(property_found)}")

        return stress_score + property_score, reasons

    def analyze_category(self, category: str) -> Tuple[int, List[str]]:
        if pd.isna(category) or not category: return 0, []
        cat_lower = str(category).lower()
        
        if any(cat in cat_lower for cat in settings.HIGH_VALUE_CATEGORIES):
            return 25, [f"High-value category: {category}"]
        if any(cat in cat_lower for cat in settings.MEDIUM_VALUE_CATEGORIES):
            return 15, [f"Medium-value category: {category}"]
        if any(cat in cat_lower for cat in settings.LIFESTYLE_CATEGORIES):
            return 10, [f"Lifestyle category: {category}"]
        return 0, []

    def calculate_lead_score(self, contact: pd.Series) -> Tuple[int, List[str], Dict[str, int]]:
        """
        Calculates the lead score by calling enrichment functions with the necessary dependencies.
        """
        all_reasons, scores = [], {}

        # Bio & Category (no external requests)
        scores['bio_score'], reasons = self.analyze_bio(contact.get('bio'))
        all_reasons.extend(reasons)
        scores['category_score'], reasons = self.analyze_category(contact.get('category'))
        all_reasons.extend(reasons)

        # Website & Zillow Scraping (requires ProxyManager)
        # We assume an 'address' column might exist for Zillow.
        scores['zillow_score'], reasons = web_scraper.scrape_zillow_property_data(
            contact.get('address'), self.proxy_manager
        )
        all_reasons.extend(reasons)
        scores['website_score'], reasons = web_scraper.analyze_website(
            contact.get('website'), self.proxy_manager
        )
        all_reasons.extend(reasons)
        
        # Social Media (requires SocialMediaAnalyzer, which uses ProxyManager)
        scores['social_score'], reasons = self.social_media_analyzer.analyze_social_media_deep(
            contact.get('username'), contact.get('name')
        )
        all_reasons.extend(reasons)

        # Email Validation (no external requests)
        is_valid, reason = email_validator.validate_email_free(contact.get('email_extracted'))
        scores['email_score'] = 5 if is_valid else 0
        all_reasons.append("Valid email found" if is_valid else f"Email issue: {reason}")
        
        # Business & Public Records (placeholders, no external requests yet)
        scores['business_score'], reasons = business_records.check_business_registration(
            contact.get('name'), contact.get('category'))
        all_reasons.extend(reasons)
        scores['bankruptcy_score'], reasons = public_records.check_bankruptcy_records(contact.get('name'))
        all_reasons.extend(reasons)
        scores['county_score'], reasons = public_records.check_county_records(
            contact.get('name'), contact.get('location'))
        all_reasons.extend(reasons)
        
        total_score = sum(scores.values())
        return min(total_score, 100), all_reasons, scores