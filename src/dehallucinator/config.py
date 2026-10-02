"""All tunable numbers live here (manual Section 4.4).

Each owner edits only their own lines.
"""

# Claim Extractor (A) / API (D)
MAX_INPUT_CHARS = 5000
MIN_CLAIM_WORDS = 4

# Evidence Retriever (B)
WIKI_TOP_PAGES = 3
EVIDENCE_PER_CLAIM = 3
HTTP_TIMEOUT_S = 5
HTTP_RETRIES = 2
CACHE_TTL_DAYS = 7

# Verifier (C)
NLI_MODEL = "cross-encoder/nli-deberta-v3-xsmall"
SUPPORT_THRESHOLD = 0.70
CONTRADICT_THRESHOLD = 0.70
