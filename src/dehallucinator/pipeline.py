"""Pipeline (Role D): connects extract -> retrieve -> verify -> correct (FR-4.2)."""

import logging
import time
from collections.abc import Callable
from typing import TypeVar

from dehallucinator.claims.extractor import extract_claims
from dehallucinator.correct.corrector import correct
from dehallucinator.evidence.retriever import retrieve_evidence
from dehallucinator.models import CheckedAnswer
from dehallucinator.verify.verifier import trust_score, verify_claims

logger = logging.getLogger(__name__)

T = TypeVar("T")


def check_answer(text: str) -> CheckedAnswer:
    """Run the full dehallucination pipeline on one AI answer.

    Raises ValueError if ``text`` is empty or longer than MAX_INPUT_CHARS (checked by the
    Claim Extractor, FR-1.1). The time taken by each stage is logged in milliseconds.
    """
    timings: dict[str, float] = {}

    claims = _timed("extract", timings, lambda: extract_claims(text))
    if claims:
        evidence = _timed("retrieve", timings, lambda: retrieve_evidence(claims))
        verdicts = _timed("verify", timings, lambda: verify_claims(claims, evidence))
    else:
        # Nothing to check: skip the network calls and the NLI model.
        verdicts = []
    score = _timed("score", timings, lambda: trust_score(verdicts))
    corrected = _timed("correct", timings, lambda: correct(text, claims, verdicts))

    logger.info(
        "check_answer: %d claims, trust %.1f, %s",
        len(claims),
        score,
        ", ".join(f"{stage} {ms:.0f} ms" for stage, ms in timings.items()),
    )
    return CheckedAnswer(
        original=text,
        corrected=corrected,
        claims=claims,
        verdicts=verdicts,
        trust_score=score,
    )


def _timed(stage: str, timings: dict[str, float], step: Callable[[], T]) -> T:
    start = time.perf_counter()
    result = step()
    timings[stage] = (time.perf_counter() - start) * 1000
    return result
