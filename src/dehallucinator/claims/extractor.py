"""Claim Extractor (Role A): splits an AI answer into factual claims."""

import re
from functools import lru_cache

import spacy
from spacy.language import Language

from dehallucinator.config import MAX_INPUT_CHARS, MIN_CLAIM_WORDS
from dehallucinator.models import Claim

SPACY_MODEL = "en_core_web_sm"

# Words and phrases that signal an opinion rather than a checkable fact (FR-1.3).
OPINION_MARKERS = (
    "i think",
    "i believe",
    "in my opinion",
    "maybe",
    "perhaps",
    "probably",
    "best",
    "worst",
    "beautiful",
    "amazing",
    "should",
)
OPINION_PATTERN = re.compile(r"\b(" + "|".join(OPINION_MARKERS) + r")\b", re.IGNORECASE)


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


def is_factual(sentence: str) -> bool:
    """Return False for sentences that cannot be fact-checked (FR-1.3).

    A sentence is dropped if it is a question, contains an opinion marker,
    starts with "I" or "We", or has fewer than MIN_CLAIM_WORDS words.
    """
    if sentence.rstrip().endswith("?"):
        return False
    if OPINION_PATTERN.search(sentence):
        return False
    first_word = sentence.split()[0].lower()
    if first_word in ("i", "we"):
        return False
    return len(sentence.split()) >= MIN_CLAIM_WORDS


def extract_claims(text: str) -> list[Claim]:
    """Return the factual claims found in ``text``.

    Non-factual sentences are dropped (DH-162). Compound splitting, pronoun
    replacement and de-duplication come in later stories.
    """
    sentences = split_sentences(validate_input(text))
    claims: list[Claim] = []
    for index, sentence in enumerate(sentences):
        if is_factual(sentence):
            claims.append(Claim(id=len(claims) + 1, text=sentence, sentence_index=index))
    return claims
