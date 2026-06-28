# Phase 8.5 — Delivery & Deployment

**Mode: Default for setup; the deploy itself is a Human action.** Working code that can't be shipped safely isn't done.

- **Environments.** Separate dev / staging / prod with parity. Never test in prod.
- **CI pipeline.** On every push: install -> lint -> type-check -> test -> security scan -> build. Red CI blocks merge. The automated form of the loop's gates.
- **CD / deploy strategy.** Pick one and make rollback trivial: **blue-green** (two environments, switch traffic), **canary** (route a small % first, watch, widen), or **rolling**. **The rollback path must be tested before you need it.**
- **Infrastructure as Code.** Infra in version-controlled files (Terraform, etc.), not clicked together by hand. Reproducible, reviewable, rollback-able.
- **Secrets as a system.** Not "don't hardcode" — a real secret store (vault / cloud secret manager), injected at runtime, rotated, never in git, never in logs. Scan repo + history for leaks.
- **Feature flags.** Decouple deploy from release: ship dark, flip on for a cohort, kill instantly if it misbehaves — no redeploy.
- **Migrations.** Forward-only, reversible where possible, **decoupled from code deploy** (expand-migrate-contract) so you can roll back code without orphaning data.

**Exit gate:** CI green; deploy succeeds to staging; rollback proven; secrets in a vault; migrations reversible.
