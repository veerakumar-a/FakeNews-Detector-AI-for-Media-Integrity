"""Fact-check / news API helpers.

This module wraps NewsAPI (https://newsapi.org) for demo use. It expects
an environment variable NEWSAPI_KEY. If not present, callers should fallback
to demo results.
"""
import os
import requests
from typing import List, Dict

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY")
NEWSAPI_URL = "https://newsapi.org/v2/everything"


def search_newsapi(query: str, limit: int = 5) -> List[Dict]:
    """Return simplified list of articles from NewsAPI matching query.

    If NEWSAPI_KEY not set, raise RuntimeError so callers can fallback.
    """
    if not NEWSAPI_KEY:
        raise RuntimeError("NEWSAPI_KEY not set")

    params = {
        "q": query,
        "pageSize": limit,
        "language": "en",
        "sortBy": "relevancy",
    }
    headers = {"Authorization": NEWSAPI_KEY}
    resp = requests.get(NEWSAPI_URL, params=params, headers=headers, timeout=6)
    resp.raise_for_status()
    data = resp.json()
    out = []
    for a in data.get("articles", [])[:limit]:
        out.append({
            "title": a.get("title"),
            "source": a.get("source", {}).get("name"),
            "url": a.get("url"),
            "summary": a.get("description") or "",
        })
    return out
