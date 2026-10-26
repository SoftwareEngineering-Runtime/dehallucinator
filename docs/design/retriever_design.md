# Evidence Retriever: Design (DH-189)

Module: `src/dehallucinator/evidence/` (`retriever.py`, `ranker.py`, `kb.py`, `cache.py`).
Requirements covered: FR-2.1 to FR-2.8.

## Class diagram

The retriever is built from functions grouped in modules, so each module is shown
as a class with the `<<module>>` stereotype.

```mermaid
classDiagram
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
    class retriever {
        <<module>>
        +retrieve_evidence(claims) list~Evidence~
        +build_query(claim_text) str
        +search_wikipedia(query) list~str~
        +fetch_page_text(title) dict
        -_wiki_get(params) dict
        +page_url(title) str
    }
    class ranker {
        <<module>>
        +rank_snippets(claim_text, pages, top_n) list~dict~
        +make_snippets(text) list~str~
        +split_sentences(text) list~str~
    }
    class kb {
        <<module>>
        +load_kb_pages(kb_dir) list~dict~
    }
    class cache {
        <<module>>
        +get_cached_page(title) dict
        +put_cached_page(title, page) None
    }
    class WikipediaAPI {
        <<external>>
    }
    class SQLite {
        <<external>>
        wiki_cache.sqlite3
    }
    class KBFiles {
        <<external>>
        data/kb/*.txt
    }

    retriever ..> Claim : reads
    retriever ..> Evidence : creates
    retriever --> ranker : ranks snippets
    retriever --> kb : loads local pages
    retriever --> cache : reads and writes pages
    retriever --> WikipediaAPI : HTTP GET with retries
    cache --> SQLite : parameterised queries
    kb --> KBFiles : reads once, then cached in memory
```

## Sequence diagram: retrieve_evidence()

```mermaid
sequenceDiagram
    participant P as Pipeline
    participant R as retriever
    participant C as cache
    participant W as Wikipedia API
    participant K as kb
    participant K2 as ranker

    P->>R: retrieve_evidence(claims)
    loop for each claim
        R->>R: build_query(claim.text) [spaCy]
        R->>W: search_wikipedia(query) [top WIKI_TOP_PAGES titles]
        alt request fails (timeout, 429, 5xx)
            W--xR: error, retry up to HTTP_RETRIES, log warning
            Note over R: after retries, no Wikipedia pages (local KB only)
        else request ok
            W-->>R: page titles
        end
        loop for each title
            R->>C: get_cached_page(title)
            alt cached and younger than CACHE_TTL_DAYS
                C-->>R: page
            else miss or expired
                R->>W: fetch_page_text(title)
                W-->>R: page text
                R->>C: put_cached_page(title, page)
            end
        end
        R->>K: load_kb_pages()
        K-->>R: KB pages (source local_kb)
        R->>K2: rank_snippets(claim.text, all pages)
        K2-->>R: top snippets with relevance 0 to 1
        R->>R: build Evidence (source wikipedia or local_kb)
    end
    R-->>P: list of Evidence (empty for a claim with no usable snippet)
```
