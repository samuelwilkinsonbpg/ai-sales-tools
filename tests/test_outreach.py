from __future__ import annotations

from typing import Any

from ai_sales_tools.outreach import Prospect, SenderInfo, generate_cold_email, generate_linkedin_message


def test_generate_cold_email_includes_prospect_context(fake_client: Any) -> None:
    def responder(kwargs: dict[str, Any]) -> str:
        assert "Series A" in kwargs["messages"][0]["content"]
        return "Hi Jane, saw you just raised a Series A..."

    client = fake_client(responder)
    prospect = Prospect(name="Jane", company="Acme", role="VP Sales", context="just raised a Series A")
    sender = SenderInfo(name="Sam", company="DisplAI", product="AI sales tooling")

    result = generate_cold_email(client, prospect, sender)

    assert "Jane" in result


def test_generate_linkedin_message_is_shorter_budget(fake_client: Any) -> None:
    captured: dict[str, Any] = {}

    def responder(kwargs: dict[str, Any]) -> str:
        captured.update(kwargs)
        return "Hi Jane — noticed the Series A news, would love to connect."

    client = fake_client(responder)
    prospect = Prospect(name="Jane", company="Acme")
    sender = SenderInfo(name="Sam", company="DisplAI", product="AI sales tooling")

    generate_linkedin_message(client, prospect, sender)

    assert captured["max_tokens"] < 400
