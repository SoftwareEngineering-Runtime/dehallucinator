
# Test Plan and Test Cases

**Project 39: Dehallucination Add-On Module ("Dehallucinator")**

Owner: Ralph D'souza (Role C). Each member writes the test cases for their own use case.

## 1. Scope

This document outlines the testing strategy for the Dehallucination Add-On Module. It covers unit testing for individual modules (Claim Extractor, Evidence Retriever, Verifier & Scorer, Corrector & Integrator), integration testing for component handoffs, system testing for the end-to-end API, and security testing.

## 2. Test Levels

- **Unit testing:** isolated testing of individual functions using mocks and fakes (no internet or model downloads permitted).
- **Integration testing:** testing the data flow between connected modules (e.g., Extractor → Retriever → Verifier).
- **System testing:** end-to-end testing of the complete `/check` API and pipeline using the 10 predefined sample answers.
- **Security testing:** verifying boundary limits, malformed inputs, and checking for vulnerabilities using bandit and pip-audit.

## 3. Environment

- **Language & tools:** Python 3.11, pytest, pytest-cov, ruff
- **Infrastructure:** Jenkins CI/CD pipeline, Docker, SonarQube Cloud
- **Dependencies:** spaCy (`en_core_web_sm`), transformers (`nli-deberta-v3-xsmall`), SQLite (caching)

## 4. Entry and Exit Criteria

- **Entry criteria:** code must be pushed via a pull request to `main`, pass the Jenkins pipeline linting (ruff), and pass the SonarQube Quality Gate.
- **Exit criteria:** all modules must achieve ≥ 80% line and branch coverage. All test cases listed in this document must pass, with 0 critical security vulnerabilities.

## 5. Traceability Matrix

| Requirement | Test cases |
|---|---|
| FR-1.1 | TC-1-01, TC-1-02 |
| FR-1.2 | TC-1-03 |
| FR-1.3 | TC-1-04, TC-1-05, TC-1-06 |
| FR-1.4 | TC-1-07 |
| FR-1.5 | TC-1-08 |
| FR-1.6 | TC-1-09 |
| FR-1.7 | TC-1-10 |
| FR-2.x (Role B) | See [UC-2 test cases](../test_cases_UC-2.md) traceability table |
| FR-3.1 | TC-3-07 |
| FR-3.2 | TC-3-06 |
| FR-3.3 | TC-3-02, TC-3-03, TC-3-05 |
| FR-3.4 | TC-3-04 |
| FR-3.5 | TC-3-10, TC-3-11 |
| FR-3.6 | TC-3-08, TC-3-09 |
| FR-4.x (Role D) | *To be added* |

## 6. Test Cases

Each use case has 8–10 test cases, with at least 2 error or edge cases. "Automated test" names the pytest function that checks the case. The Actual and Pass/Fail columns are filled in during Sprint 3 (validation report).

### UC-1: Extract factual claims (Owner: Sai Nikitha Perumalla, Role A)

Automated tests: `tests/unit/test_extractor.py`

| TC ID | FR | Type | Description | Input | Expected result | Automated test | Actual | Pass/Fail |
|---|---|---|---|---|---|---|---|---|
| TC-1-01 | FR-1.1 | Error | Empty input is rejected | `""` and `"  \n\t  "` | `ValueError("Input text is empty")` | `test_tc_1_01_empty_input_is_rejected` | | |
| TC-1-02 | FR-1.1 | Boundary | Input over the limit is rejected | 5001 characters (and exactly 5000) | 5001 → `ValueError` mentioning 5000; 5000 is accepted | `test_tc_1_02_input_over_limit_is_rejected`, `test_input_exactly_at_limit_is_accepted` | | |
| TC-1-03 | FR-1.2 | Normal | Text is split into sentences | "Paris is in France. It is a large city." | 2 claims with those two sentences; "Dr." / "U.S." do not cause false splits | `test_tc_1_03_splits_two_sentences`, `test_abbreviations_do_not_cause_false_splits` | | |
| TC-1-04 | FR-1.3 | Normal | Questions are dropped | "Paris is the capital of France. Is it the largest city?" | Only the first sentence is a claim | `test_tc_1_04_questions_are_dropped` | | |
| TC-1-05 | FR-1.3 | Normal | Opinion sentences are dropped | "I think Paris is the most beautiful city.", "Maybe the tower was built in 1889." and 3 more | No claims; markers match whole words in any case ("shoulder" is kept) | `test_tc_1_05_opinion_sentences_are_dropped`, `test_opinion_markers_ignore_case`, `test_opinion_marker_must_be_a_whole_word` | | |
| TC-1-06 | FR-1.3 | Boundary | Short and first-person sentences are dropped | "Paris is big." (3 words), "Paris is very big." (4 words), "I visited Paris in 2019." | 3-word sentence dropped, 4-word sentence kept, I/We sentence dropped | `test_tc_1_06_short_sentences_are_dropped`, `test_first_person_sentences_are_dropped` | | |
| TC-1-07 | FR-1.4 | Normal | Compound sentence is split | "Einstein was born in 1879, and he won the Nobel Prize in 1921." | 2 claims; "Salt and pepper are spices." stays 1 claim | Sprint 2 (DH-163) | | |
| TC-1-08 | FR-1.5 | Normal | Leading pronoun is replaced | "The Eiffel Tower is in Paris. It is 330 m tall." | Second claim is "The Eiffel Tower is 330 m tall." | Sprint 2 (DH-164) | | |
| TC-1-09 | FR-1.6 | Edge | Duplicate claims are removed | "Paris is in France. paris is in France!" | 1 claim (first occurrence kept) | Sprint 2 (DH-165) | | |
| TC-1-10 | FR-1.7 | Normal | Claims are numbered without gaps | "Mars is the fourth planet. Is that right? Jupiter is the largest planet." | ids `[1, 2]`, sentence_index `[0, 2]`; all-opinion text returns `[]` | `test_ids_have_no_gaps_and_keep_original_sentence_index`, `test_all_sentences_non_factual_returns_empty_list` | | |

