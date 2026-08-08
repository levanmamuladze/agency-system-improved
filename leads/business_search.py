"""
Automated Business Search
Finds businesses that need websites using Google Places API and web scraping.
"""

import requests
import time
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from urllib.parse import quote_plus
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GOOGLE_PLACES_API_KEY, SEARCH_SETTINGS


@dataclass
class BusinessLead:
    """A potential lead from search results."""
    name: str
    address: str
    phone: str
    website: str
    rating: float
    review_count: int
    place_id: str
    niche: str
    city: str
    has_website: bool
    website_quality: str  # 'none', 'bad', 'basic', 'good'
    priority: str  # 'hot', 'warm', 'cold'


class BusinessSearcher:
    """
    Search for businesses that need websites.
    
    Supports:
    - Google Places API (recommended, requires API key)
    - Fallback scraping methods
    """
    
    # Business types that commonly need website help
    NICHES = {
        'barbershop': ['barber shop', 'barbershop', 'mens haircut'],
        'salon': ['hair salon', 'beauty salon', 'nail salon'],
        'restaurant': ['restaurant', 'diner', 'eatery'],
        'cafe': ['cafe', 'coffee shop', 'espresso bar'],
        'taverna': ['taverna', 'greek tavern', 'meze restaurant'],
        'plumber': ['plumber', 'plumbing service', 'plumbing company'],
        'electrician': ['electrician', 'electrical contractor', 'electrical service'],
        'hvac': ['hvac', 'air conditioning', 'heating cooling'],
        'landscaping': ['landscaping', 'lawn care', 'lawn service'],
        'cleaning': ['cleaning service', 'house cleaning', 'janitorial'],
        'auto_repair': ['auto repair', 'mechanic', 'car repair'],
        'dentist': ['dentist', 'dental office', 'dental clinic'],
        'gym': ['gym', 'fitness center', 'personal trainer'],
        'daycare': ['daycare', 'child care', 'preschool'],
        'pet_services': ['pet grooming', 'dog grooming', 'pet salon', 'veterinary'],
        'florist': ['florist', 'flower shop', 'floral'],
        'bakery': ['bakery', 'cake shop', 'pastry shop'],
        'photography': ['photographer', 'photography studio', 'photo studio'],
        'real_estate': ['real estate agent', 'realtor', 'real estate office'],
        'insurance': ['insurance agent', 'insurance agency'],
        'accountant': ['accountant', 'cpa', 'tax preparer', 'bookkeeper'],
        'lawyer': ['lawyer', 'attorney', 'law office'],
    }
    
    def __init__(self, api_key: str = None):
        """
        Initialize searcher.
        
        Args:
            api_key: Google Places API key. If None, uses config or limited scraping.
        """
        self.api_key = api_key or GOOGLE_PLACES_API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def search_google_places(
        self,
        query: str,
        location: str,
        radius_meters: int = 10000,
        max_results: int = 60
    ) -> List[Dict]:
        """
        Search Google Places API for businesses.
        
        Args:
            query: Business type (e.g., "barber shop")
            location: City or address (e.g., "Austin, TX")
            radius_meters: Search radius (default 10km)
            max_results: Maximum results to return (max 60 with pagination)
            
        Returns:
            List of place dictionaries
        """
        if not self.api_key or self.api_key == 'your-google-places-api-key':
            print("⚠️  No Google Places API key configured.")
            print("   Get one at: https://console.cloud.google.com/apis/credentials")
            print("   Then add it to config.py")
            return []
        
        # First, geocode the location
        geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
        geo_response = self.session.get(geocode_url, params={
            'address': location,
            'key': self.api_key
        })
        
        if geo_response.status_code != 200:
            print(f"❌ Geocoding failed: {geo_response.status_code}")
            return []
            
        geo_data = geo_response.json()
        if not geo_data.get('results'):
            print(f"❌ Could not find location: {location}")
            return []
            
        lat = geo_data['results'][0]['geometry']['location']['lat']
        lng = geo_data['results'][0]['geometry']['location']['lng']
        
        # Search for places
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        all_results = []
        next_page_token = None
        
        while len(all_results) < max_results:
            params = {
                'location': f"{lat},{lng}",
                'radius': radius_meters,
                'keyword': query,
                'key': self.api_key
            }
            
            if next_page_token:
                params = {'pagetoken': next_page_token, 'key': self.api_key}
                time.sleep(2)  # Required delay for pagination
            
            response = self.session.get(places_url, params=params)
            
            if response.status_code != 200:
                print(f"❌ Places API error: {response.status_code}")
                break
                
            data = response.json()
            
            if data.get('status') != 'OK' and data.get('status') != 'ZERO_RESULTS':
                print(f"❌ API error: {data.get('status')} - {data.get('error_message', '')}")
                break
                
            results = data.get('results', [])
            all_results.extend(results)
            
            next_page_token = data.get('next_page_token')
            if not next_page_token:
                break
                
            print(f"   Found {len(all_results)} businesses so far...")
        
        return all_results[:max_results]
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed info about a place including website.
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Place details dictionary
        """
        if not self.api_key or self.api_key == 'your-google-places-api-key':
            return None
            
        url = "https://maps.googleapis.com/maps/api/place/details/json"
        response = self.session.get(url, params={
            'place_id': place_id,
            'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status,opening_hours',
            'key': self.api_key
        })
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'OK':
                return data.get('result')
        return None
    
    def check_website_quality(self, url: str) -> str:
        """
        Quick check of website quality.
        
        Returns: 'none', 'bad', 'basic', or 'good'
        """
        if not url:
            return 'none'
            
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            
            if response.status_code != 200:
                return 'bad'
            
            html = response.text.lower()
            
            # Check for signs of a bad/basic website
            bad_signs = [
                'wix.com' in response.url,
                'weebly.com' in response.url,
                'squarespace.com' in response.url,
                'godaddy' in response.url,
                'under construction' in html,
                'coming soon' in html,
                'website coming' in html,
                len(html) < 5000,  # Very short page
            ]
            
            basic_signs = [
                'wordpress' in html and 'theme' in html,
                response.url.count('/') <= 3,  # Single page
                'template' in html,
            ]
            
            # Check for mobile responsiveness
            has_viewport = 'viewport' in html
            
            if sum(bad_signs) >= 2:
                return 'bad'
            elif sum(basic_signs) >= 2 or not has_viewport:
                return 'basic'
            else:
                return 'good'
                
        except Exception:
            return 'bad'
    
    def search_niche(
        self,
        niche: str,
        city: str,
        state: str = '',
        max_results: int = 50,
        check_websites: bool = True
    ) -> List[BusinessLead]:
        """
        Search for businesses in a specific niche and location.
        
        Args:
            niche: Business type (use key from NICHES or custom query)
            city: City name
            state: State abbreviation (optional)
            max_results: Max businesses to find
            check_websites: Whether to check website quality (slower but more accurate)
            
        Returns:
            List of BusinessLead objects, sorted by priority
        """
        # Get search terms for this niche
        if niche in self.NICHES:
            search_terms = self.NICHES[niche]
        else:
            search_terms = [niche]
        
        location = f"{city}, {state}".strip(', ')
        all_leads = []
        seen_place_ids = set()
        
        print(f"\n🔍 Searching for {niche} businesses in {location}...")
        
        for term in search_terms:
            print(f"   Searching: {term}...")
            places = self.search_google_places(term, location, max_results=max_results)
            
            for place in places:
                place_id = place.get('place_id')
                if place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)
                
                # Get detailed info
                details = self.get_place_details(place_id)
                if not details:
                    continue
                
                # Skip permanently closed businesses
                if place.get('business_status') == 'CLOSED_PERMANENTLY':
                    continue
                
                website = details.get('website', '')
                has_website = bool(website)
                
                # Check website quality if enabled
                if check_websites and has_website:
                    website_quality = self.check_website_quality(website)
                    time.sleep(0.5)  # Be nice to servers
                else:
                    website_quality = 'none' if not has_website else 'unknown'
                
                # Determine priority
                if not has_website:
                    priority = 'hot'
                elif website_quality in ['bad', 'basic']:
                    priority = 'warm'
                else:
                    priority = 'cold'
                
                lead = BusinessLead(
                    name=details.get('name', ''),
                    address=details.get('formatted_address', ''),
                    phone=details.get('formatted_phone_number', ''),
                    website=website,
                    rating=place.get('rating', 0),
                    review_count=place.get('user_ratings_total', 0),
                    place_id=place_id,
                    niche=niche,
                    city=city,
                    has_website=has_website,
                    website_quality=website_quality,
                    priority=priority
                )
                
                all_leads.append(lead)
                
                if len(all_leads) >= max_results:
                    break
            
            if len(all_leads) >= max_results:
                break
        
        # Sort by priority (hot first, then warm, then cold)
        priority_order = {'hot': 0, 'warm': 1, 'cold': 2}
        all_leads.sort(key=lambda x: (priority_order[x.priority], -x.review_count))
        
        return all_leads
    
    def search_multiple_niches(
        self,
        niches: List[str],
        city: str,
        state: str = '',
        results_per_niche: int = 20
    ) -> List[BusinessLead]:
        """
        Search multiple niches in one city.
        
        Args:
            niches: List of niche names
            city: City name
            state: State abbreviation
            results_per_niche: Max results per niche
            
        Returns:
            Combined list of leads
        """
        all_leads = []
        
        for niche in niches:
            leads = self.search_niche(niche, city, state, results_per_niche)
            all_leads.extend(leads)
            print(f"   ✓ Found {len(leads)} {niche} leads")
            time.sleep(1)
        
        return all_leads
    
    def export_leads(self, leads: List[BusinessLead], filename: str):
        """Export leads to CSV file."""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            if not leads:
                return
            writer = csv.DictWriter(f, fieldnames=asdict(leads[0]).keys())
            writer.writeheader()
            for lead in leads:
                writer.writerow(asdict(lead))
        
        print(f"✓ Exported {len(leads)} leads to {filename}")


class YelpSearcher:
    """
    Search Yelp for businesses.
    Requires Yelp Fusion API key (free tier: 5000 calls/day).
    Get key at: https://www.yelp.com/developers/v3/manage_app
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.yelp.com/v3"
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}'
            })
    
    def search(
        self,
        term: str,
        location: str,
        limit: int = 50
    ) -> List[Dict]:
        """
        Search Yelp for businesses.
        
        Args:
            term: Search term (e.g., "barber")
            location: Location string (e.g., "Austin, TX")
            limit: Max results (max 50 per request)
            
        Returns:
            List of business dictionaries
        """
        if not self.api_key:
            print("⚠️  No Yelp API key configured.")
            print("   Get one at: https://www.yelp.com/developers/v3/manage_app")
            return []
        
        url = f"{self.base_url}/businesses/search"
        
        all_results = []
        offset = 0
        
        while len(all_results) < limit:
            response = self.session.get(url, params={
                'term': term,
                'location': location,
                'limit': min(50, limit - len(all_results)),
                'offset': offset
            })
            
            if response.status_code != 200:
                print(f"❌ Yelp API error: {response.status_code}")
                break
            
            data = response.json()
            businesses = data.get('businesses', [])
            
            if not businesses:
                break
                
            all_results.extend(businesses)
            offset += len(businesses)
            
            if len(businesses) < 50:
                break
        
        return all_results
    
    def to_leads(self, businesses: List[Dict], niche: str) -> List[BusinessLead]:
        """Convert Yelp results to BusinessLead objects."""
        leads = []
        
        for biz in businesses:
            # Yelp doesn't provide website info directly
            # Would need to scrape individual pages or use business details endpoint
            
            lead = BusinessLead(
                name=biz.get('name', ''),
                address=', '.join(biz.get('location', {}).get('display_address', [])),
                phone=biz.get('phone', ''),
                website='',  # Yelp doesn't expose this in search
                rating=biz.get('rating', 0),
                review_count=biz.get('review_count', 0),
                place_id=biz.get('id', ''),
                niche=niche,
                city=biz.get('location', {}).get('city', ''),
                has_website=False,  # Unknown
                website_quality='unknown',
                priority='warm'  # Default since we don't know website status
            )
            leads.append(lead)
        
        return leads


