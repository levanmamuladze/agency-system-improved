"""
Configuration for LMLabs Client Acquisition System

SETUP:
1. Get a Google Places API key: https://console.cloud.google.com/apis/credentials
   Enable: Places API, Geocoding API  |  Cost: first $200/month free
2. Set it below or as env var: export GOOGLE_PLACES_API_KEY=your-key
3. Run: python run.py init
4. Search: python run.py find-leads --niche restaurant --city Thessaloniki --save
"""

import os

# =============================================================================
# LMLABS INFO
# =============================================================================

AGENCY_NAME = "LMLabs"
AGENCY_WEBSITE = "lmlabs.dev"
AGENCY_EMAIL = "lmlabs.dev@gmail.com"
AGENCY_PHONE = "+30 683 678 188"
AGENCY_CALENDLY = "https://calendly.com/lmlabs-dev/30min"  # TODO: Create a Calendly and paste link here
YOUR_NAME = "LMLabs"

DEFAULT_CITY = "Thessaloniki"
DEFAULT_COUNTRY = "Greece"

# =============================================================================
# API KEYS
# =============================================================================

GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "your-google-places-api-key")
YELP_API_KEY = os.environ.get("YELP_API_KEY", "your-yelp-api-key")

# =============================================================================
# SEARCH SETTINGS
# =============================================================================

SEARCH_SETTINGS = {
    "radius_meters": 15000,
    "max_results_per_niche": 50,
    "check_websites": True,
    "delay_between_requests": 0.5,
}

# =============================================================================
# DATABASE
# =============================================================================

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "data", "leads.db")
EXPORT_PATH = os.path.join(os.path.dirname(__file__), "data", "exports")

# =============================================================================
# PACKAGES (EUR)
# =============================================================================

PACKAGES = {
    "starter": {"name": "Starter", "price": 700, "pages": 1, "delivery": "5-7 days"},
    "business": {"name": "Business", "price": 1400, "pages": 5, "delivery": "1-2 weeks"},
    "growth": {"name": "Growth", "price": 2500, "pages": "8-10", "delivery": "2-3 weeks"},
}

# =============================================================================
# LEAD SCORING
# =============================================================================

SCORE_THRESHOLDS = {
    "excellent_lead": 30,
    "good_lead": 50,
    "maybe_lead": 70,
    "skip": 100,
}

SCORING_WEIGHTS = {
    "no_ssl": 20,
    "slow_load": 15,
    "not_mobile_friendly": 20,
    "no_meta_description": 10,
    "no_title": 10,
    "no_h1": 5,
    "no_cta": 15,
    "no_contact_info": 10,
    "outdated_design": 15,
    "broken_images": 10,
}

# =============================================================================
# OUTREACH
# =============================================================================

MAX_FOLLOWUPS = 5
FOLLOWUP_SCHEDULE = [1, 3, 5, 7, 10]

# =============================================================================
# NICHES (Greek market optimized)
# =============================================================================

NICHES = [
    "restaurant", "cafe", "barbershop", "salon", "gym", "fitness",
    "dentist", "doctor", "clinic", "real_estate", "plumber", "electrician",
    "hvac", "landscaping", "cleaning", "lawyer", "accountant", "auto_repair",
    "pet_services", "photography", "bakery", "pharmacy", "hotel", "taverna",
    "mechanic", "other",
]

# =============================================================================
# LEAD STATUSES
# =============================================================================

LEAD_STATUSES = [
    "found", "analyzed", "contacted", "followed_up", "replied",
    "call_booked", "proposal_sent", "closed_won", "closed_lost",
    "not_interested", "invalid",
]

# =============================================================================
# HTTP
# =============================================================================

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 10


def show_config():
    print(f"Agency: {AGENCY_NAME}")
    print(f"Email: {AGENCY_EMAIL}")
    print(f"Phone: {AGENCY_PHONE}")
    print(f"Default city: {DEFAULT_CITY}")
    print(f"Database: {DATABASE_PATH}")
    print(f"Google API key set: {GOOGLE_PLACES_API_KEY != 'your-google-places-api-key'}")
