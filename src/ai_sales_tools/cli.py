"""Command-line interface for the ai-sales-tools package."""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

from .call_summary import summarize_call
from .client import get_client
from .lead_scoring import score_lead
from .outreach import Prospect, SenderInfo, generate_cold_email, generate_linkedin_message
from .proposal import DealContext, generate_proposal

app = typer.Typer(add_completion=False, help="AI-powered sales tools built on the Anthropic API.")
console = Console()


def _read_text(value: Optional[str], file: Optional[Path]) -> str:
    if file:
        return file.read_text()
    if value:
        return value
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise typer.BadParameter("Provide the text directly, via --file, or pipe it on stdin.")


@app.command()
def outreach(
    name: str = typer.Option(..., help="Prospect's name"),
    company: str = typer.Option(..., help="Prospect's company"),
    sender_name: str = typer.Option(..., help="Your name"),
    sender_company: str = typer.Option(..., help="Your company"),
    product: str = typer.Option(..., help="One-line description of what you sell"),
    role: Optional[str] = typer.Option(None, help="Prospect's role/title"),
    context: Optional[str] = typer.Option(None, help="Relevant context about the prospect"),
    pain_point: Optional[str] = typer.Option(None, help="Likely pain point to address"),
    channel: str = typer.Option("email", help="'email' or 'linkedin'"),
) -> None:
    """Draft a personalized cold outreach message."""
    client = get_client()
    prospect = Prospect(name=name, company=company, role=role, context=context, pain_point=pain_point)
    sender = SenderInfo(name=sender_name, company=sender_company, product=product)
    generate = generate_linkedin_message if channel == "linkedin" else generate_cold_email
    console.print(generate(client, prospect, sender))


@app.command("score-lead")
def score_lead_cmd(
    notes: Optional[str] = typer.Option(None, help="Lead notes as a string"),
    file: Optional[Path] = typer.Option(None, help="Path to a file with lead notes"),
    icp: Optional[str] = typer.Option(None, help="Ideal customer profile description"),
) -> None:
    """Score and summarize an inbound lead."""
    client = get_client()
    text = _read_text(notes, file)
    result = score_lead(client, text, icp=icp)
    console.print_json(data=asdict(result))


@app.command("summarize-call")
def summarize_call_cmd(
    transcript: Optional[str] = typer.Option(None, help="Call transcript as a string"),
    file: Optional[Path] = typer.Option(None, help="Path to a transcript file"),
) -> None:
    """Summarize a sales call transcript into CRM-ready notes."""
    client = get_client()
    text = _read_text(transcript, file)
    result = summarize_call(client, text)
    console.print_json(data=asdict(result))


@app.command()
def proposal(
    company: str = typer.Option(..., help="Prospect's company"),
    contact: str = typer.Option(..., help="Contact name"),
    problem: str = typer.Option(..., help="Problem they're facing"),
    solution: str = typer.Option(..., help="Proposed solution"),
    pricing: Optional[str] = typer.Option(None, help="Pricing details"),
    timeline: Optional[str] = typer.Option(None, help="Timeline"),
) -> None:
    """Generate a one-page sales proposal."""
    client = get_client()
    deal = DealContext(
        prospect_company=company,
        contact_name=contact,
        problem=problem,
        proposed_solution=solution,
        pricing=pricing,
        timeline=timeline,
    )
    result = generate_proposal(client, deal)
    console.print(Markdown(result))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
