# DH-200: Software Validation Report

**Project:** Dehallucinator  
**Team:** Team 14  
**Prepared by:** Ralph D'souza (Role C — Verifier & Scorer)  
**Validation date:** 15 November 2026  
**Status:** VALIDATED — system and security tests merged and passing

## 1. Objective

The objective of this report is to validate the Dehallucinator software against the functional requirements and test cases documented in the project test plan.

Validation focuses on four primary use cases:

- **UC-1:** Extract factual claims from chatbot responses.
- **UC-2:** Retrieve relevant evidence for extracted claims.
- **UC-3:** Verify claims against evidence and calculate trust scores.
- **UC-4:** Correct or annotate chatbot responses and expose the functionality through an API and decorator.

The report documents actual automated test execution results, requirements traceability, code coverage, identified limitations, and the current validation status.

## 2. Test Environment

| Component | Configuration |
|---|---|
| Operating system | Windows |
| Python | 3.11.9 |
| Test framework | pytest 9.1.1 |
| Coverage tool | pytest-cov 7.1.0 |
| Source directory | `src/dehallucinator/` |
| Test directory | `tests/` |
| Development environment | Python virtual environment (`.venv`) |
| CI and quality tools | Jenkins, Ruff, SonarCloud |
| Validation method | Automated test execution and coverage analysis |

## 3. Test Execution Summary

Automated tests were executed locally using pytest.

### 3.1 Full Test Suite

**Command:**

`python -m pytest tests/ -q`

**Observed result:**

- Passed: **186**
- Failed: **0**
- Skipped: **0**
- Execution time: **55.08 seconds**
- Warnings: **2** (non-failing third-party library warnings)

The full test suite was executed after PR #56 (System Tests) and PR #57 (Security Tests) were merged into `main`. All 186 tests passed, including the integrated system and security tests, with no failures or skipped tests.

### 3.2 Use-Case Validation Results

| Use case | Test files | Passed | Failed |
|---|---|---:|---:|
| UC-1: Claim Extraction | `test_extractor.py` | 36 | 0 |
| UC-2: Evidence Retrieval | Retriever, ranker, cache, KB, retry and retrieval tests | 32 | 0 |
| UC-3: Claim Verification | `test_verifier.py` | 13 | 0 |
| UC-4: Correction and Integration | `test_corrector.py`, `test_api.py`, `test_guard.py` | 37 | 0 |
| **Total** | | **118** | **0** |

The 118 tests represent the separately executed use-case test groups. They are not an additional 118 tests beyond the full-suite total.

## 4. Functional Requirements Validation

### 4.1 UC-1 — Extract Factual Claims

**Test file:** `tests/unit/test_extractor.py`  
**Execution result:** 36 passed, 0 failed  
**Execution time:** 1.80 seconds

| Test case | Validation scenario | Result |
|---|---|---|
| TC-1-01 | Empty input is rejected | PASS |
| TC-1-02 | Input exceeding the length limit is rejected | PASS |
| TC-1-03 | Multiple sentences are separated | PASS |
| TC-1-04 | Questions are excluded | PASS |
| TC-1-05 | Opinion statements are excluded | PASS |
| TC-1-06 | Short sentences are excluded | PASS |
| TC-1-07 | Compound sentences are split | PASS |
| TC-1-08 | Leading pronouns are resolved | PASS |
| TC-1-09 | Duplicate claims are removed | PASS |

**Outcome:** All nine documented UC-1 test cases have passing automated tests. Additional tests cover input boundaries, sentence numbering, pronouns, and text normalization.

### 4.2 UC-2 — Retrieve Evidence

**Test files:** `test_retriever.py`, `test_ranker.py`, `test_cache.py`, `test_kb.py`, `test_retries_and_cache.py`, `test_retrieve_evidence.py`  
**Execution result:** 32 passed, 0 failed  
**Execution time:** 1.54 seconds across two test runs

| Test case | Validation scenario | Result |
|---|---|---|
| TC-2-01 | Named entities prioritized in search queries | PASS |
| TC-2-02 | Stop words removed and query limited to eight words | PASS |
| TC-2-03 | Wikipedia search request uses correct parameters | PASS |
| TC-2-04 | Page text is truncated and URL constructed | PASS |
| TC-2-05 | Evidence ranked by relevance | PASS |
| TC-2-06 | Local knowledge base loaded correctly | PASS |
| TC-2-07 | Cached Wikipedia pages reused | PASS |
| TC-2-08 | Knowledge base fallback when Wikipedia is unavailable | PASS |
| TC-2-09 | Missing evidence handled without failure | PASS |
| TC-2-10 | SQL-like input handled safely by cache | PASS |

**Outcome:** All ten documented UC-2 test cases have passing automated tests. Network failure handling, caching, knowledge-base fallback, and empty-result scenarios were also tested.

### 4.3 UC-3 — Verify Claims and Calculate Trust Scores

**Test file:** `tests/unit/test_verifier.py`  
**Execution result:** 13 passed, 0 failed  
**Execution time:** 11.69 seconds

