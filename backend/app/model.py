# backend/app/model.py
# Lightweight placeholder model wrapper. For hackathon/demo use a small rule-based fallback
# Replace with a fine-tuned transformers checkpoint for production.

from typing import Dict, Any
import math


class NewsModel:
    """Tiny heuristic model for demo purposes.

    It returns a confidence in [0.05, 0.95] where higher means more likely Real.
    """

    def __init__(self, model_name: str | None = None) -> None:
        # Placeholder: in production replace with an actual model loader
        self.name = model_name or "placeholder-rule-model"

    def predict(self, text: str) -> Dict[str, Any]:
        text_l = (text or "").lower()
        if not text_l.strip():
            # no content -> uncertain
            score = 0.5
        else:
            # base confidence increases with length and reduces with sensational tokens
            base = 0.55 if len(text_l.split()) > 40 else 0.5
            sensational = [
                "miracle",
                "shocking",
                "secret",
                "exposed",
                "cure",
                "unbelievable",
                "overnight",
            ]
            penalty = 0.0
            for w in sensational:
                # penalize per-occurrence but with diminishing returns
                count = text_l.count(w)
                if count:
                    penalty += 0.18 * (1 - math.exp(-0.5 * count))

            score = base - penalty

        # clamp and convert to probabilities (fake, real)
        score = max(0.05, min(0.95, score))
        label = "Real" if score >= 0.5 else "Fake"
        return {"label": label, "confidence": float(score), "probabilities": [float(1 - score), float(score)]}
