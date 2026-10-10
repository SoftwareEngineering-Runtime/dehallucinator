# LLM prompt log – Role A (Sai Nikitha Perumalla)

## DH-151 project skeleton – 2026-09-19
Tool: Claude
Prompt: "Create the project skeleton from manual Section 4: folder layout, pydantic models for
Claim, Evidence, Verdict and CheckedAnswer, config constants, stub functions for each role,
and one skipped placeholder test per test file."
What I kept: folder layout, models.py, config.py, stubs, model tests
What I changed: added pyproject.toml settings and README team table
I can explain it: yes

## DH-161 input validation + sentence splitting – 2026-10-06
Tool: Claude
Prompt: "Implement extract_claims for FR-1.1 and FR-1.2: reject empty or >5000-char input
with ValueError, split sentences with spaCy en_core_web_sm loaded only once, and return
numbered Claim objects. Write tests TC-1-01 to TC-1-03 plus edge cases."
What I kept: validate_input, split_sentences, get_nlp with lru_cache, the tests
What I changed: replaced a nested enumerate with a plain loop so the numbering is easier
to read and still works once DH-162 starts dropping sentences
I can explain it: yes

## DH-162 non-factual sentence filter – 2026-10-10
Tool: Claude
Prompt: "Add is_factual() for FR-1.3: drop questions, sentences containing an opinion marker
(whole words, any case), sentences starting with I/We, and sentences shorter than
MIN_CLAIM_WORDS. Keep claim IDs gap-free but keep the original sentence_index.
Write tests TC-1-04 to TC-1-06 plus edge cases."
What I kept: is_factual, OPINION_PATTERN regex, the tests
What I changed: used a \b word-boundary regex so "shoulder" is not treated as "should"
I can explain it: yes
