# The Engineering Pillars + Scaling Ladder

The Loop is *how* you build; these are *what good means*. Weave through every phase. **The NFRs tell you how hard to push each one.**

- **Reliability** — *keeps working when things go wrong?* Timeouts, retries w/ backoff+jitter, **idempotency**, circuit breakers, graceful degradation. Litmus: kill any one dependency — fail safely or catastrophically?
- **Scalability** — *works at 10x/100x?* Statelessness, caching, queues + backpressure, pooling, partitioning, replicas. **Measure before optimizing.**
- **Durability** — *data survives failure?* Replicated storage, backups + *tested* restores, no hard-delete without a safety net. A backup you've never restored is a hope.
- **Consistency** — *everyone sees coherent data?* Choose **strong** vs **eventual** on purpose. Transactions, locks, atomic ops, compare-and-swap, unique constraints.
- **Security** — *can it be abused?* See [`34_security.md`](34_security.md). All input hostile; authorize every path; secrets in a vault.
- **Governance** — *data handled lawfully and accountably?* See [`35_governance_compliance.md`](35_governance_compliance.md). Regime, lifecycle, audit, access — Phase 1 onward.
- **Observability** — *can you see prod?* Logs, metrics, traces, health checks, correlation IDs. If you can't see it, you can't operate it.
- **Performance** — *fast enough for its purpose?* Profile first, then cache/batch/parallelize/kill N+1s. "Fast enough" is the NFR, not ego.
- **Cost** — *economically sane to run?* Right-sizing, autoscaling with caps, bounded retries/queues, budget alerts.
- **Maintainability** — *can humans (and Claude) safely change it next quarter?* Small modules, clear names, types, tests, docs, ADRs, runbook. The cumulative payoff of the whole discipline.

## Scaling Ladder: Script -> Distributed System

The same Loop builds a 100-line script and a multi-service platform — the Pillars just intensify:

1. **Single script** — correctness, basic validation, a few tests.
2. **Library** — clean interfaces, full tests, docs, semver. (+ testability, contract stability.)
3. **Single-process app / API** — persistence, structured errors, logging, config, health check, API contract. (+ durability, observability, security basics, governance if PII.)
4. **Multi-instance service** — statelessness, shared datastore, metrics, graceful shutdown, load balancing, CI/CD. (+ scalability, stronger reliability, delivery pipeline.)
5. **Distributed system** — service boundaries, retries/idempotency/circuit breakers, queues + backpressure, distributed tracing, explicit consistency model, tested recovery, autoscaling w/ cost caps, full compliance. (+ all Pillars at max.)

Climbing a rung -> **return to Phase 1 and re-state the NFRs.** A design correct at rung 3 can be wrong at rung 5; re-design, don't bolt on.
