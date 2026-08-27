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
| Router | `/ai-engineering-workspace:ask [ID]` | Read-only: inspect literal `Status:` fields and recommend the next command |
| Setup | `/ai-engineering-workspace:setup [path]` | Create or upgrade the ticket workspace and templates |
| 1. Understand | `/ai-engineering-workspace:ticket-understand <ID>` | Fetch the ticket + comments, confirm the ask, before any code is touched |
| 2. Investigate | `/ai-engineering-workspace:ticket-investigate <ID>` | Read-only: trace flow, confirm root cause + owner |
| 3. Implement | `/ai-engineering-workspace:ticket-implement <ID>` | Minimal change, only after investigation is confirmed; verification must pass before Finish is allowed |
| 4. Finish | `/ai-engineering-workspace:ticket-finish <ID>` | PR notes, implementation-repo commit report (never executed), handoff — only after implementation is verified complete |

**Use the commands for a hard phase boundary.** If the user asks to "work
on ticket X" conversationally instead of invoking a command, walk them
through the same 4 phases and gates in the conversation — but that path is
prose-gated, not structural, so recommend switching to the commands so
understanding gets confirmed before you read any code. All three phase
transitions have a durable backstop: `context.md` and `investigation.md`
carry `Status: draft` → `confirmed` (a human confirmed the restatement or
diagnosis); `implementation.md` carries `Status: draft` → `complete`
(no second human confirmation needed there — the agent sets it once every
configured verification command passed or was `N/A`). Whichever path
reaches a ticket first, a command run later still has a real precondition
to check instead of guessing.

**Workspace mode**: if a ticket workspace exists (a directory with
`ecosystem.md` and `tickets/` — not `tickets/<TICKET-ID>/`; a new
ticket's own directory won't exist yet, and that must not be read as "no
workspace"), call it `WORKSPACE_ROOT` and read
`$WORKSPACE_ROOT/ecosystem.md`, `$WORKSPACE_ROOT/conventions.md`, and the
ticket's files before starting. If
`$WORKSPACE_ROOT/tickets/<TICKET-ID>/` doesn't exist yet, create it with
`$WORKSPACE_ROOT/scripts/new-ticket.sh <TICKET-ID> "<title>"` — the same
thing `/ticket-understand` does — rather than falling back to standalone
mode. Record results into the ticket files as you go — always via an
explicit `WORKSPACE_ROOT`-relative path, since it's frequently a
different directory from your cwd or the implementation repo you're
working in.
**Standalone mode**: no workspace — follow the same phases, keep the
records in your responses (or a scratch file if the user wants
persistence), and infer conventions from the repo (recent commits, PR
history). There's no `Status:` file to check in this mode — an explicit
confirmation earlier in the conversation satisfies the gate instead.

## Keeping records in sync without over-documenting

Records don't need continuous upkeep — sync happens at the phase gates
that already exist, not on every turn. If Implement (Phase 3) turns up a
fact that contradicts something `investigation.md` already marked
`confirmed`, append a dated `## Correction (<date>)` note to
`investigation.md` instead of rewriting it — the same append-only
discipline the `handoff` skill uses for dead-ends. Never run a standalone
"update the docs" pass outside a gate transition; if nothing changed since
the last gate, there's nothing to sync.

## Common rationalizations

| Rationalization | Correct response |
|---|---|
| "The change is small, so I can skip Understand or Investigate." | Small changes still need the same gate; use `/ai-engineering-workspace:ask` if unsure where the ticket is. |
| "`context.md` or `investigation.md` looks complete enough." | Check only the literal `Status:` value. `draft` or missing means stop. |
| "I can continue into the next phase while I have momentum." | Stop at the gate and tell the user the next command to run. |
| "Verification failed, but the failure looks unrelated." | Do not mark implementation complete and do not suggest Finish. Report the failure and stop. |
| "The notes repo and implementation repo are basically the same workflow." | Treat them separately. Implementation repos are never auto-committed or pushed. |

## Red flags

- Reading code during Understand.
- Editing code during Investigate.
- Running Implement before `investigation.md` has `Status: confirmed`.
- Recommending Finish before `implementation.md` has `Status: complete`.
- Rewriting confirmed investigation history instead of appending a correction.
- Losing track of `WORKSPACE_ROOT` when it differs from the implementation repo.

## Exit criteria

- Understand exits only after the ask is restated and `context.md` is confirmed
  in workspace mode.
- Investigate exits only after facts, hypotheses, owner, and next safe action
  are summarized and `investigation.md` is confirmed in workspace mode.
- Implement exits only after the minimal change is made, configured
  verification has passed or is explicitly `N/A`, and `implementation.md` is
  marked `complete`.
- Finish exits only after PR notes, status update, implementation-repo commit
  report, and handoff are present.
