from dehallucinator.config import EVIDENCE_PER_CLAIM
from dehallucinator.evidence.ranker import make_snippets, rank_snippets

EIFFEL = {
    "title": "Eiffel Tower",
    "url": "https://en.wikipedia.org/wiki/Eiffel_Tower",
    "text": "The Eiffel Tower is in Paris. It was completed in 1889. "
    "It is made of iron.",
}
BANANA = {
    "title": "Banana",
    "url": "https://en.wikipedia.org/wiki/Banana",
    "text": "Bananas are yellow. They grow in tropical regions.",
}


def test_snippet_is_sentence_plus_next_sentence():
    assert make_snippets("One. Two. Three.") == ["One. Two.", "Two. Three.", "Three."]


def test_tc_2_05_ranked_by_relevance_across_sources():
    claim = "The Eiffel Tower was completed in 1889"
    results = rank_snippets(claim, [BANANA, EIFFEL])

    assert 0 < len(results) <= EVIDENCE_PER_CLAIM
    assert results[0]["title"] == "Eiffel Tower"
    assert "1889" in results[0]["text"]
    scores = [r["relevance"] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(0 <= s <= 1 for s in scores)
    assert all(r["url"] and r["title"] for r in results)
    assert all(r["title"] != "Banana" for r in results)


def test_empty_inputs_return_empty_list():
    assert rank_snippets("", [EIFFEL]) == []
    assert rank_snippets("The Eiffel Tower", []) == []
