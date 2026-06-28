# The Data Layer (depth)

Beyond *which* store (see [`30_decision_frameworks.md`](30_decision_frameworks.md)):

- **Schema design.** Normalize until it hurts, denormalize until it works. Normalize by default (no duplicate sources of truth); denormalize deliberately for read performance, knowing you now own keeping copies in sync.
- **Indexing.** Index the columns hot queries filter/sort/join on — and only those. Every index speeds reads, slows writes, costs space. Read the query plan (`EXPLAIN`); don't guess.
- **The N+1 problem.** The silent killer: a loop firing one query per item (1 for the list + N for details). Fix with eager loading / joins / batching. Always check when an ORM is involved.
- **Transactions & isolation.** Wrap multi-step invariants in a transaction. Know your isolation level (read-committed vs repeatable-read vs serializable) — it determines which races (dirty / non-repeatable / phantom reads) are possible.
- **Migrations.** Versioned, reviewed, forward-only, reversible where possible. **Expand -> migrate -> contract** so schema and code deploy and roll back independently. Never hand-edit prod schema.
- **Caching & invalidation.** Cache to cut load and latency — but cache invalidation is famously one of the hard problems. Pick a strategy (TTL, write-through, write-behind) and a clear answer to *when does stale data refresh*. A cache without an invalidation plan is a correctness bug waiting to happen.
