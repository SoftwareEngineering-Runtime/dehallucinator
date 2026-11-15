# Maintenance Plan

**Project 39: Dehallucination Add-On Module ("Dehallucinator")**
Owner: Satwik (Role D). Manual Section 11.5. Each member keeps maintaining the module they built.

## 1. Who maintains what

| Area | Files | Owner |
|---|---|---|
| Claim Extractor | `src/dehallucinator/claims/` | Sai Nikitha Perumalla (A) |
| Evidence Retriever, KB, cache | `src/dehallucinator/evidence/`, `data/kb/` | Shreya Raghuraj (B) |
| Verifier & Scorer, NLI model | `src/dehallucinator/verify/` | Ralph D'souza (C) |
| Corrector, pipeline, API, UI, decorator | `correct/`, `pipeline.py`, `api.py`, `guard.py`, `ui_render.py`, `ui/` | Satwik (D) |
| CI/CD: Jenkins, Docker, security scans | `Jenkinsfile`, `Dockerfile`, `ci/` | Satwik (D) |
| Shared models and config | `models.py`, `config.py` | Everyone; changes need all four to agree |

Every change, including maintenance, follows the normal workflow: a Jira ticket, a branch, a
pull request with one approval, and a green Jenkins build (lint, security scan, tests with at
least 80% coverage).

## 2. Dependency updates

All versions in `requirements.txt` are pinned with `==`, so a build today installs exactly what
was tested.

- **Security fixes (immediately).** The Jenkins *Security scan* stage runs `pip-audit` on every
  build and fails when a pinned version has a known vulnerability. Upgrade only that package to
  the fixed version and check `pip check`. Example: DH-182 found 42 vulnerabilities and upgraded
  pillow 12.3 → 13.0, which also needed Streamlit 1.64 → 1.66 because 1.64 does not allow pillow 13.
- **Routine updates (once per semester).** Run `pip list --outdated`, update one group per pull
  request (web: FastAPI/Starlette/uvicorn; NLP: spaCy/thinc/blis; ML: torch/transformers/
  tokenizers; UI: Streamlit/pillow), then run the full test suite and the 10 demo samples.
- **Linked versions.** The spaCy model `en_core_web_sm` must match the installed spaCy minor
  version (`python -m spacy validate`). torch, transformers and tokenizers are updated together.
- **Docker.** The image installs with `--only-binary :all:`, so every new version must have a
  Linux wheel for Python 3.11; if one does not, keep the old version. Rebuild the image after any
  dependency change.
- **Python.** The project targets Python 3.11 (`pyproject.toml`). Moving to a newer Python means
  updating `pyproject.toml`, the Dockerfile base image and the Jenkins `PYTHON` setting together.

## 3. Configuration changes

All tunable values live in `src/dehallucinator/config.py`; nothing is hard-coded elsewhere.

| Setting | Effect of a change | Also check |
|---|---|---|
| `MAX_INPUT_CHARS` (5000) | Input limit for the extractor, API and UI | SRS FR-1.1/FR-4.4, NFR-3, security tests |
| `MIN_CLAIM_WORDS` | Which sentences count as claims | UC-1 tests, demo samples |
| `WIKI_TOP_PAGES`, `EVIDENCE_PER_CLAIM`, `WIKI_MAX_CHARS` | Amount of evidence and speed | NFR-1 (≤ 20 s per answer) |
| `HTTP_TIMEOUT_S`, `HTTP_RETRIES`, `CACHE_TTL_DAYS` | Network behaviour and cache freshness | NFR-2 (works when Wikipedia is down) |
| `NLI_MODEL` | The verifier model | Retune the two thresholds; rebuild the Docker image (the model is baked in) |
| `SUPPORT_THRESHOLD`, `CONTRADICT_THRESHOLD` | How strict the verdicts are | Re-run all 10 samples: every planted mistake must stay CONTRADICTED, no true sentence may be flagged |
| `USER_AGENT` | Identifies us to Wikipedia | Must keep a working contact address |

Deployment settings that are not in `config.py`: the Jenkins `APP_PORT` (host port of the deployed
container, 8010) and `PYTHON` (path of the Python 3.11 interpreter on the Jenkins agent).

