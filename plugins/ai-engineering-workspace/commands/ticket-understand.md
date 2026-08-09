---
description: "Phase 1 of ticket-workflow: fetch and confirm understanding of a ticket before any code investigation starts."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are starting ticket $ARGUMENTS. This is Phase 1 of 4: Understand.

1. Detect workspace mode: does a directory with `ecosystem.md` and
   `tickets/` exist (current dir or a notes repo the user points to)?
   - Workspace mode: read `ecosystem.md`, `conventions.md`, and
     `tickets/$ARGUMENTS/context.md` if present. If
     `tickets/$ARGUMENTS/` doesn't exist yet, run
     `./scripts/new-ticket.sh $ARGUMENTS "<title>"` first (ask for a short
     title if the user hasn't given one).
   - Standalone mode: skip file reads; work from what the user has said in
     this conversation.
2. Fetch the ticket's raw content (title, description, all comments):
   - Workspace mode: use the command recorded under "Ticket source" in
     `conventions.md`. If no command is recorded, ask the user for it once
     and suggest saving it to `conventions.md` for next time.
   - Standalone mode: use what the user already provided in conversation;
     ask only for what's missing.
3. Record the raw ask and comments into `context.md` (workspace mode). The
   template's `Status:` line starts as `draft` — leave it as `draft`.
4. Output a restatement covering: goal, user-visible problem, expected vs.
   current behavior, explicit in/out of scope, open questions.
5. STOP. Do not read or search any code. Do not create or write
   `investigation.md`. Wait for the user to confirm the restatement.
6. Once the user confirms, update `context.md`'s `Status:` line to
   `confirmed` (workspace mode only — standalone mode has no file to
   update; the user's confirmation in this conversation is the only
   record). If `context.md` predates this field and has no `Status:` line
   at all, add one directly under the H1 title reading `Status: confirmed`
   instead of trying to find a line to replace.

Tell the user to run `/ai-engineering-workspace:ticket-investigate $ARGUMENTS`.
