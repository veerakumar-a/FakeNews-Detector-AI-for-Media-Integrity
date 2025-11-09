# backend/app/explain.py
import re
import html
from typing import List, Tuple

HIGHLIGHT_WORDS = [
    "shocking",
    "miracle",
    "secret",
    "exposed",
    "cure",
    "unbelievable",
    "exclusive",
    "claims",
]


def highlight_keywords(text: str) -> Tuple[str, List[str]]:
    """Escape incoming text to avoid XSS then highlight known sensational words.

    Returns (highlighted_html, keywords_list).
    """
    if not text:
        return ("", [])

    # Escape HTML to avoid XSS, then perform case-insensitive replacement
    escaped = html.escape(text)
    highlighted = escaped
    for w in HIGHLIGHT_WORDS:
        # use a word-boundary aware regex to avoid partial matches
        highlighted = re.sub(rf"(?i)\b({re.escape(w)})\b",
                             r"<mark class='bg-yellow-200 text-red-700 font-semibold'>\1</mark>",
                             highlighted)

    # return top simple keywords (first 12 words frequency)
    words = re.findall(r"\w+", text.lower())
    freq = {}
    for t in words:
        if len(t) <= 3:
            continue
        freq[t] = freq.get(t, 0) + 1
    sorted_kw = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    top = [k for k, _ in sorted_kw[:12]]
    return (highlighted, top)
