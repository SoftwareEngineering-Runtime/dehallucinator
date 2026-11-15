# LLM prompt log — Role C (Verifier \& Scorer)



## DH-173 trust score calculation — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement trust\_score to calculate an overall trust score from verdict labels, mapping SUPPORTED to 1.0, NOT\_ENOUGH\_INFO to 0.5, and CONTRADICTED to 0.0, and returning a score from 0 to 100."

What I kept: The label-to-score mapping, averaging logic, and conversion to a 0–100 score.

What I changed: Added unit tests for empty, fully supported, fully contradicted, and mixed verdict lists.

I can explain it: yes



## DH-171 NLI model lazy loading — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement lazy loading for the NLI tokenizer and sequence classification model using the existing config.NLI\_MODEL setting."

What I kept: The module-level tokenizer and model variables and the lazy-loading logic in \_load\_model().

What I changed: Sorted imports and applied Ruff formatting.

I can explain it: yes



## DH-172 claim verification and mocked tests — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement verify\_claims using NLI probabilities from the model's id2label mapping, and add mocked tests for supported, contradicted, not-enough-info, evidence filtering, and lazy model loading."

What I kept: The claim-to-evidence matching, threshold-based verdict selection, confidence scoring, and use of model.config.id2label.

What I changed: Added mocked tests for verdict outcomes, evidence filtering, and lazy model loading; ran pytest coverage and Ruff checks.

I can explain it: yes

## DH-183 SonarQube security fixes — 2026-11

Tool: ChatGPT

Prompt: "Help me resolve the SonarQube security findings by locking Python dependency versions and hashes, updating the Dockerfile to install verified dependencies, and checking the results step by step."

What I kept: Hash-locked dependencies in `requirements.lock.txt`, hash verification during Docker dependency installation, and a pinned spaCy model.

What I changed: Verified dependency installation locally using `pip --dry-run --require-hashes`, committed the changes on a separate branch, and checked the SonarCloud results. The Quality Gate passed with zero new issues and zero security hotspots. Docker build was not tested locally.

I can explain it: yes

## DH-198 System tests — 2026-11

Tool: ChatGPT

Prompt: "Help me prepare and validate the end-to-end system tests, fix Ruff formatting issues, and resolve the missing strict=True argument in zip()."

What I kept: The end-to-end testing approach and the correction to `zip(..., strict=True)`.

What I changed: Applied Ruff formatting, corrected the flagged code in `tests/system/test_end_to_end.py`, reran Ruff checks successfully, and pushed the updated branch for review.

I can explain it: yes

## DH-199 Security tests — 2026-11

Tool: ChatGPT

Prompt: "Help me verify the security tests and resolve any Ruff formatting or linting issues before updating the pull request."

What I kept: The existing security-test cases and the suggested linting workflow.

What I changed: Formatted `tests/security/test_security.py`, confirmed `ruff check .` passed, and pushed the changes to the security-test pull request.

I can explain it: yes

## DH-200 Validation report — 2026-11

Tool: ChatGPT

Prompt: "Help me prepare a validation report covering the test plan, requirements traceability, unit and integration results, system and security testing, coverage, limitations, and validation status. Guide me through verifying the results before documenting them."

What I kept: The validation report structure, requirements-to-tests mapping, and separation of verified results from outstanding validation items.

What I changed: Ran the full test suite and relevant use-case test groups, checked coverage, documented 167 passed and 2 skipped tests, recorded 94% combined statement-and-branch coverage, and marked the overall status as partially validated where acceptance evidence remained incomplete.

I can explain it: yes

## DH-205 README: Verifier & Scorer section — 2026-11-15

Tool: ChatGPT

Prompt: "Help me write the Verifier & Scorer (Role C) README section in the same format as the other team members, using my actual verifier.py implementation and configuration values. Verify the changes before proceeding."

What I kept: The six-step explanation of evidence matching, NLI inference, threshold-based verdicts, missing evidence, numerical consistency checks, and trust-score calculation.

What I changed: Confirmed the NLI model and 0.70 thresholds against `config.py`, corrected the documented test-case range to TC-3-02 through TC-3-11, and repaired an unintended Unicode encoding change so the README diff contained only the Role C addition.

I can explain it: yes