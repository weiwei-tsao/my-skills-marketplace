---
name: ai-engineering-workspace
description: Structured ticket workflow for AI-assisted engineering across multiple repos. Use when starting, implementing, finishing, or resuming an engineering ticket — investigate read-only first, confirm the owner repo, make the smallest safe change, and always leave a handoff for the next session.
---

# AI Engineering Workspace

Treat each ticket as an independent context package:

```text
Problem context + repo ownership + investigation evidence + next safe action
```

This avoids repeating investigations, editing the wrong repo, mixing facts
with guesses, broad refactors, and losing UAT/PROD/acceptance status across
sessions.

## Workspace layout

The workspace (a notes repo, separate from the code repos) contains:

- `ecosystem.md` — repo map, ownership rules, request/data flow
- `conventions.md` — branch/commit/PR/Slack/test conventions
- `tickets/<ID>/` — one folder per ticket: `context.md`, `investigation.md`,
  `implementation.md`, `test.md`, `pr.md`, `handoff.md`, `timeline.md`
- `tickets/_template/` — templates for the files above
- `scripts/new-ticket.sh <ID> "<title>"` — scaffold a new ticket folder
- `prompts/` — the five phase prompts referenced below

If the user's workspace doesn't exist yet, offer to scaffold it from this
skill's bundled files (copy `ecosystem.md`, `conventions.md`, `tickets/_template/`,
`scripts/`, `prompts/` and adapt `ecosystem.md` to their repos).

## Workflow phases

Pick the phase matching where the ticket stands, read its prompt file, and
follow it:

1. **Investigate** (`prompts/01-start-investigation.md`) — read-only. Read
   `ecosystem.md`, `conventions.md`, the ticket's `context.md` and
   `handoff.md`. Trace the flow across repos, separate facts from
   hypotheses, record findings in `investigation.md`. No code edits.
2. **Implement** (`prompts/02-implement.md`) — only after the owner repo is
   confirmed. Check directory, branch, `git status`, and diff first; then the
   smallest safe change. Update `implementation.md` and `test.md`.
3. **Finish** (`prompts/03-finish-ticket.md`) — generate PR title/description,
   commit message, test notes, and Slack update into `pr.md`; update
   `handoff.md`.
4. **Resume** (`prompts/04-resume-from-handoff.md`) — new session on an
   existing ticket: summarize status from the ticket files, verify git state,
   continue from `handoff.md`. Don't redo old investigation.
5. **Update handoff** (`prompts/05-update-handoff.md`) — before ending any
   long session: status, branch, changed files, test results, blockers, next
   steps, do-not-do notes.

For cross-repo bug diagnosis specifically, follow
`skills/structured-bug-fix.md` (five phases: gather context → trace flow →
confirm owner repo → minimal implementation → test and handoff).

## Golden rules

- Do not edit code before root cause and owner repo are reasonably confirmed.
- Always check current repo, branch, `git status`, and diff before editing.
- Smallest safe change; no unrelated formatting or broad refactors.
- Never leave a session without a useful `handoff.md`.
