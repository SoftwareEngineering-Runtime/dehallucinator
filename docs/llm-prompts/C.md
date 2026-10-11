# LLM prompt log — Role C (Verifier \& Scorer)



## DH-173 trust score calculation — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement trust\_score to calculate an overall trust score from verdict labels, mapping SUPPORTED to 1.0, NOT\_ENOUGH\_INFO to 0.5, and CONTRADICTED to 0.0, and returning a score from 0 to 100."

What I kept: The label-to-score mapping, averaging logic, and conversion to a 0–100 score.

What I changed: Added unit tests for empty, fully supported, fully contradicted, and mixed verdict lists.

I can explain it: yes



## DH-171 NLI model lazy loading — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement lazy loading for the NLI tokenizer and sequence classification model using the existing config.NLI\_MODEL setting."

What I kept: The module-level tokenizer and model variables and the lazy-loading logic in \_load\_model().

What I changed: Sorted imports and applied Ruff formatting.

I can explain it: yes



## DH-172 claim verification and mocked tests — 2026-10-10



Tool: ChatGPT

Prompt: "Help me implement verify\_claims using NLI probabilities from the model's id2label mapping, and add mocked tests for supported, contradicted, not-enough-info, evidence filtering, and lazy model loading."

What I kept: The claim-to-evidence matching, threshold-based verdict selection, confidence scoring, and use of model.config.id2label.

What I changed: Added mocked tests for verdict outcomes, evidence filtering, and lazy model loading; ran pytest coverage and Ruff checks.

I can explain it: yes

