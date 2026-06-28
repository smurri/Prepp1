# Spec — Agent Eval Engine (Phase 1)

## What it does
A library that **scores an AI agent's execution path** (the ordered sequence of tool calls it
made to answer a question) by comparing it to one or more **reference paths** — known-good
executions previously observed for the same question. The output is a similarity score in
`[0,1]` plus an explainable breakdown of which reference it matched best.

## Users & primary use cases
- **Eval/benchmark authors** registering known-good paths and scoring candidate agent runs.
- **Agent developers** in CI: assert a new agent build still takes good paths (`score >= 0.8`).
- **Researchers** comparing scoring strategies (swap comparator/aggregation, compare results).

## Inputs & outputs (concrete, typed)
- **Step**: `Step(tool="search", args={"q": "weather"})` — `tool: str` (required, non-empty),
  `args: Mapping[str, Any]` (optional).
- **Trace** (a path): `Trace.from_tools(["search", "lookup", "summarize"])` — `steps: tuple[Step, ...]`.
- **Register**: `engine.add_reference(question_id: str, trace: Trace) -> int` (returns reference id).
- **Score**: `engine.score(question_id: str, candidate: Trace) -> ScoreResult`.
  - `ScoreResult.score: float` ∈ `[0,1]`; `.best: ReferenceScore | None`;
    `.breakdown: tuple[ReferenceScore, ...]` (per-reference, sorted desc).

Example: references `["search","lookup","summarize"]` and `["lookup","summarize"]`;
candidate `["search","lookup","summarize"]` → `score == 1.0` (exact match to ref 1).
Candidate `["search","calculate"]` → low score; breakdown shows best partial match.

## System boundaries
- **In scope**: in-memory storage of references per question; pluggable similarity comparators;
  pluggable aggregation across references; explainable result objects; typed errors.
- **Out of scope**: HTTP/RPC, persistence/DB, auth, *generating* agent paths, judging factual
  correctness of the agent's final answer, learning/training weights from data.

## Assumptions (decided in YOLO mode)
1. A "path" is fully captured by its ordered tool calls; tool **name** is the primary signal,
   args are an **optional** secondary signal (off by default).
2. References are grouped by an opaque `question_id: str` supplied by the caller.
3. Order generally matters → default comparator is order-sensitive (normalized edit distance).
4. "Resembles a good path" = **best** match among references → default aggregation is `max`.
5. Single-process library; lightly thread-safe so it can sit behind a concurrent harness.

## Non-goals
No persistence, no network, no NL understanding of tool semantics, no automatic threshold
tuning, no ranking of references by "quality" beyond what the caller encodes by registering them.

## Success criteria ("done")
- Public API (`Step`, `Trace`, `EvalEngine`, `ScoreResult`, comparators, aggregations) is stable
  and typed. Scores provably in `[0,1]`. Identity → `1.0`.
- Full test suite green (unit + boundary + adversarial + **property-based** invariants).
- Lint/format clean; README with runnable examples; ADRs + design committed.

## Non-functional requirements
- **Scale**: in-memory, single process. Target: thousands of references/question, paths up to
  a few hundred steps. Scoring is `O(R · m · n)` (R refs, m·n edit-distance DP) — fine at this size.
- **Latency**: a single `score()` over a handful of short references is sub-millisecond.
- **Availability/Durability**: N/A (library, no persistence; lifecycle owned by the host process).
- **Consistency**: store mutations guarded by a lock; `score()` is a pure read, never mutates.
- **Security/Governance**: no I/O, no eval, no PII assumptions; inputs validated at the boundary.
- **Data sensitivity**: caller-owned; library treats `args`/metadata as opaque, never logs them.

## Open questions — resolved (YOLO)
- *Args in scoring?* → Supported via a pluggable step-similarity, **default tool-name-only**.
- *Multiple references aggregation?* → Pluggable; **default `max`** (also `mean`, `top-k mean`).
- *Unknown question?* → Raise `UnknownQuestionError` (distinct from "0 similarity").
