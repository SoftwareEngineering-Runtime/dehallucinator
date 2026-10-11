# LLM prompt log – Role D (Satwik)

## DH-153 basic Jenkins pipeline – 2026-10-04
Tool: Claude
Prompt: "Write a Jenkinsfile for a Multibranch Pipeline on my Windows laptop with the stages
Checkout, Setup, Lint and Unit tests from manual 11.1, and help me set up Jenkins LTS locally."
What I kept: the four stages, the runCmd helper for Windows (bat) and Linux (sh) agents, the
PYTHON environment variable for the Python 3.11 path, JUnit result publishing
What I changed: renamed the helper from run to runCmd after the first build failed because
run clashes with a built-in Jenkins step
I can explain it: TODO

## DH-159 SRS section UC-4, FR-4.x and external interfaces – 2026-10-06
Tool: Claude
Prompt: "Draft SRS section 3.4 for the Corrector & Integration module in the same format as
sections 3.1 to 3.3: UC-4, FR-4.1 to FR-4.6, and the /check and /health API."
What I kept: the use case, the six requirements and the API table
What I changed: aligned it with the other sections (grey for unverified claims as in NFR-6,
trust score 100 when there are no claims as in FR-3.6, 422 for malformed JSON)
I can explain it: TODO

## DH-175 corrector – 2026-10-10
Tool: Claude
Prompt: "Implement correct(text, claims, verdicts) for FR-4.1: replace CONTRADICTED claims with
the evidence snippet and source, tag NOT_ENOUGH_INFO claims [unverified] and SUPPORTED claims
with their source, and handle claims the extractor reworded. Write tests TC-4-01 to TC-4-05
plus edge cases."
What I kept: the edit-list approach (find each claim in its sentence, then apply all edits
left to right), the tag formats, the tests
What I changed: reused the extractor's get_nlp and skipped whitespace-only sentences so the
sentence numbering matches the Claim Extractor; trimmed sentence spans so tags stay before a
paragraph break
I can explain it: TODO

## DH-176 check_answer() pipeline – 2026-10-10
Tool: Claude
Prompt: "Implement check_answer(text) for FR-4.2: run extract, retrieve, verify, score and
correct in order, return a CheckedAnswer, log each stage's time in milliseconds, and raise
ValueError for invalid input. Unit-test it with the four stages faked."
What I kept: the _timed helper, the single log line per answer, the tests with fake stages
What I changed: skip the retriever and verifier when there are no claims, so a greeting does
not trigger network calls or load the NLI model
I can explain it: TODO

## DH-177 REST API – 2026-10-10
Tool: Claude
Prompt: "Build the FastAPI app for FR-4.4: POST /check calling check_answer and GET /health,
422 for invalid input including blank text and malformed JSON, and 500 with a generic message
and no stack trace for unexpected errors. Write tests TC-4-06 to TC-4-09 with check_answer
faked."
What I kept: the CheckRequest model with the 5000-character limit and blank-text check, the
try/except in the endpoint, the tests
What I changed: made the endpoint a plain def so the slow pipeline runs in a worker thread,
and checked it by hand with uvicorn (/health ok, blank text 422, greeting returns trust 100)
I can explain it: TODO

## DH-187 architecture doc: API, UI and deployment – 2026-10-10
Tool: Claude
Prompt: "Write Section 4 of the architecture document for the API, UI and deployment, in the
same layout as the Evidence Retriever architecture doc, with a component diagram, the
/check request flow and a deployment diagram (GitHub, Jenkins, Docker, SonarQube)."
What I kept: the three Mermaid diagrams, the component and error-handling tables
What I changed: marked the decorator, UI, Docker and full Jenkins pipeline as planned for
Sprint 2 so the doc matches what is built today
I can explain it: TODO
