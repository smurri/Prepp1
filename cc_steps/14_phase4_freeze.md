# Phase 4 — Design Freeze + Decomposition

**Mode: Plan.** Lock the blueprint, then break it into shippable pieces.

```
Finalize the architecture with all validation fixes. Then decompose into work.

Constraints:
- simplicity prioritized; no speculative abstractions
- record key tradeoffs as ADRs
- DECOMPOSE into VERTICAL SLICES: each slice is a thin end-to-end path delivering
  one working capability (input -> logic -> storage -> output), not a horizontal
  layer. Sequence so a working skeleton exists after slice 1.
- list slice build order and dependencies
- note decisions deferred to implementation time
```

**Vertical slices, not horizontal layers.** Build one thin path all the way through first (a "walking skeleton"), then widen. Gets you working software in hours, surfaces integration problems early, always demoable. The opposite — all models, then all services, then all endpoints — leaves you with nothing that runs until the very end.

**Exit gate:** design finalized; vertical slices + build order listed; ADRs recorded. **Commit `docs/design.md`. Then `/clear`.**
