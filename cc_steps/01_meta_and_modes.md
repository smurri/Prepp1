# 01 — Meta-Rules & Claude Code Modes

Read this first. These rules and the mode mapping govern every phase.

## The Load-Bearing Ideas

1. **Iterate-to-gate.** No phase ends because Claude produced output. It ends when output passes an explicit, checkable exit condition. Every phase is a loop, not a step.
2. **Files are memory; the chat is scratch.** Every gate leaves a committed artifact (spec, design doc, plan file, code, tests, runbook). That artifact carries state forward — the quality strategy *and* the token strategy.
3. **The human owns irreversibility.** Merges, deletes, deploys, schema changes, migrations, anything touching secrets or money — your decision, every time, no matter how confident Claude sounds.
4. **Right-size everything.** A throwaway script and a payment platform are different sports. Match depth to stakes. Over-engineering a prototype is as much a failure as under-engineering a bank.

## Claude Code Modes -> Phase Mapping

Claude Code has **permission modes** that physically constrain what Claude can do. Cycle the three core modes with **Shift+Tab** (Windows native installs may need **Alt+M** or `/plan`). The status line shows the current mode — glance at it before every risky instruction.

| Mode | What it allows | Phases |
|---|---|---|
| **Plan Mode** (`plan mode on`) | **Read-only sandbox.** Read, search, grep, web-fetch — but no file writes, no shell, no tests, no git. Enforced at the tool level. | -2, 1, 1.5, 2, 3, 9 — the *thinking* phases |
| **Default / Edit** | Edits and runs, but **asks permission** on first file write and first shell command. The safe middle ground. | 5, 6, 7, 8 — the *building* phases |
| **Auto-Accept** (`accept edits on`) | Skips edit/basic-fs prompts. `git push`, `npm test`, `curl` still prompt. Fast, but you've stopped reviewing diffs live. | Narrow: a trusted pre-planned slice, or mechanical work reviewed at the commit |
| **Auto** (flag-only) | Classifier checks every action; safe ones run silently, risky ones (deploys, mass deletion, force-push, `curl \| bash`) blocked. Plan-tier feature. | Safer than auto-accept for long autonomous stretches — still not for irreversible actions |
| **bypassPermissions / YOLO** (`--dangerously-skip-permissions`) | **Everything runs, no prompts, no classifier, no guardrails.** | **Never on your host.** Containers/VMs only. No protection against prompt injection. |

### The canonical workflow (how Claude Code's own creators use it)
Start in **Plan Mode**, iterate on the plan until it's right (edit the plan file directly with **Ctrl+G** rather than describing changes in chat), then **Shift+Tab into Default/Edit** and tell Claude to execute. Plan first, build second — the planning phases are the cheapest in tokens and the most valuable in outcome.

### Mode discipline = the loop's gates, enforced by the tool
- The **DESIGN-ONLY** rule (Phase 0) is *literally* Plan Mode. You don't trust Claude to hold back — the mode makes writing impossible.
- Plans live in `~/.claude/plans/` as markdown, surviving `/clear` and compaction. That's your design artifact — file-as-memory, built in.
- **Dual-Claude** for security-sensitive work: Session A writes the plan in Plan Mode; a *fresh* Session B with no investment critiques it. The independent reviewer catches what the author can't. (Phase 3, operationalized.)
- Gotcha: cycling *through* Plan Mode with Shift+Tab can inject a "work without stopping for clarifying questions" reminder even if you never approved a plan. If you want clarifying questions, enter Plan Mode deliberately.

## The Meta-Rules

### Iterate-to-gate
The default failure mode of AI-assisted development is **accepting the first output**. Every phase has an **exit gate** — a concrete condition. Loop until it's met. Tell Claude up front:

> "Iterate on this until **[gate]**. After each revision, self-check against the gate and tell me PASS or FAIL — if FAIL, what's still missing. Don't move on until it's PASS and I confirm."

### Token economy is an engineering skill
- **One concern per prompt.** Bundled asks get shallow work on each.
- **`/clear` between phases.** The committed artifact carries state — Claude re-reads the file, not the whole chat.
- **`/compact` mid-phase** when a loop sprawls.
- **Plan Mode is cheap** (no tools run) — do expensive thinking there.
- **Point to paths, don't re-paste.** Claude has file tools.
- **Kill bad loops early.** Re-running a flawed direction amplifies the mistake.

### Human-owns-irreversibility
You execute or approve anything that can't be cheaply undone: merges to main, force-pushes, history-rewriting rebases, deletions, dropping data, deploys, releases, publishing packages, schema changes and migrations, anything touching secrets/credentials/money, and changes to access control, CI, or production settings. **Confidence is not authorization.** Never run irreversible work in auto-accept or YOLO.

### Other useful tools
`/clear` (fresh context between phases) · `/compact` (summarize mid-phase) · `/permissions` (pre-allow/deny commands) · subdirectory `CLAUDE.md` files (per-area conventions in a monorepo).