Error and edge cases: TC-1-01, TC-1-02, TC-1-06, TC-1-09.

### UC-2: Retrieve evidence for a claim (Owner: Shreya Raghuraj, Role B)

See [`docs/test_cases_UC-2.md`](../test_cases_UC-2.md) (TC-2-01 to TC-2-10).

### UC-3: Verify a claim against its evidence (Owner: Ralph D'souza, Role C)

Automated tests: `tests/unit/test_verifier.py`

| TC ID | FR | Type | Description | Input | Expected result | Automated test | Actual | Pass/Fail |
|---|---|---|---|---|---|---|---|---|
| TC-3-02 | FR-3.3 | Positive | High entailment supports the claim | Claim: “Paris is in France.” Evidence: “Paris is the capital of France.” | SUPPORTED; score 0.9; matching evidence returned | `test_tc_3_02_high_entailment_is_supported` | | |
| TC-3-03 | FR-3.3 | Positive | High contradiction contradicts the claim | Claim: “Paris is in Italy.” Evidence: “Paris is the capital of France.” | CONTRADICTED; score 0.9; matching evidence returned | `test_tc_3_03_high_contradiction_is_contradicted` | | |
| TC-3-04 | FR-3.4 | Negative | Claim has no evidence | Claim: “Unknown fact.” No evidence supplied | NOT_ENOUGH_INFO; score 0.0; no best evidence; model not called | `test_tc_3_04_no_evidence_is_not_enough_info` | | |
| TC-3-05 | FR-3.3 | Boundary | Evidence is uncertain | Claim: “The fact is true.” Evidence: “Some unrelated information.” | NOT_ENOUGH_INFO; score 0.7; best evidence returned | `test_tc_3_05_uncertain_evidence_is_not_enough_info` | | |
| TC-3-06 | FR-3.2 | Positive | Only evidence matching the claim is used | One evidence item for claim 2 and one for claim 1 | SUPPORTED; matching evidence selected; predictor called once with matching pair | `test_tc_3_06_only_matching_claim_evidence_is_used` | | |
| TC-3-07 | FR-3.1 | Positive | Model and tokenizer are loaded on demand | Model and tokenizer initially unset | Both loaded using configured NLI model | `test_tc_3_07_model_is_loaded_lazily` | | |
| TC-3-08 | FR-3.6 | Boundary | Empty verdict list returns the default trust score | Empty list `[]` | Trust score is 100.0 | `test_trust_score_empty_list` | | |
| TC-3-09 | FR-3.6 | Normal | Trust score averages mixed verdicts | One SUPPORTED, one NOT_ENOUGH_INFO, one CONTRADICTED verdict | Trust score is 50.0 | `test_trust_score_mixed_verdicts` | | |
| TC-3-10 | FR-3.5 | Negative | A number mismatch for the same named entity forces contradiction | Claim: “Einstein was born in 1879.” Evidence: “Einstein was born in 1899.” | CONTRADICTED; score is `max(max_contradiction, 0.75)`; matching evidence returned | `test_tc_3_10_year_mismatch_forces_contradicted` | | |
| TC-3-11 | FR-3.5 | Positive | Matching numbers do not trigger the mismatch rule | Claim: “Einstein was born in 1879.” Evidence: “Einstein was born in 1879.” | SUPPORTED; score 0.9; matching evidence returned | `test_tc_3_11_matching_numbers_remain_supported` | | |

### UC-4: Check and correct a chatbot answer (Owner: Satwik, Role D)

*To be added (DH-196).*

| TC ID | FR | Type | Description | Input | Expected result | Automated test | Actual | Pass/Fail |
|---|---|---|---|---|---|---|---|---|
