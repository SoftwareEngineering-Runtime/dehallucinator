"""Claim Extractor (Role A): splits an AI answer into factual claims."""

from dehallucinator.models import Claim


def extract_claims(text: str) -> list[Claim]:
    """Return the factual claims found in ``text``."""
    raise NotImplementedError("DH-161: implemented in Sprint 1")
