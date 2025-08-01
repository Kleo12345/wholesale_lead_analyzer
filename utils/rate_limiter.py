# wholesale_lead_analyzer/utils/rate_limiter.py

import time
import random
import logging
from collections import defaultdict, deque
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """Manages request timing to prevent blacklisting."""
    
    def __init__(self):
        # Track requests per domain
        self.domain_requests: Dict[str, deque] = defaultdict(deque)
        
        # Rate limits per domain (requests per minute)
        self.domain_limits = {
            'zillow.com': 6,  # Conservative for Zillow
            'instagram.com': 10,
            'linkedin.com': 8,
            'facebook.com': 5,
            'google.com': 12,
            'default': 10
        }
        
        # Backoff tracking
        self.backoff_until: Dict[str, datetime] = {}
        self.consecutive_failures: Dict[str, int] = defaultdict(int)
        
    def get_domain(self, url: str) -> str:
        """Extract domain from URL."""
        if '//' in url:
            domain = url.split('/')[2]
        else:
            domain = url.split('/')[0]
        return domain.lower()
    
    def can_make_request(self, url: str) -> bool:
        """Check if request can be made without hitting rate limits."""
        domain = self.get_domain(url)
        
        # Check if in backoff period
        if domain in self.backoff_until:
            if datetime.now() < self.backoff_until[domain]:
                return False
            else:
                del self.backoff_until[domain]
        
        # Clean old requests (older than 1 minute)
        now = time.time()
        while (self.domain_requests[domain] and 
               now - self.domain_requests[domain][0] > 60):
            self.domain_requests[domain].popleft()
        
        # Check rate limit
        limit = self.domain_limits.get(domain, self.domain_limits['default'])
        return len(self.domain_requests[domain]) < limit
    
    def wait_if_needed(self, url: str) -> float:
        """Wait if necessary to respect rate limits."""
        domain = self.get_domain(url)
        
        if not self.can_make_request(url):
            # Calculate wait time
            if domain in self.backoff_until:
                wait_time = (self.backoff_until[domain] - datetime.now()).total_seconds()
                if wait_time > 0:
                    logger.info(f"Backing off {domain} for {wait_time:.1f}s")
                    time.sleep(wait_time)
                    return wait_time
            
            # Wait for rate limit window
            if self.domain_requests[domain]:
                oldest_request = self.domain_requests[domain][0]
                wait_time = 60 - (time.time() - oldest_request)
                if wait_time > 0:
                    logger.info(f"Rate limiting {domain} for {wait_time:.1f}s")
                    time.sleep(wait_time)
                    return wait_time
        
        # Add random delay to appear more human-like
        random_delay = self._get_random_delay(domain)
        time.sleep(random_delay)
        
        # Record this request
        self.domain_requests[domain].append(time.time())
        
        return random_delay
    
    def _get_random_delay(self, domain: str) -> float:
        """Get random delay based on domain sensitivity."""
        base_delays = {
            'zillow.com': (2.0, 5.0),
            'instagram.com': (1.5, 3.0),
            'linkedin.com': (2.0, 4.0),
            'facebook.com': (2.5, 5.0),
        }
        
        min_delay, max_delay = base_delays.get(domain, (1.0, 3.0))
        return random.uniform(min_delay, max_delay)
    
    def record_success(self, url: str):
        """Record successful request."""
        domain = self.get_domain(url)
        self.consecutive_failures[domain] = 0
    
    def record_failure(self, url: str, status_code: Optional[int] = None):
        """Record failed request and implement backoff."""
        domain = self.get_domain(url)
        self.consecutive_failures[domain] += 1
        
        # Implement exponential backoff
        failures = self.consecutive_failures[domain]
        
        if status_code == 429:  # Rate limited
            backoff_time = min(300, 30 * (2 ** min(failures, 5)))  # Max 5 minutes
            logger.warning(f"Rate limited on {domain}, backing off for {backoff_time}s")
        elif status_code in [403, 503]:  # Blocked/unavailable
            backoff_time = min(600, 60 * failures)  # Max 10 minutes
            logger.warning(f"Blocked on {domain}, backing off for {backoff_time}s")
        else:
            backoff_time = min(180, 15 * failures)  # Max 3 minutes
        
        self.backoff_until[domain] = datetime.now() + timedelta(seconds=backoff_time)
    
    def get_delay_recommendation(self, domain: str, request_count: int) -> float:
        """Get recommended delay based on request history."""
        base_delay = self._get_random_delay(domain)[1]  # Use max of range
        
        # Increase delay if many recent requests
        if request_count > 50:
            multiplier = min(3.0, 1 + (request_count - 50) / 100)
            base_delay *= multiplier
        
        return base_delay
    
    def reset_domain_limits(self, domain: str):
        """Reset limits for a domain (e.g., after changing proxy)."""
        if domain in self.domain_requests:
            self.domain_requests[domain].clear()
        if domain in self.backoff_until:
            del self.backoff_until[domain]
        self.consecutive_failures[domain] = 0
        logger.info(f"Reset rate limits for {domain}")
    
    def get_status_report(self) -> Dict:
        """Get current rate limiting status."""
        now = datetime.now()
        report = {
            'active_domains': len(self.domain_requests),
            'domains_in_backoff': len([d for d, until in self.backoff_until.items() 
                                     if until > now]),
            'total_failures': sum(self.consecutive_failures.values()),
            'domain_status': {}
        }
        
        for domain in self.domain_requests:
            recent_requests = len(self.domain_requests[domain])
            in_backoff = domain in self.backoff_until and self.backoff_until[domain] > now
            
            report['domain_status'][domain] = {
                'recent_requests': recent_requests,
                'consecutive_failures': self.consecutive_failures[domain],
                'in_backoff': in_backoff,
                'backoff_until': self.backoff_until.get(domain, None)
            }
        
        return report