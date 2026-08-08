"""
Lead Finder Module

Helps organize and validate leads found manually through:
- Google Maps searches
- Yelp browsing
- Facebook business pages
- Local directories
- Yellow Pages

Note: Automated scraping of Google/Yelp violates their ToS.
This module focuses on organizing manually collected leads.
"""

import re
import csv
from dataclasses import dataclass, asdict
from typing import Optional, List
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import NICHES


@dataclass
class Lead:
    """Represents a business lead."""
    name: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    niche: Optional[str] = None
    source: str = "manual"  # Where you found them
    notes: str = ""
    
    def to_dict(self):
        return asdict(self)


class LeadFinder:
    """
    Helps organize and validate manually collected leads.
    
    FINDING LEADS - Manual Methods:
    
    1. GOOGLE MAPS METHOD (Best for local businesses)
       - Search: "[niche] in [city]" (e.g., "barbershops in Chicago")
       - Click each result, check if they have a website
       - If website exists: note it for analysis
       - If no website: EXCELLENT lead - note their phone/address
       
    2. YELP METHOD (Good for service businesses)
       - Browse: yelp.com/search?find_desc=[niche]&find_loc=[city]
       - Sort by "Newest" to find new businesses
       - Check each listing's website link
       - Many have outdated/no websites
       
    3. FACEBOOK METHOD (Good for small businesses)
       - Search: "[niche] [city]" on Facebook
       - Filter by "Pages"
       - Check their linked website
       - Message them directly on FB if no website
       
    4. LOCAL DIRECTORIES
       - Yellow Pages (yellowpages.com)
       - Chamber of Commerce websites
       - Local business associations
       - Industry-specific directories
    """
    
    def __init__(self):
        self.leads: List[Lead] = []
    
    def add_lead(
        self,
        name: str,
        website: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        niche: Optional[str] = None,
        source: str = "manual",
        notes: str = ""
    ) -> Lead:
        """
        Add a new lead to the collection.
        
        Args:
            name: Business name (required)
            website: Website URL (can be None for no-website leads)
            email: Contact email
            phone: Phone number
            city: City location
            state: State/region
            niche: Business type (restaurant, barbershop, etc.)
            source: Where you found them (google_maps, yelp, facebook, etc.)
            notes: Any additional notes
        
        Returns:
            The created Lead object
        """
        # Clean and validate inputs
        website = self._clean_website(website) if website else None
        email = self._clean_email(email) if email else None
        phone = self._clean_phone(phone) if phone else None
        niche = self._validate_niche(niche)
        
        lead = Lead(
            name=name.strip(),
            website=website,
            email=email,
            phone=phone,
            city=city.strip() if city else None,
            state=state.strip() if state else None,
            niche=niche,
            source=source,
            notes=notes
        )
        
        self.leads.append(lead)
        return lead
    
    def _clean_website(self, url: str) -> str:
        """Clean and normalize website URL."""
        url = url.strip().lower()
        
        # Remove common prefixes for consistency
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        
        # Remove trailing slashes
        url = url.rstrip('/')
        
        return url
    
    def _clean_email(self, email: str) -> Optional[str]:
        """Validate and clean email."""
        email = email.strip().lower()
        
        # Basic email validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            return email
        return None
    
    def _clean_phone(self, phone: str) -> str:
        """Clean phone number, keep only digits and +."""
        # Keep digits and + sign
        cleaned = re.sub(r'[^\d+]', '', phone)
        return cleaned
    
    def _validate_niche(self, niche: Optional[str]) -> Optional[str]:
        """Validate niche against allowed list."""
        if not niche:
            return None
        
        niche = niche.strip().lower().replace(' ', '_')
        
        if niche in NICHES:
            return niche
        
        # Try to match partial
        for valid_niche in NICHES:
            if niche in valid_niche or valid_niche in niche:
                return valid_niche
        
        return "other"
    
    def import_from_csv(self, filepath: str) -> List[Lead]:
        """
        Import leads from a CSV file.
        
        Expected columns:
        name, website, email, phone, city, state, niche, source, notes
        
        Returns:
            List of imported Lead objects
        """
        imported = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                lead = self.add_lead(
                    name=row.get('name', ''),
                    website=row.get('website'),
                    email=row.get('email'),
                    phone=row.get('phone'),
                    city=row.get('city'),
                    state=row.get('state'),
                    niche=row.get('niche'),
                    source=row.get('source', 'csv_import'),
                    notes=row.get('notes', '')
                )
                imported.append(lead)
        
        return imported
    
    def export_to_csv(self, filepath: str) -> None:
        """Export all leads to a CSV file."""
        if not self.leads:
            print("No leads to export")
            return
        
        fieldnames = [
            'name', 'website', 'email', 'phone',
            'city', 'state', 'niche', 'source', 'notes'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for lead in self.leads:
                writer.writerow(lead.to_dict())
        
        print(f"Exported {len(self.leads)} leads to {filepath}")
    
    def get_no_website_leads(self) -> List[Lead]:
        """Get leads that don't have a website - BEST prospects."""
        return [lead for lead in self.leads if not lead.website]
    
    def get_leads_by_niche(self, niche: str) -> List[Lead]:
        """Filter leads by niche."""
        niche = niche.lower().replace(' ', '_')
        return [lead for lead in self.leads if lead.niche == niche]
    
    def get_leads_by_city(self, city: str) -> List[Lead]:
        """Filter leads by city."""
        city = city.lower()
        return [lead for lead in self.leads if lead.city and lead.city.lower() == city]


# =============================================================================
# SEARCH TEMPLATES - Copy these to your browser
# =============================================================================

SEARCH_TEMPLATES = {
    "google_maps": "https://www.google.com/maps/search/{niche}+in+{city}",
    "yelp": "https://www.yelp.com/search?find_desc={niche}&find_loc={city}",
    "facebook": "https://www.facebook.com/search/pages/?q={niche}%20{city}",
    "yellowpages": "https://www.yellowpages.com/search?search_terms={niche}&geo_location_terms={city}",
}


def generate_search_urls(niche: str, city: str) -> dict:
    """
    Generate search URLs for finding leads.
    
    Usage:
        urls = generate_search_urls("barbershop", "Chicago")
        # Open each URL in browser, manually collect leads
    """
    return {
        platform: url.format(niche=niche.replace(' ', '+'), city=city.replace(' ', '+'))
        for platform, url in SEARCH_TEMPLATES.items()
    }


def print_lead_finding_guide():
    """Print a guide for manually finding leads."""
    guide = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        LEAD FINDING GUIDE                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP 1: PICK YOUR NICHE + CITY
─────────────────────────────────
Start with ONE niche and ONE city. Examples:
  • Barbershops in Chicago
  • Restaurants in Austin
  • Dentists in Miami

STEP 2: GOOGLE MAPS (Best Method)
─────────────────────────────────
1. Go to Google Maps
2. Search: "[niche] in [city]"
3. For EACH result:
   - Click it
   - Look at their website link
   - If NO website → Add to leads (HOT LEAD!)
   - If website looks OLD/BAD → Add to leads (GOOD LEAD)
   - Note their phone number and address

STEP 3: LOOK FOR THESE RED FLAGS
─────────────────────────────────
✓ No website at all
✓ Website is just a Facebook page
✓ Website looks like it's from 2005
✓ Website doesn't work on mobile
✓ "Under construction" pages
✓ Broken images
✓ No contact form
✓ Generic Wix/Weebly template look

STEP 4: COLLECT THIS INFO
─────────────────────────────────
For each lead, try to get:
  1. Business name (required)
  2. Website (if any)
  3. Phone number (important!)
  4. Email (if visible)
  5. City/Address
  6. Owner name (if visible)

STEP 5: ADD TO SYSTEM
─────────────────────────────────
Run: python run.py add-lead --name "Business" --website "site.com" ...

OR: Add to a CSV and import with:
    python run.py import-csv --file leads.csv

PRO TIPS:
─────────────────────────────────
• Spend 1 hour = collect 20-30 leads
• Focus on businesses that NEED clients (not big chains)
• Look for "Est. 2020+" businesses - they're growing
• Check reviews - active business = more likely to pay
• Avoid chains (McDonald's, Supercuts, etc.)
• Owner-operated businesses are BEST

═══════════════════════════════════════════════════════════════════════════════
"""
    print(guide)


if __name__ == "__main__":
    print_lead_finding_guide()
    
    # Example: Generate search URLs
    print("\nExample Search URLs for 'barbershop' in 'Chicago':")
    urls = generate_search_urls("barbershop", "Chicago")
    for platform, url in urls.items():
        print(f"  {platform}: {url}")
