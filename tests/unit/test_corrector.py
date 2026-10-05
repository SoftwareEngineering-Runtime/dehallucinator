"""Tests for the Corrector (Role D)."""

from dehallucinator.correct.corrector import UNVERIFIED_TAG, correct
from dehallucinator.models import Claim, Evidence, Verdict

EIFFEL_URL = "https://en.wikipedia.org/wiki/Eiffel_Tower"


def make_evidence(claim_id: int, snippet: str, url: str = EIFFEL_URL) -> Evidence:
    return Evidence(
        claim_id=claim_id,
        source="wikipedia",
        source_url=url,
        title="Eiffel Tower",
        snippet=snippet,
        relevance=0.9,
    )


def make_verdict(claim_id: int, label: str, evidence: Evidence | None = None) -> Verdict:
    return Verdict(claim_id=claim_id, label=label, score=0.9, best_evidence=evidence)


def test_tc_4_01_contradicted_claim_is_replaced_with_correction_and_source():
    text = "The Eiffel Tower was completed in 1899."
    claims = [Claim(id=1, text=text, sentence_index=0)]
    evidence = make_evidence(1, "The Eiffel Tower was completed in 1889.")
    verdicts = [make_verdict(1, "CONTRADICTED", evidence)]

    result = correct(text, claims, verdicts)

    assert result == (f"The Eiffel Tower was completed in 1889. [corrected, source: {EIFFEL_URL}]")
    assert "1899" not in result


def test_tc_4_02_not_enough_info_claim_is_tagged_unverified():
    text = "The Eiffel Tower has 1,710 steps."
    claims = [Claim(id=1, text=text, sentence_index=0)]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO")]

    assert correct(text, claims, verdicts) == f"{text} {UNVERIFIED_TAG}"


def test_tc_4_03_supported_claim_is_tagged_with_its_source():
    text = "The Eiffel Tower is located in Paris."
    claims = [Claim(id=1, text=text, sentence_index=0)]
    evidence = make_evidence(1, "The Eiffel Tower is on the Champ de Mars in Paris.")
    verdicts = [make_verdict(1, "SUPPORTED", evidence)]

    assert correct(text, claims, verdicts) == f"{text} [source: {EIFFEL_URL}]"


def test_tc_4_04_mixed_answer_keeps_non_claim_text_unchanged():
    text = (
        "Hello! The Eiffel Tower was completed in 1899. "
        "I hope this helps. The Eiffel Tower is located in Paris."
    )
    claims = [
        Claim(id=1, text="The Eiffel Tower was completed in 1899.", sentence_index=1),
        Claim(id=2, text="The Eiffel Tower is located in Paris.", sentence_index=3),
    ]
    verdicts = [
        make_verdict(1, "CONTRADICTED", make_evidence(1, "It was completed in 1889.")),
        make_verdict(2, "SUPPORTED", make_evidence(2, "It is in Paris.")),
    ]

    result = correct(text, claims, verdicts)

    assert result == (
        f"Hello! It was completed in 1889. [corrected, source: {EIFFEL_URL}] "
        f"I hope this helps. The Eiffel Tower is located in Paris. [source: {EIFFEL_URL}]"
    )


def test_tc_4_05_contradicted_without_evidence_and_missing_verdict_are_unverified():
    text = "Mars has two moons. Mars is the largest planet."
    claims = [
        Claim(id=1, text="Mars has two moons.", sentence_index=0),
        Claim(id=2, text="Mars is the largest planet.", sentence_index=1),
    ]
    verdicts = [make_verdict(1, "CONTRADICTED", evidence=None)]  # no verdict for claim 2

    assert correct(text, claims, verdicts) == (
        f"Mars has two moons. {UNVERIFIED_TAG} Mars is the largest planet. {UNVERIFIED_TAG}"
    )


def test_no_claims_returns_text_unchanged():
    assert correct("Hi there, how can I help?", [], []) == "Hi there, how can I help?"


def test_claim_is_found_case_insensitively_and_without_final_full_stop():
    text = "Paris is the capital of France and its largest city."
    claims = [Claim(id=1, text="paris is the capital of France.", sentence_index=0)]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO")]

    assert correct(text, claims, verdicts) == (
        f"Paris is the capital of France {UNVERIFIED_TAG} and its largest city."
    )


