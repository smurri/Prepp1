# Phase 10 — Operate

Shipping is the start, not the end. For anything in the **product** tier:

- **Monitoring & SLOs.** Define "healthy" as numbers (e.g. 99.9% availability, p99 < 300ms), dashboard them, alert when at risk.
- **Alerting & on-call.** Alerts fire on *symptoms users feel*, route to a human, are actionable — every alert has a runbook entry. Page on real problems only; alert fatigue kills response.
- **Runbook triggers.** Not just "how the system works" — "when X alert fires, do Y." Write one entry per top failure mode from validation.
- **Incident response.** A known process: detect -> mitigate -> communicate -> resolve -> blameless post-mortem -> fix the class of bug. Practice before you need it.
- **Data lifecycle.** Retention windows, deletion on request (GDPR/CCPA), PII minimization, backups aging out — automated, not manual.
- **Feedback loop.** Production reality (errors, latency, usage) flows back into the next spec. The loop is a cycle, not a line.

**Exit gate (ongoing):** monitoring live, alerts actionable, runbook entries exist, someone owns on-call.
