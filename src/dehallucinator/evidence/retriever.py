"""Evidence Retriever (Role B): finds evidence for each claim."""

import logging
import time
from functools import lru_cache
from urllib.parse import quote

import requests
import spacy

from dehallucinator.config import (
    HTTP_RETRIES,
    HTTP_TIMEOUT_S,
    MAX_QUERY_WORDS,
    USER_AGENT,
    WIKI_API_URL,
    WIKI_MAX_CHARS,
    WIKI_TOP_PAGES,
)
from dehallucinator.evidence.cache import get_cached_page, put_cached_page
from dehallucinator.evidence.kb import load_kb_pages
from dehallucinator.evidence.ranker import rank_snippets
from dehallucinator.models import Claim, Evidence

_HEADERS = {"User-Agent": USER_AGENT}

logger = logging.getLogger(__name__)


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
    """GET the Wikipedia API; retry timeouts and server errors (FR-2.7)."""
    for attempt in range(HTTP_RETRIES + 1):
        try:
            resp = requests.get(
                WIKI_API_URL,
                params={**params, "format": "json"},
                headers=_HEADERS,
                timeout=HTTP_TIMEOUT_S,
            )
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            status = getattr(exc.response, "status_code", None)
            retryable = status is None or status >= 500 or status == 429
            logger.warning(
                "Wikipedia request failed (attempt %d of %d): %s",
                attempt + 1,
                HTTP_RETRIES + 1,
                exc,
            )
            if not retryable or attempt == HTTP_RETRIES:
                raise
            time.sleep(0.5 * 2**attempt)
    raise RuntimeError("unreachable")


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
    """Fetch plain text of a page, cached for CACHE_TTL_DAYS (FR-2.3, FR-2.6)."""
    cached = get_cached_page(title)
    if cached is not None:
        return cached
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
            result = {
                "title": page["title"],
                "url": page_url(page["title"]),
                "text": text[:WIKI_MAX_CHARS],
            }
            put_cached_page(title, result)
            return result
    return None


def retrieve_evidence(claims: list[Claim]) -> list[Evidence]:
    """Return evidence snippets for the given claims (FR-2)."""
    results: list[Evidence] = []
    for claim in claims:
        query = build_query(claim.text)
        pages = []
        for title in search_wikipedia(query):
            page = fetch_page_text(title)
            if page:
                pages.append(page)
        pages.extend(load_kb_pages())  # local KB works even when offline (FR-2.4)
        for hit in rank_snippets(claim.text, pages):
            is_kb = hit["url"].startswith("kb://")
            results.append(
                Evidence(
                    claim_id=claim.id,
                    source="local_kb" if is_kb else "wikipedia",
                    source_url=hit["url"],
                    title=hit["title"],
                    snippet=hit["text"],
                    relevance=hit["relevance"],
                )
            )
    return results
