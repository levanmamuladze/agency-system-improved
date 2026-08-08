"""
Template for local secrets.

SETUP (one time):
  1. Copy this file to config_local.py
       PowerShell:  Copy-Item config_local.example.py config_local.py
  2. Paste your real API key(s) into config_local.py
  3. Run the app — config.py picks them up automatically

config_local.py is gitignored and must NEVER be committed.
Any value set here overrides the matching placeholder in config.py.
"""

GOOGLE_PLACES_API_KEY = "your-google-places-api-key"  # replace in config_local.py
# YELP_API_KEY = "your-yelp-api-key"
