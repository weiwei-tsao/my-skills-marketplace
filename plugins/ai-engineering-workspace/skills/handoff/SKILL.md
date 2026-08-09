---
name: handoff
description: Persist and restore working context across AI sessions on a ticket. Use when ending or pausing work (save), when starting where a handoff file exists (resume), or on "pick up where I left off" / "wrap up this session" / "save handoff".
---

# Handoff: cross-session context persistence

A new session starts with zero memory. This skill serializes working state
into a handoff file at session end and restores it at the next start. The
value comes from the file **replacing** the old session's history — it must
stay far smaller than the history it replaces (~1500–2500 tokens).

**File location**:
- If the caller invoking this skill supplies an explicit target path
  (e.g. a ticket-workflow phase command that already knows
  `$WORKSPACE_ROOT/tickets/<TICKET-ID>/handoff.md`), use that path
  exactly and skip the detection below — the caller's knowledge of where
  the workspace actually lives is more reliable than a fresh cwd check.
- Otherwise, detect it yourself: workspace mode (a `tickets/<TICKET-ID>/`
  folder exists relative to the current directory): `tickets/<TICKET-ID>/handoff.md`.
- Standalone (no caller-supplied target and no workspace detected):
  `.handoff/HANDOFF.md` at repo root (or `.handoff/<TICKET-ID>.md` if
  several tickets are active).

## Core principle: information decays at different rates

| Section | Decay | Rule on resume |
|---|---|---|
| Code facts | Fast | **Verify before trusting** — code may have moved |
| Decisions | Slow | Trust unless the requirement changed |
| Progress | Per-session | The cursor — update every save |
| Dead-ends | Append-only | Never delete; this is the "don't retry" list |

Every code fact MUST carry an anchor (`path/to/file :: symbol`) so it can be
re-checked. No anchor → record it as inference, not fact. Unverifiable
claims launder uncertainty into false confidence.

## `save` — end of session

1. Read the existing handoff file (if any); append, don't overwrite history.
2. Record: current status, completed work, repo + branch + `git status`,
   changed files, diff summary, tests run and results, environment/acceptance
   status, blockers, next steps, do-not-do notes.
3. Anchor every code fact; mark anything unverified as "(inferred)".
4. Progress = done / in-progress / next. Keep "next" actionable enough for a
   cold session; prune superseded items.
5. Reference artifacts (commit, PR, ADR, plan file) by path/ID — don't
   re-transcribe what's already durable elsewhere. The file captures what's
   *only in your head*.
6. If the next step calls for specific skills/tools, name them.
7. Over budget without losing something that lives nowhere else? Split the
   ticket, don't grow the file.

In workspace mode also refresh `investigation.md`, `implementation.md`,
`test.md`, `pr.md`, `timeline.md` if they've drifted.

## `resume` — start of session

1. Read the handoff file.
2. **Verify code facts first**: for each anchor, confirm the file/symbol
   still exists and the relationship holds (grep/read, not memory). Mark
   ✅ confirmed / ⚠️ changed / ❌ gone.
3. Report a short recovery summary: where things stand, what's next, any
   ⚠️/❌ facts needing attention. Never silently act on stale facts.
4. Check current repo, branch, `git status`, and diff.
5. Follow references (commits/PRs/ADRs) when the next step needs them;
   load any skills the file suggests.
6. Continue from "next steps". Don't redo old investigation unless the
   handoff is inconsistent or evidence is missing.

## What NOT to do

- Don't overwrite dead-ends or old decisions — append.
- Don't record a code fact without an anchor.
- Don't present inferred claims as confirmed.
- Don't let the file grow unbounded.
