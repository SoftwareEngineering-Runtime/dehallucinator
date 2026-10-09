"""Tests for the Evidence Retriever (Role B)."""

import pytest
from spacy.lang.en.stop_words import STOP_WORDS

from dehallucinator.evidence.retriever import MAX_QUERY_WORDS, build_query


def test_tc_2_01_entities_come_before_noun_chunks():
    query = build_query("The famous bridge was designed by Gustave Eiffel in Paris.")
    words = query.split()
    assert "Gustave" in words and "Paris" in words
    if "bridge" in words:
        assert words.index("Gustave") < words.index("bridge")
        assert words.index("Paris") < words.index("bridge")


def test_tc_2_02_stop_words_removed_and_capped_at_8_words():
    claim = (
        "The history of the ancient Roman Empire and its many emperors, generals, "
        "senators, architects, and engineers is often studied by modern historians "
        "in universities around Europe."
    )
    words = build_query(claim).split()
    assert 0 < len(words) <= MAX_QUERY_WORDS
    assert not any(w.lower() in STOP_WORDS for w in words)


@pytest.mark.parametrize("empty", ["", "   ", None])
def test_empty_claim_returns_empty_query(empty):
    assert build_query(empty) == ""
