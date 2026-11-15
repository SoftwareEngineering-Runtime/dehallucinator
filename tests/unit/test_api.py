"""Tests for the API (Role D). check_answer is faked, so no network or model is used."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from dehallucinator import pipeline
from dehallucinator.api import app
from dehallucinator.models import CheckedAnswer, Claim, Verdict

client = TestClient(app)

TEXT = "The Eiffel Tower is located in Paris."
ANSWER = CheckedAnswer(
    original=TEXT,
    corrected=f"{TEXT} [unverified]",
    claims=[Claim(id=1, text=TEXT, sentence_index=0)],
    verdicts=[Verdict(claim_id=1, label="NOT_ENOUGH_INFO", score=0.0)],
    trust_score=50.0,
)


@pytest.fixture
def fake_check(monkeypatch):
    calls = []

    def check_answer(text):
        calls.append(text)
        return ANSWER

    monkeypatch.setattr(pipeline, "check_answer", check_answer)
    return calls


def test_tc_4_06_check_returns_checked_answer(fake_check):
    response = client.post("/check", json={"text": TEXT})

    assert response.status_code == 200
    assert response.json() == ANSWER.model_dump()
    assert fake_check == [TEXT]


def test_tc_4_07_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"text": ""},
        {"text": "   \n "},
        {"text": 42},
        {"text": "x" * 5001},
        {"message": TEXT},
    ],
    ids=["missing", "empty", "blank", "wrong-type", "too-long", "wrong-field"],
)
def test_tc_4_08_invalid_input_returns_422(fake_check, body):
    response = client.post("/check", json=body)

    assert response.status_code == 422
    assert fake_check == []  # the pipeline is never called


def test_tc_4_08_malformed_json_returns_422(fake_check):
    response = client.post(
        "/check", content='{"text": "unterminated', headers={"Content-Type": "application/json"}
    )

    assert response.status_code == 422
    assert fake_check == []


def test_exactly_5000_characters_is_accepted(fake_check):
    response = client.post("/check", json={"text": "x" * 5000})

    assert response.status_code == 200


def test_value_error_from_pipeline_returns_422(monkeypatch):
    def check_answer(text):
        raise ValueError("Input exceeds 5000 characters")

    monkeypatch.setattr(pipeline, "check_answer", check_answer)

    response = client.post("/check", json={"text": TEXT})

    assert response.status_code == 422
    assert response.json() == {"detail": "Input exceeds 5000 characters"}


def test_tc_4_09_unexpected_error_returns_500_without_stack_trace(monkeypatch, caplog):
    def check_answer(text):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(pipeline, "check_answer", check_answer)

    response = client.post("/check", json={"text": TEXT})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "secret internal detail" not in response.text
    assert "Traceback" not in response.text
    assert "secret internal detail" in caplog.text  # still logged for the team


def test_script_input_is_returned_as_json_data_not_html(monkeypatch):
    script = "<script>alert(1)</script> The Eiffel Tower is in Paris."
    monkeypatch.setattr(
        pipeline,
        "check_answer",
        lambda text: ANSWER.model_copy(update={"original": text, "corrected": text}),
    )

    response = client.post("/check", json={"text": script})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["original"] == script


def test_committed_openapi_spec_matches_the_app():
    # docs/design/openapi.json is the API spec in the design doc (DH-191). Regenerate it with
    # python -c "import json; from dehallucinator.api import app;
    #            print(json.dumps(app.openapi(), indent=2))" > docs/design/openapi.json
    spec_path = Path(__file__).resolve().parents[2] / "docs" / "design" / "openapi.json"

    assert json.loads(spec_path.read_text(encoding="utf-8")) == app.openapi()
