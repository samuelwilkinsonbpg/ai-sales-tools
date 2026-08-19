"""Streamlit demo UI for ai-sales-tools — one form per tool, no local setup required.

Deploy on Streamlit Community Cloud (share.streamlit.io): point it at this file. Works out of
the box with zero cost — with no ANTHROPIC_API_KEY set, each tool shows a canned sample result
instead of calling the API. Add a key under the app's Secrets to switch to live generation.
See README.md for the full walkthrough.
"""

from __future__ import annotations

import os
from typing import Any, Callable

import streamlit as st

from ai_sales_tools import (
    CallSummary,
    DealContext,
    LeadScore,
    Prospect,
    SenderInfo,
    generate_cold_email,
    generate_linkedin_message,
    generate_proposal,
    get_client,
    score_lead,
    summarize_call,
)

st.set_page_config(page_title="AI Sales Tools", page_icon="📈", layout="centered")

try:
    # st.secrets raises (rather than returning the default) when no secrets.toml
    # exists at all, which is the normal case for this app's free demo mode.
    _secret_api_key = st.secrets.get("ANTHROPIC_API_KEY", "")
except Exception:
    _secret_api_key = ""
api_key = _secret_api_key or os.environ.get("ANTHROPIC_API_KEY", "")
DEMO_MODE = not api_key

st.title("📈 AI Sales Tools")
st.caption(
    "Live demo of [ai-sales-tools](https://github.com/samuelwilkinsonbpg/ai-sales-tools) "
    "— built on the Anthropic API."
)

if DEMO_MODE:
    st.info(
        "Running in **free demo mode** — no ANTHROPIC_API_KEY is configured, so the buttons "
        "below show a canned sample result instead of calling the API (no cost, no key needed). "
        "The app owner can add a key under Settings → Secrets to switch to live generation.",
        icon="🧪",
    )


