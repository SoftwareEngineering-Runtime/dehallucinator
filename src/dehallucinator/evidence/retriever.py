"""Evidence Retriever (Role B): finds evidence for each claim."""

from functools import lru_cache
from urllib.parse import quote

import requests
import spacy

from dehallucinator.config import (
    HTTP_TIMEOUT_S,
    MAX_QUERY_WORDS,
    USER_AGENT,
    WIKI_API_URL,
    WIKI_MAX_CHARS,
    WIKI_TOP_PAGES,
)
from dehallucinator.models import Claim, Evidence

_HEADERS = {"User-Agent": USER_AGENT}


@lru_cache(maxsize=1)
def _get_nlp():
    """Load the spaCy model once and reuse it."""
    return spacy.load("en_core_web_sm")


def build_query(claim_text: str) -> str:
    """Build a Wikipedia search query from a claim (FR-2.1).

    Entities come first, then noun chunks. Stop words and punctuation are
    removed, duplicates are dropped, and the result is capped at
    MAX_QUERY_WORDS words.
    """
    text = (claim_text or "").strip()
    if not text:
        return ""

    doc = _get_nlp()(text)
    words: list[str] = []
    seen: set[str] = set()

    def add_tokens(tokens) -> None:
        for tok in tokens:
            if len(words) >= MAX_QUERY_WORDS:
                return
            if tok.is_stop or tok.is_punct or tok.is_space:
                continue
            key = tok.text.lower()
            if key in seen:
                continue
            seen.add(key)
            words.append(tok.text)

    for ent in doc.ents:
        add_tokens(ent)
    for chunk in doc.noun_chunks:
        add_tokens(chunk)

    return " ".join(words)


def _wiki_get(params: dict) -> dict:
    resp = requests.get(
        WIKI_API_URL,
        params={**params, "format": "json"},
        headers=_HEADERS,
        timeout=HTTP_TIMEOUT_S,
    )
    resp.raise_for_status()
    return resp.json()


def page_url(title: str) -> str:
    """Build the Wikipedia page URL for a title."""
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"))


def search_wikipedia(query: str) -> list[str]:
    """Return up to WIKI_TOP_PAGES page titles for the query (FR-2.2)."""
    if not query:
        return []
    try:
        data = _wiki_get(
            {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": WIKI_TOP_PAGES,
            }
        )
    except requests.RequestException:
        return []
    return [hit["title"] for hit in data.get("query", {}).get("search", [])]


def fetch_page_text(title: str) -> dict | None:
    """Fetch plain text of a page, first WIKI_MAX_CHARS chars (FR-2.3)."""
    try:
        data = _wiki_get(
            {
                "action": "query",
                "prop": "extracts",
                "explaintext": 1,
                "redirects": 1,
                "titles": title,
            }
        )
    except requests.RequestException:
        return None
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        text = page.get("extract")
        if text:
            return {
                "title": page["title"],
                "url": page_url(page["title"]),
                "text": text[:WIKI_MAX_CHARS],
            }
    return None


def retrieve_evidence(claims: list[Claim]) -> list[Evidence]:
    """Return evidence snippets for the given claims."""
    raise NotImplementedError("Implemented by Role B in Sprint 1")
