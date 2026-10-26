---
name: kev
description: Use when the user asks about kev (jaredpalmer/kev), self-hosted decision models, or running a Jev-compatible System One API locally. Contains background, install/serve commands, and API usage.
---

# Kev — self-hosted decision models

Kev (https://github.com/jaredpalmer/kev, Apache-2.0, by Jared Palmer) is a family of small
**decision models** built on Qwen base models, answering yes/no, multiple-choice, and rating
questions. It's a self-hostable alternative to TypeSafe's Jev service (see the `jev-ai`
skill) and **shares the same API** — existing Jev client code works unchanged.

## Key facts

- Model sizes: 0.8B → 27B parameters (`jaredpalmer/kev-4b`, etc.; kev-27B is full weights, 51 GB)
- Calibrated probabilities (fitted temperatures), question isolation via attention masks
- Documents up to 65,536 tokens; runs on CUDA and Apple Silicon (MLX on Macs)
- Fine-tunable on custom labeled data; one-command Modal deployment
- Requires Python 3.12+ and uv

## Install and serve

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve
uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009
```

## API (Jev-compatible)

`POST /v1/systemone`:

```json
{
  "state": "Customer text to evaluate",
  "model": "kev-latest",
  "questions": {
    "routing": {
      "type": "choice",
      "instructions": "Which team?",
      "criteria": {"billing": "...", "shipping": "..."}
    }
  }
}
```

## Configuration (env vars)

`KEV_DTYPE` (fp32/bf16), `KEV_DEVICE` (cuda/mps/cpu), `KEV_API_KEY`, `KEV_TEMPERATURE`,
`KEV_TRUNCATE_STATES`.

## Getting more context

For anything beyond this (new releases, fine-tuning details), WebFetch the repo README at
https://github.com/jaredpalmer/kev rather than answering from memory — the project is
newer than training data and moves fast.
