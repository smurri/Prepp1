# Phase 1 — Problem Understanding (NO CODE)

**Mode: Plan.** Convert a fuzzy idea into a precise spec. Not code, not architecture — a crisp definition of *what* and *why*.

```
Explain this system as a software product: <your system>

Produce:
- what it does (one tight paragraph)
- users and their primary use cases
- inputs and outputs — with concrete example values AND types
- system boundaries (explicitly in-scope vs out-of-scope)
- assumptions you are making
- non-goals (what we deliberately do NOT do)
- success criteria — what "done" concretely means
- NON-FUNCTIONAL REQUIREMENTS: expected scale (RPS, data volume, users),
  latency target, availability target, consistency needs, durability needs,
  data sensitivity / compliance constraints (PII? payments? health?)
- open questions you need answered before design can begin
```

**The real deliverables are the open-questions list and the NFRs.** If Claude has zero questions about a non-trivial system, the spec is too shallow — push back. The NFRs size everything: a 10-RPS internal tool and a 100k-RPS public API are *different systems* even with identical features.

**Exit gate:** zero open questions; I/O concrete and typed; NFRs stated. **Commit `docs/spec.md`. Then `/clear`.**
