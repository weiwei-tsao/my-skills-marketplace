---
name: ai-engineering-workspace
description: Scaffold and navigate a structured ticket workspace for AI-assisted engineering on any team. Use when the user wants to set up a ticket workspace, asks how the ai-engineering-workspace suite works, or you need to pick between its skills (ticket-workflow, structured-bug-fix, handoff).
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
| `ticket-workflow` | Working a ticket end to end: investigate → implement → finish | Applies the phase discipline without ticket files |
| `structured-bug-fix` | Diagnosing a bug, especially cross-repo | Works in any repo; presents diagnosis before editing |
| `handoff` | Saving state before ending a session, or resuming one | Uses `.handoff/HANDOFF.md` at repo root |
| this skill | Scaffolding the workspace, or routing between the above | — |

**Workspace detection**: a directory containing `ecosystem.md` and
`tickets/` is a ticket workspace. When one exists (current dir or a notes
repo the user points to), the other skills read/write ticket files there.
When none exists, they degrade to standalone mode — never block on missing
workspace files.

## Scaffolding a workspace

When the user wants to set up the workspace, interview first (skip anything
already known from context or the repo itself):

1. **Scope** — single repo or multiple? List repos with one-line ownership
   ("who owns what kind of fix").
2. **Flow** — how does a request/data travel across the codebase(s)?
   (entry point → routing → data fetch → shared code → upstream/source)
3. **Ticket IDs** — format, e.g. `ABC-123`. Used in branch names and commits.
4. **Stages** — environments before production (staging/UAT?) and who
   accepts (PM/editor/dev)?
5. **Conventions** — branch/commit/PR format; where updates are posted
   (Slack/Teams/issue comments) and the preferred tone.
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

Fill the templates with the interview answers — don't leave placeholder
text behind for sections you have answers to. Show the generated
`ecosystem.md` and `conventions.md` for confirmation; they are the two
files every other skill reads first.

New tickets: `./scripts/new-ticket.sh <TICKET-ID> "short title"`.

## Golden rules (all suite skills inherit these)

- Do not edit code before root cause and owner location are reasonably confirmed.
- Always check current repo, branch, `git status`, and diff before editing.
- Smallest safe change; no unrelated formatting or broad refactors.
- Separate facts (evidence-backed), hypotheses (guesses), and decisions.
- Never end a session without a useful handoff.
