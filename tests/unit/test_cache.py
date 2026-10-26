from dehallucinator.evidence.cache import get_cached_page, put_cached_page

PAGE = {"title": "Eiffel Tower", "url": "u", "text": "The tower is 330 metres tall."}
DAY = 24 * 60 * 60


def test_miss_returns_none(tmp_path):
    assert get_cached_page("Nope", path=tmp_path / "c.db") is None


def test_hit_returns_stored_page(tmp_path):
    db = tmp_path / "c.db"
    put_cached_page("Eiffel Tower", PAGE, path=db, now=1000.0)
    assert get_cached_page("Eiffel Tower", path=db, now=1000.0 + DAY) == PAGE


def test_expired_entry_is_ignored(tmp_path):
    db = tmp_path / "c.db"
    put_cached_page("Eiffel Tower", PAGE, path=db, now=1000.0)
    assert get_cached_page("Eiffel Tower", path=db, now=1000.0 + 8 * DAY) is None


def test_sql_like_title_is_safe(tmp_path):
    db = tmp_path / "c.db"
    evil = "x'; DROP TABLE pages; --"
    put_cached_page(evil, PAGE, path=db, now=1000.0)
    assert get_cached_page(evil, path=db, now=1000.0) == PAGE
    assert get_cached_page("Eiffel Tower", path=db, now=1000.0) is None
