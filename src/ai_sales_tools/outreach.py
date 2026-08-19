"""Cold outreach message generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import DEFAULT_MODEL, complete

SYSTEM_PROMPT = (
    "You are an expert B2B sales development rep who writes concise, specific, "
    "non-generic cold outreach. You never use hype words like 'revolutionary' or "
    "'game-changing', never write more than 150 words for an email or 60 words for "
    "a LinkedIn message, and always end with a single low-friction call to action."
)


@dataclass
class Prospect:
    name: str
    company: str
    role: str | None = None
    context: str | None = None  # e.g. "just raised a Series A", "posted about hiring SDRs"
    pain_point: str | None = None


@dataclass
class SenderInfo:
    name: str
    company: str
    product: str  # one-line description of what you sell


def generate_cold_email(
    client: Any,
    prospect: Prospect,
    sender: SenderInfo,
    *,
    model: str = DEFAULT_MODEL,
) -> str:
    """Draft a cold outreach email personalized to the prospect."""
    prompt = _build_prompt("email", prospect, sender)
    return complete(client, system=SYSTEM_PROMPT, prompt=prompt, model=model, max_tokens=400)


def generate_linkedin_message(
    client: Any,
    prospect: Prospect,
    sender: SenderInfo,
    *,
    model: str = DEFAULT_MODEL,
) -> str:
    """Draft a short LinkedIn connection/outreach message personalized to the prospect."""
    prompt = _build_prompt("LinkedIn connection message", prospect, sender)
    return complete(client, system=SYSTEM_PROMPT, prompt=prompt, model=model, max_tokens=200)


def _build_prompt(channel: str, prospect: Prospect, sender: SenderInfo) -> str:
    lines = [
        f"Write a {channel} from {sender.name} at {sender.company}.",
        f"What {sender.company} sells: {sender.product}",
        f"Prospect: {prospect.name}, {prospect.role or 'unknown role'} at {prospect.company}",
    ]
    if prospect.context:
        lines.append(f"Relevant context about the prospect: {prospect.context}")
    if prospect.pain_point:
        lines.append(f"Likely pain point to address: {prospect.pain_point}")
    lines.append(
        "Reference the context naturally, connect it to a concrete benefit of the product, "
        "and do not invent facts not given above. Return only the message text, no subject "
        "line, no preamble."
    )
    return "\n".join(lines)
