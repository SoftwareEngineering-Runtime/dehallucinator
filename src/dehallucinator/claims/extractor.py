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

# Places where a compound sentence may be split into two claims (FR-1.4).
COMPOUND_SPLIT_PATTERN = re.compile(r"\s*;\s*|,\s+(?:and|but)\s+", re.IGNORECASE)
SUBJECT_DEPS = ("nsubj", "nsubjpass", "expl")

# Pronoun replacement (FR-1.5): which pronouns refer to people and which to things.
PERSON_PRONOUNS = {"he": False, "she": False, "his": True, "her": True}
THING_PRONOUNS = {"it": False, "its": True, "they": False, "their": True}
NAMED_ENTITY_LABELS = (
    "PERSON",
    "NORP",
    "FAC",
    "ORG",
    "GPE",
    "LOC",
    "PRODUCT",
    "EVENT",
    "WORK_OF_ART",
)


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


def has_subject_and_verb(text: str) -> bool:
    """Return True if ``text`` has its own subject and a verb (FR-1.4)."""
    doc = get_nlp()(text)
    has_subject = any(token.dep_ in SUBJECT_DEPS for token in doc)
    has_verb = any(token.pos_ in ("VERB", "AUX") for token in doc)
    return has_subject and has_verb


def split_compound(sentence: str) -> list[str]:
    """Split a compound sentence at ";", ", and" or ", but" (FR-1.4).

    A split is made only when both parts have their own subject and verb, so
    "He was tired, but happy." stays one claim. Each part ends with the
    sentence's final punctuation and starts with a capital letter.
    """
    match = COMPOUND_SPLIT_PATTERN.search(sentence)
    if match is None:
        return [sentence]

    end_mark = sentence[-1] if sentence[-1] in ".!" else ""
    left = sentence[: match.start()].strip()
    right = sentence[match.end() :].strip()
    if not left or not right:
        return [sentence]
    if not (has_subject_and_verb(left) and has_subject_and_verb(right)):
        # Try the next split point in the right-hand part only.
        rest = split_compound(right)
        if len(rest) == 1:
            return [sentence]
        return [left + sentence[match.start() : match.end()] + rest[0], *rest[1:]]

    left = left.rstrip(".!") + end_mark
    right = right[0].upper() + right[1:]
    return [left, *split_compound(right)]


class EntityMemory:
    """Remembers the most recent person and thing named so far (FR-1.5)."""

    def __init__(self) -> None:
        self.person: str | None = None
        self.thing: str | None = None

    def update(self, text: str) -> None:
        """Remember the named entities in ``text``; a sentence's subject wins over others."""
        doc = get_nlp()(text)
        subjects = {chunk.root.i: chunk.text for chunk in doc.noun_chunks}
        person = thing = None
        person_is_subject = thing_is_subject = False
        for ent in doc.ents:
            if ent.label_ not in NAMED_ENTITY_LABELS:
                continue
            # Use the full noun phrase ("The Eiffel Tower") when the entity is the subject.
            is_subject = ent.root.dep_ in SUBJECT_DEPS
            name = subjects.get(ent.root.i, ent.text) if is_subject else ent.text
            if ent.label_ == "PERSON":
                if not person_is_subject:
                    person, person_is_subject = name, is_subject
            elif not thing_is_subject:
                thing, thing_is_subject = name, is_subject
        self.person = person or self.person
        self.thing = thing or self.thing


def replace_leading_pronoun(claim: str, memory: EntityMemory) -> str:
    """Replace a leading pronoun with the entity it refers to (FR-1.5).

    "He"/"She" use the last person named and "It"/"They" the last thing; the
    possessive forms become "<entity>'s". The claim is unchanged if no entity
    has been named yet.
    """
    first, _, rest = claim.partition(" ")
    pronoun = first.lower()
    if pronoun in PERSON_PRONOUNS:
        entity, possessive = memory.person, PERSON_PRONOUNS[pronoun]
    elif pronoun in THING_PRONOUNS:
        entity, possessive = memory.thing, THING_PRONOUNS[pronoun]
    else:
        return claim
    if entity is None or not rest:
        return claim
    replacement = entity + "'s" if possessive else entity
    return replacement[0].upper() + replacement[1:] + " " + rest


def extract_claims(text: str) -> list[Claim]:
    """Return the factual claims found in ``text``.

    Non-factual sentences are dropped (DH-162), compound sentences are split
    into one claim per part (DH-163) and leading pronouns are replaced with
    the entity they refer to (DH-164).
    """
    sentences = split_sentences(validate_input(text))
    memory = EntityMemory()
    claims: list[Claim] = []
    for index, sentence in enumerate(sentences):
        if not is_factual(sentence):
            memory.update(sentence)
            continue
        for part in split_compound(sentence):
            part = replace_leading_pronoun(part, memory)
            memory.update(part)
            claims.append(Claim(id=len(claims) + 1, text=part, sentence_index=index))
    return claims
