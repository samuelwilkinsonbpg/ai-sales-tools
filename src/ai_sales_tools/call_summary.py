"""Sales call / meeting transcript summarizer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .client import DEFAULT_MODEL, complete, extract_json

SYSTEM_PROMPT = (
    "You are a sales enablement assistant that turns raw call transcripts into "
    "structured notes for a CRM. Only report what is actually said in the transcript "
    "— never invent details or outcomes. Always respond with a single valid JSON "
    "object and nothing else."
)

RESPONSE_SHAPE = """{
  "summary": "3-5 sentence summary of the call",
  "action_items": ["action1", "action2"],
  "objections": ["objection1"],
  "next_steps": "what should happen next and by when, if stated",
  "sentiment": "Positive | Neutral | Negative"
}"""


@dataclass
class CallSummary:
    summary: str
    next_steps: str
    sentiment: str
    action_items: list[str] = field(default_factory=list)
    objections: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CallSummary":
        return cls(
            summary=data["summary"],
            next_steps=data.get("next_steps", ""),
            sentiment=data.get("sentiment", "Neutral"),
            action_items=list(data.get("action_items", [])),
            objections=list(data.get("objections", [])),
        )


def summarize_call(
    client: Any,
    transcript: str,
    *,
    model: str = DEFAULT_MODEL,
) -> CallSummary:
    """Summarize a raw sales call transcript into CRM-ready structured notes."""
    prompt = f"Transcript:\n{transcript}\n\nReturn exactly this JSON shape:\n{RESPONSE_SHAPE}"
    text = complete(client, system=SYSTEM_PROMPT, prompt=prompt, model=model, max_tokens=800)
    return CallSummary.from_dict(extract_json(text))