def quick_search(niche: str, city: str, state: str = '', max_results: int = 30):
    """
    Quick search function for command line use.
    
    Example:
        quick_search('barbershop', 'Austin', 'TX')
    """
    searcher = BusinessSearcher()
    leads = searcher.search_niche(niche, city, state, max_results)
    
    print(f"\n{'='*60}")
    print(f"Found {len(leads)} potential leads")
    print(f"{'='*60}\n")
    
    hot_leads = [l for l in leads if l.priority == 'hot']
    warm_leads = [l for l in leads if l.priority == 'warm']
    
    print(f"🔥 HOT LEADS (no website): {len(hot_leads)}")
    for lead in hot_leads[:10]:
        print(f"   • {lead.name}")
        print(f"     📍 {lead.address}")
        print(f"     📞 {lead.phone}")
        print(f"     ⭐ {lead.rating} ({lead.review_count} reviews)")
        print()
    
    print(f"\n🌡️  WARM LEADS (bad/basic website): {len(warm_leads)}")
    for lead in warm_leads[:10]:
        print(f"   • {lead.name}")
        print(f"     🌐 {lead.website}")
        print(f"     📞 {lead.phone}")
        print(f"     Quality: {lead.website_quality}")
        print()
    
    return leads


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Search for business leads')
    parser.add_argument('niche', help='Business type (e.g., barbershop, restaurant)')
    parser.add_argument('city', help='City name')
    parser.add_argument('--state', '-s', default='', help='State abbreviation')
    parser.add_argument('--max', '-m', type=int, default=30, help='Max results')
    parser.add_argument('--export', '-e', help='Export to CSV file')
    
    args = parser.parse_args()
    
    leads = quick_search(args.niche, args.city, args.state, args.max)
    
    if args.export:
        searcher = BusinessSearcher()
        searcher.export_leads(leads, args.export)
