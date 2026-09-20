# dehallucinator

Dehallucination add-on module for AI chatbots – SE mini-project (Project 39), UE24CS341A, PES University.

The module sits between a chatbot and the user. It splits the chatbot's answer into factual claims,
finds evidence for each claim in trusted sources (Wikipedia and local documents), labels each claim
as supported, contradicted or unverified, and returns a corrected answer with a trust score.

```
Chatbot answer → [A] Extract claims → [B] Find evidence → [C] Verify & score → [D] Correct → User
```

## Team

| Role | Feature | Member |
|---|---|---|
| A | Claim Extractor + Scrum Master | Sai Nikitha Perumalla |
| B | Evidence Retriever | Shreya |
| C | Verifier & Scorer | Ralph |
| D | Corrector & Integrator (API + UI) | Satwik |

## Setup

Requires Python 3.11.

```bash
git clone https://github.com/SoftwareEngineering-Runtime/dehallucinator.git
cd dehallucinator
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
pytest
```

## Project layout

```
src/dehallucinator/
  models.py              shared data models (Claim, Evidence, Verdict, CheckedAnswer)
  config.py              all thresholds and constants
  claims/extractor.py    [A] extract_claims(text)
  evidence/retriever.py  [B] retrieve_evidence(claims)
  verify/verifier.py     [C] verify_claims(claims, evidence), trust_score(verdicts)
  correct/corrector.py   [D] correct(text, claims, verdicts)
  pipeline.py            [D] check_answer(text)
  guard.py, api.py       [D] chatbot decorator and FastAPI app
ui/app.py                [D] Streamlit demo chatbot
tests/                   unit, integration, system and security tests
docs/                    sprint logs, LLM prompt logs, final documents
```

## Workflow

- Work is tracked in Jira (project key `DH`); one branch per story: `feature/DH-<n>-<short-name>`.
- Commit messages start with the Jira key, e.g. `DH-151 add shared data models`.
- `main` is protected: open a pull request, get one approval, merge with a merge commit.
- Before every commit: `ruff format . && ruff check . && pytest -m "not slow"`.
