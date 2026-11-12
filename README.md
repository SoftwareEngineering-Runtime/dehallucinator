# dehallucinator

Dehallucination add-on module for AI chatbots – SE mini-project (Project 39), UE24CS341A, PES University.

The module sits between a chatbot and the user. It splits the chatbot's answer into factual claims,
finds evidence for each claim in trusted sources (Wikipedia and local documents), labels each claim
as supported, contradicted or unverified, and returns a corrected answer with a trust score.

```
Chatbot answer → [A] Extract claims → [B] Find evidence → [C] Verify & score → [D] Correct → User
```

## Example

Input (one wrong year, one opinion):

> The Eiffel Tower is in Paris, and it was completed in 1899. It is about 330 metres tall.
> I think it is beautiful.

What the module does with it (real output of `check_answer()`):

| # | Claim | Verdict | Source |
|---|---|---|---|
| 1 | The Eiffel Tower is in Paris. | SUPPORTED (0.98) | Wikipedia: Eiffel Tower |
| 2 | The Eiffel Tower was completed in 1899. | **CONTRADICTED** (0.98) | Wikipedia: Eiffel Tower ("built the tower from 1887 to 1889") |
| 3 | The Eiffel Tower is about 330 metres tall. | SUPPORTED (0.93) | Wikipedia |

- The opinion "I think it is beautiful." is not a claim, so it is left alone.
- The compound first sentence became two claims, and "it" was replaced by "The Eiffel Tower".
- Trust score: **66.7 / 100**. The corrected answer tags each supported claim with its source and
  puts the Wikipedia evidence, marked `[corrected, source: …]`, next to the wrong year.

## Team

| Role | Feature | Member |
|---|---|---|
| A | Claim Extractor + Scrum Master | Sai Nikitha Perumalla |
| B | Evidence Retriever | Shreya Raghuraj |
| C | Verifier & Scorer | Ralph D'souza |
| D | Corrector & Integrator (API + UI) | Satwik |

## Setup

Requires Python 3.11 and an internet connection for the first run (spaCy model, NLI model and
Wikipedia). Without internet the retriever falls back to the local knowledge base in `data/kb/`.

```bash
git clone https://github.com/SoftwareEngineering-Runtime/dehallucinator.git
cd dehallucinator
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Check an answer from Python:

```python
from dehallucinator.pipeline import check_answer

result = check_answer("The Eiffel Tower was completed in 1899.")
print(result.trust_score)
print(result.corrected)
```

The first call downloads the NLI model (`cross-encoder/nli-deberta-v3-xsmall`)
and can take 30 s or more; later calls reuse the loaded models and the Wikipedia cache
(`data/wiki_cache.sqlite3`).

### Running the tests

```bash
ruff format --check . && ruff check .     # lint (line length 100)
pytest -m "not slow"                      # unit + integration tests, no internet needed
pytest --cov=src --cov-branch             # with coverage (target: 80%, currently 92%)
```

Unit tests mock the network and the NLI model, so they run offline in a few seconds.

## Project layout

```
src/dehallucinator/
  models.py              shared data models (Claim, Evidence, Verdict, CheckedAnswer)
  config.py              all thresholds and constants
  claims/extractor.py    [A] extract_claims(text)
  evidence/retriever.py  [B] retrieve_evidence(claims)
  evidence/ranker.py     [B] TF-IDF snippet ranking
  evidence/kb.py         [B] local knowledge base loader
  evidence/cache.py      [B] SQLite cache for Wikipedia pages
  verify/verifier.py     [C] verify_claims(claims, evidence), trust_score(verdicts)
  correct/corrector.py   [D] correct(text, claims, verdicts)
  pipeline.py            [D] check_answer(text)
  guard.py, api.py       [D] @dehallucinate decorator and FastAPI app
  ui_render.py           [D] HTML helpers for the demo UI
