import pytest
from spacy.lang.en.stop_words import STOP_WORDS

from dehallucinator.config import MAX_QUERY_WORDS, WIKI_MAX_CHARS, WIKI_TOP_PAGES
from dehallucinator.evidence import retriever
from dehallucinator.evidence.retriever import build_query


class FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def test_tc_2_01_entities_come_before_noun_chunks():
    words = build_query("The famous bridge was designed by Gustave Eiffel in Paris.").split()
    assert "Gustave" in words and "Paris" in words and "bridge" in words
    assert words.index("Gustave") < words.index("bridge")
    assert words.index("Paris") < words.index("bridge")


def test_tc_2_02_stop_words_removed_and_capped_at_8_words():
    claim = (
        "The history of the ancient Roman Empire and its many emperors, generals, "
        "senators, architects, and engineers is often studied by modern historians "
        "in universities around Europe."
    )
    words = build_query(claim).split()
    assert 0 < len(words) <= MAX_QUERY_WORDS
    assert not any(w.lower() in STOP_WORDS for w in words)


@pytest.mark.parametrize("empty", ["", "   ", None])
def test_empty_claim_returns_empty_query(empty):
    assert build_query(empty) == ""


def test_tc_2_03_search_uses_limit_and_user_agent(monkeypatch):
    seen = {}

    def fake_get(url, params, headers, timeout):
        seen.update(params=params, headers=headers)
        return FakeResp({"query": {"search": [{"title": "Eiffel Tower"}]}})

    monkeypatch.setattr(retriever.requests, "get", fake_get)
    assert retriever.search_wikipedia("Eiffel Tower") == ["Eiffel Tower"]
    assert seen["params"]["srlimit"] == WIKI_TOP_PAGES == 3
    assert "User-Agent" in seen["headers"]


def test_tc_2_04_fetch_truncates_and_builds_url(monkeypatch):
    payload = {
        "query": {"pages": {"1": {"title": "Eiffel Tower", "extract": "x" * 10000}}}
    }
    monkeypatch.setattr(retriever.requests, "get", lambda *a, **k: FakeResp(payload))
    page = retriever.fetch_page_text("Eiffel Tower")
    assert len(page["text"]) == WIKI_MAX_CHARS == 6000
    assert page["url"] == "https://en.wikipedia.org/wiki/Eiffel_Tower"
