"""
Website Analyzer Module

Analyzes websites and scores them based on quality indicators.
Lower score = worse website = better lead for us.

Checks:
- SSL certificate (HTTPS)
- Mobile responsiveness
- Page load speed
- SEO basics (title, meta, h1)
- Call-to-action presence
- Contact information
- Design age indicators
"""

import re
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import SCORING_WEIGHTS, USER_AGENT, REQUEST_TIMEOUT


@dataclass
class WebsiteIssue:
    """Represents a single issue found on a website."""
    name: str
    description: str
    severity: str  # "critical", "major", "minor"
    points_deducted: int
    fix_suggestion: str


@dataclass
class AnalysisResult:
    """Complete analysis result for a website."""
    url: str
    score: int  # 0-100, lower = worse website
    issues: List[WebsiteIssue] = field(default_factory=list)
    load_time: float = 0.0
    has_ssl: bool = False
    is_mobile_friendly: bool = True
    has_title: bool = False
    has_meta_description: bool = False
    has_h1: bool = False
    has_cta: bool = False
    has_contact_info: bool = False
    is_reachable: bool = True
    raw_html: str = ""
    
    @property
    def lead_quality(self) -> str:
        """Return lead quality rating based on score."""
        if self.score <= 30:
            return "EXCELLENT"  # Website is terrible
        elif self.score <= 50:
            return "GOOD"       # Many issues
        elif self.score <= 70:
            return "MAYBE"      # Some issues
        else:
            return "SKIP"       # Website is decent
    
    @property
    def issue_summary(self) -> List[str]:
        """Return list of issue descriptions for outreach."""
        return [issue.description for issue in self.issues]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "url": self.url,
            "score": self.score,
            "lead_quality": self.lead_quality,
            "issues": [
                {
                    "name": i.name,
                    "description": i.description,
                    "severity": i.severity,
                    "fix_suggestion": i.fix_suggestion
                }
                for i in self.issues
            ],
            "load_time": self.load_time,
            "has_ssl": self.has_ssl,
            "is_mobile_friendly": self.is_mobile_friendly,
            "has_title": self.has_title,
            "has_meta_description": self.has_meta_description,
            "has_h1": self.has_h1,
            "has_cta": self.has_cta,
            "has_contact_info": self.has_contact_info,
            "is_reachable": self.is_reachable,
        }


