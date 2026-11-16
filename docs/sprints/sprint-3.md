# Sprint 3 – Validation + release (10 Nov – 16 Nov 2026)

Scrum Master: Sai Nikitha Perumalla (Role A)

**Goal:** Release-ready: Docker image and full 8-stage Jenkins pipeline, SonarQube quality gate
passing, system and security tests, validation report, coverage report, maintenance plan,
README sections from every role, LLM prompt logs complete, slides, final report and a
rehearsed demo.

**Committed stories (18, 38 points):** DH-180, DH-181, DH-183, DH-191, DH-198, DH-199, DH-200,
DH-201, DH-202, DH-203, DH-204, DH-205, DH-206, DH-207, DH-208, DH-214, DH-215, DH-216
(DH-180, DH-181 and DH-191 carried over from Sprint 2)
**Completed by 16 Nov:** 17 of 18 (36 of 38 points). Only DH-208 (demo rehearsals) is still
open; its backup recording and the pre-cached demo samples are done.

### Features and quality (Epics E7, E9)

| Ticket | Story | Owner | Points | Evidence | Status |
|---|---|---|---|---|---|
| DH-180 | Full 8-stage Jenkins pipeline | Satwik (D) | 5 | PR #39 | Done |
| DH-181 | Docker image (wheels only, CPU torch, model baked in) | Satwik (D) | 3 | PR #38 | Done |
| DH-183 | SonarQube quality gate passing (hash-locked Docker dependencies) | Ralph (C) | 3 | PR #58 | Done |
| DH-198 | System tests on the 10 sample answers | Ralph (C) | 3 | PR #56 | Done |
| DH-199 | Security tests | Ralph (C) | 3 | PR #57 | Done |
| DH-200 | Validation report | Ralph (C) | 3 | PR #59 | Done |
| DH-201 | Coverage report export (PDF) | Satwik (D) | 1 | PR #55 | Done |

### Documentation, release and process (Epics E8, E10, E11)

| Ticket | Task | Owner | Points | Evidence | Status |
|---|---|---|---|---|---|
| DH-191 | Design: Corrector, pipeline and API spec | Satwik (D) | 3 | PR #40 | Done |
| DH-202 | Maintenance plan | Satwik (D) | 2 | PR #54 | Done |
| DH-203 | README: overview, setup and Claim Extractor | Nikitha (A) | 1 | PRs #43, #51 | Done |
| DH-204 | README: Evidence Retriever + Role B prompt log | Shreya (B) | 1 | PRs #49, #50 | Done |
| DH-205 | README: Verifier + Role C prompt log | Ralph (C) | 1 | PRs #60, #61 | Done |
| DH-206 | README: API, UI and deployment | Satwik (D) | 1 | PR #47 | Done |
| DH-207 | Final report and presentation slides | Shreya (B), finished by Nikitha (A) | 3 | 13-slide deck; SE deliverables PDF (`docs/exports/`) | Done |
| DH-208 | Demo rehearsals and backup recording | Nikitha (A) | 2 | samples pre-cached, backup recording | In progress |
| DH-214 | Sprint 2 log | Nikitha (A) | 1 | PR #45 | Done |
| DH-215 | Commit exported final documents | Nikitha (A) | 1 | PR #46 | Done |
| DH-216 | Sprint 3 log | Nikitha (A) | 1 | this file | Done |

**Quality at the end of the sprint** (from `pytest`, `ruff` and SonarQube Cloud, 16 Nov):
186 tests passing, 0 failed, 0 skipped (unit 165, integration 3, system 10, security 8); 94%
line + branch coverage on the Jenkins suite (`-m "not slow"`), 97% with the system tests;
every module at least 86%; `ruff` clean; SonarQube quality gate on `main` passing; all 10 demo
samples give the expected verdicts (8 planted mistakes CONTRADICTED, 2 all-correct answers
scored 100).

## Planning (10 Nov)

- Closed Sprint 2 (16 of 19 done) and moved DH-180, DH-181 and DH-191 into Sprint 3.
- Took every remaining release item from the manual (Section 9.4 and the deliverables table):
  system and security tests, validation report, coverage report, maintenance plan, README
  sections, slides, final report and demo rehearsals.
