from __future__ import annotations

from typing import Any, Callable

import pytest


class _TextBlock:
    def __init__(self, text: str) -> None:
        self.type = "text"
        self.text = text


class _Message:
    def __init__(self, text: str) -> None:
        self.content = [_TextBlock(text)]


class FakeAnthropic:
    """Minimal stand-in for anthropic.Anthropic that avoids network calls in tests."""

    def __init__(self, responder: Callable[[dict[str, Any]], str]) -> None:
        self._responder = responder
        self.last_kwargs: dict[str, Any] | None = None
        self.messages = self

    def create(self, **kwargs: Any) -> _Message:
        self.last_kwargs = kwargs
        return _Message(self._responder(kwargs))


@pytest.fixture
def fake_client() -> Callable[[Callable[[dict[str, Any]], str]], FakeAnthropic]:
    def _make(responder: Callable[[dict[str, Any]], str]) -> FakeAnthropic:
        return FakeAnthropic(responder)

    return _make
