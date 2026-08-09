---
name: ticket-workflow
description: Phase-gated workflow for working an engineering ticket — read-only investigation first, minimal implementation only after ownership is confirmed, then PR notes and handoff. Use when starting, implementing, or finishing a ticket, or when the user names a ticket ID.
---

# Ticket Workflow

Four gated phases, each with its own slash command for a hard,
user-controlled phase boundary — the agent can't see a later phase's
instructions until the user runs that phase's command, so it can't
self-chain ahead.

| Phase | Command | Purpose |
|---|---|---|
| 1. Understand | `/ai-engineering-workspace:ticket-understand <ID>` | Fetch the ticket + comments, confirm the ask, before any code is touched |
| 2. Investigate | `/ai-engineering-workspace:ticket-investigate <ID>` | Read-only: trace flow, confirm root cause + owner |
| 3. Implement | `/ai-engineering-workspace:ticket-implement <ID>` | Minimal change, only after investigation is confirmed |
| 4. Finish | `/ai-engineering-workspace:ticket-finish <ID>` | PR notes, commit (user-confirmed, via `git-commit` skill if installed), handoff |

**Use the commands for a hard phase boundary.** If the user asks to "work
on ticket X" conversationally instead of invoking a command, walk them
through the same 4 phases and gates in the conversation — but that path is
prose-gated, not structural, so recommend switching to the commands so
understanding gets confirmed before you read any code. Both paths write
the same `Status:` field in `context.md`/`investigation.md` (`draft` →
`confirmed`), so whichever path reaches a ticket first, a command run
later still has a real precondition to check instead of guessing.

**Workspace mode**: if a ticket workspace exists (a directory with
`ecosystem.md` and `tickets/<TICKET-ID>/`), read `ecosystem.md`,
`conventions.md`, and the ticket's files before starting, and record
results into the ticket files as you go.
**Standalone mode**: no workspace — follow the same phases, keep the
records in your responses (or a scratch file if the user wants
persistence), and infer conventions from the repo (recent commits, PR
history). There's no `Status:` file to check in this mode — an explicit
confirmation earlier in the conversation satisfies the gate instead.
