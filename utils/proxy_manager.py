# wholesale_lead_analyzer/utils/proxy_manager.py

import requests
import random
import logging
from typing import List, Dict, Optional, Tuple
from configs import settings
from utils.web_utils import dynamic_sleep # Use the centralized rate limiter

logger = logging.getLogger(__name__)

class ProxyManager:
    """Manages proxy loading, rotation, and USA geo-filtering for web scraping."""

    def __init__(self, use_free_proxies_as_fallback: bool = True):
        """
        Initializes the ProxyManager.

        It will first try to load proxies from settings.py. If none are found,
        it can fall back to loading free proxies from the web.
        """
        self.proxies: List[Dict[str, str]] = []
        self.current_proxy_index = 0
        self.failed_proxies = set()
        self.load_proxies(use_free_proxies_as_fallback)

    def load_proxies(self, use_free_proxies_as_fallback: bool):
        """
        Loads proxies, prioritizing the list from settings.py.
        """
        if settings.PROXIES:
            logger.info(f"Loading {len(settings.PROXIES)} proxies from settings.py")
            # For user-provided proxies, we assume they are reliable and don't test them initially.
            self.proxies = [{"http": p, "https": p} for p in settings.PROXIES]
        elif use_free_proxies_as_fallback:
            logger.info("No proxies found in settings. Falling back to loading free proxies.")
            self._load_and_filter_free_proxies()
        else:
            logger.warning("No proxies configured in settings.py and fallback is disabled. Running without proxies.")

    def _load_and_filter_free_proxies(self):
        """Loads and filters free proxies from public sources."""
        proxy_sources = [
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
            'https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'
        ]
        all_proxies = []
        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxy_list = [p.strip() for p in response.text.strip().split('\n') if ':' in p]
                    all_proxies.extend(proxy_list)
                    logger.info(f"Loaded {len(proxy_list)} potential proxies from {source}")
            except Exception as e:
                logger.warning(f"Failed to load proxies from {source}: {e}")

        # Test and filter proxies for the target country from settings
        if settings.TARGET_COUNTRY == "USA":
            logger.info("Filtering for working USA proxies...")
            self.proxies = self._filter_proxies_by_country(all_proxies, "United States")
            logger.info(f"Found {len(self.proxies)} working USA proxies.")
        else:
            # If target is not USA, just grab some working ones without country check
            self.proxies = self._filter_proxies_by_country(all_proxies, None)
            logger.info(f"Found {len(self.proxies)} working generic proxies.")


    def _filter_proxies_by_country(self, proxy_list: List[str], country_name: Optional[str]) -> List[Dict[str, str]]:
        """Tests proxies and keeps only those based in the specified country."""
        working_proxies = []
        random.shuffle(proxy_list) # Test a random sample

        for proxy_str in proxy_list[:200]: # Test a max of 200 to save time
            proxy_dict = {"http": f'http://{proxy_str}', "https": f'http://{proxy_str}'}
            is_valid, proxy_country = self._test_proxy(proxy_dict)

            if is_valid and (country_name is None or proxy_country == country_name):
                working_proxies.append(proxy_dict)
                if len(working_proxies) >= 25:  # Stop after finding 25 good proxies
                    break
        return working_proxies

    def _test_proxy(self, proxy: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """Tests if a proxy works and returns its country."""
        try:
            # ip-api is a good, free service for this
            response = requests.get('http://ip-api.com/json', proxies=proxy, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('status') == 'success', data.get('country')
        except Exception:
            return False, None
        return False, None


    def get_proxy(self) -> Optional[Dict[str, str]]:
        """
        Gets a working proxy from the list, rotating if necessary.
        This is the main method other modules should call.
        """
        if not self.proxies:
            return None

        # Rotate to the next available proxy, skipping failed ones
        for _ in range(len(self.proxies)):
            proxy_candidate = self.proxies[self.current_proxy_index]
            if self.current_proxy_index not in self.failed_proxies:
                return proxy_candidate
            self._rotate_proxy()

        # If all proxies have failed, try reloading them
        logger.error("All proxies have failed. Attempting to reload.")
        self.failed_proxies.clear()
        self.load_proxies(use_free_proxies_as_fallback=True)
        return self.proxies[0] if self.proxies else None

    def _rotate_proxy(self):
        """Rotates to the next proxy in the list."""
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)

    def mark_current_proxy_failed(self):
        """Marks the currently used proxy as failed and rotates to the next one."""
        if not self.proxies:
            return
        logger.warning(f"Marking proxy {self.proxies[self.current_proxy_index]} as failed.")
        self.failed_proxies.add(self.current_proxy_index)
        self._rotate_proxy()