ui/app.py                [D] Streamlit demo chatbot
data/kb/                 15 trusted local documents (offline evidence)
data/samples.json        10 sample chatbot answers with planted mistakes
tests/                   unit, integration, system and security tests
docs/                    SRS, architecture, design, test plan, sprint logs, LLM prompt logs
```

## Claim Extractor (Role A)

`extract_claims(text) -> list[Claim]` in `src/dehallucinator/claims/extractor.py` turns an answer
into short, standalone facts that the retriever can search for and the verifier can check one at
a time. It uses spaCy (`en_core_web_sm`), loaded once and shared with the corrector so both number
sentences the same way.

| Step | What it does | Requirement |
|---|---|---|
| 1. Validate | Rejects empty or whitespace-only input and input over 5000 characters (`ValueError`) | FR-1.1 |
| 2. Split sentences | spaCy sentence boundaries, so "Dr." and "U.S." do not cause false splits | FR-1.2 |
| 3. Keep facts only | Drops questions, opinions ("I think", "maybe", "best", "should" …), sentences starting with I/We, and sentences under 4 words | FR-1.3 |
| 4. Split compounds | Splits at `;`, `, and`, `, but` only when both parts have their own subject and verb, so "Salt and pepper are spices." stays whole | FR-1.4 |
| 5. Replace pronouns | A leading He/She/His/Her uses the last person named, It/Its/They/Their the last thing; the sentence's subject wins ("It" after "The Eiffel Tower is in Paris." is the tower, not Paris) | FR-1.5 |
| 6. Remove duplicates | Ignores case, punctuation and spacing; keeps the first occurrence | FR-1.6 |
| 7. Number claims | `id` 1, 2, 3 … with no gaps; `sentence_index` is the original sentence, even for split claims, so the corrector can find where to put its tag | FR-1.7 |

```python
>>> from dehallucinator.claims.extractor import extract_claims
>>> [c.text for c in extract_claims(
...     "Einstein was born in 1879, and he won the Nobel Prize in 1921. Was he a genius? "
...     "Einstein was born in 1879!")]
['Einstein was born in 1879.', 'Einstein won the Nobel Prize in 1921.']
```

Tests: `tests/unit/test_extractor.py` (TC-1-01 to TC-1-10, 97% coverage). Design: class and
sequence diagrams in [`docs/design/extractor_design.md`](docs/design/extractor_design.md).

## Evidence Retriever (Role B)

_To be written by Shreya (DH-204)._

## Verifier & Scorer (Role C)

_To be written by Ralph (DH-205)._

## API, UI and deployment (Role D)

This part turns the four stages into something you can use: `check_answer()` runs them in order,
the Corrector rewrites the answer, and the result is available from Python, a REST API, a one-line
decorator for chatbots, and a demo UI.

| Piece | File | What it does | Requirement |
|---|---|---|---|
| Corrector | `src/dehallucinator/correct/corrector.py` | `correct(text, claims, verdicts)` rewrites the answer from the verdicts | FR-4.1 |
| Pipeline | `src/dehallucinator/pipeline.py` | `check_answer(text)` runs extract → retrieve → verify → score → correct and logs each stage's time | FR-4.2 |
| Decorator | `src/dehallucinator/guard.py` | `@dehallucinate` makes any function that returns a `str` return a `CheckedAnswer` | FR-4.3 |
| REST API | `src/dehallucinator/api.py` | FastAPI app with `POST /check` and `GET /health` | FR-4.4 |
| Demo UI | `ui/app.py`, `src/dehallucinator/ui_render.py` | Streamlit page with 10 sample answers, colour-coded claims and the corrected answer | FR-4.5, FR-4.6 |

How the Corrector rewrites each claim:

| Verdict | What happens |
|---|---|
| CONTRADICTED | Replaced by the evidence snippet + `[corrected, source: <url>]` |
| NOT_ENOUGH_INFO | Kept + `[unverified]` |
| SUPPORTED | Kept + `[source: <url>]` |

Text that is not a claim (greetings, opinions) is left as it is. If the Claim Extractor reworded a
claim (a replaced pronoun or a split compound), the tag goes at the end of that sentence.

Real output for "Mars is the fourth planet from the Sun. Mars has three natural satellites.":

> Mars is the fourth planet from the Sun. [source: https://en.wikipedia.org/wiki/Mars] Mars has two
> natural satellites that are small and irregular in shape: Phobos and Deimos. With a significant
> axial tilt of 25 degrees, Mars experiences seasons, like Earth (which has an axial tilt of 23.5
> degrees). [corrected, source: kb://mars.txt]

Trust score 50.0: one claim SUPPORTED, one CONTRADICTED by the local knowledge base.

Run the commands below from the repository root with `src` on the Python path:
`export PYTHONPATH=src` (Windows PowerShell: `$env:PYTHONPATH = "src"`).

### From Python

```python
from dehallucinator.pipeline import check_answer
from dehallucinator.guard import dehallucinate

