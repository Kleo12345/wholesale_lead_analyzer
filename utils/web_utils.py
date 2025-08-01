# wholesale_lead_analyzer/utils/web_utils.py

import time
import random
from configs import settings

def get_random_user_agent() -> str:
    """Returns a random user-agent string from settings."""
    return random.choice(settings.USER_AGENTS)

def dynamic_sleep():
    """
    Pauses execution for a short, random interval based on RATE_LIMIT settings
    to respect website rate limits and avoid blacklisting.
    """
    time.sleep(random.uniform(settings.RATE_LIMIT_MIN_DELAY, settings.RATE_LIMIT_MAX_DELAY))