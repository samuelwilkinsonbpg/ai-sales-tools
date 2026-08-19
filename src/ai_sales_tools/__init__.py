"""AI-powered sales tools built on the Anthropic API."""

from .call_summary import CallSummary, summarize_call
from .client import get_client
from .lead_scoring import LeadScore, score_lead
from .outreach import Prospect, SenderInfo, generate_cold_email, generate_linkedin_message
from .proposal import DealContext, generate_proposal

__all__ = [
    "get_client",
    "Prospect",
    "SenderInfo",
    "generate_cold_email",
    "generate_linkedin_message",
    "LeadScore",
    "score_lead",
    "CallSummary",
    "summarize_call",
    "DealContext",
    "generate_proposal",
]
