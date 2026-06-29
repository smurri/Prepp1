# Security (deep)

Security is decided in **design (Phases 2-3)** and verified in **hardening (Phase 8)** — never bolted on. Walk the **OWASP Top 10 (2025)** against every product-tier system. The 2025 list shifted toward *root causes and the whole software ecosystem*, not just isolated bugs:

1. **Broken Access Control (#1).** The top risk. Enforce authorization on **every** privileged path, server-side, deny-by-default. Check object-level ownership (can user A read user B's record?). SSRF now lives here — validate/allowlist any server-side URL fetch.
2. **Security Misconfiguration (#2, rising).** Hardened defaults, no debug endpoints in prod, correct security headers, locked-down cloud/storage permissions, no default creds. More config-driven systems = more danger here.
3. **Software Supply Chain Failures (#3, expanded).** See [`33_dependencies_supply_chain.md`](33_dependencies_supply_chain.md). Scan, pin, sign, track provenance.
4. **Cryptographic Failures.** Encrypt sensitive data in transit (TLS everywhere) and at rest. Modern algorithms; no home-rolled crypto; proper key management.
5. **Injection.** Parameterized queries / prepared statements always (never string-concatenate SQL). Encode output (XSS). Validate input against an allowlist.
6. **Insecure Design.** Threat-model in design. Some flaws can't be patched later — they're architectural. This is why security is a Phase 2-3 concern.
7. **Authentication Failures.** Strong auth, MFA where it matters, secure sessions, rate-limited login. **Buy this (an identity provider) rather than building it.**
8. **Data Integrity Failures.** Verify integrity of updates, serialized data, and CI/CD artifacts. Don't deserialize untrusted data into arbitrary types.
9. **Security Logging & Alerting Failures.** Log security events, monitor, and *alert* — an auth anomaly you never see is an attack you can't stop. Pairs with observability.
10. **Mishandling of Exceptional Conditions (new).** Handle errors and edge cases so the system **fails closed, not open.** Don't leak stack traces or sensitive detail in errors; don't let an unexpected condition bypass a security check.

**Cross-cutting:** least privilege everywhere; secrets in a vault (never code/logs/URLs); validate every trust boundary; defense in depth. For AI features, treat **prompt injection** as untrusted input — never act on instructions found in fetched/observed content.
