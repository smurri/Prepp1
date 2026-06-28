# Governance & Compliance

For anything touching personal, financial, or health data, governance is a hard requirement:

- **Know your regime.** **GDPR** (EU — consent, deletion, portability, breach notification), **CCPA/CPRA** (California), **HIPAA** (US health), **PCI-DSS** (card data — usually: don't store it, use a provider), **SOC 2** (controls attestation for B2B). Identify which apply *in Phase 1* — they shape the design.
- **Data classification.** Know what's sensitive (PII, PHI, secrets); minimize collection, restrict access, encrypt, log access.
- **Data lifecycle & residency.** Retention limits, automated deletion (incl. right-to-be-forgotten), and where data is legally allowed to live.
- **Audit trail.** Tamper-evident logs of who did what to sensitive data and when. Required by most regimes, invaluable in incidents.
- **Access governance.** Role-based access, least privilege, periodic access review, separation of duties for sensitive ops.
- **Accessibility & i18n (user-facing apps).** **WCAG** accessibility is a legal requirement in many jurisdictions and simply correct. Plan internationalization (unicode, locale, timezones, translatable strings) early — retrofitting is painful.
