# personal-agent

A personal CLI coding agent built on [pydantic-ai](https://ai.pydantic.dev) with long-term memory via [Hy-Memory](https://github.com/Tencent-Hunyuan/Hy-Memory).

## Features (For now i guess)

- **Coder** capability: files, shell, repo context, planning, sub-agents
- **WebSearch** for docs and error messages
- **Advisor** second-opinion model when stuck
- **Long-term memory**: recalls relevant facts each prompt, saves new ones via a `save_memory` tool (stored under `~/.hy_memory/`)

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
export OPENAI_API_KEY=...   # used by the agent and by Hy-Memory (LLM + embeddings)
```

## Run

```bash
uv run personal-agent
```

## Memory

Hy-Memory runs in `pro` mode (LLM fact extraction + semantic search). To use a different OpenAI-compatible endpoint for memory, set `MEMORY_LLM_*` / `MEMORY_EMBEDDER_*` env vars.

## Configuration (env vars, all optional)

| Variable | Default | Purpose |
|---|---|---|
| `AGENT_MODEL` | `openai:gpt-5.6-sol` | Main agent model |
| `ADVISOR_MODEL` | `openai:gpt-5.6-sol` | Second-opinion model |
| `MEMORY_MODE` | `pro` | Hy-Memory mode (`lite` = embeddings only, no LLM calls) |
| `MEMORY_USER_ID` | `test` | Memory namespace per user |
