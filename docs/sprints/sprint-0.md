# Sprint 0 – Setup (18 Sep – 4 Oct 2026)

Scrum Master: Sai Nikitha Perumalla (Role A)

**Goal:** Everyone can clone and run the project; repo, Jira, CI and SonarQube set up; SRS written.

**Committed stories (10, 25 points):** DH-151, DH-152, DH-153, DH-154, DH-155, DH-156,
DH-157, DH-158, DH-159, DH-160
**Completed:** 10 of 10 (25 of 25 points)
**Carried over:** none

| Ticket | Story | Owner | Points | Evidence |
|---|---|---|---|---|
| DH-151 | Protected GitHub repo with code skeleton, models and config | Nikitha (A) | 3 | PR #1 |
| DH-152 | Jira linked to GitHub so commits and PRs show on tickets | Nikitha (A) | 1 | GitHub for Jira app |
| DH-153 | Basic Jenkins pipeline (lint + tests on every branch) | Satwik (D) | 5 | PR #5, `Jenkinsfile` |
| DH-154 | SonarQube Cloud analysis on every PR | Ralph (C) | 2 | PR #2, `sonar-project.properties` |
| DH-155 | 15 trusted local knowledge-base documents | Shreya (B) | 3 | PR #3, `data/kb/` |
| DH-156 | SRS: UC-1 and FR-1.x (Claim Extractor) | Nikitha (A) | 2 | `docs/srs/` |
| DH-157 | SRS: Introduction, NFRs, UC-2 and FR-2.x | Shreya (B) | 3 | `docs/srs/` |
| DH-158 | SRS: UC-3, FR-3.x and validation approach | Ralph (C) | 2 | `docs/srs/` |
| DH-159 | SRS: UC-4, FR-4.x and external interfaces | Satwik (D) | 2 | `docs/srs/` |
| DH-160 | Compile and export the final SRS | Shreya (B) | 2 | PR #4, `docs/srs/SRS_Dehallucinator.pdf` |

## Planning (18 Sep)

- Agreed the four roles from the team manual: A Claim Extractor + Scrum Master, B Evidence
  Retriever, C Verifier & Scorer, D Corrector, API and UI.
- Set up the Jira Scrum board (project DH) with epics E1–E10 and the four sprints.
- Agreed the working rules: one Jira ticket per piece of work, one branch per ticket,
  every change merged through a pull request with one approval, daily stand-up on WhatsApp.

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
| 18 Sep | Nikitha | Jira board, epics and Sprint 0 tickets created; sprint started |
| 19–20 Sep | Nikitha | DH-151: project config, data models, module stubs, test skeleton, README |
| 2 Oct | Nikitha | GitHub repo created in the SoftwareEngineering-Runtime org; branch protection on `main`; PR #1 merged |
| 3 Oct | Ralph | DH-154: SonarQube Cloud configuration |
| 4 Oct | Satwik | DH-153: basic Jenkins pipeline |
| Sep – Oct | All | DH-156 to DH-159: SRS sections written in the shared SRS draft |
| 5 Oct | Shreya | DH-155: 15 knowledge-base documents |
| 6 Oct | Shreya | DH-160: final SRS compiled and exported |

The Sprint 0 pull requests #2 to #5 were reviewed and merged on 5–6 Oct, at the start of Sprint 1.

## Review (4 Oct)

<!-- Confirm on the call who demoed what; edit if anything differs. -->

- **Nikitha:** the protected repo (one approval required, merge commits only), the project
  skeleton running `pytest`, and Jira showing commits and PRs on each ticket.
- **Shreya:** the 15 knowledge-base documents and the compiled SRS.
- **Ralph:** SonarQube Cloud analysing pull requests.
- **Satwik:** the Jenkins pipeline running lint and tests on a branch.

## Retrospective

<!-- Draft based on what happened this sprint. Confirm or change on the call. -->

**Went well**
- All 10 stories done; everyone can clone the repo and run the tests.
- Branch protection, Jira–GitHub link, Jenkins and SonarQube were all in place before
  feature work started.
- The SRS was written by all four members, each owning their own use case and FRs.

**Didn't go well**
- Jira setup took several attempts: the default workflow sent new tickets straight to
  Done, and the first ticket import had to be redone.
- The SRS was drafted in Google Docs, so its edit history isn't in the repo.
- The Sprint 0 pull requests were opened at the very end of the sprint and merged a day
  or two after it closed.

**We will change**
- Keep documents in the repo as Markdown and change them through pull requests like code.
- Open pull requests as soon as a ticket is done, not at the end of the sprint.
- Run `ruff format .`, `ruff check .` and `pytest` before every push.

**Burndown:** _screenshot to be added (`docs/sprints/img/sprint-0-burndown.png`)._
<!-- Then replace the line above with: ![Sprint 0 burndown](img/sprint-0-burndown.png) -->
