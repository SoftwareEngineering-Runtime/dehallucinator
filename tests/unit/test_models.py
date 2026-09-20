"""Tests for the shared data models (Role A)."""

import pytest
from pydantic import ValidationError

from dehallucinator.models import CheckedAnswer, Claim, Evidence, Verdict


def make_evidence(**overrides) -> Evidence:
    data = {
        "claim_id": 1,
        "source": "wikipedia",
        "source_url": "https://en.wikipedia.org/wiki/Paris",
        "title": "Paris",
        "snippet": "Paris is the capital of France.",
        "relevance": 0.9,
    }
    data.update(overrides)
    return Evidence(**data)


def test_claim_holds_its_fields():
    claim = Claim(id=1, text="Paris is the capital of France.", sentence_index=0)
    assert claim.id == 1
    assert claim.sentence_index == 0


def test_evidence_rejects_unknown_source():
    with pytest.raises(ValidationError):
        make_evidence(source="blog")


@pytest.mark.parametrize("relevance", [-0.1, 1.1])
def test_evidence_relevance_must_be_between_0_and_1(relevance):
    with pytest.raises(ValidationError):
        make_evidence(relevance=relevance)


def test_verdict_rejects_unknown_label():
    with pytest.raises(ValidationError):
        Verdict(claim_id=1, label="MAYBE", score=0.5)


def test_verdict_best_evidence_is_optional():
    verdict = Verdict(claim_id=1, label="NOT_ENOUGH_INFO", score=0.0)
    assert verdict.best_evidence is None


def test_checked_answer_trust_score_capped_at_100():
    with pytest.raises(ValidationError):
        CheckedAnswer(original="x", corrected="x", claims=[], verdicts=[], trust_score=101)
