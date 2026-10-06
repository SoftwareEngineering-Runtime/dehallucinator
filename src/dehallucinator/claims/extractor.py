"""Claim Extractor (Role A): splits an AI answer into factual claims."""

from functools import lru_cache

import spacy
from spacy.language import Language

from dehallucinator.config import MAX_INPUT_CHARS
from dehallucinator.models import Claim

SPACY_MODEL = "en_core_web_sm"


@lru_cache(maxsize=1)
def get_nlp() -> Language:
    """Load the spaCy English model once and reuse it on every call."""
    return spacy.load(SPACY_MODEL)


def validate_input(text: str) -> str:
    """Return the stripped text, or raise ValueError if it is empty or too long (FR-1.1)."""
    stripped = text.strip()
    if not stripped:
        raise ValueError("Input text is empty")
    if len(text) > MAX_INPUT_CHARS:
        raise ValueError(f"Input exceeds {MAX_INPUT_CHARS} characters")
    return stripped


def split_sentences(text: str) -> list[str]:
    """Split text into sentences using spaCy (FR-1.2)."""
    doc = get_nlp()(text)
    return [sent.text.strip() for sent in doc.sents if sent.text.strip()]


def extract_claims(text: str) -> list[Claim]:
    """Return the factual claims found in ``text``.

    For now every sentence becomes one claim. Filtering (DH-162), compound
    splitting, pronoun replacement and de-duplication come in later stories.
    """
    sentences = split_sentences(validate_input(text))
    claims: list[Claim] = []
    for index, sentence in enumerate(sentences):
        claims.append(Claim(id=len(claims) + 1, text=sentence, sentence_index=index))
    return claims
