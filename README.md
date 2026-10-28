# personal-agent

A toolkit of agent skills and a personal CLI coding agent, for use with GPT and Claude. See [AGENTS.md](AGENTS.md) for the layout and conventions.

## Skills

Portable skill definitions live in `skills/<name>/SKILL.md`, with per-platform config in `skills/<name>/agents/<platform>.yaml`:

- **gmail-cleanup** — triage Gmail, alert on suspected security threats, trash clear junk and final job rejections, and add confirmed appointments to the matching Google Calendar. Never sends email.

Claude Code–only skills live in `.claude/skills/` and are auto-discovered when working in this repo.

## CLI agent

A personal CLI coding agent built on [pydantic-ai](https://ai.pydantic.dev) with long-term memory via [Hy-Memory](https://github.com/Tencent-Hunyuan/Hy-Memory).

- **Coder** capability: files, shell, repo context, planning, sub-agents
- **WebSearch** for docs and error messages
- **Advisor** second-opinion model when stuck
- **Long-term memory**: recalls relevant facts each prompt, saves new ones via a `save_memory` tool (stored under `~/.hy_memory/`)

### Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
export OPENAI_API_KEY=...   # used by the agent and by Hy-Memory (LLM + embeddings)
```

### Run

```bash
uv run personal-agent
```

### Memory

Hy-Memory runs in `pro` mode (LLM fact extraction + semantic search). To use a different OpenAI-compatible endpoint for memory, set `MEMORY_LLM_*` / `MEMORY_EMBEDDER_*` env vars.

### Configuration (env vars, all optional)

| Variable | Default | Purpose |
|---|---|---|
| `AGENT_MODEL` | `openai:gpt-5.6-sol` | Main agent model |
| `ADVISOR_MODEL` | `openai:gpt-5.6-sol` | Second-opinion model |
| `MEMORY_MODE` | `pro` | Hy-Memory mode (`lite` = embeddings only, no LLM calls) |
| `MEMORY_USER_ID` | `test` | Memory namespace per user |
