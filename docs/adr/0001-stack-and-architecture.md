# ADR 0001 — Stack & architecture

**Status:** Accepted · **Phase:** 1.5

- **Language/runtime:** Python ≥ 3.11. *Driving NFR:* testability + clean API design; Python's
  dataclasses, `Protocol`, and type hints express immutable value objects and pluggable
  strategies concisely. Stdlib-only at runtime (zero deps) keeps the library trivially adoptable.
- **Datastore:** None. *Driving NFR:* the constraint is explicit — "no database, all state
  in-memory". A `dict[str, dict[int, Trace]]` reference store suffices.
- **Architecture:** Single module package (modular monolith at library scale). Facade
  (`EvalEngine`) over swappable `PathComparator` and `Aggregation` strategies. *Driving NFR:*
  maintainability + extensibility without speculative layers.
- **Sync/async:** Synchronous. Pure CPU work, no I/O — async would add complexity for no gain.
- **API style:** In-process library API (no REST/GraphQL/gRPC). *Driving NFR:* "library, not a
  web service."

**One-way doors:** the public type/contract surface (`Step`, `Trace`, `ScoreResult`, comparator
protocol). Frozen early and versioned with semver; additive changes only within `0.x` → `1.x`.