def run(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Call a tool against a fresh Anthropic client, surfacing API errors in the UI."""
    try:
        with st.spinner("Asking Claude..."):
            return fn(get_client(api_key=api_key), *args, **kwargs)
    except Exception as exc:  # bad key, rate limit, network error, etc.
        st.error(f"Generation failed: {exc}")
        return None


SAMPLE_COLD_EMAIL = """Hi Jane,

Congrats on Acme's Series A — exciting stage to be scaling the sales team.

I'm Sam at DisplAI. We help fast-growing sales orgs cut the time reps spend writing outreach, \
using AI trained on what actually gets replies.

Worth a 15-minute call this week to see if it'd fit how your team is scaling?

Best,
Sam"""

SAMPLE_LINKEDIN = (
    "Hi Jane — congrats on the Series A! I work with sales teams like Acme's on cutting "
    "outreach time with AI. Open to connecting?"
)

SAMPLE_LEAD_SCORE = LeadScore(
    score=82,
    tier="Hot",
    summary=(
        "Enterprise buyer with approved budget and an internal champion already identified — "
        "evaluating two other vendors on a tight Q3 timeline."
    ),
    recommended_next_step="Schedule a technical demo this week before the competing evaluations conclude.",
    buying_signals=["Budget approved for Q3", "Champion identified (VP Eng)", "Actively comparing vendors"],
    risks=["Competing against two other vendors", "Tight decision timeline"],
)

SAMPLE_CALL_SUMMARY = CallSummary(
    summary=(
        "Prospect's current tool can't handle their volume and support response times are too "
        "slow. They need a replacement live before their Q4 renewal, with budget around $30k/yr."
    ),
    next_steps="Rep to send a proposal by Friday.",
    sentiment="Positive",
    action_items=["Send proposal by Friday", "Confirm implementation timeline fits before Q4 renewal"],
    objections=["Needs to be live before Q4 renewal date"],
)

SAMPLE_PROPOSAL = """# Overview
Acme Corp's sales reps currently spend hours each week writing outreach by hand, slowing pipeline growth.

# The Problem
Manual outreach doesn't scale with headcount and pulls reps away from selling.

# Our Solution
AI-generated, personalized outreach drafted in seconds, grounded in real prospect context.

# Pricing
$1,200/mo

# Timeline
Live within 2 weeks of kickoff.

# Next Steps
Schedule a 15-minute call to confirm scope and get started."""


tool = st.sidebar.radio("Tool", ["Cold Outreach", "Lead Scoring", "Call Summary", "Proposal"])

if tool == "Cold Outreach":
    st.header("✉️ Cold Outreach Generator")
    with st.form("outreach"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Prospect")
            name = st.text_input("Name", "Jane Doe")
            company = st.text_input("Company", "Acme Corp")
            role = st.text_input("Role (optional)", "VP Sales")
            context = st.text_area("Context / trigger event (optional)", "Acme just raised a Series A")
            pain_point = st.text_input("Likely pain point (optional)", "")
        with col2:
            st.subheader("You")
            sender_name = st.text_input("Your name", "Sam")
            sender_company = st.text_input("Your company", "DisplAI")
            product = st.text_area("What you sell (one line)", "AI tools that help reps sell faster")
            channel = st.radio("Channel", ["email", "linkedin"], horizontal=True)
        submitted = st.form_submit_button("Generate")

    if submitted:
        if DEMO_MODE:
            result = SAMPLE_LINKEDIN if channel == "linkedin" else SAMPLE_COLD_EMAIL
        else:
            prospect = Prospect(
                name=name,
                company=company,
                role=role or None,
                context=context or None,
                pain_point=pain_point or None,
            )
            sender = SenderInfo(name=sender_name, company=sender_company, product=product)
            generate = generate_linkedin_message if channel == "linkedin" else generate_cold_email
            result = run(generate, prospect, sender)
        if result:
            st.text_area("Result", result, height=220)

elif tool == "Lead Scoring":
    st.header("🎯 Lead Qualification & Scoring")
    with st.form("lead_scoring"):
        notes = st.text_area(
            "Lead notes",
            "Inbound demo request from the VP Eng at a 200-person Series B SaaS company. "
            "They mentioned budget is approved for Q3 and they're evaluating 2 other vendors.",
            height=150,
        )
        icp = st.text_input("Ideal customer profile (optional)", "Series B+ SaaS companies, 50+ employees")
        submitted = st.form_submit_button("Score Lead")

    if submitted:
        result = SAMPLE_LEAD_SCORE if DEMO_MODE else run(score_lead, notes, icp=icp or None)
        if result:
            c1, c2 = st.columns(2)
            c1.metric("Score", f"{result.score}/100")
            c2.metric("Tier", result.tier)
            st.write(result.summary)
            if result.buying_signals:
                st.markdown("**Buying signals**\n" + "\n".join(f"- {s}" for s in result.buying_signals))
            if result.risks:
                st.markdown("**Risks**\n" + "\n".join(f"- {r}" for r in result.risks))
            st.markdown(f"**Recommended next step:** {result.recommended_next_step}")

elif tool == "Call Summary":
    st.header("📞 Call/Meeting Summarizer")
    with st.form("call_summary"):
        transcript = st.text_area(
            "Call transcript",
            "Rep: Thanks for hopping on. What's driving the search right now?\n"
            "Prospect: Our current tool can't handle our volume and support is slow. "
            "We'd need this live before our Q4 renewal, budget is around $30k/yr.\n"
            "Rep: We can hit that timeline. I'll send a proposal by Friday.",
            height=200,
        )
        submitted = st.form_submit_button("Summarize")

    if submitted:
        result = SAMPLE_CALL_SUMMARY if DEMO_MODE else run(summarize_call, transcript)
        if result:
            st.write(result.summary)
            st.markdown(f"**Sentiment:** {result.sentiment}")
            if result.action_items:
                st.markdown("**Action items**\n" + "\n".join(f"- {a}" for a in result.action_items))
            if result.objections:
                st.markdown("**Objections**\n" + "\n".join(f"- {o}" for o in result.objections))
            st.markdown(f"**Next steps:** {result.next_steps}")

elif tool == "Proposal":
    st.header("📄 Proposal Generator")
    with st.form("proposal"):
        company = st.text_input("Prospect company", "Acme Corp")
        contact = st.text_input("Contact name", "Jane Doe")
        problem = st.text_area("Problem they're facing", "Reps spend hours a week writing outreach by hand")
        solution = st.text_area("Proposed solution", "AI-generated, personalized outreach in seconds")
        pricing = st.text_input("Pricing (optional)", "$1,200/mo")
        timeline = st.text_input("Timeline (optional)", "Live within 2 weeks")
        submitted = st.form_submit_button("Generate Proposal")

    if submitted:
        if DEMO_MODE:
            result = SAMPLE_PROPOSAL
        else:
            deal = DealContext(
                prospect_company=company,
                contact_name=contact,
                problem=problem,
                proposed_solution=solution,
                pricing=pricing or None,
                timeline=timeline or None,
            )
            result = run(generate_proposal, deal)
        if result:
            st.markdown(result)
