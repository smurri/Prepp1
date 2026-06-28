# Phase 1.5 — Technology Selection

**Mode: Plan.** The decisions here constrain every later phase and are hard to reverse once code exists. Make them explicitly, tied to the NFRs — not by habit or hype. Full tables in [`30_decision_frameworks.md`](30_decision_frameworks.md).

```
Given the spec and its NFRs (docs/spec.md), recommend the foundational stack.
For EACH choice: options, tradeoffs, recommendation, and which NFR drives it.

- Language / runtime (ecosystem fit, team skill, performance profile, hiring)
- Datastore(s): SQL vs NoSQL vs key-value vs graph vs time-series vs search vs
  blob — and whether polyglot persistence is justified
- Data access: raw queries vs query builder vs ORM
- Architecture: single module -> modular monolith -> services -> serverless
- Sync vs async: request/response vs queues/events/streaming
- API style (if any): REST vs GraphQL vs gRPC vs none (library)
- Hosting/runtime target: VM vs container vs serverless vs managed PaaS
- Build vs buy vs adopt: auth, payments, search, email, etc.

Flag anything you'd defer, and any one-way doors (expensive to reverse).
Record each as a one-paragraph ADR.
```

**Default to boring, proven technology** and spend your "innovation budget" only where the problem demands it. The right datastore is usually **PostgreSQL** until an NFR forces otherwise. The right architecture is usually a **modular monolith** until scale or team size forces splitting. Distributed systems buy scale at the cost of enormous operational complexity — don't pay it before you must.

**Exit gate:** language, datastore(s), architecture, sync/async, API style chosen, each with rationale + the driving NFR. **Commit `docs/adr/`.**
