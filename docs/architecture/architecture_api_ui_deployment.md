# Architecture: API, UI and Deployment (Role D)

Owner: Satwik (Role D). Section 4 of the Architecture Document.

## 1. Purpose
Connects the four pipeline stages into one call and makes it usable from outside: a REST API
for any application, a decorator for Python chatbots, and a demo UI for end users. Also covers
how the system is built, tested and deployed. Requirements: FR-4.1 to FR-4.6, NFR-3, NFR-5.

## 2. Components

```mermaid
flowchart LR
    user([End user]) --> ui[Streamlit demo UI<br/>ui/app.py]
    client([Any app / chatbot]) -->|HTTP JSON| api[FastAPI app<br/>api.py]
    bot([Python chatbot]) --> guard["@dehallucinate<br/>guard.py"]
    ui --> pipe
    api --> pipe
    guard --> pipe
    subgraph core [Core pipeline]
        pipe["check_answer()<br/>pipeline.py"]
        pipe --> A[Claim Extractor<br/>Role A]
        pipe --> B[Evidence Retriever<br/>Role B]
        pipe --> C[Verifier & Scorer<br/>Role C]
        pipe --> D[Corrector<br/>corrector.py]
    end
```

*Figure 4.1: Entry points (UI, API, decorator) and how they reach the core pipeline.*

| Component | Module | Responsibility | Requirement | Status |
|---|---|---|---|---|
| Corrector | `correct/corrector.py` `correct` | Rewrites the answer from the verdicts: CONTRADICTED claims replaced by the evidence and its source, NOT_ENOUGH_INFO tagged `[unverified]`, SUPPORTED tagged with the source | FR-4.1 | Sprint 1 |
| Pipeline | `pipeline.py` `check_answer` | Runs extract → retrieve → verify → score → correct, logs each stage's time, returns a `CheckedAnswer` | FR-4.2 | Sprint 1 |
| REST API | `api.py` `app` | `POST /check` and `GET /health`; validates input; maps errors to HTTP status codes | FR-4.4, NFR-3 | Sprint 1 |
| Decorator | `guard.py` `dehallucinate` | Wraps any function that returns a `str` so it returns a `CheckedAnswer` | FR-4.3 | Sprint 2 |
| Demo UI | `ui/app.py` | Sample drop-down and paste box; colour-coded claims, sources, trust score and corrected answer | FR-4.5, FR-4.6 | Sprint 2 |

The API, the UI and the decorator all call the same `check_answer()`, so every entry point
gives the same result and the pipeline is tested once.

## 3. Interfaces

**Pipeline:** `check_answer(text: str) -> CheckedAnswer`, where
`CheckedAnswer = {original, corrected, claims, verdicts, trust_score}` (defined in `models.py`).
Raises `ValueError` for empty input or input over `MAX_INPUT_CHARS` (5000).

**Corrector:** `correct(text: str, claims: list[Claim], verdicts: list[Verdict]) -> str`.
It splits sentences with the Claim Extractor's own spaCy model and skips whitespace-only
sentences in the same way, so a claim's `sentence_index` points at the same sentence in both modules.

**REST API** (served with `uvicorn dehallucinator.api:app`):

| Endpoint | Request | Responses |
|---|---|---|
| `POST /check` | `{"text": "<AI answer>"}`; 1 to 5000 characters, not blank | 200: `CheckedAnswer` JSON. 422: invalid or malformed input. 500: `{"detail": "Internal server error"}` |
| `GET /health` | none | 200: `{"status": "ok"}` |

Request flow for `POST /check`:

```mermaid
sequenceDiagram
    participant Client
    participant API as FastAPI /check
    participant P as check_answer()
    participant S as Stages A, B, C
    participant D as correct()
    Client->>API: POST {"text": ...}
    API->>API: validate (1–5000 chars, not blank)
    alt invalid input
        API-->>Client: 422
    else valid
        API->>P: check_answer(text)
        P->>S: extract, retrieve, verify, score
        S-->>P: claims, evidence, verdicts, trust score
        P->>D: correct(text, claims, verdicts)
        D-->>P: corrected text
        P-->>API: CheckedAnswer
        API-->>Client: 200 CheckedAnswer JSON
    end
```

