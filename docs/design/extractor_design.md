# Claim Extractor: Design (DH-188)

Module: `src/dehallucinator/claims/extractor.py`.
Requirements covered: FR-1.1 to FR-1.7.

## Class diagram

The extractor is mostly functions in one module, so the module is shown as a class
with the `<<module>>` stereotype. `EntityMemory` is a real class: it remembers the last
person and the last thing named, for pronoun replacement.

```mermaid
classDiagram
    class Claim {
        +int id
        +str text
        +int sentence_index
    }
    class extractor {
        <<module>>
        +extract_claims(text) list~Claim~
        +validate_input(text) str
        +split_sentences(text) list~str~
        +is_factual(sentence) bool
        +split_compound(sentence) list~str~
        +has_subject_and_verb(text) bool
        +replace_leading_pronoun(claim, memory) str
        +normalise(claim) str
        +get_nlp() Language
    }
    class EntityMemory {
        +str person
        +str thing
        +update(text) None
    }
    class config {
        <<module>>
        MAX_INPUT_CHARS = 5000
        MIN_CLAIM_WORDS = 4
    }
    class spaCy {
        <<external>>
        en_core_web_sm
    }

    extractor ..> Claim : creates
    extractor --> EntityMemory : one per call
    extractor --> config : limits
    extractor --> spaCy : sentences, parse, entities (loaded once)
    EntityMemory --> spaCy : named entities
```

## Sequence diagram: extract_claims()

```mermaid
sequenceDiagram
    participant P as Pipeline
    participant E as extractor
    participant S as spaCy
    participant M as EntityMemory

    P->>E: extract_claims(text)
    E->>E: validate_input(text)
    alt empty or over MAX_INPUT_CHARS
        E--xP: ValueError
    end
    E->>S: split_sentences(text)
    S-->>E: sentences
    loop for each sentence (index i)
        E->>E: is_factual(sentence)
        alt question, opinion, I/We, or under MIN_CLAIM_WORDS
            E->>M: update(sentence)
            Note over E: sentence dropped, but its entities are remembered
        else factual
            E->>S: split_compound(sentence) [subject + verb check per part]
            S-->>E: parts
            loop for each part
                E->>M: replace_leading_pronoun(part)
                M-->>E: part with He/She/It/They replaced
                E->>M: update(part)
                E->>E: normalise(part), skip if already seen
                E->>E: Claim(id = next id, text = part, sentence_index = i)
            end
        end
    end
    E-->>P: list of Claim (ids 1, 2, 3 ... with no gaps)
```

## Design decisions

| Decision | Reason |
|---|---|
| spaCy model loaded once with `lru_cache` | Loading takes about a second; the corrector reuses the same model, so sentence numbers match. |
| A compound sentence is split only when both parts have a subject and a verb | Keeps lists like "Salt and pepper are spices." as one claim (FR-1.4). |
| The subject of a sentence wins over other entities in `EntityMemory` | In "The Eiffel Tower is in Paris. It is 330 m tall.", "It" means the tower, not Paris (FR-1.5). |
| He/She look up people only; It/They look up things only | In "Apple was founded by Steve Jobs.", "It" is Apple and "He" is Steve Jobs. |
| De-duplication runs after pronoun replacement | "It is in Paris." is caught as a repeat of "The Eiffel Tower is in Paris." (FR-1.6). |
| `sentence_index` is the original sentence, even for split claims | The corrector uses it to find where to put the tag in the answer. |
