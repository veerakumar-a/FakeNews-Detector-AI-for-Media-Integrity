"""Lightweight TextRank-style summarizer for demo (no external deps).

This builds a sentence-similarity graph using token overlap and runs a simple
PageRank iteration to score sentences and return the top few.
"""
import re
from math import sqrt
from typing import List


def tokenize_words(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())


def sentence_tokens(sentence: str):
    return re.findall(r"\w+", sentence.lower())


def sentence_similarity(s1_tokens, s2_tokens):
    if not s1_tokens or not s2_tokens:
        return 0.0
    s1_set = set(s1_tokens)
    s2_set = set(s2_tokens)
    common = s1_set.intersection(s2_set)
    if not common:
        return 0.0
    # normalized overlap
    return len(common) / (sqrt(len(s1_set)) * sqrt(len(s2_set)))


def textrank(sentences: List[str], top_k: int = 3, max_iter: int = 50, d: float = 0.85):
    n = len(sentences)
    if n == 0:
        return []
    if n <= top_k:
        return sentences

    tokenized = [sentence_tokens(s) for s in sentences]
    # build weight matrix
    weights = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            w = sentence_similarity(tokenized[i], tokenized[j])
            weights[i][j] = w
            weights[j][i] = w

    # normalize rows
    out_sum = [sum(weights[i]) for i in range(n)]

    scores = [1.0 / n] * n
    for _ in range(max_iter):
        new_scores = [ (1 - d) / n ] * n
        for i in range(n):
            for j in range(n):
                if out_sum[j] != 0:
                    new_scores[i] += d * (weights[i][j] / out_sum[j]) * scores[j]
        scores = new_scores

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    top_idx = [i for i, _ in ranked[:top_k]]
    # preserve original order
    top_idx_sorted = sorted(top_idx)
    summary = [sentences[i] for i in top_idx_sorted]
    return summary


def summarize_text(text: str, sentences_k: int = 3) -> str:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return ""
    top = textrank(sentences, top_k=sentences_k)
    return " ".join(top)
