"""Corrector (Role D): rewrites or flags wrong claims.

Each claim is tagged in place according to its verdict (FR-4.1):

- CONTRADICTED -> replaced by the evidence snippet + ``[corrected, source: <url>]``
- NOT_ENOUGH_INFO -> kept + ``[unverified]``
- SUPPORTED -> kept + ``[source: <url>]``

A claim is found in the answer by its text, searched inside the sentence given by
``sentence_index``. The Claim Extractor may reword a claim (pronoun replacement,
compound splitting), so when the text cannot be found the tag is added at the end of
that sentence instead.
"""

import re
from dataclasses import dataclass

from dehallucinator.claims.extractor import get_nlp
from dehallucinator.models import Claim, Evidence, Verdict

UNVERIFIED_TAG = "[unverified]"


@dataclass(frozen=True)
class _Edit:
    start: int
    end: int
    replacement: str
    fallback: str  # inserted at sentence_end if the edit overlaps an earlier one
    sentence_end: int


def correct(text: str, claims: list[Claim], verdicts: list[Verdict]) -> str:
    """Return the corrected answer text."""
    if not claims:
        return text

    verdict_by_claim = {verdict.claim_id: verdict for verdict in verdicts}
    sentences = _sentence_spans(text)
    claims_per_sentence: dict[int, int] = {}
    for claim in claims:
        claims_per_sentence[claim.sentence_index] = (
            claims_per_sentence.get(claim.sentence_index, 0) + 1
        )

    edits = []
    for claim in sorted(claims, key=lambda c: c.id):
        sentence = _sentence_bounds(text, sentences, claim.sentence_index)
        alone = claims_per_sentence[claim.sentence_index] == 1
        edit = _edit_for(text, claim, verdict_by_claim.get(claim.id), sentence, alone)
        if edit is not None:
            edits.append(edit)
    return _apply(text, edits)


def _edit_for(
    text: str,
    claim: Claim,
    verdict: Verdict | None,
    sentence: tuple[int, int],
    alone_in_sentence: bool,
) -> _Edit | None:
    label = verdict.label if verdict else "NOT_ENOUGH_INFO"
    evidence = verdict.best_evidence if verdict else None
    if label == "CONTRADICTED" and evidence is None:
        label = "NOT_ENOUGH_INFO"
    if label == "SUPPORTED" and evidence is None:
        return None

    span = _locate(text, claim.text, sentence)
    sentence_start, sentence_end = sentence

    if label == "CONTRADICTED" and evidence is not None:
        correction = _correction(evidence)
        fallback = f" [correction: {correction}]"
        if span:
            return _Edit(span[0], span[1], correction, fallback, sentence_end)
        if alone_in_sentence:
            return _Edit(sentence_start, sentence_end, correction, fallback, sentence_end)
        return _Edit(sentence_end, sentence_end, fallback, fallback, sentence_end)

    tag = f" [source: {evidence.source_url}]" if label == "SUPPORTED" else f" {UNVERIFIED_TAG}"
    if span:
        return _Edit(span[0], span[1], text[span[0] : span[1]] + tag, tag, sentence_end)
    return _Edit(sentence_end, sentence_end, tag, tag, sentence_end)


def _correction(evidence: Evidence) -> str:
    snippet = " ".join(evidence.snippet.split())
    return f"{snippet} [corrected, source: {evidence.source_url}]"


def _locate(text: str, claim_text: str, sentence: tuple[int, int]) -> tuple[int, int] | None:
    """Find the claim inside its sentence; returns absolute (start, end) or None."""
    start, end = sentence
    window = text[start:end]
    needle = claim_text.strip()
    for candidate in (needle, needle.rstrip(".!?").rstrip()):
        if not candidate:
            continue
        match = re.search(re.escape(candidate), window, flags=re.IGNORECASE)
        if match:
            return start + match.start(), start + match.end()
    return None


def _sentence_bounds(text: str, sentences: list[tuple[int, int]], index: int) -> tuple[int, int]:
    if 0 <= index < len(sentences):
        return sentences[index]
    return 0, len(text.rstrip())


def _apply(text: str, edits: list[_Edit]) -> str:
    """Apply edits left to right; an edit overlapping an earlier one becomes an insertion."""
    replacements: list[_Edit] = []
    insertions: list[_Edit] = []
    last_end = 0
    for edit in sorted(edits, key=lambda e: (e.start, e.end)):
        if edit.start == edit.end:
            insertions.append(edit)
        elif edit.start < last_end:
            at = edit.sentence_end
            insertions.append(_Edit(at, at, edit.fallback, edit.fallback, at))
        else:
            replacements.append(edit)
            last_end = edit.end

    # An insertion must never land inside text that another edit replaces.
    moved = []
    for insertion in insertions:
        at = insertion.start
        for replacement in replacements:
            if replacement.start < at < replacement.end:
                at = replacement.end
        moved.append(_Edit(at, at, insertion.replacement, insertion.fallback, at))

    parts = []
    cursor = 0
    for edit in sorted(replacements + moved, key=lambda e: (e.start, e.end)):
        parts.append(text[cursor : edit.start])
        parts.append(edit.replacement)
        cursor = edit.end
    parts.append(text[cursor:])
    return "".join(parts)


def _sentence_spans(text: str) -> list[tuple[int, int]]:
    """Character spans of each sentence, numbered the same way as the Claim Extractor.

    Uses the extractor's spaCy model, skips whitespace-only sentences like it does, and
    trims surrounding whitespace so a tag lands right after the sentence's last character.
    """
    spans = []
    for sent in get_nlp()(text).sents:
        raw = sent.text
        if not raw.strip():
            continue
        start = sent.start_char + (len(raw) - len(raw.lstrip()))
        end = sent.start_char + len(raw.rstrip())
        spans.append((start, end))
    return spans