| Test case | Validation scenario | Result |
|---|---|---|
| TC-3-02 | High entailment produces a supported verdict | PASS |
| TC-3-03 | High contradiction produces a contradicted verdict | PASS |
| TC-3-04 | Missing evidence produces an insufficient-information verdict | PASS |
| TC-3-05 | Uncertain evidence is handled | PASS |
| TC-3-06 | Only evidence matching the claim is used | PASS |
| TC-3-07 | Model and tokenizer are loaded lazily | PASS |
| TC-3-08 | Empty verdict list returns default trust score | PASS |
| TC-3-09 | Mixed verdicts produce an averaged trust score | PASS |
| TC-3-10 | Numeric mismatch forces contradiction | PASS |
| TC-3-11 | Matching numbers do not trigger mismatch detection | PASS |

An additional automated test, `test_tc_3_12_number_mid_sentence_remains_supported`, also passed.

**Outcome:** All ten documented UC-3 test cases have passing automated tests. Verification behavior, missing evidence, model initialization, numeric consistency, and trust-score calculations were validated.

### 4.4 UC-4 — Correct and Integrate Chatbot Answers

**Test files:** `test_corrector.py`, `test_api.py`, `test_guard.py`  
**Execution result:** 37 passed, 0 failed  
**Execution time:** 2.11 seconds across two test runs

| Test case | Validation scenario | Result |
|---|---|---|
| TC-4-01 | Contradicted claim replaced with correction and source | PASS |
| TC-4-02 | Unverifiable claim flagged | PASS |
| TC-4-03 | Supported claim tagged with source | PASS |
| TC-4-04 | Non-claim text preserved | PASS |
| TC-4-05 | Missing evidence and missing verdict handled | PASS |
| TC-4-06 | `/check` endpoint returns checked answer | PASS |
| TC-4-07 | Health endpoint returns expected response | PASS |
| TC-4-08 | Invalid input and malformed JSON rejected | PASS |
| TC-4-09 | Unexpected errors handled without exposing stack traces | PASS |
| TC-4-10 | Decorator returns checked chatbot output | PASS |

**Outcome:** All ten documented UC-4 test cases have passing automated tests. Additional tests cover input validation, error handling, formatting, and decorator behavior.

## 5. Code Coverage Analysis

**Command:**

`python -m pytest tests/ --cov=src/dehallucinator --cov-branch --cov-report=term-missing -q`

**Observed result:** 186 passed, 0 failed, 0 skipped, with **97% combined statement-and-branch coverage**.

| Module | Reported combined coverage |
|---|---:|
| API | 100% |
| Claim extractor | 97% |
| Configuration | 100% |
| Corrector | 94% |
| Evidence cache | 88% |
| Knowledge base | 100% |
| Evidence ranker | 94% |
| Evidence retriever | 93% |
| Guard | 100% |
| Data models | 100% |
| Pipeline | 100% |
| UI rendering | 100% |
| Verifier | 99% |
| **Overall** | **97%** |

The updated coverage report recorded 643 statements, 17 missed statements, 198 branches, and 12 partially covered branches.

All listed modules achieved at least 88% combined coverage. The overall coverage increased from 94% to 97% after the system and security tests were merged.

The reported percentage combines statement and branch coverage; it does not separately establish each module's line and branch coverage percentages.

## 6. Reliability, Security, and Error Handling

The executed automated tests covered the following behaviors:

- Rejection of invalid and oversized inputs.
- Safe handling of SQL-like cache titles.
- Handling of missing evidence and unavailable Wikipedia services.
- Retry behavior and local knowledge-base fallback.
- API rejection of malformed requests.
- Prevention of stack-trace disclosure in unexpected API errors.
- Preservation of response formatting and non-claim text.

The dedicated system and security test suites from PR #56 and PR #57 have been merged and successfully executed as part of the full test suite.

These results provide evidence of functional reliability, security-related behavior, and end-to-end integration.

## 7. Known Limitations

The following limitations remain:

- The 97% coverage figure is a combined statement-and-branch metric, not independent proof of each module's line and branch coverage.
- Tests using mocked HTTP responses do not independently establish live Wikipedia service availability.
- Passing automated security tests does not guarantee the absence of all security vulnerabilities.

The system and security test suites are no longer pending integration.

## 8. Validation Conclusion

The observed results demonstrate successful automated validation of the documented functional test cases across UC-1, UC-2, UC-3, and UC-4.

**Key results:**

- 39 documented functional test cases have corresponding passing automated tests.
- 118 tests passed across the separately executed use-case test groups.
- The full test suite recorded **186 passed, 0 failed, and 0 skipped**.
- Overall combined statement-and-branch coverage reached **97%**.
- The verifier module achieved **99% combined coverage**.
- System and security test suites were merged and executed successfully.
- Reliability and error-handling scenarios were exercised successfully.

**Final status: VALIDATED**

The Dehallucinator software has successfully completed the documented automated functional validation, including the integrated system and security test suites. All 186 tests passed without failures or skips.

The limitations listed above remain applicable, and this validation status does not imply that every possible production scenario or security risk has been tested.

## 9. Supporting Evidence

- `docs/test-plan/test_plan.md`
- `docs/test_cases_UC-2.md`
- `docs/exports/Team14_Project_Test_Plan.pdf`
- `docs/exports/Team14_Test_Cases.xlsx`
- `docs/exports/Team14_Coverage_Report.pdf`
- `tests/unit/`
- `tests/system/`
- `tests/security/`
- Pull requests #56 and #57

---

**Report prepared for:** DH-200 — Validation Report  
**Project:** Dehallucinator, Team 14  
**Prepared by:** Ralph D'souza