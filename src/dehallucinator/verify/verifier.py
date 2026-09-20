"""Verifier & Scorer (Role C): labels each claim using its evidence."""

from dehallucinator.models import Claim, Evidence, Verdict


def verify_claims(claims: list[Claim], evidence: list[Evidence]) -> list[Verdict]:
    """Return one verdict per claim."""
    raise NotImplementedError("Implemented by Role C in Sprint 1")


def trust_score(verdicts: list[Verdict]) -> float:
    """Return the overall trust score (0-100) for an answer."""
    raise NotImplementedError("Implemented by Role C in Sprint 1")
