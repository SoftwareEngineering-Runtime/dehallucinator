"""Tests for the Verifier (Role C)."""

from unittest.mock import patch

from dehallucinator.models import Claim, Evidence, Verdict
from dehallucinator.verify import verifier
from dehallucinator.verify.verifier import trust_score, verify_claims


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


@patch("dehallucinator.verify.verifier._predict")
def test_tc_3_02_high_entailment_is_supported(mock_predict):
    mock_predict.return_value = [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]

    claims = [Claim(id=1, text="Paris is in France.", sentence_index=0)]
    evidence = [
        Evidence(
            claim_id=1,
            source="local_kb",
            source_url="kb://test",
            title="Test",
            snippet="Paris is the capital of France.",
            relevance=1.0,
        )
    ]

    verdicts = verify_claims(claims, evidence)

    assert verdicts[0].label == "SUPPORTED"
    assert verdicts[0].score == 0.9
    assert verdicts[0].best_evidence == evidence[0]


@patch("dehallucinator.verify.verifier._predict")
def test_tc_3_04_no_evidence_is_not_enough_info(mock_predict):
    claims = [Claim(id=2, text="Unknown fact.", sentence_index=1)]

    verdicts = verify_claims(claims, [])

    assert verdicts[0].label == "NOT_ENOUGH_INFO"
    assert verdicts[0].score == 0.0
    assert verdicts[0].best_evidence is None
    mock_predict.assert_not_called()


@patch("dehallucinator.verify.verifier._predict")
def test_tc_3_03_high_contradiction_is_contradicted(mock_predict):
    mock_predict.return_value = [{"entailment": 0.05, "contradiction": 0.9, "neutral": 0.05}]

    claims = [Claim(id=1, text="Paris is in Italy.", sentence_index=0)]
    evidence = [
        Evidence(
            claim_id=1,
            source="local_kb",
            source_url="kb://test",
            title="Test",
            snippet="Paris is the capital of France.",
            relevance=1.0,
        )
    ]

    verdicts = verify_claims(claims, evidence)

    assert verdicts[0].label == "CONTRADICTED"
    assert verdicts[0].score == 0.9
    assert verdicts[0].best_evidence == evidence[0]


@patch("dehallucinator.verify.verifier._predict")
def test_tc_3_05_uncertain_evidence_is_not_enough_info(mock_predict):
    mock_predict.return_value = [{"entailment": 0.3, "contradiction": 0.2, "neutral": 0.5}]

    claims = [Claim(id=1, text="The fact is true.", sentence_index=0)]
    evidence = [
        Evidence(
            claim_id=1,
            source="local_kb",
            source_url="kb://test",
            title="Test",
            snippet="Some unrelated information.",
            relevance=1.0,
        )
    ]

    verdicts = verify_claims(claims, evidence)

    assert verdicts[0].label == "NOT_ENOUGH_INFO"
    assert verdicts[0].score == 0.7
    assert verdicts[0].best_evidence == evidence[0]


@patch("dehallucinator.verify.verifier._predict")
def test_tc_3_06_only_matching_claim_evidence_is_used(mock_predict):
    mock_predict.return_value = [{"entailment": 0.9, "contradiction": 0.05, "neutral": 0.05}]

    claims = [Claim(id=1, text="Paris is in France.", sentence_index=0)]
    evidence = [
        Evidence(
            claim_id=2,
            source="local_kb",
            source_url="kb://other",
            title="Other",
            snippet="This belongs to another claim.",
            relevance=1.0,
        ),
        Evidence(
            claim_id=1,
            source="local_kb",
            source_url="kb://test",
            title="Test",
            snippet="Paris is the capital of France.",
            relevance=1.0,
        ),
    ]

    verdicts = verify_claims(claims, evidence)

    assert verdicts[0].label == "SUPPORTED"
    assert verdicts[0].best_evidence == evidence[1]
    mock_predict.assert_called_once_with(
        [("Paris is the capital of France.", "Paris is in France.")]
    )


@patch("transformers.AutoModelForSequenceClassification.from_pretrained")
@patch("transformers.AutoTokenizer.from_pretrained")
def test_tc_3_07_model_is_loaded_lazily(mock_tokenizer_load, mock_model_load):
    mock_tokenizer = mock_tokenizer_load.return_value
    mock_model = mock_model_load.return_value

    verifier._model = None
    verifier._tokenizer = None

    tokenizer, model = verifier._load_model()

    assert tokenizer is mock_tokenizer
    assert model is mock_model
    mock_tokenizer_load.assert_called_once_with(verifier.config.NLI_MODEL)
    mock_model_load.assert_called_once_with(verifier.config.NLI_MODEL)
