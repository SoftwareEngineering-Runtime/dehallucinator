from unittest.mock import MagicMock, patch

import pytest
import requests

from dehallucinator.config import HTTP_RETRIES
from dehallucinator.evidence import retriever


def _http_error(status):
    resp = MagicMock()
    resp.status_code = status
    return requests.HTTPError(response=resp)


def test_retries_then_succeeds():
    ok = MagicMock()
    ok.json.return_value = {"query": {"search": []}}
    ok.raise_for_status.return_value = None
    with patch.object(retriever.requests, "get", side_effect=[requests.Timeout(), ok]) as get:
        assert retriever._wiki_get({"action": "query"}) == {"query": {"search": []}}
    assert get.call_count == 2


def test_gives_up_after_retries():
    with patch.object(retriever.requests, "get", side_effect=requests.ConnectionError()) as get:
        with pytest.raises(requests.ConnectionError):
            retriever._wiki_get({"action": "query"})
    assert get.call_count == HTTP_RETRIES + 1


def test_client_error_is_not_retried():
    bad = MagicMock()
    bad.raise_for_status.side_effect = _http_error(404)
    with patch.object(retriever.requests, "get", return_value=bad) as get:
        with pytest.raises(requests.HTTPError):
            retriever._wiki_get({"action": "query"})
    assert get.call_count == 1


def test_network_down_falls_back_to_kb_only():
    claim = retriever.Claim(id=1, text="The Eiffel Tower is 330 metres tall.", sentence_index=0)
    kb_page = {
        "title": "Eiffel Tower",
        "url": "kb://eiffel_tower.txt",
        "text": "The tower is 330 metres tall. It was built in 1889.",
    }
    with (
        patch.object(retriever.requests, "get", side_effect=requests.Timeout()),
        patch.object(retriever, "build_query", return_value="Eiffel Tower"),
        patch.object(retriever, "load_kb_pages", return_value=[kb_page]),
    ):
        result = retriever.retrieve_evidence([claim])
    assert result
    assert all(e.source == "local_kb" for e in result)


def test_fetch_page_text_uses_cache_without_network():
    cached = {"title": "Eiffel Tower", "url": "u", "text": "cached text"}
    with (
        patch.object(retriever, "get_cached_page", return_value=cached),
        patch.object(retriever, "_wiki_get") as wiki,
    ):
        assert retriever.fetch_page_text("Eiffel Tower") == cached
    wiki.assert_not_called()


def test_fetch_page_text_stores_result_in_cache():
    data = {"query": {"pages": {"1": {"title": "Eiffel Tower", "extract": "Text."}}}}
    with (
        patch.object(retriever, "_wiki_get", return_value=data),
        patch.object(retriever, "put_cached_page") as put,
    ):
        page = retriever.fetch_page_text("Eiffel Tower")
    assert page["text"] == "Text."
    put.assert_called_once_with("Eiffel Tower", page)
