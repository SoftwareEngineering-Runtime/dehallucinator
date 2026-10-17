"""Integration tests for the full dehallucinator pipeline."""

from dehallucinator import pipeline
from dehallucinator.models import Evidence, Verdict


def test_pipeline_corrects_contradicted_claim(monkeypatch):
    text = "The Eiffel Tower was completed in 1899."

    def fake_retrieve(claims):
        return [
            Evidence(
                claim_id=claims[0].id,
                source="wikipedia",
                source_url="https://en.wikipedia.org/wiki/Eiffel_Tower",
                title="Eiffel Tower",
                snippet="The Eiffel Tower was completed in 1889.",
                relevance=0.95,
            )
        ]

    monkeypatch.setattr(pipeline, "retrieve_evidence", fake_retrieve)
    monkeypatch.setattr(
        pipeline,
        "verify_claims",
        lambda claims, evidence: [
            Verdict(
                claim_id=claims[0].id,
                label="CONTRADICTED",
                score=0.99,
                best_evidence=evidence[0],
            )
        ],
    )

    result = pipeline.check_answer(text)

    assert len(result.claims) == 1
    assert result.verdicts[0].label == "CONTRADICTED"
    assert "completed in 1889" in result.corrected
    assert "[corrected, source:" in result.corrected


def test_pipeline_tags_supported_claim(monkeypatch):
    text = "The Eiffel Tower is located in Paris."

    def fake_retrieve(claims):
        return [
            Evidence(
                claim_id=claims[0].id,
                source="wikipedia",
                source_url="https://en.wikipedia.org/wiki/Eiffel_Tower",
                title="Eiffel Tower",
                snippet="The Eiffel Tower is located in Paris.",
                relevance=0.95,
            )
        ]

    monkeypatch.setattr(pipeline, "retrieve_evidence", fake_retrieve)
    monkeypatch.setattr(
        pipeline,
        "verify_claims",
        lambda claims, evidence: [
            Verdict(
                claim_id=claims[0].id,
                label="SUPPORTED",
                score=0.99,
                best_evidence=evidence[0],
            )
        ],
    )

    result = pipeline.check_answer(text)

    assert len(result.claims) == 1
    assert result.verdicts[0].label == "SUPPORTED"
    assert "[source: https://en.wikipedia.org/wiki/Eiffel_Tower]" in result.corrected


def test_pipeline_skips_retrieval_when_no_claims(monkeypatch):
    def unexpected_retrieval(claims):
        raise AssertionError("Retrieval should be skipped when there are no claims")

    monkeypatch.setattr(pipeline, "retrieve_evidence", unexpected_retrieval)

    result = pipeline.check_answer("Hello! How can I help you today?")

    assert result.claims == []
    assert result.verdicts == []
    assert result.trust_score == 100.0
    assert result.corrected == "Hello! How can I help you today?"
