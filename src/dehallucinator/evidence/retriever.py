"""Evidence Retriever (Role B): finds evidence for each claim."""

from functools import lru_cache

import spacy

from dehallucinator.models import Claim, Evidence

MAX_QUERY_WORDS = 8


@lru_cache(maxsize=1)
def _get_nlp():
    """Load the spaCy model once and reuse it."""
    return spacy.load("en_core_web_sm")


def build_query(claim_text: str) -> str:
    """Build a Wikipedia search query from a claim (FR-2.1).

    Entities come first, then noun chunks. Stop words and punctuation are
    removed, duplicates are dropped, and the result is capped at
    MAX_QUERY_WORDS words.
    """
    text = (claim_text or "").strip()
    if not text:
        return ""

    doc = _get_nlp()(text)
    words: list[str] = []
    seen: set[str] = set()

    def add_tokens(tokens) -> None:
        for tok in tokens:
            if len(words) >= MAX_QUERY_WORDS:
                return
            if tok.is_stop or tok.is_punct or tok.is_space:
                continue
            key = tok.text.lower()
            if key in seen:
                continue
            seen.add(key)
            words.append(tok.text)

    for ent in doc.ents:
        add_tokens(ent)
    for chunk in doc.noun_chunks:
        add_tokens(chunk)

    return " ".join(words)


def retrieve_evidence(claims: list[Claim]) -> list[Evidence]:
    """Return evidence snippets for the given claims."""
    raise NotImplementedError("Implemented by Role B in Sprint 1")
