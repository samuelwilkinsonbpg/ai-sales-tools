"""Sales proposal / one-pager generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import DEFAULT_MODEL, complete

SYSTEM_PROMPT = (
    "You are a sales engineer who writes short, concrete B2B proposals. Ground every "
    "claim in the deal context given — never invent pricing, features, or timelines "
    "that weren't provided. Write in plain Markdown with clear section headings."
)


@dataclass
class DealContext:
    prospect_company: str
    contact_name: str
    problem: str
    proposed_solution: str
    pricing: str | None = None
    timeline: str | None = None


def generate_proposal(
    client: Any,
    deal: DealContext,
    *,
    model: str = DEFAULT_MODEL,
) -> str:
    """Generate a one-page Markdown sales proposal grounded in the given deal context."""
    sections = ["Overview", "The Problem", "Our Solution"]
    if deal.pricing:
        sections.append("Pricing")
    if deal.timeline:
        sections.append("Timeline")
    sections.append("Next Steps")

    lines = [
        f"Write a one-page sales proposal for {deal.prospect_company}, "
        f"addressed to {deal.contact_name}.",
        f"Problem they're facing: {deal.problem}",
        f"Proposed solution: {deal.proposed_solution}",
    ]
    if deal.pricing:
        lines.append(f"Pricing: {deal.pricing}")
    if deal.timeline:
        lines.append(f"Timeline: {deal.timeline}")
    lines.append(
        f"Structure it with Markdown headings: {', '.join(sections)}. "
        "Keep it under 400 words total."
    )
    prompt = "\n".join(lines)
    return complete(client, system=SYSTEM_PROMPT, prompt=prompt, model=model, max_tokens=900)
