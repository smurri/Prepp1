# Phase 8 — Hardening

**Mode: Default.** The system works; now make it survive production. The Pillars ([`36_pillars.md`](36_pillars.md)) become an explicit checklist, sized to the NFRs.

```
Harden for production. Address each Pillar:

RELIABILITY — timeouts on every external call; retries w/ backoff + jitter;
  idempotency on anything retried; circuit breakers; graceful degradation.
SCALABILITY — find the real bottleneck FIRST (measure), then fix it;
  statelessness; bounded queues; backpressure; connection pooling.
DURABILITY — what must never be lost, how it's backed up, a TESTED restore.
CONSISTENCY — unambiguous source of truth; transactions/locks where invariants hold.
SECURITY — full OWASP pass: access control on every path, input validation,
  parameterized queries, secrets from a vault, no PII in logs.
GOVERNANCE — data retention + deletion path, audit logging, compliance controls.
OBSERVABILITY — structured logs, metrics (latency/error/throughput/saturation),
  health checks, correlation IDs, traces.
PERFORMANCE — optimize the measured hot path; kill N+1s.
COST — bounded resource use; budget alerts; no unbounded retries/queues.
MAINTAINABILITY — remove duplication/dead code; full types; docs; a runbook.
```

**Performance pointer:** "improve performance" with no measurement invites random micro-optimization. Force the sequence: *identify the bottleneck with evidence, then optimize that specific thing.*

See also: [`34_security.md`](34_security.md), [`35_governance_compliance.md`](35_governance_compliance.md), [`31_data_layer.md`](31_data_layer.md).

**Exit gate:** every applicable Pillar gate met; types + linter clean; runs from a fresh checkout; zero secrets in code; runbook drafted.
