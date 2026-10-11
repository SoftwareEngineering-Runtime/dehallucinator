"""FastAPI app exposing /check and /health (Role D, FR-4.4).

Run with: uvicorn dehallucinator.api:app
"""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from dehallucinator import pipeline
from dehallucinator.config import MAX_INPUT_CHARS
from dehallucinator.models import CheckedAnswer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dehallucinator",
    description="Checks an AI answer against trusted sources and returns a corrected answer.",
    version="0.1.0",
)


class CheckRequest(BaseModel):
    """Body of POST /check."""

    text: str = Field(min_length=1, max_length=MAX_INPUT_CHARS, description="The AI answer")

    @field_validator("text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("text must not be blank")
        return value


@app.get("/health")
def health() -> dict[str, str]:
    """Liveness check used by Docker and Jenkins."""
    return {"status": "ok"}


@app.post("/check", response_model=CheckedAnswer)
def check(request: CheckRequest) -> CheckedAnswer:
    """Check one AI answer. A plain ``def`` so FastAPI runs it in a worker thread."""
    try:
        return pipeline.check_answer(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Log the full error for us, but never send a stack trace to the client (NFR-3).
        logger.exception("check_answer failed")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
