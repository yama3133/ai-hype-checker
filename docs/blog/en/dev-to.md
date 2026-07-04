---
title: "I Built an AI Agent That Catches AI Hype-Mongers on X — with Strands Agents + Bedrock AgentCore"
published: false
description: "AI Hype Detector scores any X (Twitter) post 0-100 for exaggeration, using a Strands Agent with two purpose-built tools, deployed on Bedrock AgentCore Runtime behind a Vercel front end."
tags: ai, bedrock, agentcore, vercel
cover_image: ./assets/thumbnail-en.jpg
canonical_url: https://github.com/yama3133/ai-hype-checker
---

> **TL;DR**
> I built **AI Hype Detector**, a small Strands Agent that reads an X post and scores it 0-100 for "AI hype-monger" energy — exaggerated claims with little to no technical substance behind them. It runs on **Bedrock AgentCore Runtime**, is called from a **Next.js app on Vercel**, and turns the whole screen red when a post scores above 70.
>
> - Production: https://ai-hype-checker.vercel.app
> - Repo: https://github.com/yama3133/ai-hype-checker

![AI Hype Detector thumbnail](./assets/thumbnail-en.jpg)

## The problem: AI hype-mongers on X

If you spend any time on X's AI corner, you know the genre: "This changes EVERYTHING," "Engineers are now obsolete," "I can't believe nobody is talking about this" — three sentences, zero specifics, maximum alarm. It's a real phenomenon with a name in Japanese, **AI驚き屋 ("AI odoroki-ya")**, roughly "the AI surprise-monger." I wanted a small, honest tool that reads one of these posts and tells you, with reasons, how much of it is substance versus noise.

Using an AI agent to detect AI-generated hype is a little on the nose. I made peace with that.

## What it does

Paste a post's text in, hit check, and you get:

- a **0-100 hype score**
- a **verdict**: Grounded / Somewhat exaggerated / Hype
- a short list of **reasons** the agent flagged it
- the **specific phrases** it flagged, quoted straight from your text

No X API, no scraping, no timeline monitoring — you copy the text yourself and paste it in. That was a deliberate scope cut: X's API pricing for search/timeline access starts around $200/month, and this is a side project, not a monitoring service.

## Two real examples

Here's the same tool on two actual X posts (screenshots are masked — author handles and avatars removed since these are real people's posts, not synthetic examples):

![Score 5 example — grounded post](./assets/screenshot-score-05.png)

*A post citing a specific benchmark, a model name, and a source link. Score: 5, verdict: Grounded.*

![Score 72 example — hype post](./assets/screenshot-score-72.png)

*A post built entirely out of stock hype phrases with nothing to verify. Score: 72, verdict: Hype — and yes, the screen turned red.*

## Architecture

![architecture](./assets/diagram-en.png)

- **Frontend**: Next.js 16 on Vercel — one page, one textarea, one button
- **Agent runtime**: Bedrock **AgentCore Runtime** (ARM64 container, built via CodeBuild, no local Docker needed)
- **Agent framework**: **Strands Agents**, two `@tool` functions plus the model's own judgment
- **Model**: Claude Sonnet 4.6 via Amazon Bedrock
- **Auth**: Vercel calls AgentCore Runtime with a scoped IAM user's access key (`bedrock-agentcore:InvokeAgentRuntime` on this one Runtime ARN only) — more on why below

## Inside the agent

The interesting part isn't the LLM call, it's the two small tools that ground it before it has to make a judgment call:

```python
@tool
def scan_hype_phrases(text: str) -> dict:
    """Scan post text for known hype/exaggeration phrase patterns."""
    return hype_scan.scan(text)  # regex hit list: "changes everything",
                                  # "no one is talking about this", etc.

@tool
def check_evidence_density(text: str) -> dict:
    """Check for URLs, numbers, model names, benchmark references."""
    return evidence_check.check(text)  # has_url / has_numbers /
                                         # has_model_name / has_benchmark_reference
```

The agent calls both tools, then combines their output with its own reading of the text to produce a single JSON verdict. One detail that mattered more than I expected: the `verdict` field is a **fixed English code** (`hype` / `exaggerated` / `grounded`), never translated, while the `reasons` array is generated in whichever language the UI is currently set to. That split exists because the UI needs a stable value to key its color coding off of, but a human reading the explanation wants it in their own language — mixing those two concerns into one LLM-generated string was going to break eventually.

## Bilingual UI, and the red screen

The UI ships in Japanese and English (`localStorage` + `navigator.language` auto-detect, same pattern I used on a previous project), and the language selection is sent along with the post text so the agent's reasons come back in the right language too — not just the static UI labels.

The one bit of flair: when the score comes back above 70, the entire page background turns red, with just enough contrast kept on the text and the result card (still white) to stay readable. It's a small thing, but it's the difference between "here's a score" and "here's a score you can feel."

## What's out of scope (for now)

- No X API integration — everything is manual copy/paste
- No per-account history or consistency checking against someone's past posts
- No auto-generated share image for the result

All of it is a genuinely small project — one Strands Agent, two tools, one page — but it's a clean example of composing **AgentCore Runtime + Strands Agents + Vercel** without any of the pieces feeling forced into place.

- Production: https://ai-hype-checker.vercel.app
- Repo: https://github.com/yama3133/ai-hype-checker
