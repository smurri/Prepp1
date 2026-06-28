# CLAUDE.md — Agent Eval Engine (`agent_eval`)

## What this is
An in-memory **library** that scores how well an AI agent's execution path (a sequence of
tool calls) matches previously observed **reference paths** for the same question.
Scaling-ladder rung: **Library** (clean interfaces, full tests, docs, semver). No HTTP, no
DB, no persistence — all state in memory.

## Stack & versions
- Language: **Python ≥ 3.11** (stdlib only at runtime — zero runtime dependencies).
- Tooling: **uv** (env + deps), **pytest** + **hypothesis** (tests), **ruff** (lint/format).
- Layout: `src/` layout, package `agent_eval`.

## Commands (run from repo root)
- Install / sync env:  `uv sync`
- Run tests:           `uv run pytest -q`
- Coverage:            `uv run pytest --cov=agent_eval`
- Lint:                `uv run ruff check .`
- Format:              `uv run ruff format .`

> On Windows + Git Bash, prepend PATH once per shell: `export PATH="$HOME/.local/bin:$PATH"`.

## Directory map
- `src/agent_eval/models.py`      — `Step`, `Trace` (immutable value objects).
- `src/agent_eval/comparators.py` — `PathComparator` protocol + Sequence/Jaccard/LCS/Composite.
- `src/agent_eval/aggregation.py` — combine per-reference scores (max / mean / top-k).
- `src/agent_eval/results.py`     — `ScoreResult`, `ReferenceScore` (explainable output).
- `src/agent_eval/store.py`       — in-memory reference store (thread-safe).
- `src/agent_eval/engine.py`      — `EvalEngine` facade (the public entry point).
- `src/agent_eval/errors.py`      — typed exception hierarchy.
- `tests/`                        — unit, boundary, adversarial, property-based.
- `docs/spec.md`, `docs/design.md`, `docs/adr/` — frozen artifacts.

## Conventions
- Public API: small functions, full type hints, docstrings. Value objects are **frozen**.
- Scores are **always in `[0.0, 1.0]`**. This is an invariant — property-tested.
- Validate inputs at the boundary (`EvalEngine`); fail loudly with typed errors.
- Comparators and aggregators are **pluggable** (dependency injection), never hard-coded.

## Domain notes (non-obvious)
- A "path" = ordered tool calls. Order usually matters → default comparator is order-sensitive
  (normalized edit distance). Jaccard (order-insensitive) is available for set-style scoring.
- One question may have **many** valid references. Default aggregation = **max** ("did it
  resemble *a* known-good path?").
- Unknown question → `UnknownQuestionError`. Empty-vs-empty trace similarity = `1.0`;
  empty-vs-nonempty = `0.0`.

## Never touch
- Don't add persistence, network, or runtime dependencies — constraints forbid them.
- Don't weaken the `[0,1]` invariant or make `score` mutate stored references.
