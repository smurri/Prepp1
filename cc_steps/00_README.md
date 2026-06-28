# Claude Code Engineering Steps

The Staff+ playbook for building any app with Claude Code, split into one file per phase. Read [`01_meta_and_modes.md`](01_meta_and_modes.md) first — it holds the rules and the mode mapping that govern every phase.

> You are not *asking for code*. You are *running a software delivery pipeline* in which Claude is a fast, tireless, occasionally overconfident team of engineers — and **you are the tech lead who owns every gate and every irreversible decision.**

## How to use this folder

- Point Claude at the relevant file per phase, e.g. *"Follow `claude_steps/10_phase1_spec.md`."*
- Each phase is a **loop with an exit gate**, not a one-shot step. Don't advance until the gate passes.
- Each gate leaves a **committed artifact** (spec, design, code, tests). Files are memory; `/clear` between phases.
- **You** own every irreversible action (merge, deploy, delete, migration, secrets).

## The Loop

```
-2 TRIAGE -> -1 CONTEXT -> 0 ROLE -> 1 SPEC -> 1.5 TECH -> 2 DESIGN -> 3 VALIDATE
   -> 4 FREEZE -> 5 IMPLEMENT -> 6 TEST -> 7 DEBUG -> 8 HARDEN -> 8.5 DELIVER
   -> 9 REVIEW -> 10 OPERATE
```

## Files

**Foundations**
- [`01_meta_and_modes.md`](01_meta_and_modes.md) — load-bearing ideas, meta-rules, Claude Code mode->phase mapping

**Phases**
- [`02_phase-2_triage.md`](02_phase-2_triage.md) — right-size: throwaway / prototype / product
- [`03_phase-1_context.md`](03_phase-1_context.md) — `CLAUDE.md`, toolchain, clean branch
- [`04_phase0_role.md`](04_phase0_role.md) — role setting + guardrails
- [`10_phase1_spec.md`](10_phase1_spec.md) — problem understanding, NFRs (no code)
- [`11_phase1.5_tech.md`](11_phase1.5_tech.md) — technology selection
- [`12_phase2_design.md`](12_phase2_design.md) — system design / architecture
- [`13_phase3_validate.md`](13_phase3_validate.md) — adversarial design validation
- [`14_phase4_freeze.md`](14_phase4_freeze.md) — freeze + vertical-slice decomposition
- [`15_phase5_implement.md`](15_phase5_implement.md) — controlled, slice-by-slice
- [`16_phase6_test.md`](16_phase6_test.md) — test design (separate phase)
- [`17_phase7_debug.md`](17_phase7_debug.md) — execute + debug loop
- [`18_phase8_harden.md`](18_phase8_harden.md) — hardening (the Pillars)
- [`19_phase8.5_deliver.md`](19_phase8.5_deliver.md) — CI/CD, deploy, rollback, secrets
- [`20_phase9_review.md`](20_phase9_review.md) — final skeptical review
- [`21_phase10_operate.md`](21_phase10_operate.md) — monitoring, SLOs, incidents

**Cross-cutting references** (used across phases)
- [`30_decision_frameworks.md`](30_decision_frameworks.md) — language, SQL vs NoSQL, architecture, API style, build-vs-buy, hosting
- [`31_data_layer.md`](31_data_layer.md) — schema, indexing, N+1, transactions, migrations, caching
- [`32_api_design.md`](32_api_design.md) — versioning, pagination, errors, rate limiting, idempotency
- [`33_dependencies_supply_chain.md`](33_dependencies_supply_chain.md) — choosing libs, lockfiles, scanning, licenses
- [`34_security.md`](34_security.md) — OWASP Top 10 (2025), deep
- [`35_governance_compliance.md`](35_governance_compliance.md) — GDPR/HIPAA/PCI/SOC2, data lifecycle, audit, a11y/i18n
- [`36_pillars.md`](36_pillars.md) — the engineering Pillars + scaling ladder
- [`99_quick_reference.md`](99_quick_reference.md) — one-page cheat sheet + full mental model
