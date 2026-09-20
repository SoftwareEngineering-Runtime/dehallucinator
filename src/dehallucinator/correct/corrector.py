"""Corrector (Role D): rewrites or flags wrong claims."""

from dehallucinator.models import Claim, Verdict


def correct(text: str, claims: list[Claim], verdicts: list[Verdict]) -> str:
    """Return the corrected answer text."""
    raise NotImplementedError("Implemented by Role D in Sprint 1")
