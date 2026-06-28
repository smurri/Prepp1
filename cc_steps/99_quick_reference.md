# Quick Reference + Complete Mental Model

## Complete Mental Model

```
-2  TRIAGE     [plan]  throwaway / prototype / product -> right-size the rest
-1  CONTEXT    [edit]  CLAUDE.md, toolchain, clean branch                (once)
 0  ROLE       [plan]  operational rules; DESIGN-ONLY = Plan Mode
 1  SPEC       [plan]  product def + open Qs + NFRs   -> commit, /clear
 1.5 TECH      [plan]  language, store, architecture, API, build/buy -> ADRs
 2  DESIGN     [plan]  modules, typed models, contracts, data flow, 2 options
 3  VALIDATE   [plan]  adversarial critique (Pillars + OWASP) -> LOOP to no high-sev
 4  FREEZE     [plan]  lock design + vertical slices + build order -> commit, /clear
 5  IMPLEMENT  [edit]  slice-by-slice, walking skeleton first -> LOOP to green, commit
 6  TEST       [edit]  spec-driven, separate, all categories
 7  DEBUG      [edit]  root-cause-first -> LOOP to green x2, protect the tests
 8  HARDEN     [edit]  reliability/scale/durability/consistency/security/
                       governance/observability/perf/cost/maintainability
 8.5 DELIVER   [edit->human] CI, environments, deploy+rollback, IaC, secrets-vault,
                       feature flags, reversible migrations
 9  REVIEW     [plan]  drift + Pillar + OWASP check -> HUMAN merges/deploys
10  OPERATE    [ ]     monitoring, SLOs, alerts, runbook, incidents, data lifecycle
                       -> feedback flows into the next spec

MODES: plan = read-only thinking; edit = build w/ per-step approval;
       auto-accept = trusted mechanical only; YOLO = containers only, never host
THROUGHOUT: iterate-to-gate; files-are-memory (/clear,/compact,commit);
            human-owns-irreversibility; right-size to the NFRs
```

## What Separates Staff-Level Use

- **Context is the product.** A precise `CLAUDE.md` and tight scope beat clever prompting. Context-engineering, not prompt-engineering.
- **Modes are gates the tool enforces.** Plan Mode *is* design-only; default mode *is* reviewed implementation. Use them; don't rely on willpower.
- **Gates, not vibes.** Every phase exits through a checkable condition you loop on.
- **Files are memory.** Each gate leaves a committed artifact — which lets you `/clear` between phases for sharper, cheaper output.
- **Decide the foundations on purpose.** Language, datastore, architecture, build-vs-buy — against NFRs, defaulting to boring and proven. The one-way doors.
- **You review everything.** An AI dev team with no code review is a faster bug generator.
- **Vertical slices, walking skeleton first.** Working software early beats perfect components late.
- **The Pillars are requirements, not afterthoughts.** Designed in (2-3), verified in hardening (8).
- **Stop rules for irreversibility.** Merges, deletes, deploys, schema changes, migrations, secrets — human, every time.
- **Shipping is the start.** Phase 10 closes the loop: production reality feeds the next spec.

## Cheat Sheet

**Before building:** triage the tier; `CLAUDE.md` written; toolchain verified; clean branch; Plan Mode on.

**Modes:** `Shift+Tab` cycles **edit -> auto-accept -> plan**. Think in plan, build in edit, never YOLO on your host.

**Per phase:** state the gate -> loop until PASS -> commit the artifact -> `/clear`.

**Foundational choices (1.5):** language; datastore (default PostgreSQL); architecture (default modular monolith); sync/async; API style (default REST); build-vs-buy (buy auth & payments) — each tied to an NFR, recorded as an ADR.

**Per slice:** follow frozen interfaces; no extra features; validate inputs; lint + tests green; review the diff; commit.

**When debugging:** root cause before fix; fix code not tests; STOP if the design is wrong.

**Security:** walk OWASP Top 10 in design and again in review; authorize every path; secrets in a vault; all input hostile.

**Before done:** Pillars reviewed vs NFRs; CI green; rollback proven; runbook written; *you* read the diff and run the suite.

**After shipping:** monitoring, alerts, SLOs, data lifecycle live; production feedback -> next spec.

**Always:** files are memory; one concern per prompt; human owns every irreversible action; right-size to the stakes.
