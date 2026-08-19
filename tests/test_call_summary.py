from __future__ import annotations

from typing import Any

from ai_sales_tools.call_summary import summarize_call


def test_summarize_call_parses_json_response(fake_client: Any) -> None:
    response = """{
        "summary": "Prospect is evaluating three vendors, budget confirmed at $50k.",
        "action_items": ["Send security questionnaire", "Loop in their IT lead"],
        "objections": ["Concerned about implementation time"],
        "next_steps": "Follow up Friday with a proposal",
        "sentiment": "Positive"
    }"""
    client = fake_client(lambda kwargs: response)

    result = summarize_call(client, "raw transcript text...")

    assert result.sentiment == "Positive"
    assert "Send security questionnaire" in result.action_items
    assert result.objections == ["Concerned about implementation time"]


def test_summarize_call_defaults_missing_fields(fake_client: Any) -> None:
    response = '{"summary": "Short call, no clear outcome."}'
    client = fake_client(lambda kwargs: response)

    result = summarize_call(client, "raw transcript text...")

    assert result.sentiment == "Neutral"
    assert result.action_items == []
    assert result.objections == []
