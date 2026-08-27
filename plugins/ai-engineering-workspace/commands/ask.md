---
description: "Read-only router for ai-engineering-workspace tickets: inspect literal Status fields and recommend the next command."
argument-hint: [TICKET-ID]
disable-model-invocation: true
---

You are routing an ai-engineering-workspace ticket. This command is read-only.

Hard boundary:
- Do not execute any ticket phase.
- Do not create or update ticket files.
- Do not read or summarize later phase instructions.
- Only inspect file existence and literal `Status:` fields, then recommend the
  next command for the user to run.

1. Detect `WORKSPACE_ROOT`: a directory containing `ecosystem.md` and
   `tickets/`. Check, in order: the current dir; if the current dir's path
   matches `.../tickets/<TICKET-ID>/` (two levels down from a candidate
   root), its grandparent; or a notes repo the user points to. This
   two-level check exists only to make step 2's "invoked from inside the
   ticket's own directory" case work — do not walk any other ancestor.
   If none is found, say workspace mode is unavailable and recommend
   `/ai-engineering-workspace:ticket-understand <TICKET-ID>` in standalone mode
   once the user provides a ticket ID and raw ticket content.
2. Resolve the ticket ID:
   - Prefer `$ARGUMENTS` when provided.
   - Otherwise, if the current path is inside
     `$WORKSPACE_ROOT/tickets/<TICKET-ID>/`, use that ID.
   - Otherwise, if exactly one `tickets/<TICKET-ID>/` folder exists, excluding
     `tickets/_template/`, use it.
   - If still unclear, ask the user for the ticket ID and stop.
3. Inspect only these files, and only their first literal `Status:` line:
   - `$WORKSPACE_ROOT/tickets/<TICKET-ID>/context.md`
   - `$WORKSPACE_ROOT/tickets/<TICKET-ID>/investigation.md`
   - `$WORKSPACE_ROOT/tickets/<TICKET-ID>/implementation.md`
4. Recommend exactly one next command:
   - Missing ticket directory or missing `context.md`:
     `/ai-engineering-workspace:ticket-understand <TICKET-ID>`
   - `context.md` missing `Status: confirmed`:
     `/ai-engineering-workspace:ticket-understand <TICKET-ID>`
   - `investigation.md` missing or missing `Status: confirmed`:
     `/ai-engineering-workspace:ticket-investigate <TICKET-ID>`
   - `implementation.md` missing or missing `Status: complete`:
     `/ai-engineering-workspace:ticket-implement <TICKET-ID>`
   - `implementation.md` contains `Status: complete`:
     `/ai-engineering-workspace:ticket-finish <TICKET-ID>`

Output:

```text
Ticket: <TICKET-ID>
Workspace: <WORKSPACE_ROOT or standalone>
Status fields:
- context.md: <missing | Status: ...>
- investigation.md: <missing | Status: ...>
- implementation.md: <missing | Status: ...>

Next command:
<command>
```

Stop here. Do not run the recommended command yourself — wait for the user
to invoke it.
