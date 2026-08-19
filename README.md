# ai-sales-tools

AI-powered sales tools built on the [Anthropic API](https://docs.anthropic.com/). Usable as a
Python library or as a `sales-tools` CLI.

## Tools

- **Cold outreach generator** (`ai_sales_tools.outreach`) — drafts personalized cold emails or
  LinkedIn messages from a prospect's name, role, company, and any context you have (recent
  news, a pain point, etc).
- **Lead qualification & scoring** (`ai_sales_tools.lead_scoring`) — turns free-text lead notes
  into a 0–100 fit score, tier (Hot/Warm/Cold), buying signals, risks, and a recommended next
  step.
- **Call/meeting summarizer** (`ai_sales_tools.call_summary`) — turns a raw sales call transcript
  into a CRM-ready summary, action items, objections raised, next steps, and sentiment.
- **Proposal generator** (`ai_sales_tools.proposal`) — generates a one-page Markdown sales
  proposal grounded in the deal context you supply (problem, solution, pricing, timeline).

Every tool is grounded in the input you give it — prompts explicitly instruct the model not to
invent facts, pricing, or outcomes that weren't provided.

## Live demo (no local setup)

`app.py` is a [Streamlit](https://streamlit.io) UI over the same four tools — one form each,
no CLI or install required for whoever's trying it. Deploy your own copy for free in about
3 minutes:

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **New app**, pick this repo, branch `main`, main file path `app.py`.
3. Before (or after) deploying, open **Advanced settings → Secrets** and add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
4. Click **Deploy**. You'll get a public `*.streamlit.app` URL — share that link to demo the
   tools with zero setup on the visitor's end.

To run it locally instead: `pip install -e ".[web]"`, then
`ANTHROPIC_API_KEY=sk-ant-... streamlit run app.py`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
```

## CLI usage

```bash
export ANTHROPIC_API_KEY=sk-ant-...

# Cold outreach
sales-tools outreach \
  --name "Jane Doe" --company "Acme Corp" --role "VP Sales" \
  --context "Acme just raised a Series A" \
  --sender-name "Sam" --sender-company "DisplAI" \
  --product "AI tools that help reps sell faster" \
  --channel email

# Lead scoring
sales-tools score-lead --file lead-notes.txt --icp "Series B+ SaaS, 50+ employees"

# Call summary
sales-tools summarize-call --file call-transcript.txt

# Proposal
sales-tools proposal \
  --company "Acme Corp" --contact "Jane Doe" \
  --problem "Reps spend hours a week writing outreach by hand" \
  --solution "AI-generated, personalized outreach in seconds" \
  --pricing "$1,200/mo" --timeline "Live within 2 weeks"
```

## Library usage

```python
from ai_sales_tools import get_client, Prospect, SenderInfo, generate_cold_email

client = get_client()  # reads ANTHROPIC_API_KEY from the environment

prospect = Prospect(name="Jane Doe", company="Acme Corp", role="VP Sales",
                     context="Acme just raised a Series A")
sender = SenderInfo(name="Sam", company="DisplAI", product="AI sales tooling")

email = generate_cold_email(client, prospect, sender)
print(email)
```

## Testing

Tests run fully offline against a fake Anthropic client (no API key or network access needed):

```bash
pytest
```

## Configuration

| Variable            | Description                                  | Default            |
|---------------------|-----------------------------------------------|--------------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key                        | *(required)*       |
| `ANTHROPIC_MODEL`   | Model used for all tools                       | `claude-sonnet-5`  |
