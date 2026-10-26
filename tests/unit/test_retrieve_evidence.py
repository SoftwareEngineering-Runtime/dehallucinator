from unittest.mock import patch

from dehallucinator.evidence import retriever
from dehallucinator.models import Claim

CLAIM = Claim(id=1, text="The Eiffel Tower is 330 metres tall.", sentence_index=0)

PAGE = {
    "title": "Eiffel Tower",
    "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
    "text": "The tower is 330 metres tall. It was built in 1889.",
}


def test_returns_evidence_for_claim():
    with (
        patch.object(retriever, "build_query", return_value="Eiffel Tower"),
        patch.object(retriever, "search_wikipedia", return_value=["Eiffel Tower"]),
        patch.object(retriever, "fetch_page_text", return_value=PAGE),
    ):
        result = retriever.retrieve_evidence([CLAIM])

    assert result
    assert all(e.claim_id == 1 for e in result)
    assert all(e.source == "wikipedia" for e in result)
    assert all(0.0 <= e.relevance <= 1.0 for e in result)
    assert result[0].source_url == PAGE["url"]


def test_no_search_results_gives_empty_list():
    with (
        patch.object(retriever, "build_query", return_value="x"),
        patch.object(retriever, "search_wikipedia", return_value=[]),
    ):
        assert retriever.retrieve_evidence([CLAIM]) == []


def test_failed_page_fetch_is_skipped():
    with (
        patch.object(retriever, "build_query", return_value="x"),
        patch.object(retriever, "search_wikipedia", return_value=["A"]),
        patch.object(retriever, "fetch_page_text", return_value=None),
    ):
        assert retriever.retrieve_evidence([CLAIM]) == []


def test_empty_claims_list():
    assert retriever.retrieve_evidence([]) == []
