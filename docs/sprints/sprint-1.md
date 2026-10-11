# Sprint 1 – Core (5 Oct – 14 Oct 2026)

Scrum Master: Sai Nikitha Perumalla (Role A)

**Goal:** Each module works on simple input with unit tests; first integration tests;
Jenkins builds and tests every push.

**Committed stories (24, 62 points):** DH-161, DH-162, DH-166, DH-167, DH-168, DH-171,
DH-172, DH-173, DH-175, DH-176, DH-177, DH-184, DH-185, DH-186, DH-187, DH-193, DH-194,
DH-195, DH-196, DH-197, DH-210, DH-211, DH-212, DH-213
**Completed:** <!-- fill in at the end of the sprint --> _N of 24 (N of 62 points)_
**Carried over to Sprint 2:** <!-- fill in at the end of the sprint --> _..._

### Features (Epics E1–E5)

| Ticket | Story | Owner | Points | Evidence | Status |
|---|---|---|---|---|---|
| DH-161 | Validate input and split it into sentences | Nikitha (A) | 3 | PR #6 | Done |
| DH-162 | Filter out non-factual sentences | Nikitha (A) | 3 | PR #8 | Done |
| DH-166 | Build a search query from each claim | Shreya (B) | 3 | PR #7 | Done |
| DH-167 | Search Wikipedia and fetch page text | Shreya (B) | 5 | PR #11 | Done |
| DH-168 | Rank evidence snippets with TF-IDF | Shreya (B) | 3 | PR #12 | Done |
| DH-171 | Load the NLI model once | Ralph (C) | 3 | PR #10 | Done |
| DH-172 | Label each claim SUPPORTED / CONTRADICTED / NOT_ENOUGH_INFO | Ralph (C) | 5 | PR #16 | Done |
| DH-173 | Overall trust score | Ralph (C) | 2 | PR #9 | Done |
| DH-175 | Correct wrong claims and flag unverified ones | Satwik (D) | 3 | PR #18 | Done |
| DH-176 | One `check_answer()` pipeline | Satwik (D) | 3 | PR #19 | Done |
| DH-177 | REST API (`POST /check`, `GET /health`) | Satwik (D) | 3 | PR #20 | Done |

### Documentation, testing and process (Epics E7–E11)

| Ticket | Task | Owner | Points | Evidence | Status |
|---|---|---|---|---|---|
| DH-184 | Architecture overview and diagram | Nikitha (A) | 2 | PR #15 | Done |
| DH-185 | Architecture: Evidence Retriever | Shreya (B) | 1 | PR #13 | Done |
| DH-186 | Architecture: Verifier | Ralph (C) | 1 | | To Do |
| DH-187 | Architecture: API, UI and deployment | Satwik (D) | 2 | PR #21 | Done |
| DH-193 | Test cases TC-1-01..10 (UC-1) | Nikitha (A) | 2 | PR #15 | Done |
| DH-194 | Test cases TC-2-01..10 (UC-2) | Shreya (B) | 2 | PR #14 | Done |
| DH-195 | Test cases TC-3-01..10 (UC-3) and test plan | Ralph (C) | 2 | PR #17 | In Review |
| DH-196 | Test cases TC-4-01..10 (UC-4) | Satwik (D) | 2 | | To Do |
| DH-197 | Integration tests for the full pipeline | Ralph (C) | 3 | | To Do |
| DH-210 | Sprint 1 planning, stand-ups and progress tracking | Nikitha (A) | 3 | this log | In Progress |
| DH-211 | Review and merge Sprint 1 pull requests | Nikitha (A) | 3 | PR reviews | In Progress |
| DH-212 | Sprint 0 log | Nikitha (A) | 1 | `sprint-0.md` | In Review |
| DH-213 | Sprint 1 review and retrospective | Nikitha (A) | 2 | this log | In Progress |

<!-- Update the Status column on 14 Oct before the review call. -->

**Quality at the end of the sprint** (from `pytest --cov` and SonarQube Cloud, 11 Oct):
85 unit tests passing, 92% line and branch coverage, `ruff` clean, SonarQube quality gate
passing on every merged pull request.

