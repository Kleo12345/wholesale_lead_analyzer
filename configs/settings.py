# wholesale_lead_analyzer/configs/settings.py

# ==============================================================================
# NEW: ANALYSIS & SCRAPING CONFIGURATION
# ==============================================================================

# --- General & Location Settings ---
# Filter leads to only include those from this country.
# This assumes your input CSV will have a 'location' or similar column.
# Set to None to disable filtering.
TARGET_COUNTRY = "USA"

# --- Rate Limiting & Proxies ---
# The minimum and maximum delay (in seconds) between web requests.
# This helps avoid getting blacklisted. Values are for an aggressive but safe approach.
RATE_LIMIT_MIN_DELAY = 1.5
RATE_LIMIT_MAX_DELAY = 3.5

# A list of proxies to rotate through for scraping.
# Using proxies is highly recommended for any serious scraping to avoid IP bans.
# Format: "http://user:pass@host:port" or "http://host:port"
# Add your real proxy IPs here. Leave empty if you don't have any.
PROXIES = [
    # "http://user1:password@proxy1.com:8080", # Example with auth
    # "http://192.168.1.1:8888",              # Example without auth
]

ZILLOW_ZUID = "" # <--- PASTE YOUR ZUID VALUE HERE
# --- Enrichment Service Preferences ---

# Social Media Analysis
# List the platforms to focus on. Options: 'linkedin', 'instagram'
# The script will only scrape the platforms listed here.
SOCIAL_PLATFORM_FOCUS = ['linkedin', 'instagram']

# Public Records Analysis
# As discussed, these are the types of records we would prioritize if implementing
# specific county scrapers.
# - 'property_ownership': Confirms if the person owns property.
# - 'tax_liens': Shows financial distress (delinquent property taxes).
# - 'code_violations': Indicates property neglect and a potential desire to sell.
PUBLIC_RECORD_PRIORITY = ['property_ownership', 'tax_liens', 'code_violations']

# Email Validation
# 'basic': Fast check for valid format and common disposable domains (current implementation).
# 'advanced': (Future enhancement) Could use a paid API for DNS/MX checks to confirm existence.
EMAIL_VALIDATION_LEVEL = 'basic'


# ==============================================================================
# EXISTING: KEYWORD & CATEGORY DEFINITIONS
# ==============================================================================

# Financial stress indicators (max score contribution defined in scorer)
FINANCIAL_STRESS_KEYWORDS = [
    'need cash', 'quick sale', 'cash flow', 'struggling',
    'financial difficulty', 'bankruptcy', 'foreclosure',
    'divorce', 'relocating', 'moving', 'downsizing',
    'retirement', 'health issues', 'urgent', 'asap',
    'immediate', 'distressed', 'motivated seller',
    'must sell', 'below market', 'owner financing'
]

# Property ownership indicators (max score contribution defined in scorer)
PROPERTY_KEYWORDS = [
    'landlord', 'rental property', 'investment property',
    'property owner', 'fixer upper', 'renovation',
    'handyman', 'contractor', 'flipping', 'portfolio',
    'multiple units', 'apartment building', 'real estate',
    'property management', 'rehab', 'wholesale', 'investor'
]

# High-value business categories
HIGH_VALUE_CATEGORIES = [
    'construction', 'contractor', 'handyman', 'property management',
    'real estate', 'landlord', 'rental', 'property services',
    'home improvement', 'renovation'
]

# Medium-value categories
MEDIUM_VALUE_CATEGORIES = [
    'entrepreneur', 'small business', 'business owner',
    'consulting', 'business service', 'plumbing', 'electrical',
    'hvac', 'roofing', 'landscaping', 'home services'
]

# Lifestyle categories
LIFESTYLE_CATEGORIES = [
    'life coach', 'personal development', 'digital creator',
    'influencer', 'blogger', 'content creator', 'coach'
]

# Website keywords for property-related content
WEBSITE_KEYWORDS = [
    'sell your house', 'we buy houses', 'cash for homes',
    'property investment', 'real estate services',
    'home buying', 'property management', 'construction',
    'renovation', 'flipping', 'wholesale', 'investor'
]

# User agents for web scraping to avoid being blocked
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

# Common disposable email domains for validation
DISPOSABLE_DOMAINS = [
    '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
    'mailinator.com', 'throwaway.email'
]