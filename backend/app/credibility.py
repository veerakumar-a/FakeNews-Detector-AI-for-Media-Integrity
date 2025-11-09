# backend/app/credibility.py
from typing import Optional, Dict, Any

try:
    import tldextract
    _HAS_TLDEXTRACT = True
except Exception:
    tldextract = None
    _HAS_TLDEXTRACT = False


TRUSTED_DOMAINS = ["bbc.com", "reuters.com", "thehindu.com", "ndtv.com"]
BLACKLIST_DOMAINS = ["fake-news.net", "gossipbuzz.com"]


def _extract_domain(url: str) -> Optional[str]:
    if not url:
        return None
    if _HAS_TLDEXTRACT:
        try:
            e = tldextract.extract(url)
            return ".".join(part for part in [e.domain, e.suffix] if part)
        except Exception:
            return url
    # fallback: crude parse
    try:
        from urllib.parse import urlparse

        p = urlparse(url if url.startswith("http") else "http://" + url)
        host = p.hostname or url
        # strip www.
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return url


def check_source_credibility(url: str) -> Optional[Dict[str, Any]]:
    if not url:
        return None
    domain = _extract_domain(url)
    if domain in TRUSTED_DOMAINS:
        return {"domain": domain, "score": 0.9, "status": "Trusted"}
    if domain in BLACKLIST_DOMAINS:
        return {"domain": domain, "score": 0.2, "status": "Unreliable"}
    return {"domain": domain, "score": 0.5, "status": "Unknown"}
