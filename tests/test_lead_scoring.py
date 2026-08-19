from __future__ import annotations

from typing import Any

from ai_sales_tools.lead_scoring import score_lead


def test_score_lead_parses_json_response(fake_client: Any) -> None:
    response = """{
        "score": 82,
        "tier": "Hot",
        "summary": "Enterprise buyer with budget approved.",
        "buying_signals": ["budget approved", "champion identified"],
        "risks": ["long procurement cycle"],
        "recommended_next_step": "Schedule a technical demo"
    }"""
    client = fake_client(lambda kwargs: response)

    result = score_lead(client, "Enterprise lead, budget approved, champion is the VP Eng.")

    assert result.score == 82
    assert result.tier == "Hot"
    assert result.buying_signals == ["budget approved", "champion identified"]
    assert result.risks == ["long procurement cycle"]


def test_score_lead_tolerates_markdown_fences_and_missing_optional_fields(fake_client: Any) -> None:
    response = (
        '```json\n{"score": 10, "tier": "Cold", "summary": "No budget.", '
        '"recommended_next_step": "Nurture"}\n```'
    )
    client = fake_client(lambda kwargs: response)

    result = score_lead(client, "No budget, just browsing.")

    assert result.score == 10
    assert result.buying_signals == []
    assert result.risks == []


def test_score_lead_includes_icp_in_prompt(fake_client: Any) -> None:
    captured: dict[str, Any] = {}

    def responder(kwargs: dict[str, Any]) -> str:
        captured.update(kwargs)
        return (
            '{"score": 50, "tier": "Warm", "summary": "ok", '
            '"recommended_next_step": "follow up"}'
        )

    client = fake_client(responder)
    score_lead(client, "Some notes", icp="Series B+ SaaS companies with 50+ employees")

    assert "Series B+ SaaS" in captured["messages"][0]["content"]
