# backend/app/sentiment.py
from typing import Dict, Any

try:
    from textblob import TextBlob  # optional dependency for nicer sentiment
    _HAS_TEXTBLOB = True
except Exception:
    TextBlob = None
    _HAS_TEXTBLOB = False


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Return a simple sentiment dict. If TextBlob isn't installed or fails,
    return a neutral fallback so the API doesn't crash.
    """
    if not text:
        return {"polarity": 0.0, "tone": "Neutral"}
    if not _HAS_TEXTBLOB:
        # graceful fallback when textblob isn't available
        return {"polarity": 0.0, "tone": "Neutral", "note": "textblob missing"}

    try:
        tb = TextBlob(text)
        polarity = round(tb.sentiment.polarity, 3)
        if polarity > 0.2:
            tone = "Positive"
        elif polarity < -0.2:
            tone = "Negative"
        else:
            tone = "Neutral"
        return {"polarity": polarity, "tone": tone}
    except Exception:
        # Unexpected runtime error from TextBlob -> return neutral and a note
        return {"polarity": 0.0, "tone": "Neutral", "note": "textblob error"}
