# wholesale_lead_analyzer/enrichment/web_scraper.py

import requests
import re
import logging
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from urllib.parse import quote
import random 

from utils.web_utils import get_random_user_agent, dynamic_sleep
from utils.proxy_manager import ProxyManager
from configs import settings

logger = logging.getLogger(__name__)

def _make_request(url: str, proxy_manager: ProxyManager, headers: Optional[dict] = None) -> Optional[requests.Response]:
    """A robust helper function to make web requests using proxy rotation and rate limiting."""
    max_retries = 3
    if headers is None:
        headers = {'User-Agent': get_random_user_agent()}
    else:
        headers.setdefault('User-Agent', get_random_user_agent())

    for attempt in range(max_retries):
        dynamic_sleep()
        proxy = proxy_manager.get_proxy()

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

##def scrape_zillow_property_data(address: str, proxy_manager: ProxyManager) -> Tuple[int, List[str]]:
##    """Scrapes Zillow using its internal API for reliable data."""
##    if not address:
##        return 0, []
##    if not settings.ZILLOW_ZUID:
##        logger.warning("Zillow scraping skipped: ZILLOW_ZUID is not set in settings.py.")
##        return 0, ["Zillow ZUID not configured"]
##
##    # This is the search API endpoint Zillow uses internally
##    search_url = (
##        f"https://www.zillow.com/search/GetSearchPageState.htm?"
##        f"searchQueryState={{{'pagination':{{}},'mapBounds':{{}},'usersSearchTerm':'{quote(address)}','isMapVisible':True,'filterState':{{'sortSelection':{{'value':'days'}},'isForSaleByAgent':{{'value':False}},'isForSaleByOwner':{{'value':False}},'isNewConstruction':{{'value':False}},'isAuction':{{'value':False}},'isForSaleForeclosure':{{'value':False}},'isComingSoon':{{'value':False}},'isPreMarketForeclosure':{{'value':False}},'isPreMarketPreForeclosure':{{'value':False}},'isRecentlySold':{{'value':False}},'isForRent':{{'value':False}},'isAllHomes':{{'value':True}}}}}&"
##        f"wants={{'cat1':['listResults']}}&"
##        f"requestId={random.randint(2, 10)}"
##    )
##
##    headers = {
##        'Accept': 'application/json',
##        'Accept-Language': 'en-US,en;q=0.9',
##        'Cookie': f'zguid=_; zuid={settings.ZILLOW_ZUID}; zgs=_;',
##        'Referer': f'https://www.zillow.com/homes/{quote(address)}',
##        'User-Agent': get_random_user_agent()
##    }
##
##    response = _make_request(search_url, proxy_manager, headers=headers)
##    if not response:
##        return 0, ["Zillow API request failed"]
##
##    try:
##        data = response.json()
##        results = data.get('cat1', {}).get('searchResults', {}).get('listResults', [])
##        
##        if not results:
##            logger.info(f"No Zillow results found for address: {address}")
##            return 0, ["No results on Zillow"]
##            
##        # Analyze the first result, which should be the best match
##        property_info = results[0]
##        score = 0
##        reasons = []
##
##        # Indicator 1: Days on market
##        days_on_zillow = property_info.get('daysOnZillow', 0)
##        if days_on_zillow:
##            if days_on_zillow > 90:
##                score += 15
##                reasons.append(f"Long time on market: {days_on_zillow} days")
##            elif days_on_zillow > 30:
##                score += 8
##                reasons.append(f"Extended time on market: {days_on_zillow} days")
##
##        # Indicator 2: Price reduction
##        price_history = property_info.get('priceHistory', [])
##        if len(price_history) > 1:
##            latest_price = price_history[0].get('price')
##            previous_price = price_history[1].get('price')
##            if latest_price and previous_price and latest_price < previous_price:
##                score += 10
##                reasons.append("Recent price reduction found")
##
##        # Indicator 3: Distressed property types
##        if property_info.get('isPreMarketForeclosure') or property_info.get('isAuction'):
##            score += 12
##            reasons.append("Distressed property type (Auction/Foreclosure)")
##            
##        logger.info(f"Zillow score for {address}: {score}, Reasons: {reasons}")
##        return min(score, 25), reasons
##
##    except (ValueError, KeyError, IndexError) as e:
##        logger.error(f"Error parsing Zillow JSON for {address}: {e}")
##        return 0, ["Failed to parse Zillow API response"]


def analyze_website(url: str, proxy_manager: ProxyManager) -> Tuple[int, List[str]]:
    """Scrape and analyze a lead's website using the robust request handler."""
    if not url:
        return 0, []
        
    response = _make_request(url, proxy_manager)
    if not response:
        return 0, [f"Website analysis failed: Could not retrieve {url}"]

    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text().lower()
        score, reasons, found_keywords = 0, [], []
        
        for keyword in settings.WEBSITE_KEYWORDS:
            if keyword in text_content:
                score += 3
                found_keywords.append(keyword)
        
        if soup.find('form') and any(w in text_content for w in ['contact', 'quote', 'sell', 'buy']):
            score += 5
            reasons.append("Contact form with property-related content")
        
        if found_keywords:
            reasons.append(f"Website keywords found: {', '.join(found_keywords[:5])}")
            
        return min(score, 25), reasons
        
    except Exception as e:
        logger.error(f"Error parsing website content for {url}: {e}")
        return 0, [f"Website analysis failed: Parsing error"]