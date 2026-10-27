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

## DH-178 @dehallucinate decorator – 2026-10-24
Tool: Claude
Prompt: "Implement the @dehallucinate decorator for FR-4.3: wrap any function returning a str
so it returns a CheckedAnswer from check_answer, keep the name and docstring, and raise
TypeError for a non-str return. Write test TC-4-10 plus edge cases."
What I kept: functools.wraps, the isinstance check before calling the pipeline, the tests
(including decorating a method)
What I changed: typed it with ParamSpec so editors still show the wrapped function's arguments
I can explain it: TODO

## DH-179 demo chatbot UI and samples – 2026-10-24
Tool: Claude
Prompt: "Build the Streamlit demo UI for FR-4.5 and FR-4.6: a drop-down of 10 sample answers
from data/samples.json plus a paste box (max 5000 chars), one Check button, colour-coded claims
with source links, the trust score and the corrected answer, with all text HTML-escaped. Write
10 sample answers on our KB topics, some with planted mistakes. Test it with the pipeline faked."
What I kept: the ui_render module (claim cards, escaping, http-only links), the thin app.py,
the AppTest page tests, the samples
What I changed: checked every planted mistake against the KB files and against extract_claims
so each one becomes its own claim; added two fully correct samples so the demo also shows a
clean answer; ran all 10 through the real pipeline once Roles A to C were merged (8 of 8
planted mistakes caught, no true sentence flagged) after rewording four samples that the
retriever matched to the wrong page
I can explain it: TODO

## DH-196 UC-4 test cases – 2026-10-24
Tool: Claude
Prompt: "Write test cases TC-4-01 to TC-4-10 for UC-4 in the test plan, in the same table
format as UC-1 and UC-3, with at least 2 error cases, and add the FR-4.x traceability rows."
What I kept: the ten rows, each pointing at the pytest function that checks it, and the
traceability rows
What I changed: linked FR-4.2, FR-4.5 and FR-4.6 to the unit, integration and system tests
that cover them, since they have no TC-4 number of their own
I can explain it: TODO

## DH-182 bandit and pip-audit in CI – 2026-10-24
Tool: Claude
Prompt: "Add a Security scan stage to the Jenkinsfile for NFR-3 that fails on High bandit
issues or known vulnerabilities, and fix whatever it finds."
What I kept: bandit -r src ui -lll (High severity only) and pip-audit -r requirements.txt
What I changed: upgraded the vulnerable pins pip-audit found (pillow 12.3.0 -> 13.0.0,
certifi, filelock, opentelemetry-api) and streamlit 1.64.0 -> 1.66.1, because 1.64 does not
allow pillow 13; checked that bandit really exits 1 on a High issue
I can explain it: TODO

## DH-181 Docker image – 2026-10-24
Tool: Claude
Prompt: "Write a Dockerfile and .dockerignore for NFR-5 so the API runs with one command and
the container's /health returns ok."
What I kept: python:3.11-slim base, dependencies installed before the code is copied, the
spaCy and NLI models baked into the image, a non-root user, the HEALTHCHECK on /health
What I changed: used the CPU-only PyTorch index so the image does not pull the multi-GB CUDA
build; the same image can also start the Streamlit UI. Not built yet: Docker is not installed
on my laptop
I can explain it: TODO

## DH-180 full Jenkins pipeline – 2026-10-24
Tool: Claude
Prompt: "Extend the Jenkinsfile to the full pipeline from manual 11.4: all 8 stages, an 80%
coverage gate, JUnit and coverage reports published, and on main only a Docker image build
and deploy that checks /health."
What I kept: the 8 stages, pytest --cov-fail-under=80 with the HTML report published through
the HTML Publisher plugin, the main-only Build image and Deploy stages, ci/wait_for_health.py
What I changed: when Docker is missing on the agent the image stages mark the build UNSTABLE
instead of failing main for everyone; ran the pipeline on my Jenkins (all stages green,
93.5% coverage)
I can explain it: TODO
