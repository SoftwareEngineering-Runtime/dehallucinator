"""@dehallucinate decorator to plug the pipeline into any chatbot (Role D, FR-4.3).

Usage::

    from dehallucinator.guard import dehallucinate

    @dehallucinate
    def ask_bot(question: str) -> str:
        return my_llm(question)

    result = ask_bot("When was the Eiffel Tower built?")  # -> CheckedAnswer
    print(result.corrected)
"""

import functools
from collections.abc import Callable
from typing import ParamSpec

from dehallucinator import pipeline
from dehallucinator.models import CheckedAnswer

P = ParamSpec("P")


def dehallucinate(func: Callable[P, str]) -> Callable[P, CheckedAnswer]:
    """Wrap a function that returns the chatbot's answer so it returns a CheckedAnswer.

    The wrapped function keeps the original name and docstring. Raises TypeError if the
    function returns something other than a str; ValueError from the pipeline (empty or
    over-long answer) is passed through unchanged.
    """

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> CheckedAnswer:
        answer = func(*args, **kwargs)
        if not isinstance(answer, str):
            raise TypeError(
                f"@dehallucinate expects {func.__name__}() to return str, "
                f"got {type(answer).__name__}"
            )
        return pipeline.check_answer(answer)

    return wrapper
