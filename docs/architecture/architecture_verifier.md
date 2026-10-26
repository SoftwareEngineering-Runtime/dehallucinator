# Architecture — Verifier & Scorer (Role C)

## Purpose

The Verifier & Scorer evaluates each claim against its retrieved evidence using a Natural Language Inference (NLI) model. It assigns a verdict (`SUPPORTED`, `CONTRADICTED`, or `NOT_ENOUGH_INFO`) and a confidence score. The `trust_score()` function calculates an overall trust score from the verdicts.

## UML Class Diagram

```mermaid
classDiagram
    class VerifierModule {
        +verify_claims(claims, evidence) list~Verdict~
        +trust_score(verdicts) float
        -_load_model() tuple
        -_predict(pairs) list
    }

    class Claim {
        +int id
        +str text
        +int sentence_index
    }

    class Evidence {
        +int claim_id
        +str source
        +str source_url
        +str title
        +str snippet
        +float relevance
    }

    class Verdict {
        +int claim_id
        +Label label
        +float score
        +Evidence best_evidence
    }

    VerifierModule ..> Claim : reads
    VerifierModule ..> Evidence : evaluates
    VerifierModule ..> Verdict : creates
    Verdict o-- Evidence : optional best_evidence
```

*Note: `VerifierModule` represents the module-level functions in `verifier.py`, not a Python class.*

## UML Sequence Diagram — `verify_claims()`

```mermaid
sequenceDiagram
    participant Pipeline
    participant Verifier as Verifier Module
    participant Model as NLI Model

    Pipeline->>Verifier: verify_claim