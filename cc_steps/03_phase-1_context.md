# Phase -1 — Context Setup

**Mode: Default.** Done **once per project**; pays back every prompt after. Skipping it is why people complain Claude "forgets the conventions" — it never knew them.

## Create `CLAUDE.md` at the repo root
Auto-loaded into context (Plan Mode reads it too, so it shapes every plan). The single highest-leverage artifact. Include:

- **Stack & versions** — language, framework, runtime, package manager, key libraries.
- **Commands** — exactly how to install, run, build, lint, type-check, test. Wrong commands mean blind work.
- **Directory map** — what lives where, one line each. (Monorepo: add subdirectory `CLAUDE.md` files for per-area rules.)
- **Conventions** — naming, formatting, error-handling patterns, test structure, commit style.
- **"Never touch" list** — generated files, vendored code, migrations, fragile areas.
- **Domain context** — the 3-5 non-obvious things about your domain.
- **Non-functional baseline** — target latency, expected scale, availability target, data-sensitivity class.

## Verify the toolchain
Confirm Claude can run `test`, `lint`, `build`, type-check. A Claude that can't run your tests codes with its eyes closed — it can't close its own feedback loop and iterate-to-gate collapses.

## Start clean
Dedicated feature branch from clean git state. Every phase ends at a commit: cheap rollback, clean `git bisect`, readable history.

**Exit gate:** `CLAUDE.md` accurate; Claude ran your test command once; clean branch.
