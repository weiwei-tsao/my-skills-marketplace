# AI-Assisted Engineering Workspace

This repository is not just a notes repo. It is a structured workspace that helps AI coding agents understand, investigate, implement, test, and hand off engineering tickets safely.

## Core idea

Each ticket should be treated as an independent context package:

```text
Problem context + repo ownership + investigation evidence + next safe action
```

The goal is to make every Claude Code / Cursor / Codex session start with the right context and avoid:

- repeating the same investigation
- editing the wrong repository
- mixing facts with guesses
- making broad refactors
- losing UAT / PROD / acceptance status
- carrying huge sessions until context becomes expensive or unreliable

## Recommended workflow

### 1. Create a new ticket workspace

```bash
./scripts/new-ticket.sh PUB-11743 "TP top-right nav fallback text"
```

This creates:

```text
tickets/PUB-11743/
  context.md
  investigation.md
  implementation.md
  test.md
  handoff.md
  pr.md
  timeline.md
```

### 2. Start with read-only investigation

Use:

```text
prompts/01-start-investigation.md
```

Do not let the AI edit code until repo ownership and root cause are reasonably clear.

### 3. Implement only after investigation

Use:

```text
prompts/02-implement.md
```

The AI should read the ticket files, check branch/status/diff, then make the smallest safe change.

### 4. Finish with PR notes and handoff

Use:

```text
prompts/03-finish-ticket.md
```

The AI should generate PR description, Slack update, test notes, and update `handoff.md`.

## File responsibilities

| File | Purpose |
|---|---|
| `ecosystem.md` | Global repo map and ownership rules |
| `conventions.md` | Team communication, PR, test, deploy conventions |
| `tickets/<ID>/context.md` | What the ticket is about |
| `tickets/<ID>/investigation.md` | Facts, evidence, hypotheses, root cause |
| `tickets/<ID>/implementation.md` | Small safe implementation plan and actual changes |
| `tickets/<ID>/test.md` | Local/UAT/regression/acceptance checklist |
| `tickets/<ID>/handoff.md` | Current state for the next AI session |
| `tickets/<ID>/pr.md` | PR title, description, Slack update |
| `tickets/<ID>/timeline.md` | Human timeline: Slack, UAT, deploy, acceptance |

## Golden rule

Before asking AI to code, make it read:

```text
- ecosystem.md
- conventions.md
- tickets/<ID>/context.md
- tickets/<ID>/handoff.md
- tickets/<ID>/investigation.md
```

Then ask it to summarize its understanding and inspect git state before editing.
