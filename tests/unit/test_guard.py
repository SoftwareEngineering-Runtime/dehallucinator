"""Tests for the @dehallucinate decorator (Role D). check_answer is faked."""

import pytest

from dehallucinator import pipeline
from dehallucinator.guard import dehallucinate
from dehallucinator.models import CheckedAnswer

ANSWER = "The Eiffel Tower is located in Paris."


@pytest.fixture
def fake_check(monkeypatch):
    calls = []

    def check_answer(text):
        calls.append(text)
        return CheckedAnswer(
            original=text,
            corrected=f"{text} [unverified]",
            claims=[],
            verdicts=[],
            trust_score=50.0,
        )

    monkeypatch.setattr(pipeline, "check_answer", check_answer)
    return calls


def test_tc_4_10_decorated_function_returns_checked_answer(fake_check):
    @dehallucinate
    def bot(question: str) -> str:
        return ANSWER

    result = bot("Where is the Eiffel Tower?")

    assert isinstance(result, CheckedAnswer)
    assert result.original == ANSWER
    assert result.corrected == f"{ANSWER} [unverified]"
    assert fake_check == [ANSWER]


def test_arguments_are_passed_through(fake_check):
    @dehallucinate
    def bot(question, *, style="short"):
        return f"{question} ({style})"

    bot("Mars is red", style="long")

    assert fake_check == ["Mars is red (long)"]


def test_name_and_docstring_are_kept():
    @dehallucinate
    def ask_bot(question: str) -> str:
        """Ask the chatbot a question."""
        return ANSWER

    assert ask_bot.__name__ == "ask_bot"
    assert ask_bot.__doc__ == "Ask the chatbot a question."
    assert ask_bot.__wrapped__.__name__ == "ask_bot"


@pytest.mark.parametrize("bad_return", [None, 42, ["a list"], b"bytes"])
def test_non_string_return_raises_type_error(fake_check, bad_return):
    @dehallucinate
    def bot():
        return bad_return

    with pytest.raises(TypeError, match="bot\(\) to return str"):
        bot()
    assert fake_check == []  # the pipeline is never called


def test_value_error_from_pipeline_is_passed_through(monkeypatch):
    def check_answer(text):
        raise ValueError("Input text is empty")

    monkeypatch.setattr(pipeline, "check_answer", check_answer)

    @dehallucinate
    def bot():
        return ""

    with pytest.raises(ValueError, match="empty"):
        bot()


def test_can_decorate_a_method(fake_check):
    class Bot:
        def __init__(self, reply):
            self.reply = reply

        @dehallucinate
        def ask(self, question):
            return self.reply

    assert Bot(ANSWER).ask("Where?").original == ANSWER
