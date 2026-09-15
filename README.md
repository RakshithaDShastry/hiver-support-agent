# [Brand] AI Support Agent — Hiver SDE Intern Assignment

> **TODO:** One-line description once brand + intent taxonomy are decided (Day 1).

## What this is
An AI support agent for **[brand]** built on the Kaggle "Customer Support on
Twitter" dataset. It classifies incoming messages, drafts a reply grounded in
how the brand has historically resolved similar issues, and decides whether
to auto-handle or escalate to a human — with a stated reason.

## Quickstart (reproduce headline results in <15 min)
```bash
git clone <repo-url>
cd hiver-support-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env      # then add your ANTHROPIC_API_KEY

# TODO: exact commands to fetch subsampled data + run pipeline + run eval
```

## Repo structure
```
data/
  raw/            # subsampled raw data (not the full 3M-row dataset)
  processed/      # cleaned/filtered data for the chosen brand
  golden_set/     # 150–250 hand-labelled examples + labelling notes
src/              # pipeline code (classification, retrieval, generation, escalation, eval)
notebooks/        # exploration only — no pipeline logic lives here
reports/          # final report, decision log
tests/            # sanity tests for the pipeline
```

## Report
See `reports/report.md` for problem framing, baselines, failure analysis,
and the decision log.

## Status
🚧 In progress — Day 1: dataset exploration + brand selection.
