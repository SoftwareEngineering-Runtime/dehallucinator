"""Tests for check_answer() (Role D). The four stages are replaced with fakes."""

import logging

import pytest

from dehallucinator import pipeline
from dehallucinator.models import CheckedAnswer, Claim, Evidence, Verdict

TEXT = "The Eiffel Tower was completed in 1899. It is located in Paris."
URL = "https://en.wikipedia.org/wiki/Eiffel_Tower"


def make_evidence(claim_id: int, snippet: str) -> Evidence:
    return Evidence(
        claim_id=claim_id,
        source="wikipedia",
        source_url=URL,
        title="Eiffel Tower",
        snippet=snippet,
        relevance=0.9,
    )


CLAIMS = [
    Claim(id=1, text="The Eiffel Tower was completed in 1899.", sentence_index=0),
    Claim(id=2, text="The Eiffel Tower is located in Paris.", sentence_index=1),
]
EVIDENCE = [
    make_evidence(1, "The Eiffel Tower was completed in 1889."),
    make_evidence(2, "The tower is on the Champ de Mars in Paris."),
]
VERDICTS = [
    Verdict(claim_id=1, label="CONTRADICTED", score=0.94, best_evidence=EVIDENCE[0]),
    Verdict(claim_id=2, label="SUPPORTED", score=0.97, best_evidence=EVIDENCE[1]),
]


@pytest.fixture
def fake_stages(monkeypatch):
    """Replace every stage with a fake that records how it was called."""
    calls = []

    def extract(text):
        calls.append(("extract", text))
        return CLAIMS

    def retrieve(claims):
        calls.append(("retrieve", claims))
        return EVIDENCE

    def verify(claims, evidence):
        calls.append(("verify", claims, evidence))
        return VERDICTS

    def score(verdicts):
        calls.append(("score", verdicts))
        return 50.0

    def correct(text, claims, verdicts):
        calls.append(("correct", text, claims, verdicts))
        return "CORRECTED"

    monkeypatch.setattr(pipeline, "extract_claims", extract)
    monkeypatch.setattr(pipeline, "retrieve_evidence", retrieve)
    monkeypatch.setattr(pipeline, "verify_claims", verify)
    monkeypatch.setattr(pipeline, "trust_score", score)
    monkeypatch.setattr(pipeline, "correct", correct)
    return calls


def test_stages_run_in_order_and_pass_their_outputs_along(fake_stages):
    pipeline.check_answer(TEXT)

    assert fake_stages == [
        ("extract", TEXT),
        ("retrieve", CLAIMS),
        ("verify", CLAIMS, EVIDENCE),
        ("score", VERDICTS),
        ("correct", TEXT, CLAIMS, VERDICTS),
    ]


def test_returns_checked_answer_with_every_field(fake_stages):
    result = pipeline.check_answer(TEXT)

    assert result == CheckedAnswer(
        original=TEXT,
        corrected="CORRECTED",
        claims=CLAIMS,
        verdicts=VERDICTS,
        trust_score=50.0,
    )


def test_no_claims_skips_retriever_and_verifier(fake_stages, monkeypatch):
    monkeypatch.setattr(pipeline, "extract_claims", lambda text: [])

    result = pipeline.check_answer("Hello! How can I help you today?")

    stages = [call[0] for call in fake_stages]
    assert stages == ["score", "correct"]
    assert result.claims == [] and result.verdicts == []


def test_each_stage_time_is_logged_in_milliseconds(fake_stages, caplog):
    with caplog.at_level(logging.INFO, logger="dehallucinator.pipeline"):
        pipeline.check_answer(TEXT)

    message = caplog.records[-1].getMessage()
    for stage in ("extract", "retrieve", "verify", "score", "correct"):
        assert f"{stage} " in message
    assert message.count(" ms") == 5
    assert "2 claims" in message and "trust 50.0" in message


@pytest.mark.parametrize("bad_input", ["", "   \n\t", "x" * 5001])
def test_invalid_input_raises_value_error(bad_input):
    # Uses the real Claim Extractor, which validates the input (FR-1.1).
    with pytest.raises(ValueError):
        pipeline.check_answer(bad_input)


def test_error_in_a_stage_is_not_swallowed(fake_stages, monkeypatch):
    def broken(claims):
        raise RuntimeError("retriever down")

    monkeypatch.setattr(pipeline, "retrieve_evidence", broken)

    with pytest.raises(RuntimeError, match="retriever down"):
        pipeline.check_answer(TEXT)


def test_real_corrector_and_trust_score_with_faked_retriever_and_verifier(monkeypatch):
    # Real extractor, corrector and trust score; only the network/model stages are faked.
    monkeypatch.setattr(pipeline, "retrieve_evidence", lambda claims: EVIDENCE)
    monkeypatch.setattr(pipeline, "verify_claims", lambda claims, evidence: VERDICTS)
    text = "The Eiffel Tower was completed in 1899. The Eiffel Tower is located in Paris."

    result = pipeline.check_answer(text)

    assert [c.text for c in result.claims] == [c.text for c in CLAIMS]
    assert result.trust_score == 50.0
    assert result.corrected == (
        f"The Eiffel Tower was completed in 1889. [corrected, source: {URL}] "
        f"The Eiffel Tower is located in Paris. [source: {URL}]"
    )
