# Test Cases: UC-2 Retrieve Evidence (TC-2-01 to TC-2-10)

Module: Evidence Retriever (Role B). Requirements: FR-2.1 to FR-2.8, NFR-2, NFR-3.

## Test cases

| ID | Title | Requirement | Type | Preconditions | Input | Steps | Expected result | Automated test |
|---|---|---|---|---|---|---|---|---|
| TC-2-01 | Entities come first in query | FR-2.1 | Normal | spaCy model loaded | "The famous bridge was designed by Gustave Eiffel in Paris." | Call `build_query` | Query contains Gustave, Paris and bridge; entity words appear before noun-chunk words | `test_tc_2_01_entities_come_before_noun_chunks` |
| TC-2-02 | Stop words removed, max 8 words | FR-2.1 | Normal | spaCy model loaded | Long claim with more than 8 content words | Call `build_query` | At most 8 words; no stop words | `test_tc_2_02_stop_words_removed_and_capped_at_8_words` |
| TC-2-03 | Wikipedia search request | FR-2.2 | Normal | HTTP mocked | Query "Eiffel Tower" | Call `search_wikipedia` | Request uses `srlimit=3` and sends a User-Agent header; returns page titles | `test_tc_2_03_search_uses_limit_and_user_agent` |
| TC-2-04 | Page text fetch | FR-2.3 | Normal | HTTP mocked | Title "Eiffel Tower", 10000-char extract | Call `fetch_page_text` | Text cut to 6000 chars; URL is `https://en.wikipedia.org/wiki/Eiffel_Tower` | `test_tc_2_04_fetch_truncates_and_builds_url` |
| TC-2-05 | Snippets ranked by relevance | FR-2.5 | Normal | Two pages, one relevant and one not | Claim "The Eiffel Tower was completed in 1889" | Call `rank_snippets` | At most 3 results, best first, relevance between 0 and 1 (cosine score); irrelevant page excluded | `test_tc_2_05_ranked_by_relevance_across_sources` |
| TC-2-06 | KB loaded once at start-up | FR-2.4 | Normal | `data/kb/` contains .txt files | Start retriever, then retrieve for two claims | Inspect KB loading | Every `data/kb/*.txt` is loaded as a page with source "local_kb"; files are read once, not per claim | Sprint 2 |
| TC-2-07 | Wikipedia page cached and reused | FR-2.6 | Normal | Empty SQLite cache, HTTP mocked | Same page requested twice; then again with a cache entry 8 days old | Call fetch with cache | Second request makes no HTTP call; the 8-day-old entry is fetched again | Sprint 2 |
| TC-2-08 | Wikipedia down: KB fallback | FR-2.7, NFR-2 | Error | HTTP mocked to time out; claim on a KB topic | Claim about a topic covered by the KB | Call `retrieve_evidence` | 2 retries with 5 s timeout, warning logged, Evidence with source "local_kb" returned, no exception | Sprint 2 |
| TC-2-09 | No evidence found | FR-2.8 | Error | Wikipedia returns no hits; no KB match | Claim "Zxqv blorf quux." and an empty claim list | Call `retrieve_evidence` | No Evidence for the nonsense claim; empty list for an empty claim list | Sprint 2 (`rank_snippets` empty case already tested) |
| TC-2-10 | SQL-like input does not break cache | NFR-3 | Error | Cache enabled | Title or claim containing `'; DROP TABLE pages; --` | Call retrieve, then retrieve a normal claim | No exception; cache table intact; later lookups still work | Sprint 2 |

Also automated now: `test_empty_claim_returns_empty_query` (FR-2.1, empty claim) and `test_empty_inputs_return_empty_list` (FR-2.5, empty input).

## Traceability (requirement to test case)

| Requirement | Description | Test cases |
|---|---|---|
| FR-2.1 | Build search query per claim | TC-2-01, TC-2-02 |
| FR-2.2 | Search Wikipedia, top 3, User-Agent | TC-2-03 |
| FR-2.3 | Fetch page text, first 6000 chars | TC-2-04 |
| FR-2.4 | Load local KB once at start-up | TC-2-06 |
| FR-2.5 | Rank snippets by TF-IDF cosine, top 3 | TC-2-05 |
| FR-2.6 | Cache Wikipedia pages in SQLite, 7 days | TC-2-07 |
| FR-2.7 | No crash on network failure, retry twice, KB fallback | TC-2-08 |
| FR-2.8 | No Evidence when nothing found | TC-2-09 |
| NFR-2 | Works when Wikipedia is down | TC-2-08 |
| NFR-3 | SQL-like input must not break the cache | TC-2-10 |

Error cases: TC-2-08, TC-2-09, TC-2-10.