## Planning (5 Oct)

- Closed Sprint 0 (10 of 10 stories done) and started Sprint 1 with 24 tickets.
- Every ticket has an owner and story points; each member has at least one feature story,
  one documentation ticket and one test-case ticket so contributions are visible.
- Agreed that every pull request must pass Jenkins lint and tests and the SonarQube
  quality gate, and get one approval, before it is merged.

## Daily stand-ups

<!-- Paste the WhatsApp stand-ups here in the format from the team manual (2.3):
Stand-up – <name> – <date>
Yesterday: ...
Today: ...
Blockers: ... -->

_To be pasted from the team WhatsApp group._

### Activity log (from GitHub and Jira)

| Date | Who | What |
|---|---|---|
| 5–6 Oct | All | Sprint 0 pull requests #2–#5 reviewed and merged |
| 6 Oct | Nikitha | DH-161: input validation and sentence splitting (PR #6) |
| 9 Oct | Shreya | DH-166: search query builder (PR #7) |
| 10 Oct | Nikitha | DH-162: non-factual filter (PR #8); DH-184/193: docs moved into the repo (PR #15) |
| 10 Oct | Ralph | DH-173: trust score (PR #9); DH-171: NLI model loading (PR #10); DH-172: claim verification (PR #16); DH-195: UC-3 test cases (PR #17) |
| 10 Oct | Shreya | DH-167: Wikipedia search (PR #11); DH-168: snippet ranking (PR #12); DH-185: retriever architecture (PR #13); DH-194: UC-2 test cases (PR #14) |
| 11 Oct | Shreya | Fixed `ruff format` and `zip(strict=True)` findings on PRs #11 and #12 |
| 11 Oct | Satwik | DH-175: corrector (PR #18); DH-176: pipeline (PR #19); DH-177: REST API (PR #20); DH-187: API/UI/deployment architecture (PR #21) |
| 11 Oct | Satwik | Fixed the SonarQube reliability finding on PR #18 |
| 11 Oct | Nikitha | Reviewed and merged PRs #11, #12, #16, #18–#21; Jira board updated |

## Review (14 Oct)

<!-- Fill in during the 15-minute call: each person demos their Done tickets. -->

- **Nikitha:** _claim extraction on a sample answer (validation, sentence split, opinion
  and question filtering); architecture overview and UC-1 test cases in `docs/`._
- **Shreya:** _search query, Wikipedia fetch and TF-IDF ranking for a sample claim;
  retriever architecture and UC-2 test cases._
- **Ralph:** _NLI verdicts and trust score for sample claims; UC-3 test cases._
- **Satwik:** _`POST /check` returning a corrected answer end to end; API/UI/deployment
  architecture._

## Retrospective

<!-- Draft based on what happened this sprint. Confirm or change on the call. -->

**Went well**
- All four modules work end to end: `POST /check` takes an answer and returns a corrected
  one with a trust score.
- 85 unit tests at 92% coverage, above the 80% target.
- Every change went through a reviewed pull request, and reviews caught real problems
  (formatting, a SonarQube reliability finding, test-case documentation).
- All documents now live in the repo, so documentation work is reviewed and visible too.

**Didn't go well**
- Most pull requests arrived on 10–11 Oct, the last days of the sprint, leaving little
  time for review and fixes.
- Some pull requests failed the lint check because of an editor using an 88-character
  line length instead of our 100.
- Some documentation was pasted from a word processor and did not render as Markdown
  on GitHub.
- Integration tests (DH-197) were not started until the end of the sprint.

**We will change**
- Open a pull request as soon as each story is done, and aim for the first PRs by the
  middle of the sprint.
- Run `ruff format . && ruff check . && pytest` before every push (or add a pre-commit hook).
- Write documents directly in Markdown and check the GitHub preview before opening a PR.
- Schedule integration tests early in Sprint 2, now that the full pipeline exists.

**Burndown:** _screenshot to be added (`docs/sprints/img/sprint-1-burndown.png`)._
<!-- Then replace the line above with: ![Sprint 1 burndown](img/sprint-1-burndown.png) -->
