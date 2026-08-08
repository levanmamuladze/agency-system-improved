"""
Helpers for classifying a business's web presence.

A business's "website" (as reported by Google Places, or pasted into the
analyzer) is often NOT a real standalone site — it's a Facebook page, a
third-party listing, or a free page-builder page. Those are prime leads, so we
detect them instead of treating them like a proper website.
"""

from urllib.parse import urlparse

# Social profiles — not a real website.
SOCIAL_DOMAINS = {
    "facebook.com", "m.facebook.com", "fb.com", "fb.me",
    "instagram.com", "linktr.ee", "linktree.com", "beacons.ai",
    "twitter.com", "x.com", "tiktok.com", "youtube.com", "youtu.be",
    "linkedin.com", "wa.me", "t.me", "vk.com", "pinterest.com",
}

# Third-party directories / marketplaces — also not their own site.
DIRECTORY_DOMAINS = {
    "yelp.com", "tripadvisor.com", "foursquare.com", "yellowpages.com",
    "booking.com", "thefork.com", "e-table.gr", "vrisko.gr", "xo.gr",
}

# Free / auto page-builder subdomains — weak, upgradeable presence.
BUILDER_HOSTS = {
    "business.site",        # Google's free site builder
    "sites.google.com",     # Google Sites
    "wixsite.com",          # unmapped Wix
    "weebly.com",
    "godaddysites.com",
    "square.site",
    "blogspot.com",
    "wordpress.com",        # free WP (not self-hosted)
    "mystrikingly.com",
    "webnode.com",
    "jimdosite.com",
}

NON_SITE = {"social", "directory", "builder"}


def _host(url: str) -> str:
    """Return the bare lowercase host (no scheme, no www, no port)."""
    if "//" not in url:
        url = "http://" + url
    host = urlparse(url).netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(":")[0]


def _matches(host: str, domains) -> bool:
    return any(host == d or host.endswith("." + d) for d in domains)


def classify_web_presence(url) -> str:
    """
    Classify a business's 'website' URL.

    Returns one of:
      'none'      - empty / missing
      'social'    - a social profile (Facebook/Instagram/Linktree/...)
      'directory' - a third-party listing (Yelp/TripAdvisor/...)
      'builder'   - a free/auto page-builder subdomain (business.site/wixsite/...)
      'site'      - looks like their own standalone website
    """
    if not url or not str(url).strip():
        return "none"
    host = _host(str(url))
    if not host:
        return "none"
    if _matches(host, SOCIAL_DOMAINS):
        return "social"
    if _matches(host, DIRECTORY_DOMAINS):
        return "directory"
    if _matches(host, BUILDER_HOSTS):
        return "builder"
    return "site"
