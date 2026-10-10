"""Verifier & Scorer (Role C): labels each claim using its evidence."""

from transformers import AutoModelForSequenceClassification, AutoTokenizer

from dehallucinator import config
from dehallucinator.models import Claim, Evidence, Verdict

_tokenizer = None
_model = None


def _load_model():
    """Lazily load the NLI model and tokenizer into module-level variables."""
    global _tokenizer, _model

    if _model is None or _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(config.NLI_MODEL)
        _model = AutoModelForSequenceClassification.from_pretrained(config.NLI_MODEL)

    return _tokenizer, _model


def verify_claims(claims: list[Claim], evidence: list[Evidence]) -> list[Verdict]:
    """Return one verdict per claim."""
    raise NotImplementedError("Implemented by Role C in Sprint 1")


def trust_score(verdicts: list[Verdict]) -> float:
    """Return the overall trust score (0-100) for an answer."""
    if not verdicts:
        return 100.0

    score_map = {
        "SUPPORTED": 1.0,
        "NOT_ENOUGH_INFO": 0.5,
        "CONTRADICTED": 0.0,
    }

    total = sum(score_map[v.label] for v in verdicts)
    avg = total / len(verdicts)
    return round(avg * 100, 1)
