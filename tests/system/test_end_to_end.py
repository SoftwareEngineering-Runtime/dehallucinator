"""System tests for the 10 provided Dehallucinator samples (DH-198)."""

import json
from pathlib import Path

import pytest

from dehallucinator import pipeline
from dehallucinator.evidence import retriever

SAMPLES_PATH = Path(__file__).resolve().parents[2] / "data" / "samples.json"

with SAMPLES_PATH.open(encoding="utf-8") as file:
    SAMPLES = json.load(file)


@pytest.fixture(autouse=True)
def offline_wikipedia(monkeypatch):
    """Use the real local KB without making Wikipedia requests."""
    monkeypatch.setattr(retriever, "search_wikipedia", lambda query: [])


@pytest.mark.slow
@pytest.mark.parametrize("sample", SAMPLES, ids=lambda sample: str(sample["id"]))
def test_end_to_end_samples(sample):
    """Check the complete pipeline against each sample's expected claims."""
    result = pipeline.check_answer(sample["answer"])

    assert result.original == sample["answer"]
    assert len(result.claims) == len(result.verdicts)
    assert 0 <= result.trust_score <= 100
    assert result.corrected.strip()

    verdicts_by_claim = {
        claim.text.strip(): verdict
        for claim, verdict in zip(result.claims, result.verdicts, strict=True)
    }

    for hallucination in sample["hallucinations"]:
        assert hallucination in verdicts_by_claim, (
            f"Sample {sample['id']}: expected claim was not extracted"
        )
        assert verdicts_by_claim[hallucination].label == "CONTRADICTED", (
            f"Sample {sample['id']}: hallucination was not detected"
        )

    if not sample["hallucinations"]:
        assert all(verdict.label != "CONTRADICTED" for verdict in result.verdicts), (
            f"Sample {sample['id']}: correct answer was falsely flagged"
        )
