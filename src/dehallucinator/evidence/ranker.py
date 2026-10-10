"""Rank evidence snippets for a claim (FR-2.5)."""

import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from dehallucinator.config import EVIDENCE_PER_CLAIM

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    return [s.strip() for s in _SENTENCE_SPLIT.split(text or "") if s.strip()]


def make_snippets(text: str) -> list[str]:
    """Each snippet is a sentence plus the next sentence (the last stands alone)."""
    sentences = split_sentences(text)
    return [" ".join(sentences[i : i + 2]) for i in range(len(sentences))]


def rank_snippets(
    claim_text: str, pages: list[dict], top_n: int = EVIDENCE_PER_CLAIM
) -> list[dict]:
    """Return the top_n snippets across all pages, best first.

    pages: dicts with "title", "url", "text" (as returned by fetch_page_text).
    Each result has "text", "title", "url" and "relevance" (0 to 1, TF-IDF cosine).
    Snippets with zero relevance are dropped.
    """
    candidates = []
    for page in pages:
        for snippet in make_snippets(page.get("text", "")):
            candidates.append(
                {"text": snippet, "title": page["title"], "url": page["url"]}
            )
    if not (claim_text or "").strip() or not candidates:
        return []

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(
            [claim_text] + [c["text"] for c in candidates]
        )
    except ValueError:  # nothing left after removing stop words
        return []

    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    for candidate, score in zip(candidates, scores):
        candidate["relevance"] = round(float(min(max(score, 0.0), 1.0)), 4)

    ranked = sorted(candidates, key=lambda c: c["relevance"], reverse=True)
    return [c for c in ranked if c["relevance"] > 0][:top_n]
