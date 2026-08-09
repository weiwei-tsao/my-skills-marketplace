---
name: ai-engineering-workspace
description: Scaffold and navigate a structured ticket workspace for AI-assisted engineering on any team. Use when the user wants to set up a ticket workspace, asks how the ai-engineering-workspace suite works, or you need to pick between its skills (ticket-workflow, structured-bug-fix, handoff, complete-ticket).
---

# AI Engineering Workspace

Treat each engineering ticket as an independent context package:

```text
Problem context + code ownership + investigation evidence + next safe action
```

AI coding sessions are short-lived and stateless; tickets are long-lived and
cross-session. This suite externalizes session memory into files so any new
session (Claude Code, Cursor, Codex, …) can pick up a ticket cold — without
repeating investigations, editing the wrong repo, mixing facts with guesses,
or losing test/acceptance status.

## The suite

Each skill works on its own — install once, use only what the project needs:

| Skill | Use when | Standalone (no workspace) |
|---|---|---|
| `ticket-workflow` | Working a ticket end to end via `/ticket-understand` -> `/ticket-investigate` -> `/ticket-implement` -> `/ticket-finish` | Applies the phase discipline without ticket files |
| `structured-bug-fix` | Diagnosing a bug, especially cross-repo | Works in any repo; presents diagnosis before editing |
| `handoff` | Saving state before ending a session, or resuming one | Uses `.handoff/HANDOFF.md` at repo root |
| `complete-ticket` | Turning a finished or intentionally drafted ticket into private context plus public-safe reusable knowledge | Draft mode only without workspace files |
| this skill | Scaffolding the workspace, or routing between the above | — |

**Workspace detection**: a directory containing `ecosystem.md` and
`tickets/` is a ticket workspace. When one exists (current dir or a notes
repo the user points to), the other skills read/write ticket files there.
When none exists, they degrade to standalone mode — never block on missing
workspace files.

`complete-ticket` is stricter than the other suite skills: final completion
requires ticket evidence, while standalone mode is draft-only.

## Scaffolding a workspace

When the user wants to set up the workspace, interview first (skip anything
already known from context or the repo itself):

1. **Scope** — single repo or multiple? List repos with one-line ownership
   ("who owns what kind of fix").
2. **Flow** — how does a request/data travel across the codebase(s)?
   (entry point → routing → data fetch → shared code → upstream/source)
3. **Ticket IDs** — format, e.g. `ABC-123`. Used in branch names and
   commits. Also: how do you fetch a ticket's raw content and comments —
   a command or MCP tool (e.g. `gh issue view <ID> --comments`)? →
   recorded as `conventions.md`'s "Ticket source".
4. **Stages** — environments before production (staging/UAT?) and who
   accepts (PM/editor/dev)?
5. **Conventions** — branch/commit/PR format; where updates are posted
   (Slack/Teams/issue comments) and the preferred tone. Also: typecheck/
   lint/test/build commands (mark any that don't apply as N/A) →
   recorded as `conventions.md`'s "Verification commands".
6. **Location** — dedicated notes repo, or a `workspace/` (or `.tickets/`)
   folder inside the main repo?

Then scaffold from this skill's `templates/` directory:

```text
<workspace>/
  ecosystem.md          ← templates/ecosystem.md, filled from answers 1–2
  conventions.md        ← templates/conventions.md, filled from answers 3–5
  tickets/_template/    ← templates/tickets/*  (copy as-is)
  scripts/new-ticket.sh ← templates/scripts/new-ticket.sh (chmod +x)
```

Upgrading an existing workspace to a newer plugin version: re-copy
`templates/tickets/*` and `templates/scripts/new-ticket.sh` over the
workspace's `tickets/_template/` and `scripts/new-ticket.sh` so it picks up
template changes (e.g. the `Status:` field) — the scaffold step above only
runs once, at workspace creation.

Fill the templates with the interview answers — don't leave placeholder
text behind for sections you have answers to. Show the generated
`ecosystem.md` and `conventions.md` for confirmation; they are the two
files every other skill reads first.

New tickets: `./scripts/new-ticket.sh <TICKET-ID> "short title"` creates
`context.md` only; run `/ticket-understand <TICKET-ID>` next — the rest of
a ticket's files are created lazily as each phase command needs them.

## Golden rules (all suite skills inherit these)

- Do not edit code before root cause and owner location are reasonably confirmed.
- Always check current repo, branch, `git status`, and diff before editing.
- Smallest safe change; no unrelated formatting or broad refactors.
- Separate facts (evidence-backed), hypotheses (guesses), and decisions.
- Never end a session without a useful handoff.
- Never run `git commit` without showing the user the exact message and
  getting explicit confirmation first. Never run `git push`.
