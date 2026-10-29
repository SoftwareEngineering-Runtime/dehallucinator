"""Display helpers for the Streamlit demo UI (Role D, FR-4.5, FR-4.6).

Kept separate from ui/app.py so the HTML building and escaping can be unit-tested.
Every piece of answer or evidence text goes through html.escape before it is put into
HTML, so a script or tag in the input is shown as text, never run (NFR-3).
"""

import html
import json
from dataclasses import dataclass
from pathlib import Path

from dehallucinator.config import MAX_INPUT_CHARS
from dehallucinator.models import CheckedAnswer, Label

SAMPLES_PATH = Path(__file__).resolve().parents[2] / "data" / "samples.json"

# Green / red / grey as in NFR-6 and FR-4.6.
LABEL_STYLE: dict[Label, tuple[str, str]] = {
    "SUPPORTED": ("#1a7f37", "Supported"),
    "CONTRADICTED": ("#cf222e", "Contradicted"),
    "NOT_ENOUGH_INFO": ("#6e7781", "Unverified"),
}


@dataclass(frozen=True)
class ClaimRow:
    text: str
    label: Label
    score: float
    source_title: str | None
    source_url: str | None
    evidence: str | None


def load_samples(path: Path = SAMPLES_PATH) -> list[dict]:
    """Load the demo sample answers; each has at least an id, title and answer."""
    samples = json.loads(path.read_text(encoding="utf-8"))
    for sample in samples:
        if not sample.get("title") or not isinstance(sample.get("answer"), str):
            raise ValueError(f"Sample {sample.get('id')} needs a title and an answer")
        if len(sample["answer"]) > MAX_INPUT_CHARS:
            raise ValueError(f"Sample {sample['id']} is longer than {MAX_INPUT_CHARS} chars")
    return samples


def claim_rows(result: CheckedAnswer) -> list[ClaimRow]:
    """One row per claim, joined with its verdict (a claim without one is unverified)."""
    verdicts = {verdict.claim_id: verdict for verdict in result.verdicts}
    rows = []
    for claim in result.claims:
        verdict = verdicts.get(claim.id)
        evidence = verdict.best_evidence if verdict else None
        rows.append(
            ClaimRow(
                text=claim.text,
                label=verdict.label if verdict else "NOT_ENOUGH_INFO",
                score=verdict.score if verdict else 0.0,
                source_title=evidence.title if evidence else None,
                source_url=evidence.source_url if evidence else None,
                evidence=evidence.snippet if evidence else None,
            )
        )
    return rows


def claim_html(row: ClaimRow) -> str:
    """Coloured HTML card for one claim. All text is escaped."""
    colour, label_text = LABEL_STYLE[row.label]
    parts = [
        f'<div style="border-left:6px solid {colour};padding:6px 12px;margin:8px 0;">',
        f'<span style="color:{colour};font-weight:600;">{label_text}</span>',
        f' <span style="opacity:0.7;">({row.score:.0%})</span><br>',
        html.escape(row.text),
    ]
    if row.evidence:
        parts.append(f"<br><small><i>Evidence:</i> {html.escape(row.evidence)}</small>")
    if row.source_url:
        parts.append(f"<br><small>Source: {source_html(row.source_title, row.source_url)}</small>")
    parts.append("</div>")
    return "".join(parts)


def source_html(title: str | None, url: str) -> str:
    """A link for http(s) sources; plain text for anything else (e.g. kb://file.txt)."""
    label = html.escape(title or url)
    if url.startswith(("https://", "http://")):
        return f'<a href="{html.escape(url, quote=True)}" target="_blank">{label}</a>'
    return f"{label} ({html.escape(url)})"


def trust_colour(score: float) -> str:
    """Green for 75 and above, red below 40, grey in between."""
    if score >= 75:
        return LABEL_STYLE["SUPPORTED"][0]
    if score < 40:
        return LABEL_STYLE["CONTRADICTED"][0]
    return LABEL_STYLE["NOT_ENOUGH_INFO"][0]
