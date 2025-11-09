"""Optional transformer-based summarizer used only if transformers is installed
and a model is provided via SUMMARIZER_MODEL env var (or default HuggingFace model).

This file is intentionally optional — if transformers isn't installed this module
will raise an ImportError and the code will fall back to the lightweight textrank summarizer.
"""
import os

def summarize_with_transformer(text: str, max_length: int = 120, min_length: int = 30) -> str:
    try:
        from transformers import pipeline
    except Exception as e:
        raise RuntimeError("transformers not available") from e

    model_name = os.environ.get("SUMMARIZER_MODEL")
    # if not set, use a small default summarization-capable model name (still requires download)
    if not model_name:
        model_name = "sshleifer/distilbart-cnn-12-6"

    summarizer = pipeline("summarization", model=model_name)
    # Hugging Face pipelines will chunk long inputs; for demo keep simple
    out = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    if isinstance(out, list) and len(out) > 0 and isinstance(out[0], dict):
        return out[0].get("summary_text", "")
    return str(out)
