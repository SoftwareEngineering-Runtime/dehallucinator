# LLM prompt log – Role A (Sai Nikitha Perumalla)

## DH-151 project skeleton – 2026-09-19
Tool: Claude
Prompt: "Create the project skeleton from manual Section 4: folder layout, pydantic models for
Claim, Evidence, Verdict and CheckedAnswer, config constants, stub functions for each role,
and one skipped placeholder test per test file."
What I kept: folder layout, models.py, config.py, stubs, model tests
What I changed: added pyproject.toml settings and README team table
I can explain it: yes

## DH-161 input validation + sentence splitting – 2026-10-06
Tool: Claude
Prompt: "Implement extract_claims for FR-1.1 and FR-1.2: reject empty or >5000-char input
with ValueError, split sentences with spaCy en_core_web_sm loaded only once, and return
numbered Claim objects. Write tests TC-1-01 to TC-1-03 plus edge cases."
What I kept: validate_input, split_sentences, get_nlp with lru_cache, the tests
What I changed: replaced a nested enumerate with a plain loop so the numbering is easier
to read and still works once DH-162 starts dropping sentences
I can explain it: yes

## DH-162 non-factual sentence filter – 2026-10-10
Tool: Claude
Prompt: "Add is_factual() for FR-1.3: drop questions, sentences containing an opinion marker
(whole words, any case), sentences starting with I/We, and sentences shorter than
MIN_CLAIM_WORDS. Keep claim IDs gap-free but keep the original sentence_index.
Write tests TC-1-04 to TC-1-06 plus edge cases."
What I kept: is_factual, OPINION_PATTERN regex, the tests
What I changed: used a \b word-boundary regex so "shoulder" is not treated as "should"
I can explain it: yes

## DH-212 Sprint 0 log – 2026-10-12
Tool: Claude
Prompt: "Write docs/sprints/sprint-0.md using the sprint log template in manual Section 13.4.
Use the Sprint 0 tickets DH-151 to DH-160 from Jira with owner, points and the PR or file that
proves each one is done. Replace the daily stand-up section with a progress log table built
from the GitHub PR history and Jira, then add the review and a short retrospective."
What I kept: the ticket table, progress log, review and retrospective
What I changed: corrected the PR numbers against GitHub and removed the stand-up section
I can explain it: yes

## DH-163 compound sentence split – 2026-10-26
Tool: Claude Code
Prompt: "Add split_compound() to the Claim Extractor for FR-1.4. Split a sentence at ';',
', and' or ', but' only when both parts have their own subject and verb (check with the
spaCy dependency parse: nsubj/nsubjpass/expl plus a VERB or AUX). Keep lists like 'Salt and
pepper are spices.' as one claim, end each part with the sentence's full stop and capitalise
the second part. Every part keeps the original sentence_index. Write TC-1-07 plus tests for
lists, a part without its own subject, semicolons and three-way splits."
What I kept: has_subject_and_verb, split_compound (recursive for several split points), tests
What I changed: wrote TC-1-07 with the name repeated until pronoun replacement (DH-164)
existed, then switched it back to "he" as in the test plan
I can explain it: yes

## DH-164 leading pronoun replacement – 2026-10-26
Tool: Claude Code
Prompt: "Implement FR-1.5: replace a leading pronoun with the most recent named entity from
earlier sentences. He/She/His/Her should only match people (PERSON), It/Its/They/Their only
things (ORG, GPE, LOC, FAC, ...); ignore DATE and CARDINAL entities. Prefer the subject of the
previous sentence, using the full noun phrase, so in 'The Eiffel Tower is in Paris. It is
330 m tall.' the pronoun becomes 'The Eiffel Tower', not 'Paris'. Possessives become
'<entity>'s'. Leave the claim unchanged if no entity has been seen. Write TC-1-08 and tests."
What I kept: EntityMemory class, replace_leading_pronoun, the person/thing pronoun tables
What I changed: updated TC-1-03 to expect "Paris is a large city." and split a long test
string that ruff flagged (line length 100)
I can explain it: yes

## DH-165 duplicate removal and numbering – 2026-10-26
Tool: Claude Code
Prompt: "Implement FR-1.6 and FR-1.7: remove duplicate claims, ignoring case, punctuation and
extra spaces, keeping the first occurrence, and keep claim ids 1, 2, 3 ... with no gaps while
sentence_index still points at the original sentence. Run de-duplication after pronoun
replacement so 'It is in Paris.' is caught as a repeat. Write TC-1-09 and tests."
What I kept: normalise(), the seen-set in extract_claims, the tests
What I changed: added the test for a duplicate that only appears after pronoun replacement
I can explain it: yes

## DH-188 Claim Extractor class and sequence diagrams – 2026-10-26
Tool: Claude Code
Prompt: "Write docs/design/extractor_design.md in the same format as the retriever design doc:
a Mermaid class diagram of the extractor module (shown as a <<module>>), EntityMemory, Claim,
config and spaCy, a sequence diagram of extract_claims() covering validation, filtering,
compound split, pronoun replacement and de-duplication, and a table of design decisions."
What I kept: both diagrams and the design decisions table
What I changed: checked that every function in the diagram exists in extractor.py
I can explain it: yes

## DH-192 compile Architecture and Design documents – 2026-11-07
Tool: Claude Code
Prompt: "Compile the architecture and design docs from docs/architecture and docs/design into
one PDF for the Team 14 submission: cover page with members and roles, one part per role,
Mermaid diagrams rendered, links to repo files turned into plain text. Also build the test
plan PDF with the Actual and Pass/Fail columns filled from a real pytest run."
What I kept: the PDF build and layout
What I changed: restored sections 1.3–1.5 of architecture.md that were lost in the DH-190
merge, and fixed a ';' inside a Mermaid Note that stopped the verifier sequence diagram
rendering
I can explain it: yes

## DH-203 README overview, setup and Claim Extractor section – 2026-11-07
Tool: Claude Code
Prompt: "Update README.md: add a real example from check_answer() at the top, setup steps
including the spaCy model and a Python usage snippet, how to run lint, tests and coverage,
the current project layout, and a Claim Extractor section with one row per step mapped to
FR-1.1 to FR-1.7. Leave empty sections for the Retriever, Verifier and API/UI owners."
What I kept: the example table, setup, layout and the Claim Extractor section
What I changed: removed a model download size I could not confirm
I can explain it: yes

## DH-213 Sprint 1 review and retrospective – 2026-11-07
Tool: Claude Code
Prompt: "Finish docs/sprints/sprint-1.md: fill in completed and carried-over tickets from the
closed Jira sprint, update every ticket's status and evidence (PR number), extend the progress
log with the late PRs #22, #24 and #25, and finish the review and retrospective."
What I kept: the updated tables, progress log, review and retrospective
What I changed: left out the Sprint 1 burndown chart because the Jira chart was not usable
I can explain it: yes