result = check_answer("The Eiffel Tower was completed in 1899.")
print(result.trust_score, result.corrected)

@dehallucinate
def ask_bot(question: str) -> str:
    return my_llm(question)  # your chatbot

ask_bot("When was the Eiffel Tower built?")  # returns a CheckedAnswer
```

`check_answer` raises `ValueError` for empty input or input over 5000 characters; the decorator
raises `TypeError` if the function does not return a `str`.

### REST API

```bash
uvicorn dehallucinator.api:app --port 8000
curl http://localhost:8000/health
# {"status":"ok"}
curl -X POST http://localhost:8000/check -H "Content-Type: application/json" \
     -d '{"text": "Mars has three natural satellites."}'
```

| Status | When |
|---|---|
| 200 | Body is the `CheckedAnswer` (`original`, `corrected`, `claims`, `verdicts`, `trust_score`) |
| 422 | Missing, empty, blank or over-long `text`, wrong type, or malformed JSON |
| 500 | Unexpected error; the response says only `"Internal server error"`, the details go to the server log |

Interactive docs are at `http://localhost:8000/docs`. The full spec is
[`docs/design/openapi.json`](docs/design/openapi.json).

### Demo UI

```bash
streamlit run ui/app.py
```

Pick one of the 10 sample answers (8 with a planted mistake, 2 fully correct) or paste your own,
then press **Check**. The page shows the trust score, each claim in green (supported), red
(contradicted) or grey (unverified) with its evidence and source, and the corrected answer. All
answer text is HTML-escaped, so a `<script>` in the input is shown as text.

### Docker

```bash
docker build -t dehallucinator .
docker run --rm -p 8000:8000 dehallucinator          # API on http://localhost:8000
docker run --rm -p 8501:8501 dehallucinator \
    streamlit run ui/app.py --server.address=0.0.0.0 --server.port=8501   # UI on :8501
```

The image is `python:3.11-slim` with CPU-only PyTorch and the spaCy and NLI models already
downloaded, runs as a non-root user, and has a `HEALTHCHECK` on `/health`.

### CI/CD

Jenkins (on Role D's laptop) builds every branch with the [`Jenkinsfile`](Jenkinsfile):
Checkout → Setup → Lint (ruff) → Security scan (bandit, pip-audit) → Unit tests (fails below 80%
line + branch coverage; JUnit and HTML coverage reports) → Integration tests → Build image →
Deploy. The last two run on `main` only: the new container replaces the old one and Jenkins waits
for `/health` to answer.

Tests: `tests/unit/test_corrector.py`, `test_pipeline.py`, `test_api.py`, `test_guard.py` and
`test_ui.py` (TC-4-01 to TC-4-10; 94–100% coverage per module). Design:
[`docs/design/design_corrector_pipeline_api.md`](docs/design/design_corrector_pipeline_api.md);
architecture: [`docs/architecture/architecture_api_ui_deployment.md`](docs/architecture/architecture_api_ui_deployment.md).

## Workflow

- Work is tracked in Jira (project key `DH`); one branch per story: `feature/DH-<n>-<short-name>`.
- Commit messages start with the Jira key, e.g. `DH-151 add shared data models`.
- `main` is protected: open a pull request, get one approval, merge with a merge commit.
- Before every commit: `ruff format . && ruff check . && pytest -m "not slow"`.
