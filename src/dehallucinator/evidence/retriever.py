"""Evidence Retriever (Role B): finds evidence for each claim."""

from dehallucinator.models import Claim, Evidence


def retrieve_evidence(claims: list[Claim]) -> list[Evidence]:
    """Return evidence snippets for the given claims."""
    raise NotImplementedError("Implemented by Role B in Sprint 1")
