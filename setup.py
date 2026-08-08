#!/usr/bin/env python3
"""
LMLabs Agency System — Quick Setup
Run this once: python setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print()
    print("=" * 60)
    print("  LMLabs Client Acquisition System — Setup")
    print("=" * 60)
    print()

    # 1. Check Python version
    print(f"[1/5] Python version: {sys.version.split()[0]}", end="")
    if sys.version_info >= (3, 8):
        print(" ✓")
    else:
        print(" ✗ — Need Python 3.8+")
        return

    # 2. Install dependencies
    print("[2/5] Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("      Dependencies installed ✓")
    except Exception as e:
        print(f"      Warning: pip install failed — {e}")
        print("      Try manually: pip install -r requirements.txt")

    # 3. Create data directories
    print("[3/5] Creating data directories...")
    data_dir = Path(__file__).parent / "data"
    exports_dir = data_dir / "exports"
    data_dir.mkdir(exist_ok=True)
    exports_dir.mkdir(exist_ok=True)
    print("      data/ and data/exports/ created ✓")

    # 4. Initialize CRM database
    print("[4/5] Initializing CRM database...")
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from crm.database import LeadDatabase
        db = LeadDatabase()
        db.close()
        print("      Database initialized ✓")
    except Exception as e:
        print(f"      Error: {e}")
        return

    # 5. Check API key
    print("[5/5] Checking API key...")
    from config import GOOGLE_PLACES_API_KEY
    if GOOGLE_PLACES_API_KEY and GOOGLE_PLACES_API_KEY != "your-google-places-api-key":
        print("      Google Places API key found ✓")
        api_ready = True
    else:
        print("      No API key set (optional — you can do manual outreach without it)")
        api_ready = False

    # Done
    print()
    print("=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print()
    print("  NEXT STEPS:")
    print()

    if api_ready:
        print("  1. Find leads automatically:")
        print("     python run.py find-leads --niche restaurant --city Thessaloniki --save")
        print()
        print("  2. Analyze their websites:")
        print("     python run.py analyze-all")
        print()
        print("  3. Generate outreach messages:")
        print("     python run.py generate-message --lead-id 1 --type all")
        print()
    else:
        print("  OPTION A — Manual outreach (start TODAY):")
        print("  1. Open Google Maps and search for businesses")
        print("  2. Add leads manually:")
        print('     python run.py add-lead --name "Restaurant Name" --phone "+30..." --city Thessaloniki --niche restaurant')
        print("  3. Generate messages:")
        print("     python run.py generate-message --lead-id 1 --type email")
        print()
        print("  OPTION B — Set up automated search:")
        print("  1. Get API key: https://console.cloud.google.com/apis/credentials")
        print("  2. Edit config.py and paste your key")
        print("  3. Run: python run.py find-leads --niche restaurant --city Thessaloniki --save")
        print()

    print("  OTHER COMMANDS:")
    print("  python run.py stats            — View pipeline stats")
    print("  python run.py list             — View all leads")
    print("  python run.py templates        — View outreach templates")
    print("  python run.py export --file leads.csv  — Export to CSV")
    print("  python app.py                  — Launch web dashboard (localhost:5000)")
    print()
    print("  Start sending messages. Your first client is waiting.")
    print()


if __name__ == "__main__":
    main()
