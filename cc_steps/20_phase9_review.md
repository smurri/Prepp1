# Phase 9 — Final Review

**Mode: Plan** (fresh context). One skeptical pass before done.

```
Review as a skeptical engineer who did NOT write this.
- Does the implementation match the frozen spec? List any drift.
- Walk each Pillar against the NFRs — is each adequately addressed?
- Security: re-run the OWASP Top 10 mentally against the final code.
- What breaks in production that tests don't cover?
- What did we cut, defer, or stub? List as known limitations.
- Summarize the change as a PR description.
```

Then **you** read the full diff, run the suite yourself, and make the merge/deploy call. Claude proposes and writes the PR; **you** perform the irreversible action. Claude proposes, human commits — the spine of the whole discipline.

**Exit gate:** no unexplained drift; Pillars reviewed; limitations documented; human read the diff and ran the suite.
