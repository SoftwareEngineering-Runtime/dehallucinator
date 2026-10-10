"""Tests for the Claim Extractor (Role A)."""

import pytest

from dehallucinator.claims.extractor import (
    extract_claims,
    is_factual,
    split_sentences,
    validate_input,
)
from dehallucinator.config import MAX_INPUT_CHARS


@pytest.mark.parametrize("text", ["", "   \n\t  "])
def test_tc_1_01_empty_input_is_rejected(text):
    with pytest.raises(ValueError, match="empty"):
        extract_claims(text)


def test_tc_1_02_input_over_limit_is_rejected():
    with pytest.raises(ValueError, match=str(MAX_INPUT_CHARS)):
        extract_claims("a" * (MAX_INPUT_CHARS + 1))


def test_input_exactly_at_limit_is_accepted():
    text = "a" * MAX_INPUT_CHARS
    assert validate_input(text) == text


def test_validate_input_strips_surrounding_whitespace():
    assert validate_input("  Paris is in France.  ") == "Paris is in France."


def test_tc_1_03_splits_two_sentences():
    claims = extract_claims("Paris is in France. It is a large city.")
    assert [c.text for c in claims] == ["Paris is in France.", "It is a large city."]


def test_abbreviations_do_not_cause_false_splits():
    sentences = split_sentences("Dr. Smith moved to the U.S. in 1990. He works at NASA.")
    assert len(sentences) == 2


def test_claims_are_numbered_from_one_with_sentence_index():
    claims = extract_claims("Mars is a planet. Jupiter is the largest planet. Venus is very hot.")
    assert [c.id for c in claims] == [1, 2, 3]
    assert [c.sentence_index for c in claims] == [0, 1, 2]


def test_single_sentence_without_full_stop():
    claims = extract_claims("The Eiffel Tower is in Paris")
    assert len(claims) == 1
    assert claims[0].text == "The Eiffel Tower is in Paris"


def test_tc_1_04_questions_are_dropped():
    claims = extract_claims("Paris is the capital of France. Is it the largest city?")
    assert [c.text for c in claims] == ["Paris is the capital of France."]


@pytest.mark.parametrize(
    "sentence",
    [
        "I think Paris is the most beautiful city.",
        "In my opinion the Eiffel Tower is overrated.",
        "Maybe the tower was built in 1889.",
        "Everyone should visit Paris at least once.",
        "This is probably the oldest bridge in Paris.",
    ],
)
def test_tc_1_05_opinion_sentences_are_dropped(sentence):
    assert not is_factual(sentence)


def test_opinion_markers_ignore_case():
    assert not is_factual("PERHAPS the tower is 330 metres tall.")


def test_opinion_marker_must_be_a_whole_word():
    # "shoulder" contains "should" but is not an opinion marker.
    assert is_factual("The statue has a broken shoulder and arm.")


@pytest.mark.parametrize("sentence", ["I visited Paris in 2019.", "We studied the tower in class."])
def test_first_person_sentences_are_dropped(sentence):
    assert not is_factual(sentence)


def test_tc_1_06_short_sentences_are_dropped():
    assert not is_factual("Paris is big.")
    assert is_factual("Paris is very big.")


def test_ids_have_no_gaps_and_keep_original_sentence_index():
    text = "Mars is the fourth planet. Is that right? Jupiter is the largest planet."
    claims = extract_claims(text)
    assert [c.id for c in claims] == [1, 2]
    assert [c.sentence_index for c in claims] == [0, 2]


def test_all_sentences_non_factual_returns_empty_list():
    assert extract_claims("I think this is great. Why not?") == []