- Agreed merge order for Satwik's stacked PRs: #38 → #39 → #40 → #47.

## Progress log (from GitHub and Jira)

| Date | Who | What |
|---|---|---|
| 10 Nov | Nikitha | Sprint 3 started (18 tickets, 38 points); README overview and Claim Extractor section (PR #43) |
| 12 Nov | Nikitha | Role A prompt log (PR #44), Sprint 2 log (PR #45) and exported final documents (PR #46) merged after Shreya's review |
| 12 Nov | Satwik | Fixed the SonarCloud findings on #38/#39 (wheels only, SSRF-safe health check that takes only a port); posted the Docker build and `/health` result; opened README section D (PR #47) |
| 14 Nov | Shreya | kb.py tests: coverage 30% → 100% (PR #48); README section B (PR #49); Role B prompt log (PR #50) |
| 14 Nov | Nikitha | README Setup fix: `pip install -e .` so `import dehallucinator` works outside pytest (PR #51, reported by Satwik and Shreya); pre-cached all 10 demo samples and recorded a backup demo |
| 15 Nov | Satwik | Stack #38 → #39 → #40 → #47 merged; opentelemetry-api CVE fix (PR #53), maintenance plan (PR #54), coverage report PDF (PR #55) |
| 15 Nov | Shreya | Test cases TC-2-06..10 mapped to the real pytest functions (PR #52); first draft of the 13-slide deck |
| 15 Nov | Ralph | System tests and a same-subject check that stops false CONTRADICTED verdicts (PR #56); security tests (PR #57); review asked for `ruff` fixes, merged the same evening |
| 16 Nov | Ralph | Validation report, status VALIDATED (PR #59) |
| 16 Nov | Nikitha | Finished the remaining fixes on Ralph's PRs so they could merge before the demo: pinned pip and setuptools in the hash lock (PR #58), fixed the README section C numbers and encoding (PR #60), resolved the C.md conflict (PR #61); SonarQube gate on `main` green |
| 16 Nov | Nikitha | Final 13-slide deck rebuilt with current numbers and screenshots; SE deliverables PDF (use case diagram, Jira backlog, SRS, test plan, project plan, architecture and design, test and coverage reports, demo screenshots, slides) |

## Review

- **Nikitha:** README with working setup steps; all 10 demo samples cached and a backup
  recording of the demo; sprint logs for Sprints 0–3.
- **Shreya:** kb.py at 100% coverage; README section B; the first draft of the slide deck.
- **Ralph:** 10 system tests running the real pipeline on the 10 samples; 8 security tests;
  the validation report; the hash-locked Docker dependencies that made the SonarQube gate pass.
- **Satwik:** the Docker image (builds, `/health` ok, UI runs from it); the 8-stage Jenkins
  pipeline; the coverage report PDF and the maintenance plan.

## Retrospective

**Went well**
- Everything the manual asks for was merged before the demo: 186 tests, 94% coverage, the
  quality gate passing and a VALIDATED validation report.
- Reviews kept catching real problems before merge: an empty prompt-log file, a lint failure
  that would have turned Jenkins red, a lock file that pinned a vulnerable library and another
  that would have broken the Docker build.
- Testing every PR together on one branch (all open PRs merged locally, then lint, tests and
  the 10 demo samples) showed that a late verifier change did not change any demo result.

**Didn't go well**
- Most Sprint 3 work arrived in the last two days, so review and fixes were squeezed into the
  final weekend.
- One member was unreachable for most of the sprint, and the team only found out when the
  tickets were still in To Do two days before the end.
- Several PRs quoted numbers (test counts, coverage, quality gate) from before other PRs
  merged, so documents and slides disagreed until they were checked against `main`.

**We will change**
- Daily check-in on the group: everyone posts what they pushed or what blocks them.
- Flag a ticket that has not moved in two days, and agree a new owner or a smaller scope
  straight away.
- Always quote numbers from a fresh run on `main`, and say which suite they come from (Jenkins
  suite 94%, full suite 97%).

**Burndown:** Jira's Sprint 3 burndown chart is not included. It starts at 0 and goes below 0,
the same fault as the Sprint 1 chart, so it does not show the real progress. The progress log
above is the record of how the work was done.
