# Dependencies & Supply Chain

**Software Supply Chain Failures is now A03 on the OWASP Top 10 (2025)** — a top-tier risk, not housekeeping.

- **Choosing a library.** Maintained (recent commits, issue response)? Widely used (downloads, dependents)? Reasonable transitive footprint? Compatible license? Does one thing well? Prefer fewer, well-vetted dependencies.
- **Lockfiles.** Commit them. Builds must be reproducible — same inputs, same artifact, every time.
- **Vulnerability scanning.** Automated dependency scanning in CI (Dependabot, `npm audit`, Snyk). Patch known CVEs promptly.
- **License compliance.** Check before adopting — a copyleft license can have obligations incompatible with your product. Automate it.
- **Provenance & pinning.** Pin versions; prefer signed artifacts; beware typosquatting and compromised packages. The build pipeline itself is attack surface.
- **Build vs buy vs DIY (revisited).** Each dependency is a permanent liability. Sometimes 30 lines of your own beats a 200-dependency package; sometimes a battle-tested library beats your clever code. Decide deliberately.
