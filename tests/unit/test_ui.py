"""Tests for the demo UI (Role D). The pipeline is faked, so no network or model is used."""

import json
import time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from dehallucinator import pipeline
from dehallucinator.models import CheckedAnswer, Claim, Evidence, Verdict
from dehallucinator.ui_render import (
    LABEL_STYLE,
    ClaimRow,
    claim_html,
    claim_rows,
    load_samples,
    source_html,
    trust_colour,
)

APP = str(Path(__file__).resolve().parents[2] / "ui" / "app.py")
URL = "https://en.wikipedia.org/wiki/Eiffel_Tower"
_REAL_SLEEP = time.sleep  # captured at import, before tests/unit/conftest.py patches it


@pytest.fixture(autouse=True)
def _real_sleep(monkeypatch):
    # conftest.py replaces time.sleep for the retriever tests, and retriever.time is the
    # global time module, so the patch reaches Streamlit too. AppTest polls with sleep while
    # the page script runs; without a real sleep it spins and the script times out.
    monkeypatch.setattr(time, "sleep", _REAL_SLEEP)


def make_result(text="The Eiffel Tower was completed in 1899.") -> CheckedAnswer:
    evidence = Evidence(
        claim_id=1,
        source="wikipedia",
        source_url=URL,
        title="Eiffel Tower",
        snippet="The tower was built from 1887 to 1889.",
        relevance=0.9,
    )
    return CheckedAnswer(
        original=text,
        corrected=f"The tower was built from 1887 to 1889. [corrected, source: {URL}]",
        claims=[
            Claim(id=1, text=text, sentence_index=0),
            Claim(id=2, text="The Eiffel Tower is in Paris.", sentence_index=1),
        ],
        verdicts=[Verdict(claim_id=1, label="CONTRADICTED", score=0.94, best_evidence=evidence)],
        trust_score=25.0,
    )


# ---- samples.json (FR-4.5) -------------------------------------------------------------


def test_samples_file_has_ten_answers_on_kb_topics():
    samples = load_samples()
    kb_dir = Path(__file__).resolve().parents[2] / "data" / "kb"

    assert len(samples) == 10
    assert len({s["id"] for s in samples}) == 10
    for sample in samples:
        assert (kb_dir / sample["kb_file"]).exists(), sample["kb_file"]
        for wrong in sample["hallucinations"]:
            assert wrong in sample["answer"]


def test_load_samples_rejects_a_sample_without_an_answer(tmp_path):
    path = tmp_path / "samples.json"
    path.write_text(json.dumps([{"id": 1, "title": "x"}]), encoding="utf-8")

    with pytest.raises(ValueError, match="title and an answer"):
        load_samples(path)


def test_load_samples_rejects_an_over_long_answer(tmp_path):
    path = tmp_path / "samples.json"
    path.write_text(json.dumps([{"id": 1, "title": "x", "answer": "a" * 5001}]), "utf-8")

    with pytest.raises(ValueError, match="5000"):
        load_samples(path)


# ---- rendering (FR-4.6) ----------------------------------------------------------------


def test_claim_rows_join_claims_with_verdicts():
    rows = claim_rows(make_result())

    assert rows[0].label == "CONTRADICTED"
    assert rows[0].source_url == URL
    assert rows[0].evidence == "The tower was built from 1887 to 1889."
    # Claim 2 has no verdict, so it is shown as unverified.
    assert rows[1].label == "NOT_ENOUGH_INFO" and rows[1].source_url is None


@pytest.mark.parametrize("label", ["SUPPORTED", "CONTRADICTED", "NOT_ENOUGH_INFO"])
def test_each_label_gets_its_colour(label):
    row = ClaimRow("Mars is red.", label, 0.8, None, None, None)

    assert LABEL_STYLE[label][0] in claim_html(row)
    assert LABEL_STYLE[label][1] in claim_html(row)