*Figure 4.2: Request flow for `POST /check`.*

## 4. Dependencies

| Dependency | Used for |
|---|---|
| FastAPI + pydantic | REST API, request validation, JSON responses from the shared models |
| uvicorn | ASGI server that runs the API |
| Streamlit | Demo UI |
| spaCy `en_core_web_sm` | Sentence spans in the Corrector (shared with the Claim Extractor) |
| Modules A, B, C | `extract_claims`, `retrieve_evidence`, `verify_claims`, `trust_score` |
| `dehallucinator.config` | `MAX_INPUT_CHARS` |

## 5. Error handling

| Situation | Behaviour |
|---|---|
| Missing, empty, blank, wrong-type or over-long `text`, or malformed JSON | 422; the pipeline is not called |
| `ValueError` from the pipeline | 422 with the error message |
| Any other exception | Logged with its stack trace on the server; the client gets 500 with a generic message and no stack trace (NFR-3) |
| No factual claims | Retriever and Verifier are skipped; the corrected answer equals the original and the trust score is 100 |
| No evidence for a claim | The Verifier returns NOT_ENOUGH_INFO (FR-3.4) and the Corrector tags the claim `[unverified]` |

The `/check` endpoint is a plain `def`, so FastAPI runs the CPU-heavy pipeline in a worker
thread and `/health` stays responsive while a check is running.

## 6. Deployment view

```mermaid
flowchart LR
    dev([Developer]) -->|push branch, open PR| gh[(GitHub<br/>SoftwareEngineering-Runtime/dehallucinator)]
    gh -->|automatic analysis| sq[SonarQube Cloud]
    subgraph laptop [Role D laptop]
        jenkins[Jenkins LTS<br/>Multibranch Pipeline]
        subgraph docker [Docker]
            app[dehallucinator container<br/>uvicorn :8000]
        end
    end
    jenkins -->|scan every 2 min| gh
    jenkins -->|main only: build image and deploy| docker
    jenkins -->|GET /health| app
    app -->|HTTPS| wiki[(Wikipedia API)]
```

*Figure 4.3: Deployment view. Jenkins and the container run on Role D's laptop.*

- **Source control:** GitHub. `main` is protected; every change is a pull request with one
  approval. Commits start with the Jira key so they appear on the ticket.
- **CI (Jenkins):** a Multibranch Pipeline job scans the repository every 2 minutes and builds
  every branch that has a `Jenkinsfile`. Current stages (DH-153): Checkout, Setup, Lint
  (ruff), Unit tests (pytest, JUnit report). Planned for Sprint 2 (DH-180, DH-182, manual
  11.4): the full 8-stage pipeline with a security scan (bandit, pip-audit), coverage gate at
  80%, coverage report, and, on `main` only, a Docker image build, deploy and `/health` check.
- **Container (DH-181, planned):** a Docker image with Python 3.11, the dependencies, the
  spaCy model and the API, started with one command (NFR-5). Docker runs the container's
  health check against `GET /health`.
- **Code quality:** SonarQube Cloud analyses every push (DH-154, DH-183).
- **External service:** the running container needs HTTPS access to Wikipedia; without it the
  Retriever falls back to the local KB baked into the image (FR-2.7).

## 7. Testing

| Level | Tests | Notes |
|---|---|---|
| Unit | `tests/unit/test_corrector.py` (TC-4-01 to TC-4-05), `test_pipeline.py`, `test_api.py` (TC-4-06 to TC-4-09) | Stages and `check_answer` are faked, so no network or model is used |
| Integration | `tests/integration/test_pipeline.py` (Role C, DH-197) | Full `check_answer` with mocks |
| System | `tests/system/test_end_to_end.py` (DH-198) | API with the 10 sample answers |
| Security | `tests/security/test_security.py` (DH-199) | Input limits, malformed JSON, script input |
