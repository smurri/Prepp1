# Agent Eval Engine (`agent_eval`)

Score how well an AI agent handled a question by comparing its **execution path**
(the ordered sequence of tool calls) to previously observed **reference paths**.
The scoring layer behind "did the agent take a good path?".

> In-memory **library** — no HTTP, no database, no persistence. Zero runtime
> dependencies (Python stdlib only).

## Install / develop

```bash
uv sync                 # create env + install dev deps
uv run pytest -q        # run the test suite
uv run ruff check .     # lint
```

## Quick start

```python
from agent_eval import EvalEngine, Trace

engine = EvalEngine()

# Register known-good reference paths for a question.
engine.add_reference("weather-q", Trace.from_tools(["search", "lookup", "summarize"]))
engine.add_reference("weather-q", Trace.from_tools(["lookup", "summarize"]))

# Score a new agent run against them.
result = engine.score("weather-q", Trace.from_tools(["search", "lookup", "summarize"]))

print(result.score)        # 1.0  (exact match to the first reference)
print(result.best)         # ReferenceScore(reference_id=1, similarity=1.0, reference_steps=3)
for ref in result.breakdown:
    print(ref.reference_id, round(ref.similarity, 3))
```

## Core concepts

| Concept | Type | Meaning |
|---|---|---|
| **Step** | `Step(tool, args={})` | One tool call. Tool name is the primary signal; `args` optional. |
| **Trace** | `Trace.from_tools([...])` | An ordered path of tool calls. |
| **Reference** | a stored `Trace` per `question_id` | A known-good execution to compare against. |
| **ScoreResult** | returned by `score()` | Aggregated `score ∈ [0,1]` + per-reference `breakdown`. |

## Scoring is pluggable

**Comparators** decide how two paths are compared (all return `[0, 1]`):

| Comparator | Order-sensitive? | Idea |
|---|---|---|
| `SequenceComparator` *(default)* | yes | Normalized edit (Levenshtein) distance over steps. |
| `JaccardComparator` | no | Overlap of the *set* of tool names. |
| `LCSComparator` | yes | Longest-common-subsequence ratio (tolerates gaps). |
| `CompositeComparator` | — | Weighted blend of the above. |

**Aggregations** collapse per-reference scores: `MAX` *(default — "resembles a good
path?")*, `MEAN`, `TopKMean(k)`.

```python
from agent_eval import EvalEngine, JaccardComparator, MEAN, Trace, tool_and_args, SequenceComparator

# Choose strategies up front…
engine = EvalEngine(comparator=JaccardComparator(), aggregation=MEAN)

# …or override per call (e.g. give partial credit for matching args):
engine.score(
    "q", Trace.from_tools(["search"]),
    comparator=SequenceComparator(step_similarity=tool_and_args(tool_weight=0.5)),
)
```

## API

```python
engine.add_reference(question_id, trace) -> int          # returns reference id
engine.add_references(question_id, traces) -> list[int]
engine.score(question_id, candidate, *, comparator=None, aggregation=None) -> ScoreResult
engine.references(question_id) -> list[Trace]
engine.remove_reference(question_id, reference_id) -> bool
engine.clear(question_id=None) -> None
```

**Errors** (all under `AgentEvalError`): `UnknownQuestionError` (no such question),
`NoReferencesError`, `InvalidTraceError`.

## Guarantees (property-tested)

- Scores are always in `[0, 1]`; identical paths score `1.0`.
- Empty-vs-empty `= 1.0`; empty-vs-non-empty `= 0.0`. Comparators are symmetric.
- Under `MAX`, adding a reference never lowers the score.
- The reference store is thread-safe; `score()` never mutates stored data.

## Demo & UI (optional layers)

The core library is in-memory and dependency-free. On top of it, optional layers
demonstrate it against **mock backends** (the library itself stays pure):

- **Mock data** (`agent_eval.mockdata`) — realistic questions, curated reference
  paths, and candidate runs, served through two interchangeable mock backends:
  a **SQL** one (stdlib `sqlite3`, in-memory) and a **NoSQL** one (in-memory
  document store). Both implement the same `ReferenceBackend` interface.

```bash
# Headless CLI demo — load a mock DB, score every candidate run:
uv run python -m agent_eval.demo --backend sql      # or: nosql
uv run python -m agent_eval.demo --backend nosql --comparator lcs --aggregation mean
```

- **Web UI** (`ui/app.py`, Streamlit) — pick a backend, comparator, aggregation,
  a question, and a candidate path; see the score and an explainable breakdown.

```bash
uv sync --extra ui
uv run streamlit run ui/app.py
```

> The `mockdata` backends and the UI are **demo scaffolding** — they satisfy the
> "show it against a SQL/NoSQL DB with a UI" request without violating the core
> constraint that the *engine* keeps all state in memory with zero dependencies.

## Design docs

`docs/spec.md` (problem + NFRs) · `docs/design.md` (interfaces, flow, edge cases) ·
`docs/adr/` (key decisions). Built with the `cc_steps/` engineering playbook.

---

<details>
<summary>Original problem statement</summary>

Design and implement an Agent Eval Engine — a library that scores how well an AI
agent handles a new question by comparing the agent's execution path to previously
observed reference paths. Constraints: a library (no HTTP/DB/persistence), all state
in-memory, focus on clean API design, correct logic, and testability.
</details>
