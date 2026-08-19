"""Lead qualification & scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .client import DEFAULT_MODEL, complete, extract_json

SYSTEM_PROMPT = (
    "You are a sales operations analyst who scores inbound leads for a B2B sales team. "
    "Score strictly based on the notes given — never invent details. "
    "Always respond with a single valid JSON object and nothing else."
)

RESPONSE_SHAPE = """{
  "score": 0,
  "tier": "Hot | Warm | Cold",
  "summary": "1-2 sentence summary of why",
  "buying_signals": ["signal1", "signal2"],
  "risks": ["risk1"],
  "recommended_next_step": "one concrete action"
}"""


@dataclass
class LeadScore:
    score: int
    tier: str
    summary: str
    recommended_next_step: str
    buying_signals: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LeadScore":
        return cls(
            score=int(data["score"]),
            tier=data["tier"],
            summary=data["summary"],
            recommended_next_step=data["recommended_next_step"],
            buying_signals=list(data.get("buying_signals", [])),
            risks=list(data.get("risks", [])),
        )


def score_lead(
    client: Any,
    notes: str,
    *,
    icp: str | None = None,
    model: str = DEFAULT_MODEL,
) -> LeadScore:
    """Score an inbound lead from free-text notes (call notes, form fill, email thread, ...)."""
    prompt_lines = ["Score this lead on a 0-100 scale (100 = perfect fit, ready to buy now)."]
    if icp:
        prompt_lines.append(f"Ideal customer profile: {icp}")
    prompt_lines += [
        f"Lead notes:\n{notes}",
        f"Return exactly this JSON shape:\n{RESPONSE_SHAPE}",
    ]
    text = complete(
        client,
        system=SYSTEM_PROMPT,
        prompt="\n\n".join(prompt_lines),
        model=model,
        max_tokens=500,
    )
    return LeadScore.from_dict(extract_json(text))
