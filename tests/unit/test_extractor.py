"""Tests for the Claim Extractor (Role A)."""

import pytest

from dehallucinator.claims.extractor import (
    EntityMemory,
    extract_claims,
    is_factual,
    normalise,
    replace_leading_pronoun,
    split_compound,
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
    assert [c.text for c in claims] == ["Paris is in France.", "Paris is a large city."]


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


def test_tc_1_07_compound_sentence_is_split():
    claims = extract_claims("Einstein was born in 1879, and he won the Nobel Prize in 1921.")
    assert [c.text for c in claims] == [
        "Einstein was born in 1879.",
        "Einstein won the Nobel Prize in 1921.",
    ]
    assert [c.sentence_index for c in claims] == [0, 0]


def test_list_with_and_is_not_split():
    assert split_compound("Salt and pepper are spices.") == ["Salt and pepper are spices."]
    assert split_compound("Oxygen, carbon, and nitrogen are elements.") == [
        "Oxygen, carbon, and nitrogen are elements."
    ]


def test_part_without_its_own_subject_is_not_split():
    assert split_compound("The tower was old, but strong.") == ["The tower was old, but strong."]


@pytest.mark.parametrize(
    ("sentence", "parts"),
    [
        (
            "Paris is in France; Berlin is in Germany.",
            ["Paris is in France.", "Berlin is in Germany."],
        ),
        (
            "Rome is very old, but Paris is older, and Berlin is new.",
            ["Rome is very old.", "Paris is older.", "Berlin is new."],
        ),
    ],
)
def test_semicolon_and_multiple_split_points(sentence, parts):
    assert split_compound(sentence) == parts


def test_tc_1_08_leading_pronoun_is_replaced():
    claims = extract_claims("The Eiffel Tower is in Paris. It is 330 m tall.")
    assert [c.text for c in claims] == [
        "The Eiffel Tower is in Paris.",
        "The Eiffel Tower is 330 m tall.",
    ]


def test_person_and_possessive_pronouns_use_the_last_person():
    text = (
        "Marie Curie moved to Paris in 1891. She won two Nobel Prizes. "
        "Her husband was Pierre Curie."
    )
    assert [c.text for c in extract_claims(text)] == [
        "Marie Curie moved to Paris in 1891.",
        "Marie Curie won two Nobel Prizes.",
        "Marie Curie's husband was Pierre Curie.",
    ]


def test_it_and_he_pick_different_entities():
    text = "Apple was founded by Steve Jobs in 1976. It is based in Cupertino. He died in 2011."
    assert [c.text for c in extract_claims(text)][1:] == [
        "Apple is based in Cupertino.",
        "Steve Jobs died in 2011.",
    ]


def test_pronoun_without_earlier_entity_is_kept():
    assert replace_leading_pronoun("It is raining heavily today.", EntityMemory()) == (
        "It is raining heavily today."
    )


def test_pronoun_inside_a_word_is_not_replaced():
    memory = EntityMemory()
    memory.update("Paris is in France.")
    assert replace_leading_pronoun("Items are sold in Paris.", memory) == "Items are sold in Paris."


def test_tc_1_09_duplicate_claims_are_removed():
    claims = extract_claims("Paris is in France. paris is in France!")
    assert [c.text for c in claims] == ["Paris is in France."]
    assert [(c.id, c.sentence_index) for c in claims] == [(1, 0)]


def test_ids_have_no_gaps_after_duplicates_are_removed():
    text = "Mars is a red planet. Venus is very hot. Mars is a red planet. Jupiter is the largest."
    claims = extract_claims(text)
    assert [c.id for c in claims] == [1, 2, 3]
    assert [c.sentence_index for c in claims] == [0, 1, 3]


def test_duplicate_found_after_pronoun_replacement():
    claims = extract_claims("The Eiffel Tower is in Paris. It is in Paris.")
    assert [c.text for c in claims] == ["The Eiffel Tower is in Paris."]


def test_normalise_ignores_case_punctuation_and_spaces():
    assert normalise("  Paris,  is in FRANCE!! ") == "paris is in france"
