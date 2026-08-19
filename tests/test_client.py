from __future__ import annotations

import pytest

from ai_sales_tools.client import extract_json, get_client


def test_extract_json_parses_plain_json() -> None:
    assert extract_json('{"a": 1}') == {"a": 1}


def test_extract_json_parses_json_in_markdown_fence() -> None:
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}


def test_extract_json_raises_on_no_json() -> None:
    with pytest.raises(ValueError):
        extract_json("no json here")


def test_get_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        get_client()


def test_get_client_accepts_explicit_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    client = get_client(api_key="sk-ant-test")
    assert client.api_key == "sk-ant-test"
