---
name: ticket-workflow
description: Phase-gated workflow for working an engineering ticket — read-only investigation first, minimal implementation only after ownership is confirmed, then PR notes and handoff. Use when starting, implementing, or finishing a ticket, or when the user names a ticket ID.
---

# Ticket Workflow

Three gated phases. Never skip ahead: the gate out of each phase is explicit.

**Workspace mode**: if a ticket workspace exists (a directory with
`ecosystem.md` and `tickets/<TICKET-ID>/`), read `ecosystem.md`,
`conventions.md`, and the ticket's files before starting, and record results
into the ticket files as you go.
**Standalone mode**: no workspace — follow the same phases, keep the records
in your responses (or a scratch file if the user wants persistence), and
infer conventions from the repo (recent commits, PR history).

## Phase 1 — Investigate (read-only)

Goal: root cause and owner repo/module, before any edit.

1. Understand the user-visible problem or business need.
2. Trace the likely flow across the code (use `ecosystem.md`'s flow map if
   present; otherwise trace from the entry point yourself).
3. Identify the most likely owner repo/module.
4. Separate **facts** (evidence-backed), **hypotheses** (unconfirmed), and
   **decisions**. Never promote a hypothesis without evidence.
5. Record findings, evidence, open questions, next steps
   (→ `investigation.md` in workspace mode).

**Gate**: summarize confirmed facts, likely root cause, owner, and next
safest action. If root cause or owner is still a guess, stay in Phase 1.

## Phase 2 — Implement (minimal)

Before editing:

1. Confirm the owner repo/module.
2. Check current directory, branch, `git status`, and current diff.
3. Summarize the intended minimal change.

Then make the smallest safe change.

Rules:
- No unrelated refactors or formatting.
- Don't touch multiple repos/modules unless the investigation justifies it.
- Preserve existing behavior unless the ticket requires changing it.
- Record what changed and how it was tested
  (→ `implementation.md`, `test.md`).

**Gate**: change applied, checks run (typecheck/lint/tests as the repo
defines), results reported honestly — failures included.

## Phase 3 — Finish

Generate (→ `pr.md` in workspace mode):

1. PR title and description (follow `conventions.md` or repo precedent)
2. Commit message
3. Test notes
4. Short status update for the team channel

Then save a handoff — use the `handoff` skill. A ticket isn't finished
until the next session could continue it cold.
