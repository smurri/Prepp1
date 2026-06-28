# Phase 3 — Design Validation

**Mode: Plan** (ideally a **fresh Dual-Claude session** that didn't write the design). The phase beginners skip — where engineering judgment lives.

```
Critically evaluate the chosen design as an adversarial reviewer whose job is to
find everything wrong with it.

Check:
- edge cases and boundary conditions
- failure modes — and whether each is actually handled
- ambiguity / underspecified behavior
- RELIABILITY: partial failure, retries, timeouts, idempotency
- SCALABILITY: the bottleneck at 10x and 100x; N+1 query traps
- DURABILITY: can we lose data? backup/recovery story?
- CONSISTENCY: race conditions; is the source of truth unambiguous?
- SECURITY: walk the OWASP Top 10 against this design — broken access control,
  injection, SSRF, secrets, supply-chain, misconfiguration, error handling
- GOVERNANCE: PII handling, data retention/deletion, audit, compliance regime
- testability — can each module be tested in isolation?
- missing components, unhandled states, hidden coupling

For each issue: severity (high/med/low) + concrete fix.
```

**Iterate — loop this one.** Validate -> patch -> re-validate. The first pass finds obvious problems; the second finds problems the fixes introduced. Continue until no high-severity issue stands open and mediums are consciously accepted or deferred.

See also: [`34_security.md`](34_security.md), [`35_governance_compliance.md`](35_governance_compliance.md), [`36_pillars.md`](36_pillars.md).

**Exit gate:** no high-severity issue unaddressed; remaining issues explicitly accepted with rationale.
