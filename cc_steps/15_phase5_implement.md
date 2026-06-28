# Phase 5 — Implementation

**Mode: Default/Edit** (review each diff). Never "build the app." Implement one slice, drive it to green, review, commit, next.

```
Implement slice/module: <name>, per the frozen design and chosen interfaces.

Rules:
- no extra features beyond the spec
- small functions, type hints, docstrings
- validate inputs at every boundary; fail loudly and clearly
- inline handling for the failure modes identified in validation
- when written, run its lint and tests and fix until green
- if the design turns out wrong here, STOP and tell me — don't silently redesign
```

**Per-slice exit gate:** compiles, lints clean, own tests green, diff reviewed, committed. Loop until true, then next slice in dependency order.

## Non-negotiables
- **Review every diff like a PR.** Rubber-stamping replaces engineering with fast bug-generation — the habit that most separates good Claude Code users from bad.
- **Commit after each green slice.** Cheap rollback, clean bisects, a session you can `/clear`.
- **Hunt scope creep aggressively.** Claude will add caching, config, abstractions you didn't ask for — strip them.
- **Use Auto-Accept only for trusted, pre-planned mechanical work**, still reviewed at the commit.
