"""Local knowledge base: offline evidence source (FR-2.4)."""

from functools import lru_cache
from pathlib import Path
from urllib.parse import unquote

from dehallucinator.config import WIKI_MAX_CHARS

KB_DIR = Path(__file__).resolve().parents[3] / "data" / "kb"


def _title_from_url(url: str, fallback: str) -> str:
    name = unquote(url.rstrip("/").rsplit("/", 1)[-1]).replace("_", " ").strip()
    return name or fallback


@lru_cache(maxsize=1)
def load_kb_pages(kb_dir: Path = KB_DIR) -> list[dict]:
    """Read every data/kb/*.txt file once; return pages like fetch_page_text()."""
    pages: list[dict] = []
    for path in sorted(kb_dir.glob("*.txt")):
        lines = path.read_text(encoding="utf-8").splitlines()
        title = path.stem.replace("_", " ").title()
        if lines and lines[0].startswith("http"):
            title = _title_from_url(lines[0], title)
            lines = lines[1:]
        text = " ".join(ln.strip() for ln in lines if ln.strip())
        if text:
            pages.append(
                {
                    "title": title,
                    "url": f"kb://{path.name}",
                    "text": text[:WIKI_MAX_CHARS],
                }
            )
    return pages
