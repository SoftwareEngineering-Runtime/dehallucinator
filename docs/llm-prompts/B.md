# LLM prompt log – Role B (Shreya Raghuraj)

## DH-157 SRS section UC-2, FR-2.x and NFRs – 2026-10 (Sprint 0)
Tool: Claude
Prompt: "Draft SRS section 3.2 for the Evidence Retriever in the same format as sections 3.1
and 3.3: UC-2, FR-2.1 to FR-2.8 and the NFR references, following the team numbering (Chapter
3 by role, UC-n, FR-n.x, NFR-1 to NFR-6)."
What I kept: the section layout (overview, use case, requirements, NFR references,
limitations) and the interface retrieve_evidence(claims) -> list[Evidence], with a claim_id on
every Evidence and no entry for a claim with no evidence or a network failure
What I changed: supplied the actual retriever behaviour (Wikipedia plus local KB, snippets per
claim, timeout and retries) so that the section contains real values instead of placeholders
I can explain it: TODO

## DH-160 compile and export the final SRS – 2026-10 (Sprint 0)
Tool: Claude
Prompt: "Compile the four role sections into one SRS with the same use case format, NFR-n
references in every module, and the order Introduction, NFRs, sections 3.1 to 3.4 and
Validation Approach."
What I kept: the unified format and order, and the PDF and Word exports
What I changed: reviewed the compiled PDF, completed the missing team details, raised the
differences in section 3.4 with Satwik, and committed the PDF to docs/ through a branch and
pull request
I can explain it: TODO

## DH-166 search query builder – 2026-10 (Sprint 1)
Tool: Claude
Prompt: "Plan DH-166: build a Wikipedia search query from a claim with entities first, then
noun chunks, stop words removed and a maximum of 8 words, with tests TC-2-01 and TC-2-02."
What I kept: the implementation order (entities, noun-chunk fallback, stop-word filter, 8-word
cap, tests)
What I changed: wrote build_query() and tests TC-2-01 and TC-2-02 myself
I can explain it: TODO

## DH-167 Wikipedia search and page fetch, error-path review – 2026-10 (Sprint 1)
Tool: Claude
Prompt: "Here are the Jenkins and SonarQube results for PR #11 and the coverage output for
retriever.py (88% line and branch). What is missing and what should I do next?"
What I kept: the suggestion to cover the error paths (network errors in search and fetch, and
a page with no text)
What I changed: ran ruff format and re-ran the full suite on the branch before pushing
I can explain it: TODO

## Wire up retrieve_evidence() (PR #26) – 2026-10 (Sprint 2)
Tool: Claude
Prompt: "retrieve_evidence() still raises NotImplementedError. Wire it up as search, fetch and
rank returning a list of Evidence, reusing the existing functions, and tell me the steps one
at a time."
What I kept: the flow build_query -> search_wikipedia -> fetch_page_text -> rank_snippets ->
list[Evidence], reusing the existing Sprint 1 functions
What I changed: added 4 unit tests with mocked network calls
(tests/unit/test_retrieve_evidence.py); ruff clean, 92 passed, 2 skipped; this unblocked
DH-169, DH-170 and DH-189
I can explain it: TODO

## DH-169 local knowledge base (PR #27) – 2026-10 (Sprint 2)
Tool: Claude
Prompt: "Add the local KB as a second evidence source (FR-2.4) so that retrieval works
offline: load data/kb/*.txt once and rank the KB pages together with the Wikipedia pages."
What I kept: the new evidence/kb.py (kb://<filename> URLs) and retrieve_evidence() ranking KB
pages together with Wikipedia pages
What I changed: set Evidence.source to "local_kb" for KB hits, added or updated 5 tests, ruff
clean, 93 passed, 2 skipped; stacked the branch on feature/retrieve-evidence and merged in order
I can explain it: TODO

## DH-170 cache and retries (PR #28) – 2026-10 (Sprint 2)
Tool: Claude
Prompt: "Implement FR-2.6 and FR-2.7: a SQLite cache of Wikipedia pages with a time limit, and
retries on timeouts, connection errors, 429 and 5xx, so that a network failure never crashes
the retriever."
What I kept: evidence/cache.py (parameterised queries, entries reused for CACHE_TTL_DAYS = 7)
and _wiki_get retrying up to HTTP_RETRIES = 2 with a short backoff
What I changed: made retrieval continue with the local KB only when Wikipedia is unreachable,
added data/wiki_cache.sqlite3 to .gitignore, added tests/unit/conftest.py so unit tests do not
touch the real cache or sleep, wrote 10 new tests, ruff clean, 103 passed, 2 skipped
I can explain it: TODO

## DH-189 retriever design diagrams (PR #29) – 2026-10 (Sprint 2)
Tool: Claude
Prompt: "Write docs/design/retriever_design.md for the Evidence Retriever (FR-2.1 to FR-2.8):
a class diagram of the retriever, ranker, kb and cache modules and a sequence diagram of
retrieve_evidence()."
What I kept: both Mermaid diagrams (module dependencies, and query, search, cache lookup,
retries, KB and ranking in sequence)
What I changed: checked the diagrams against the final code from feature/retrieve-evidence,
DH-169 and DH-170, and merged the branch after those three
I can explain it: TODO

## DH-204 README: Evidence Retriever section (PR #49) – 2026-11-14
Tool: Claude
Prompt: "Write the Evidence Retriever (Role B) README section in the same format as the Claim
Extractor section, from my retriever.py and ranker.py: one row per step mapped to FR-2.x, the
Evidence fields, a real example and the test line."
What I kept: the seven-step table (FR-2.1 to FR-2.7), the Evidence fields description and the
example block
What I changed: ran the retriever to obtain the real output, inserted the verified values
(TC-2-01 to TC-2-04, 93% coverage of retriever.py, EVIDENCE_PER_CLAIM = 3), corrected a step
described as offline-only since the local KB is added to every claim, and recreated the change
on a fresh branch from an up-to-date main so that the PR touches only README.md
I can explain it: TODO

## DH-169 unit tests for the local KB loader (PR #48) – 2026-11-14
Tool: Claude
Prompt: "evidence/kb.py is at 30% coverage and NFR-4 asks for 80% per module. Write unit tests
covering every branch: title from URL, files with and without a URL line, empty and non-txt
files, truncation, a missing folder and the real KB."
What I kept: the seven tests in tests/unit/test_kb.py
What I changed: corrected the coverage command after the first run reported no data, applied
ruff format (one long assert wrapped, final newline added), and confirmed that kb.py rose from
30% to 100% with the full suite passing (100 passed, 2 skipped)
I can explain it: TODO