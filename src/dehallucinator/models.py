"""Shared data models passed between the pipeline stages.

These formats are frozen (manual Section 4.2). Every module reads and
returns these objects, so the four features can be built in parallel.
"""

from typing import Literal

from pydantic import BaseModel, Field

Label = Literal["SUPPORTED", "CONTRADICTED", "NOT_ENOUGH_INFO"]


class Claim(BaseModel):
    """One standalone factual statement taken from the AI answer."""

    id: int  # 1, 2, 3 ... in order of appearance
    text: str
    sentence_index: int  # which sentence of the original answer (0-based)


class Evidence(BaseModel):
    """A snippet from a trusted source that relates to one claim."""

    claim_id: int
    source: Literal["wikipedia", "local_kb"]
    source_url: str  # Wikipedia page URL or "kb://<filename>"
    title: str
    snippet: str  # 1-3 sentences of evidence text
    relevance: float = Field(ge=0.0, le=1.0)


class Verdict(BaseModel):
    """The verifier's decision for one claim."""

    claim_id: int
    label: Label
    score: float = Field(ge=0.0, le=1.0)  # confidence in the label
    best_evidence: Evidence | None = None


class CheckedAnswer(BaseModel):
    """Final output of the pipeline for one AI answer."""

    original: str
    corrected: str
    claims: list[Claim]
    verdicts: list[Verdict]
    trust_score: float = Field(ge=0.0, le=100.0)
