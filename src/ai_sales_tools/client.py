"""Thin wrapper around the Anthropic API shared by every tool in this package."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from anthropic import Anthropic

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")


def get_client(api_key: str | None = None) -> Anthropic:
    """Build an Anthropic client, reading the API key from the environment by default."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Export it or pass api_key= explicitly."
        )
    return Anthropic(api_key=key)


def complete(
    client: Any,
    *,
    system: str,
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 1024,
) -> str:
    """Send a single-turn request and return the raw text response."""
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    block = message.content[0]
    if block.type != "text":
        raise RuntimeError(f"Unexpected response block type: {block.type}")
    return block.text.strip()


def extract_json(text: str) -> Any:
    """Parse a JSON object out of a model response, tolerating markdown fences."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError(f"No JSON object found in response: {text!r}")
    return json.loads(match.group(0))