class WebsiteAnalyzer:
    """
    Analyzes websites and scores them for lead quality.
    
    Usage:
        analyzer = WebsiteAnalyzer()
        result = analyzer.analyze("example.com")
        print(f"Score: {result.score} - {result.lead_quality}")
    """
    
    def __init__(self):
        self.session = None
    
    def _ensure_session(self):
        """Create requests session if needed."""
        if self.session is None:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            })
    
    def _normalize_url(self, url: str) -> tuple:
        """
        Normalize URL and return (http_url, https_url).
        
        Returns both versions to test SSL.
        """
        url = url.strip().lower()
        
        # Remove protocol
        url = re.sub(r'^https?://', '', url)
        url = re.sub(r'^www\.', '', url)
        url = url.rstrip('/')
        
        return (f"http://{url}", f"https://{url}")
    
    def analyze(self, url: str) -> AnalysisResult:
        """
        Analyze a website and return quality score.
        
        Args:
            url: Website URL to analyze
            
        Returns:
            AnalysisResult with score and issues
        """
        self._ensure_session()
        
        http_url, https_url = self._normalize_url(url)
        result = AnalysisResult(url=url, score=100)  # Start at 100
        
        # Try to fetch the page
        html = ""
        start_time = time.time()
        
        # First try HTTPS
        try:
            response = self.session.get(
                https_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True
            )
            result.load_time = time.time() - start_time
            result.has_ssl = True
            html = response.text
            result.raw_html = html
            
        except Exception:
            # Try HTTP if HTTPS fails
            try:
                start_time = time.time()
                response = self.session.get(
                    http_url,
                    timeout=REQUEST_TIMEOUT,
                    allow_redirects=True
                )
                result.load_time = time.time() - start_time
                result.has_ssl = False
                html = response.text
                result.raw_html = html
                
            except Exception as e:
                # Website is unreachable
                result.is_reachable = False
                result.score = 0  # Best lead - they have no working website!
                result.issues.append(WebsiteIssue(
                    name="unreachable",
                    description="Website is not accessible",
                    severity="critical",
                    points_deducted=100,
                    fix_suggestion="They need a completely new website"
                ))
                return result
        
        # Analyze the HTML
        result = self._analyze_html(result, html)
        
        return result
    
    def _analyze_html(self, result: AnalysisResult, html: str) -> AnalysisResult:
        """Analyze HTML content and update result."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'lxml')
        
        # Check SSL
        if not result.has_ssl:
            result.score -= SCORING_WEIGHTS["no_ssl"]
            result.issues.append(WebsiteIssue(
                name="no_ssl",
                description="No HTTPS security certificate",
                severity="critical",
                points_deducted=SCORING_WEIGHTS["no_ssl"],
                fix_suggestion="Install an SSL certificate for security"
            ))
        
        # Check load time
        if result.load_time > 3.0:
            result.score -= SCORING_WEIGHTS["slow_load"]
            result.issues.append(WebsiteIssue(
                name="slow_load",
                description=f"Slow loading ({result.load_time:.1f}s)",
                severity="major",
                points_deducted=SCORING_WEIGHTS["slow_load"],
                fix_suggestion="Optimize images and hosting for faster speed"
            ))
        
        # Check title tag
        title = soup.find('title')
        if not title or not title.get_text().strip():
            result.has_title = False
            result.score -= SCORING_WEIGHTS["no_title"]
            result.issues.append(WebsiteIssue(
                name="no_title",
                description="Missing page title (bad for SEO)",
                severity="major",
                points_deducted=SCORING_WEIGHTS["no_title"],
                fix_suggestion="Add a descriptive title tag"
            ))
        else:
            result.has_title = True
        
        # Check meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if not meta_desc or not meta_desc.get('content', '').strip():
            result.has_meta_description = False
            result.score -= SCORING_WEIGHTS["no_meta_description"]
            result.issues.append(WebsiteIssue(
                name="no_meta_description",
                description="Missing meta description (hurts Google rankings)",
                severity="major",
                points_deducted=SCORING_WEIGHTS["no_meta_description"],
                fix_suggestion="Add a compelling meta description"
            ))
        else:
            result.has_meta_description = True
        
        # Check H1 tag
        h1 = soup.find('h1')
        if not h1 or not h1.get_text().strip():
            result.has_h1 = False
            result.score -= SCORING_WEIGHTS["no_h1"]
            result.issues.append(WebsiteIssue(
                name="no_h1",
                description="Missing main heading (H1)",
                severity="minor",
                points_deducted=SCORING_WEIGHTS["no_h1"],
                fix_suggestion="Add a clear H1 heading"
            ))
        else:
            result.has_h1 = True
        
        # Check mobile friendliness (viewport meta)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            result.is_mobile_friendly = False
            result.score -= SCORING_WEIGHTS["not_mobile_friendly"]
            result.issues.append(WebsiteIssue(
                name="not_mobile_friendly",
                description="Not mobile-friendly (no viewport)",
                severity="critical",
                points_deducted=SCORING_WEIGHTS["not_mobile_friendly"],
                fix_suggestion="Make the website responsive for mobile"
            ))
        
        # Check for CTA (buttons, forms, contact links)
        result.has_cta = self._check_cta(soup)
        if not result.has_cta:
            result.score -= SCORING_WEIGHTS["no_cta"]
            result.issues.append(WebsiteIssue(
                name="no_cta",
                description="No clear call-to-action (no buttons/forms)",
                severity="major",
                points_deducted=SCORING_WEIGHTS["no_cta"],
                fix_suggestion="Add clear CTAs like 'Book Now' or 'Contact Us'"
            ))
        
        # Check for contact info
        result.has_contact_info = self._check_contact_info(soup, html)
        if not result.has_contact_info:
            result.score -= SCORING_WEIGHTS["no_contact_info"]
            result.issues.append(WebsiteIssue(
                name="no_contact_info",
                description="No visible phone or email",
                severity="major",
                points_deducted=SCORING_WEIGHTS["no_contact_info"],
                fix_suggestion="Add contact info prominently"
            ))
        
        # Check for outdated design indicators
        if self._check_outdated_design(soup, html):
            result.score -= SCORING_WEIGHTS["outdated_design"]
            result.issues.append(WebsiteIssue(
                name="outdated_design",
                description="Design looks outdated",
                severity="major",
                points_deducted=SCORING_WEIGHTS["outdated_design"],
                fix_suggestion="Redesign with modern aesthetics"
            ))
        
        # Check for broken images
        if self._check_broken_images(soup):
            result.score -= SCORING_WEIGHTS["broken_images"]
            result.issues.append(WebsiteIssue(
                name="broken_images",
                description="Potential broken or missing images",
                severity="minor",
                points_deducted=SCORING_WEIGHTS["broken_images"],
                fix_suggestion="Fix image loading issues"
            ))
        
        # Ensure score doesn't go below 0
        result.score = max(0, result.score)
        
        return result
    
    def _check_cta(self, soup) -> bool:
        """Check if website has call-to-action elements."""
        # Look for buttons
        buttons = soup.find_all(['button', 'input'])
        if buttons:
            return True
        
        # Look for links with CTA text
        cta_keywords = [
            'contact', 'book', 'call', 'schedule', 'get started',
            'buy', 'order', 'sign up', 'subscribe', 'learn more',
            'get quote', 'free', 'appointment', 'reserve'
        ]
        
        links = soup.find_all('a')
        for link in links:
            text = link.get_text().lower()
            href = (link.get('href') or '').lower()
            for keyword in cta_keywords:
                if keyword in text or keyword in href:
                    return True
        
        # Look for forms
        forms = soup.find_all('form')
        if forms:
            return True
        
        return False
    
    def _check_contact_info(self, soup, html: str) -> bool:
        """Check if contact information is visible."""
        # Phone number patterns
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        ]
        
        for pattern in phone_patterns:
            if re.search(pattern, html):
                return True
        
        # Email patterns
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        if re.search(email_pattern, html):
            return True
        
        # mailto links
        mailto = soup.find('a', href=re.compile(r'^mailto:', re.I))
        if mailto:
            return True
        
        # tel links
        tel = soup.find('a', href=re.compile(r'^tel:', re.I))
        if tel:
            return True
        
        return False
    
    def _check_outdated_design(self, soup, html: str) -> bool:
        """Check for indicators of outdated design."""
        outdated_indicators = 0
        
        # Check for old HTML patterns
        old_elements = ['font', 'center', 'marquee', 'blink']
        for elem in old_elements:
            if soup.find(elem):
                outdated_indicators += 1
        
        # Check for table-based layouts
        tables = soup.find_all('table')
        if len(tables) > 3:  # Multiple tables often = old layout
            outdated_indicators += 1
        
        # Check for inline styles with old patterns
        if 'font-family: Arial' in html or 'font-family: Times' in html:
            outdated_indicators += 1
        
        # Check for Flash references
        if 'swf' in html.lower() or 'flash' in html.lower():
            outdated_indicators += 2
        
        # Check for old jQuery versions or patterns
        if 'jquery-1.' in html.lower() or 'jquery.min.js?v=1' in html.lower():
            outdated_indicators += 1
        
        # Check for old copyright dates
        old_years = ['© 2010', '© 2011', '© 2012', '© 2013', '© 2014', 
                     '© 2015', '© 2016', '© 2017', '© 2018', '© 2019']
        for year in old_years:
            if year in html:
                outdated_indicators += 1
                break
        
        # Check for "best viewed in" messages
        if 'best viewed' in html.lower() or 'optimized for' in html.lower():
            outdated_indicators += 2
        
        return outdated_indicators >= 2
    
    def _check_broken_images(self, soup) -> bool:
        """Check for potentially broken images."""
        images = soup.find_all('img')
        
        for img in images:
            src = img.get('src', '')
            
            # Empty src
            if not src or src == '#':
                return True
            
            # Check for common broken patterns
            if 'placeholder' in src.lower() or 'default' in src.lower():
                continue  # These are intentional
            
            # Missing alt text is a sign of poor maintenance
            if not img.get('alt') and len(images) > 3:
                return True
        
        return False
    
    def analyze_batch(self, urls: List[str]) -> List[AnalysisResult]:
        """Analyze multiple websites."""
        results = []
        for url in urls:
            print(f"Analyzing: {url}...")
            result = self.analyze(url)
            results.append(result)
            print(f"  Score: {result.score} ({result.lead_quality})")
            time.sleep(1)  # Be nice to servers
        return results


def print_analysis_report(result: AnalysisResult):
    """Print a formatted analysis report."""
    quality_colors = {
        "EXCELLENT": "\033[92m",  # Green
        "GOOD": "\033[93m",       # Yellow
        "MAYBE": "\033[94m",      # Blue
        "SKIP": "\033[91m",       # Red
    }
    reset = "\033[0m"
    
    color = quality_colors.get(result.lead_quality, "")
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        WEBSITE ANALYSIS REPORT                                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Website: {result.url}
Score: {color}{result.score}/100{reset}
Lead Quality: {color}{result.lead_quality}{reset}
Load Time: {result.load_time:.2f}s

─────────────────────────────────────────────────────────────────────────────────
CHECKS:
─────────────────────────────────────────────────────────────────────────────────
  SSL/HTTPS:        {"✓" if result.has_ssl else "✗"}
  Mobile-Friendly:  {"✓" if result.is_mobile_friendly else "✗"}
  Page Title:       {"✓" if result.has_title else "✗"}
  Meta Description: {"✓" if result.has_meta_description else "✗"}
  H1 Heading:       {"✓" if result.has_h1 else "✗"}
  Call-to-Action:   {"✓" if result.has_cta else "✗"}
  Contact Info:     {"✓" if result.has_contact_info else "✗"}

─────────────────────────────────────────────────────────────────────────────────
ISSUES FOUND ({len(result.issues)}):
─────────────────────────────────────────────────────────────────────────────────""")
    
    for issue in result.issues:
        severity_icon = {"critical": "🔴", "major": "🟠", "minor": "🟡"}.get(issue.severity, "⚪")
        print(f"  {severity_icon} {issue.description}")
        print(f"     Fix: {issue.fix_suggestion}")
    
    print("""
═══════════════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
        analyzer = WebsiteAnalyzer()
        result = analyzer.analyze(url)
        print_analysis_report(result)
    else:
        print("Usage: python website_analyzer.py <url>")
        print("Example: python website_analyzer.py example.com")
