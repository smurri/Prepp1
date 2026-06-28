# Phase 7 — Execution + Debug Loop

**Mode: Default.**

```
Run the full suite. For each failure:
- state the ROOT CAUSE before writing any fix
- fix the implementation, not the test (unless the test is genuinely wrong — justify)
- don't change the frozen design unless strictly necessary; if it is, STOP and propose first
- re-run until green. Also run linter and type-checker; they must be clean.
```

**Two failure modes this prevents:**
- *Symptom-patching* — without "root cause first," Claude papers over failures (catch-and-ignore, special-casing) and the bug survives.
- *Test-weakening* — "make it pass" can mean "weaken the assertion." Guard the tests explicitly: fixes go in the implementation; tests change only when genuinely wrong, with a stated reason.

If the loop sprawls, `/compact` and continue. Many rounds without convergence signals the design may be wrong — escalate via the STOP rule.

**Exit gate:** full suite green twice, no flakes; linter + types clean. **Commit.**
