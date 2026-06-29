# Phase -2 — Triage

**Mode: Plan.** Right-size before you start. The biggest waste in software is applying production rigor to a throwaway, or throwaway rigor to a production system. Decide the tier first — it sets how much of the loop you run.

| Tier | What it is | What you run | What you skip |
|---|---|---|---|
| **Throwaway** | One-off script, data munge, spike to learn | Phases 0, 1 (mental), 5. Minimal tests. | Design docs, hardening, CI, ops |
| **Prototype** | Demo, PoC, internal tool, hackathon | Compressed loop: light spec, quick design, build, smoke tests | Full validation, scale/HA, deep security |
| **Product** | Real users depend on it; touches money/PII | The **full loop**, all Pillars sized to NFRs | Nothing — but right-size each Pillar |

Ask up front: *Who depends on this? What breaks if it's wrong? How long will it live?*

A "quick script" that quietly becomes load-bearing is the classic path to disaster — when a throwaway crosses into product, **stop and re-enter the loop at Phase 1**, don't keep bolting onto a spike.

**Exit gate:** tier chosen; everyone agrees how much rigor this needs.
