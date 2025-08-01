# wholesale_lead_analyzer/enrichment/email_validator.py

import re
from typing import Tuple
from configs.settings import DISPOSABLE_DOMAINS

def validate_email_free(email: str) -> Tuple[bool, str]:
    """Free email validation using regex and domain check."""
    if not email:
        return False, "No email"
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Invalid format"
    
    domain = email.split('@')[1].lower()
    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable email"
    
    return True, "Valid"