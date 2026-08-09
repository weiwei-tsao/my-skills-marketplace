---
description: "Phase 2 of ticket-workflow: read-only code investigation. Requires ticket understanding already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are investigating ticket $ARGUMENTS. This is Phase 2 of 4: Investigate
(read-only).

Precondition (workspace mode): `context.md` must contain
`Status: confirmed`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run `/ticket-understand $ARGUMENTS`
first — do not use judgment about whether the content "looks" confirmed;
check the literal `Status:` value only.

Precondition (standalone mode): no file to check. Require an explicit
confirmation of the ticket understanding earlier in this conversation; if
there isn't one, stop and restate the ask for confirmation before tracing
code.

1. Read `ecosystem.md`'s flow map if present; otherwise trace from the
   entry point by reading the actual code.
2. Identify the most likely owner repo/module.
3. Separate facts (evidence-backed), hypotheses (unconfirmed), decisions.
4. Record findings, evidence, open questions, and next steps into
   `investigation.md` (create it from `tickets/_template/investigation.md`
   if it doesn't exist yet, replacing `<TICKET-ID>` with $ARGUMENTS; its
   `Status:` line starts as `draft`).

Do not edit any code in this phase.

Gate: summarize confirmed facts, likely root cause, owner, and the next
safest action. Wait for confirmation. Once confirmed, update
`investigation.md`'s `Status:` line to `confirmed` (workspace mode).

Tell the user to run `/ticket-implement $ARGUMENTS`.