## 4. Knowledge base updates

The local knowledge base is `data/kb/*.txt`: one topic per file, 300–1000 words, with the source
URL on line 1. It is the offline fallback and is ranked together with Wikipedia.

- **Adding a topic:** add `<topic>.txt` with the source URL on line 1, then add a test or sample
  that uses it. KB text from Wikipedia is CC BY-SA, so the source URL must stay on line 1.
- **Refreshing facts:** once per semester, compare each file with its source page (figures such as
  Mount Everest's height or country populations change). Update the text and the dated facts in
  `data/samples.json` if a sample depends on them.
- **Applying changes:** the KB is loaded once per process (`load_kb_pages` is cached), so restart
  the API/UI and rebuild the Docker image, which copies `data/` into the image.

## 5. Wikipedia API changes

The retriever uses the MediaWiki Action API at `WIKI_API_URL`: `action=query&list=search` to find
pages and `action=query&prop=extracts&explaintext=1` to fetch page text, always with our
`User-Agent` header.

- **Detecting a change:** unit tests mock HTTP, so they do not notice an API change. Before every
  release and after any retriever change, run the 10 demo samples through the UI (or
  `check_answer()`) against the live API and confirm every planted mistake is still
  CONTRADICTED. Live tests added later should use the existing `slow` pytest marker, so the
  default `pytest -m "not slow"` run stays offline.
- **Rate limits and outages:** timeouts and 5xx/429 responses are retried `HTTP_RETRIES` times
  with back-off; after that the retriever logs a warning and uses the KB only (FR-2.7), so the
  system keeps working with reduced evidence.
- **Cache:** fetched pages are stored in `data/wiki_cache.sqlite3` for `CACHE_TTL_DAYS`. If
  Wikipedia changes the page format, delete this file so no stale pages are reused.
- **If the API changes:** update `search_wikipedia`, `fetch_page_text` and `_wiki_get` in
  `evidence/retriever.py` together with tests TC-2-03 and TC-2-04, and re-run the demo samples.

## 6. Bug process

1. **Report** the bug in Jira as a *Bug* in project DH: steps to reproduce, input text, expected
   and actual result, label for the owning role.
2. **Severity:**

   | Severity | Example | Fix by |
   |---|---|---|
   | Critical | API crashes, stack trace returned to the client, security finding | Same day |
   | High | Wrong verdict on a demo sample, true sentence flagged as contradicted | Within 2 days |
   | Normal | Wrong tag position, unclear UI text | Next sprint |

3. **Reproduce first:** write a failing regression test that captures the bug.
4. **Fix** on a branch `fix/DH-<n>-<short-name>`; the commit message starts with the Jira key.
5. **Review:** pull request with one approval; Jenkins, SonarCloud and the coverage gate must pass.
6. **Close:** move the ticket to Done, add the test to the test plan if it covers a requirement,
   and add an entry to the LLM prompt log if an AI tool helped.

## 7. Known limitations to watch

- **Word-based ranking:** TF-IDF matches words, not meaning, so a snippet about a different
  subject can rank first. Example: "Paris is the capital and largest city of France." was matched
  to the Japan KB sentence "Tokyo is the country's capital and largest city" and flagged as
  contradicted.
- **Numbers:** the number-mismatch rule (FR-3.5) misses spelled-out numbers ("five" vs "5").
- **Language:** English only; pronoun replacement is rule-based.
- **Corrections:** the whole best snippet replaces a wrong claim, so it can include extra detail.
- **API:** no authentication or rate limiting; meant for local and demo use.
- **CI:** Jenkins runs on one laptop, so builds stop when that laptop is off.

## 8. Future work

- Semantic retrieval with sentence embeddings instead of TF-IDF, to fix the ranking problem above.
- A larger, regularly refreshed knowledge base and more sources than Wikipedia.
- Authentication and rate limiting on the API, and an async endpoint for long answers.
- Batch and cache NLI results so repeated claims are not re-verified.
- Move CI to a hosted runner, push the Docker image to a registry, and deploy from there.
- Support more languages and spelled-out numbers.
