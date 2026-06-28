# Phase 6 — Test Design

**Mode: Default.** A separate phase, deliberately — so Claude doesn't just test the happy path it implemented. Tests encode the **spec**, not current behavior.

```
Design a complete test plan for <slice>. No code yet.
- unit (normal), boundary/edge, failure/error
- adversarial / malformed / hostile inputs
- regression tests for every bug found in validation/debugging
- property-based tests for invariants (e.g. output always in [0,1])
- concurrency tests where shared state exists (races, ordering, idempotency)
- contract tests for any API (request/response shape, error codes, pagination)
Each: what it asserts and why.

Then implement them. Tests must be independent and deterministic.
```

**Critical pointer:** forbid tests that merely assert whatever the code currently does. A test that locks in a bug is worse than no test. Assertions come from the spec, not from pasting the code's output.

**Exit gate:** plan covers all categories; tests implemented, independent, deterministic.
