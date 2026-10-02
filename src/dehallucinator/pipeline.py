"""Pipeline (Role D): connects extract -> retrieve -> verify -> correct."""

from dehallucinator.models import CheckedAnswer


def check_answer(text: str) -> CheckedAnswer:
    """Run the full dehallucination pipeline on one AI answer."""
    raise NotImplementedError("Implemented by Role D in Sprint 1")
