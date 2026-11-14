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
pip install -e .                   # installs the dehallucinator package itself (from src/)
python -m spacy download en_core_web_sm
```

Without `pip install -e .`, `import dehallucinator` fails with "No module named dehallucinator"
outside pytest (pytest finds `src/` through `pyproject.toml`).

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
pytest --cov=src --cov-branch             # with coverage (target: 80% per module, currently 94%)
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

_To be written by Satwik (DH-206)._

## Workflow

- Work is tracked in Jira (project key `DH`); one branch per story: `feature/DH-<n>-<short-name>`.
- Commit messages start with the Jira key, e.g. `DH-151 add shared data models`.
- `main` is protected: open a pull request, get one approval, merge with a merge commit.
- Before every commit: `ruff format . && ruff check . && pytest -m "not slow"`.
