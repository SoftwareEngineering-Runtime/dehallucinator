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