def test_reworded_claim_alone_in_its_sentence_replaces_the_whole_sentence():
    text = "Albert Einstein was a physicist. He was born in 1900."
    claims = [Claim(id=1, text="Albert Einstein was born in 1900.", sentence_index=1)]
    evidence = make_evidence(1, "Einstein was born on 14 March 1879.", url="kb://einstein.txt")
    verdicts = [make_verdict(1, "CONTRADICTED", evidence)]

    assert correct(text, claims, verdicts) == (
        "Albert Einstein was a physicist. "
        "Einstein was born on 14 March 1879. [corrected, source: kb://einstein.txt]"
    )


def test_reworded_claims_sharing_a_sentence_get_tags_at_the_sentence_end():
    text = "Jupiter is the largest planet; it has 3 moons. Mars is red."
    claims = [
        Claim(id=1, text="Jupiter is the largest planet.", sentence_index=0),
        Claim(id=2, text="Jupiter has 3 moons.", sentence_index=0),
    ]
    verdicts = [
        make_verdict(1, "SUPPORTED", make_evidence(1, "Jupiter is the largest.", "kb://j.txt")),
        make_verdict(2, "CONTRADICTED", make_evidence(2, "Jupiter has 95 moons.", "kb://j.txt")),
    ]

    assert correct(text, claims, verdicts) == (
        "Jupiter is the largest planet [source: kb://j.txt]; it has 3 moons. "
        "[correction: Jupiter has 95 moons. [corrected, source: kb://j.txt]] Mars is red."
    )


def test_overlapping_claims_do_not_corrupt_the_text():
    text = "The Taj Mahal is in Agra, India."
    claims = [
        Claim(id=1, text="The Taj Mahal is in Agra, India.", sentence_index=0),
        Claim(id=2, text="The Taj Mahal is in Agra", sentence_index=0),
    ]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO"), make_verdict(2, "NOT_ENOUGH_INFO")]

    result = correct(text, claims, verdicts)

    assert result.replace(f" {UNVERIFIED_TAG}", "") == text
    assert result.count(UNVERIFIED_TAG) == 2


def test_multiline_evidence_snippet_is_collapsed_to_one_line():
    text = "The Great Wall of China is visible from the Moon."
    claims = [Claim(id=1, text=text, sentence_index=0)]
    evidence = make_evidence(1, "The wall is not visible\nfrom the Moon.", url="kb://wall.txt")
    verdicts = [make_verdict(1, "CONTRADICTED", evidence)]

    assert correct(text, claims, verdicts) == (
        "The wall is not visible from the Moon. [corrected, source: kb://wall.txt]"
    )


def test_out_of_range_sentence_index_falls_back_to_whole_text():
    text = "The telephone was invented in 1876."
    claims = [Claim(id=1, text=text, sentence_index=7)]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO")]

    assert correct(text, claims, verdicts) == f"{text} {UNVERIFIED_TAG}"


def test_sentence_numbering_matches_extractor_across_blank_lines():
    text = "Hello there.\n\nThe Eiffel Tower is in Paris.\n\n\nMars is the fourth planet."
    claims = [
        Claim(id=1, text="The Eiffel Tower is in Paris.", sentence_index=1),
        Claim(id=2, text="Mars is the fourth planet.", sentence_index=2),
    ]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO"), make_verdict(2, "NOT_ENOUGH_INFO")]

    assert correct(text, claims, verdicts) == (
        f"Hello there.\n\nThe Eiffel Tower is in Paris. {UNVERIFIED_TAG}\n\n\n"
        f"Mars is the fourth planet. {UNVERIFIED_TAG}"
    )


def test_tag_for_reworded_claim_stays_before_the_paragraph_break():
    text = "Albert Einstein was a physicist.\n\nHe was born in 1900.\n\nThanks!"
    claims = [Claim(id=1, text="Albert Einstein was born in 1900.", sentence_index=1)]
    verdicts = [make_verdict(1, "NOT_ENOUGH_INFO")]

    assert correct(text, claims, verdicts) == (
        f"Albert Einstein was a physicist.\n\nHe was born in 1900. {UNVERIFIED_TAG}\n\nThanks!"
    )
