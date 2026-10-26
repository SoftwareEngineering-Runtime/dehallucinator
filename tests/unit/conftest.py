import pytest

from dehallucinator.evidence import retriever


@pytest.fixture(autouse=True)
def _isolate_retriever(monkeypatch):
    """No real cache file and no real sleeping in unit tests."""
    monkeypatch.setattr(retriever, "get_cached_page", lambda *a, **k: None)
    monkeypatch.setattr(retriever, "put_cached_page", lambda *a, **k: None)
    monkeypatch.setattr(retriever.time, "sleep", lambda *_: None)
