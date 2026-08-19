from __future__ import annotations

from typing import Any

from ai_sales_tools.proposal import DealContext, generate_proposal


def test_generate_proposal_grounds_prompt_in_deal_context(fake_client: Any) -> None:
    def responder(kwargs: dict[str, Any]) -> str:
        prompt = kwargs["messages"][0]["content"]
        assert "$1,200/mo" in prompt
        assert "Manual lead scoring" in prompt
        return "# Overview\n\nAcme is spending too much time on manual lead scoring."

    client = fake_client(responder)
    deal = DealContext(
        prospect_company="Acme",
        contact_name="Jane",
        problem="Manual lead scoring takes too long",
        proposed_solution="Automated AI lead scoring",
        pricing="$1,200/mo",
    )

    result = generate_proposal(client, deal)

    assert result.startswith("# Overview")


def test_generate_proposal_omits_optional_sections_when_absent(fake_client: Any) -> None:
    captured: dict[str, Any] = {}

    def responder(kwargs: dict[str, Any]) -> str:
        captured.update(kwargs)
        return "# Overview"

    client = fake_client(responder)
    deal = DealContext(
        prospect_company="Acme",
        contact_name="Jane",
        problem="Manual process",
        proposed_solution="Automation",
    )

    generate_proposal(client, deal)

    prompt = captured["messages"][0]["content"]
    assert "Pricing" not in prompt.split("Structure it")[1]
    assert "Timeline" not in prompt.split("Structure it")[1]
