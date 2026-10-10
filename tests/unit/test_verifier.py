"""Tests for the Verifier (Role C)."""

from dehallucinator.models import Verdict
from dehallucinator.verify.verifier import trust_score


def test_trust_score_empty_list():
    assert trust_score([]) == 100.0


def test_trust_score_all_supported():
    verdicts = [
        Verdict(claim_id=1, label="SUPPORTED", score=1.0),
        Verdict(claim_id=2, label="SUPPORTED", score=1.0),
    ]
    assert trust_score(verdicts) == 100.0


def test_trust_score_all_contradicted():
    verdicts = [
        Verdict(claim_id=1, label="CONTRADICTED", score=1.0),
        Verdict(claim_id=2, label="CONTRADICTED", score=1.0),
    ]
    assert trust_score(verdicts) == 0.0


def test_trust_score_mixed_verdicts():
    verdicts = [
        Verdict(claim_id=1, label="SUPPORTED", score=1.0),
        Verdict(claim_id=2, label="NOT_ENOUGH_INFO", score=0.5),
        Verdict(claim_id=3, label="CONTRADICTED", score=1.0),
    ]
    assert trust_score(verdicts) == 50.0
