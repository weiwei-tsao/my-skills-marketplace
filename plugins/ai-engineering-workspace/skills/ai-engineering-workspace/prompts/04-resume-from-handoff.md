# Prompt: Resume From Handoff

Use this when opening a new Claude Code session for an existing ticket.

```text
You are continuing <TICKET-ID>.

Read these files first:
- ecosystem.md
- conventions.md
- tickets/<TICKET-ID>/context.md
- tickets/<TICKET-ID>/investigation.md
- tickets/<TICKET-ID>/implementation.md
- tickets/<TICKET-ID>/test.md
- tickets/<TICKET-ID>/handoff.md

Before doing any work:
1. Summarize the current ticket status.
2. Confirm what has already been done.
3. Confirm the next safest action.
4. Check current repo, branch, git status, and diff.

Then continue from handoff.md.

Do not redo old investigation unless the handoff is inconsistent or evidence is missing.
```
