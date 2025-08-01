# wholesale_lead_analyzer/enrichment/social_media.py

import requests
import json
import re
import logging
from typing import Tuple, List, Dict, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote

from utils.proxy_manager import ProxyManager
from utils.web_utils import get_random_user_agent, dynamic_sleep
from configs import settings

logger = logging.getLogger(__name__)

# --- Robust Request Helper ---
def _make_request(url: str, proxy_manager: ProxyManager) -> Optional[requests.Response]:
    """A robust helper function to make web requests using proxy rotation and rate limiting."""
    max_retries = 3
    for attempt in range(max_retries):
        dynamic_sleep()
        proxy = proxy_manager.get_proxy()
        headers = {'User-Agent': get_random_user_agent(), 'Accept-Language': 'en-US,en;q=0.5'}
        try:
            logger.info(f"Requesting {url} (Attempt {attempt+1}) using proxy: {proxy['http'] if proxy else 'None'}")
            response = requests.get(url, headers=headers, proxies=proxy, timeout=15)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request to {url} failed: {e}")
            proxy_manager.mark_current_proxy_failed()
    logger.error(f"All {max_retries} attempts failed for URL: {url}")
    return None


class SocialMediaAnalyzer:
    """Analyzes Instagram and LinkedIn profiles for real estate indicators."""

    def __init__(self, proxy_manager: ProxyManager):
        self.proxy_manager = proxy_manager

    def analyze_social_media_deep(self, username: str, name: str) -> Tuple[int, List[str]]:
        """Orchestrates social media analysis based on settings, preserving all analysis steps."""
        total_score, all_reasons = 0, []

        # Step 1: Analyze username patterns (Preserving your original logic)
        if username:
            username_score, username_reasons = self._analyze_username(username)
            total_score += username_score
            all_reasons.extend(username_reasons)

        # Step 2: Analyze Instagram, if enabled
        if 'instagram' in settings.SOCIAL_PLATFORM_FOCUS and username:
            ig_score, ig_reasons = self._scrape_instagram_profile(username)
            total_score += ig_score
            all_reasons.extend(ig_reasons)

        # Step 3: Analyze LinkedIn, if enabled
        if 'linkedin' in settings.SOCIAL_PLATFORM_FOCUS and name:
            li_score, li_reasons = self._search_and_scrape_linkedin(name)
            total_score += li_score
            all_reasons.extend(li_reasons)

        return min(total_score, 25), all_reasons

    def _analyze_username(self, username: str) -> Tuple[int, List[str]]:
        """Analyzes username for real estate and business indicators. (Your original logic)."""
        username_lower = str(username).lower()
        score, reasons = 0, []
        re_terms = ['realestate', 'property', 'homes', 'houses', 'investor', 'flip', 'rehab', 'realty']
        found_terms = [term for term in re_terms if term in username_lower]
        if found_terms:
            score += 4
            reasons.append(f"Real estate username indicator(s): {', '.join(found_terms)}")
        return min(score, 5), reasons

    def _scrape_instagram_profile(self, username: str) -> Tuple[int, List[str]]:
        """Scrapes an Instagram profile by parsing embedded JSON data."""
        url = f"https://www.instagram.com/{username}/"
        logger.info(f"Analyzing Instagram profile: {username}")
        response = _make_request(url, self.proxy_manager)
        if not response:
            return 0, [f"Instagram profile for {username} not accessible"]

        try:
            # Use a more robust method to find the JSON data
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', text=re.compile(r'window\._sharedData'))
            if not script:
                logger.warning(f"Could not find JSON data script on Instagram page for {username}.")
                return 0, ["Could not parse Instagram profile"]
            
            json_text = script.string.replace('window._sharedData =', '').rstrip(';')
            data = json.loads(json_text)
            profile = data.get('entry_data', {}).get('ProfilePage', [{}])[0].get('graphql', {}).get('user', {})

            if not profile:
                return 0, ["Could not find profile in Instagram data"]

            score, reasons = 0, []
            bio = profile.get('biography', '').lower()
            if bio:
                bio_keywords = settings.PROPERTY_KEYWORDS + settings.FINANCIAL_STRESS_KEYWORDS
                found_terms = [k for k in bio_keywords if k in bio]
                if found_terms:
                    score += 5
                    reasons.append(f"Instagram bio keywords: {', '.join(found_terms[:3])}")
            if profile.get('is_business_account'):
                score += 3
                reasons.append("Instagram is a business account")
            
            return min(score, 10), reasons
        except (json.JSONDecodeError, KeyError, IndexError, AttributeError) as e:
            logger.error(f"Error parsing Instagram JSON for {username}: {e}")
            return 0, ["Failed to parse Instagram profile data"]

    def _search_and_scrape_linkedin(self, name: str) -> Tuple[int, List[str]]:
        """
        Two-step LinkedIn analysis: 
        1. Search Google for the profile and analyze snippets.
        2. Attempt to scrape the found profile URL directly for more detail.
        (This preserves your original two-step logic).
        """
        if not name or len(name.strip().split()) < 2:
            return 0, []

        logger.info(f"Searching LinkedIn for: {name}")
        search_query = f'"{name}" site:linkedin.com/in'
        url = f"https://www.google.com/search?q={quote(search_query)}&num=5"
        response = _make_request(url, self.proxy_manager)
        if not response:
            return 0, [f"LinkedIn search for {name} failed"]

        # --- Step 1: Analyze Google Search Snippets ---
        score, reasons, profile_url = self._analyze_linkedin_search_results(response.text)
        
        # --- Step 2: Attempt Direct Scrape if a URL was found ---
        if profile_url:
            logger.info(f"Found LinkedIn profile URL: {profile_url}. Attempting direct analysis.")
            direct_score, direct_reasons = self._scrape_linkedin_profile_page(profile_url)
            score += direct_score
            reasons.extend(direct_reasons)
        
        return min(score, 10), reasons

    def _analyze_linkedin_search_results(self, html_content: str) -> Tuple[int, List[str], Optional[str]]:
        """Analyzes Google search results for LinkedIn profile info and extracts the top URL."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            search_results_text = " ".join(div.get_text().lower() for div in soup.select("div.g, div.MjjYud, div.sV3dd"))
            
            score, reasons = 0, []
            re_keywords = [
                'real estate', 'realtor', 'broker', 'property manager', 'investor', 'developer', 
                'landlord', 'flipper', 'wholesaler', 'construction', 'realty', 'acquisitions'
            ]
            found_keywords = [k for k in re_keywords if k in search_results_text]
            if found_keywords:
                score += 5
                reasons.append(f"LinkedIn search indicators: {', '.join(found_keywords[:3])}")
            
            # Extract the first valid LinkedIn profile URL
            profile_url = None
            link_tag = soup.find('a', href=re.compile(r'https://www.linkedin.com/in/'))
            if link_tag:
                profile_url = link_tag['href']

            return score, reasons, profile_url
        except Exception as e:
            logger.error(f"Error parsing LinkedIn search results: {e}")
            return 0, [], None
    
    def _scrape_linkedin_profile_page(self, profile_url: str) -> Tuple[int, List[str]]:
        """Best-effort attempt to scrape a direct LinkedIn profile URL."""
        response = _make_request(profile_url, self.proxy_manager)
        if not response:
            return 0, []
        
        # This is a best-effort attempt, as LinkedIn is heavily protected.
        # We look for simple, often-available text.
        content = response.text.lower()
        score, reasons = 0, []

        if 'experience' in content and ('owner' in content or 'founder' in content):
            score += 2
            reasons.append("Profile indicates business ownership.")
        
        return score, reasons