def test_script_in_claim_and_evidence_is_escaped():
    row = ClaimRow(
        text="<script>alert(1)</script> Paris is in France.",
        label="SUPPORTED",
        score=0.9,
        source_title='<img src=x onerror="alert(2)">',
        source_url=URL,
        evidence="<b>bold</b> evidence",
    )

    out = claim_html(row)

    assert "<script>" not in out and "<img" not in out and "<b>" not in out
    assert "&lt;script&gt;" in out and "&lt;b&gt;bold&lt;/b&gt;" in out


def test_http_source_is_a_link_and_kb_source_is_text():
    assert source_html("Eiffel Tower", URL) == (f'<a href="{URL}" target="_blank">Eiffel Tower</a>')
    assert source_html("Mars", "kb://mars.txt") == "Mars (kb://mars.txt)"


def test_javascript_url_is_never_made_a_link():
    out = source_html("click me", "javascript:alert(1)")

    assert "<a" not in out and "href" not in out


def test_quote_in_url_cannot_break_out_of_the_href():
    out = source_html("x", 'https://e.org/"onmouseover="alert(1)')

    assert '"onmouseover' not in out and "&quot;onmouseover" in out


@pytest.mark.parametrize(
    ("score", "label"),
    [
        (100, "SUPPORTED"),
        (75, "SUPPORTED"),
        (74.9, "NOT_ENOUGH_INFO"),
        (40, "NOT_ENOUGH_INFO"),
        (39.9, "CONTRADICTED"),
        (0, "CONTRADICTED"),
    ],
)
def test_trust_colour_bands(score, label):
    assert trust_colour(score) == LABEL_STYLE[label][0]


# ---- the Streamlit page ----------------------------------------------------------------


@pytest.fixture
def fake_check(monkeypatch):
    calls = []

    def check_answer(text):
        calls.append(text)
        return make_result(text)

    monkeypatch.setattr(pipeline, "check_answer", check_answer)
    return calls


def test_page_loads_with_the_first_sample_selected():
    at = AppTest.from_file(APP, default_timeout=30).run()

    assert not at.exception
    assert at.selectbox[0].value == "Eiffel Tower"
    assert len(at.selectbox[0].options) == 11  # 10 samples + "Paste your own answer"
    assert at.text_area[0].value.startswith("The Eiffel Tower was completed in 1899.")


def test_check_button_shows_trust_score_claims_and_corrected_answer(fake_check):
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()

    assert not at.exception
    assert fake_check == [at.text_area[0].value]
    page = " ".join(m.value for m in at.markdown)
    assert "25.0" in page
    assert "Contradicted" in page and "Unverified" in page
    assert "[corrected, source:" in page


def test_choosing_paste_your_own_clears_the_box():
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.selectbox[0].select("Paste your own answer").run()

    assert at.text_area[0].value == ""


def test_empty_input_shows_an_error(fake_check, monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "check_answer",
        lambda text: (_ for _ in ()).throw(ValueError("Input text is empty")),
    )
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.selectbox[0].select("Paste your own answer").run()
    at.button[0].click().run()

    assert at.error[0].value == "Invalid input: Input text is empty"


def test_unexpected_error_shows_a_generic_message(monkeypatch):
    def broken(text):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(pipeline, "check_answer", broken)
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()

    assert "secret internal detail" not in at.error[0].value
    assert "Something went wrong" in at.error[0].value


def test_answer_with_no_claims_says_so(monkeypatch):
    monkeypatch.setattr(
        pipeline,
        "check_answer",
        lambda text: CheckedAnswer(
            original=text, corrected=text, claims=[], verdicts=[], trust_score=100.0
        ),
    )
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()

    assert at.info[0].value == "No factual claims found in this answer."


def test_script_in_the_corrected_answer_is_escaped_on_the_page(monkeypatch):
    script = "<script>alert(1)</script> The Eiffel Tower is in Paris."
    monkeypatch.setattr(
        pipeline,
        "check_answer",
        lambda text: CheckedAnswer(
            original=script, corrected=script, claims=[], verdicts=[], trust_score=100.0
        ),
    )
    at = AppTest.from_file(APP, default_timeout=30).run()
    at.button[0].click().run()

    page = " ".join(m.value for m in at.markdown)
    assert "<script>" not in page and "&lt;script&gt;" in page
