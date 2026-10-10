# Architecture: Evidence Retriever (Role B)

## 1. Purpose
Finds trustworthy evidence for each claim by searching Wikipedia, fetching page
text, and returning the most relevant snippets. Requirements: FR-2.1 to FR-2.5.

## 2. Responsibilities
| Step | Responsibility | Module | Requirement |
|---|---|---|---|
| 1 | Build a search query from a claim (entities first, then noun chunks, stop words removed, max 8 words) | `evidence/retriever.py` `build_query` | FR-2.1 |
| 2 | Search Wikipedia (MediaWiki API, top 3 pages) | `evidence/retriever.py` `search_wikipedia` | FR-2.2 |
| 3 | Fetch page text (extracts API, first 6000 chars, correct page URL) | `evidence/retriever.py` `fetch_page_text` | FR-2.3 |
| 4 | Split text into snippets (sentence + next sentence) and rank by TF-IDF cosine similarity | `evidence/ranker.py` `rank_snippets` | FR-2.5 |
| 5 | Orchestrate steps 1-4 per claim and return `Evidence` objects (pending) | `evidence/retriever.py` `retrieve_evidence` | FR-2.5 |

Not in scope: extracting claims (Role A), verifying claims against evidence (Role C),
and the API/UI (Role D).

## 3. Interfaces
**Input:** `list[Claim]` from the Claim Extractor.
**Output:** `list[Evidence]` for the Verifier.

| Function | Input | Output |
|---|---|---|
| `build_query(claim_text)` | `str` | `str` (at most `MAX_QUERY_WORDS` words, `""` if empty) |
| `search_wikipedia(query)` | `str` | `list[str]` page titles (at most `WIKI_TOP_PAGES`; `[]` on error) |
| `fetch_page_text(title)` | `str` | `dict` with `title`, `url`, `text` (at most `WIKI_MAX_CHARS`), or `None` |
| `rank_snippets(claim_text, pages, top_n)` | `str`, `list[dict]` | `list[dict]` with `text`, `title`, `url`, `relevance` (0 to 1), best first |
| `retrieve_evidence(claims)` | `list[Claim]` | `list[Evidence]` |

Data flow:
`Claim -> build_query -> search_wikipedia -> fetch_page_text (per title) -> rank_snippets -> Evidence`

## 4. Dependencies
| Dependency | Used for |
|---|---|
| Wikipedia MediaWiki API (`en.wikipedia.org/w/api.php`) | search and page text; requires a User-Agent header |
| `requests` | HTTP calls (timeout `HTTP_TIMEOUT_S`) |
| `spaCy` + `en_core_web_sm` | entities and noun chunks for query building |
| `scikit-learn` | TF-IDF vectorizer and cosine similarity |
| `dehallucinator.models` | `Claim` and `Evidence` data classes |
| `dehallucinator.config` | `WIKI_TOP_PAGES`, `EVIDENCE_PER_CLAIM`, `HTTP_TIMEOUT_S`, `MAX_QUERY_WORDS`, `WIKI_MAX_CHARS`, `WIKI_API_URL`, `USER_AGENT` |

## 5. Error handling
- Network and HTTP errors: `search_wikipedia` returns `[]` and `fetch_page_text`
  returns `None`, so a claim gets no evidence instead of crashing the pipeline.
- Empty claim text: `build_query` returns `""`.
- No relevant snippet: `rank_snippets` returns `[]`.

## 6. Testing
Unit tests in `tests/unit/test_retriever.py` and `tests/unit/test_ranker.py`
(TC-2-01 to TC-2-05). All HTTP calls are mocked.
