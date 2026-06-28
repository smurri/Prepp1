# Phase 2 — System Design

**Mode: Plan.** Architecture now. Still no implementation code.

```
Design the system architecture for the approved spec and chosen stack. DESIGN ONLY.

Include:
- core modules, each with a single clear responsibility
- data models / schemas (field names + types); for SQL, the normalized schema +
  the indexes the main queries need
- public interfaces and function signatures (signatures only, no bodies)
- API contract sketch if applicable (endpoints, request/response shapes, errors)
- dependencies, with justification for each
- control flow + data flow (where is the source of truth; how data moves)
- error-handling and boundary strategy
- failure strategy: what happens when each dependency is slow or down
- trust boundaries: where untrusted input enters, where authz is enforced

Provide 2 alternative designs with tradeoffs, recommend one, note how each meets NFRs.
```

**Demand concreteness.** You want *interface signatures and typed data models*, not prose. `def score(trace: list[Step]) -> float` is a contract; "the scorer takes the trace and returns a score" is not. Locking contracts now is what lets module-by-module implementation compose.

See also: [`31_data_layer.md`](31_data_layer.md), [`32_api_design.md`](32_api_design.md).

**Exit gate:** interfaces, data models, and (if applicable) API contract concrete enough to implement against without guessing.
