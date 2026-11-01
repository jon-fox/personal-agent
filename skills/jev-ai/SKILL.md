---
name: jev-ai
description: Use when the user asks about Jev, Jev AI, TypeSafe AI, System One / decision models — or any AI model, tool, or company you don't recognize from training data. Contains background on Jev and a procedure for fetching current context before answering.
---

# Jev AI and unfamiliar AI tools

## What Jev is

Jev is TypeSafe AI's "System One" **decision model** — not an LLM. Instead of generating
text, it takes application state plus typed questions (yes/no with probability,
multiple-choice, scoring) and returns calibrated, structured decisions software can act on
directly. TypeSafe reports ~200x faster inference and ~400x lower cost than comparable
LLMs on classification tasks (~0.5s typical latency).

Use cases: classifying requests, routing tickets, scoring urgency/leads, safety checks,
RAG evaluation, human-review gating — repeated bounded decisions inside a product.

Key facts:
- Company: TypeSafe AI, San Francisco, founded 2024 (Diogo Almeida, Sasha Sheng, Erik Gafni)
- Playground + API: https://jev-ai.pro/ (REST endpoint: `POST /api/v1/systemone`)
- Docs: https://jev-ai.pro/docs and https://jev-ai.pro/what-is-jev
- GitHub: https://github.com/jev-ai
- Input: plain text, JSON, up to 4 images (PNG/JPEG ≤16 MB); English primary
- Pricing: input tokens only (output free); credit-based with per-model multipliers

## How to get context on questions like this

When asked about an AI model/tool/company you don't recognize (it may be newer than your
training data — never assume it's a typo or doesn't exist):

1. **WebSearch the exact name** (quoted, e.g. `"Jev AI"`) to establish what it is.
2. **WebFetch the official site/docs** found in step 1 for specifics (API, pricing, usage).
3. For libraries/SDKs, **prefer Context7 MCP** (`resolve-library-id` → `query-docs`) over
   web search for accurate, current API docs.
4. Answer from the fetched sources, cite them, and note what's uncertain.
5. If it's something the user will ask about again, offer to add what you learned to this
   skill (or a new one) so future sessions have it without re-searching.
