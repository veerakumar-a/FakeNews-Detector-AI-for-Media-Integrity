# backend/app/main.py
from typing import Optional

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.model import NewsModel
from app.sentiment import analyze_sentiment
from app.credibility import check_source_credibility
from app.explain import highlight_keywords
from app.summarizer import summarize_text
from app import db
import requests
import os
from pydantic import BaseModel
from typing import List
from fastapi import Header

# Simple in-memory stores for demo purposes
_subscriptions = []
_community_votes = {}

logger = logging.getLogger("fakenews")
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="FakeNews Detector API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = NewsModel()


# initialize DB file
try:
    db.init_db()
except Exception:
    # ensure that a permissions issue won't crash the app on import during tests
    pass


def _require_admin(x_admin_key: str | None = Header(default=None)):
    """Simple admin auth dependency: if ADMIN_KEY env var is set, require X-Admin-Key header to match."""
    admin_key = os.environ.get("ADMIN_KEY")
    if not admin_key:
        return True
    if x_admin_key and x_admin_key == admin_key:
        return True
    raise HTTPException(status_code=401, detail="Admin key required")


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None

    def cleaned_text(self) -> str:
        return (self.text or "").strip()


@app.post("/analyze")
async def analyze_news(payload: AnalyzeRequest):
    """Analyze either a pasted `text` or a `url` (if text missing, we try to fetch).

    Returns a JSON with label/confidence and helper info.
    """
    text = payload.cleaned_text()
    url = (payload.url or "")

    if not text and not url:
        raise HTTPException(status_code=400, detail="Provide 'text' or 'url' in JSON body")

    # If URL was provided but text is empty, attempt to fetch page text (best-effort)
    if not text and url:
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            # naive extraction: take body text — for demo it's acceptable
            # In production use proper HTML-to-text extraction
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "html.parser")
            # join visible text nodes
            text = "\n".join(soup.stripped_strings)
        except Exception as e:
            logger.exception("Failed to fetch URL %s", url)
            raise HTTPException(status_code=400, detail=f"Could not fetch url: {e}")

    try:
        result = model.predict(text)
        sentiment = analyze_sentiment(text)
        highlighted_text, keywords = highlight_keywords(text)
        source_data = check_source_credibility(url) if url else None

        return {
            "label": result["label"],
            "confidence": result["confidence"],
            "probabilities": result.get("probabilities", []),
            "sentiment": sentiment,
            "keywords": keywords,
            "highlighted": highlighted_text,
            "source": source_data,
            "raw_text": text,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unhandled error in /analyze")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def healthcheck():
    """Simple health endpoint for CI and quick checks."""
    return {"status": "ok"}


class TextRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


@app.post("/summarize")
async def summarize(req: TextRequest):
    """Return a short summary.

    If environment variable SUMMARIZER_MODEL is set or transformers are available and
    configured, attempt to use a transformer-based summarizer. Otherwise fall back to
    the lightweight TextRank summarizer implemented in `summarizer.py`.
    """
    text = (req.text or "")
    if not text and req.url:
        try:
            resp = requests.get(req.url, timeout=5)
            resp.raise_for_status()
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(resp.text, "html.parser")
            text = "\n".join(soup.stripped_strings)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not fetch url: {e}")

    if not text:
        raise HTTPException(status_code=400, detail="Provide 'text' or 'url'")

    # Prefer transformer summarizer if configured
    use_transformer = os.environ.get("USE_TRANSFORMER", "0") in ("1", "true", "True")
    if use_transformer:
        try:
            from app.summarizer_transformer import summarize_with_transformer

            summary = summarize_with_transformer(text)
            return {"summary": summary, "source": "transformer"}
        except Exception:
            # log and fall back
            logger.exception("Transformer summarizer unavailable, falling back to TextRank")

    summary = summarize_text(text, sentences_k=3)
    return {"summary": summary, "source": "textrank"}


@app.post("/fact-check")
async def fact_check(req: TextRequest):
    """Return fact-checked alternatives: use NewsAPI when NEWSAPI_KEY present, else return demo data."""
    text = (req.text or "")
    url = (req.url or "")
    demo = [
        {
            "title": "Fact Check: Viral 'miracle cure' claim debunked",
            "source": "ExampleFactCheck",
            "url": "https://example.com/fact-check-miracle-cure",
            "summary": "Independent health reporters found no evidence for the claimed cure."
        },
        {
            "title": "Related: Misleading 'big pharma secret' narrative",
            "source": "TrustedNews",
            "url": "https://trustednews.example/article/123",
            "summary": "Context and quotes from experts explaining why the narrative is misleading."
        }
    ]

    # If NewsAPI key provided, perform a lightweight search for related articles
    try:
        from app.fact_api import search_newsapi
        if text:
            q = " \"" + (text[:200].replace('\n',' ')) + "\""
        elif url:
            q = url
        else:
            q = None

        if q:
            try:
                hits = search_newsapi(q, limit=5)
                # map to same shape
                if hits:
                    return {"results": hits}
            except Exception:
                # if NewsAPI fails, fall back to demo
                pass
    except Exception:
        # fact_api not available or missing key
        pass

    return {"results": demo}


@app.post("/bias")
async def bias(req: TextRequest):
    """Simple bias heuristic: use sentiment magnitude and presence of opinion words."""
    text = (req.text or "")
    if not text:
        raise HTTPException(status_code=400, detail="Provide 'text' in body")

    # naive heuristic
    opinion_words = ["believe", "obviously", "clearly", "must", "should", "hate", "love"]
    ow = sum(1 for w in opinion_words if w in text.lower())
    sentiment = analyze_sentiment(text)
    polarity = abs(sentiment.get("polarity", 0))

    score = min(100, int((ow * 10) + polarity * 50))
    if score < 30:
        label = "Neutral"
        color = "green"
    elif score < 70:
        label = "Slightly biased"
        color = "yellow"
    else:
        label = "Highly biased"
        color = "red"

    distribution = {"neutral": max(0, 100 - score), "biased": score}
    return {"label": label, "score": score, "color": color, "distribution": distribution}


class SubscribeRequest(BaseModel):
    channel: str
    address: str


@app.post("/subscribe")
async def subscribe(req: SubscribeRequest):
    try:
        db.add_subscription(req.channel, req.address)
    except Exception:
        # fallback to in-memory store if DB unavailable
        _subscriptions.append({"channel": req.channel, "address": req.address})
    return {"status": "ok", "message": "Subscribed (demo)."}


class VoteRequest(BaseModel):
    item_id: str
    vote: int  # +1 or -1


@app.post("/community/vote")
async def community_vote(req: VoteRequest):
    try:
        score = db.add_vote(req.item_id, int(req.vote))
    except Exception:
        cur = _community_votes.get(req.item_id, 0)
        _community_votes[req.item_id] = cur + req.vote
        score = _community_votes[req.item_id]
    return {"item_id": req.item_id, "score": score}


@app.get("/community/score/{item_id}")
async def community_score(item_id: str):
    try:
        score = db.get_score(item_id)
    except Exception:
        score = _community_votes.get(item_id, 0)
    return {"item_id": item_id, "score": score}


@app.get("/admin/subscriptions")
async def admin_subscriptions():
    """Return recent subscriptions (admin view, demo only)."""
    try:
        subs = db.get_subscriptions()
    except Exception:
        subs = _subscriptions
    return {"count": len(subs), "subscriptions": subs}


@app.get("/admin/votes")
async def admin_votes():
    """Return vote scores for items."""
    try:
        votes = db.get_all_votes()
    except Exception:
        votes = _community_votes
    return {"votes": votes}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
