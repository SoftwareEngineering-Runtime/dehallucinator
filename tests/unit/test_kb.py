from dehallucinator.evidence import kb
from dehallucinator.evidence.kb import _title_from_url, load_kb_pages


def test_title_from_url_decodes_and_replaces_underscores():
    assert (
        _title_from_url("https://en.wikipedia.org/wiki/Albert_Einstein", "x") == "Albert Einstein"
    )
    assert _title_from_url("https://en.wikipedia.org/wiki/Marie%20Curie/", "x") == "Marie Curie"


def test_title_from_url_uses_fallback_when_name_is_empty():
    assert _title_from_url("/", "Fallback") == "Fallback"
    assert _title_from_url("https://x.org/___", "Fallback") == "Fallback"


def test_load_kb_pages_parses_files(tmp_path):
    (tmp_path / "a_with_url.txt").write_text(
        "https://en.wikipedia.org/wiki/Albert_Einstein\nLine one.\n\n  Line two.  \n",
        encoding="utf-8",
    )
    (tmp_path / "b_no_url.txt").write_text("Plain text here.\n", encoding="utf-8")

    pages = load_kb_pages(tmp_path)

    assert pages == [
        {
            "title": "Albert Einstein",
            "url": "kb://a_with_url.txt",
            "text": "Line one. Line two.",
        },
        {
            "title": "B No Url",
            "url": "kb://b_no_url.txt",
            "text": "Plain text here.",
        },
    ]


def test_load_kb_pages_skips_empty_and_non_txt_files(tmp_path):
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    (tmp_path / "blank.txt").write_text("  \n\n", encoding="utf-8")
    (tmp_path / "only_url.txt").write_text("https://en.wikipedia.org/wiki/X\n", encoding="utf-8")
    (tmp_path / ".gitkeep").write_text("not a kb file", encoding="utf-8")
    (tmp_path / "notes.md").write_text("ignored", encoding="utf-8")

    assert load_kb_pages(tmp_path) == []


def test_load_kb_pages_truncates_text(tmp_path, monkeypatch):
    monkeypatch.setattr(kb, "WIKI_MAX_CHARS", 10)
    (tmp_path / "long.txt").write_text("a" * 50, encoding="utf-8")

    pages = load_kb_pages(tmp_path)

    assert pages[0]["text"] == "a" * 10


def test_load_kb_pages_missing_folder_returns_empty(tmp_path):
    assert load_kb_pages(tmp_path / "does_not_exist") == []


def test_load_kb_pages_loads_real_kb():
    pages = load_kb_pages()
    assert len(pages) == 15
    for page in pages:
        assert page["url"].startswith("kb://")
        assert page["title"]
        assert page["text"].strip()
