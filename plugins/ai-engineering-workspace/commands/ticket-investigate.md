---
description: "Phase 2 of ticket-workflow: read-only code investigation. Requires ticket understanding already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are investigating ticket $ARGUMENTS. This is Phase 2 of 4: Investigate
(read-only).

Workspace root: use the `WORKSPACE_ROOT` established in
`/ai-engineering-workspace:ticket-understand` earlier in this
conversation. If it isn't clear from context, re-detect it the same way
(current dir, or ask the user) — never assume it equals the current shell
cwd.

Precondition (workspace mode):
`$WORKSPACE_ROOT/tickets/$ARGUMENTS/context.md` must contain
`Status: confirmed`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run
`/ai-engineering-workspace:ticket-understand $ARGUMENTS`
first — do not use judgment about whether the content "looks" confirmed;
check the literal `Status:` value only.

Precondition (standalone mode): no file to check. Require an explicit
confirmation of the ticket understanding earlier in this conversation; if
there isn't one, stop and restate the ask for confirmation before tracing
code.

1. If this is a bug/regression, apply the `structured-bug-fix` skill's
   Phase 2 method (root-cause checklist, then sequential flow trace; fan
   out to parallel agents only when `ecosystem.md` shows genuinely
   independent repos worth triaging first). Otherwise, read
   `$WORKSPACE_ROOT/ecosystem.md`'s flow map if present; otherwise trace
   from the entry point by reading the actual code.
2. Identify the most likely owner repo/module.
3. Separate facts (evidence-backed), hypotheses (unconfirmed), candidates
   (proposed designs), and decisions (owner-confirmed only). Investigation
   can start diagnostic and cross into design partway through: when a
   question shifts from "what is true now?" to "what should the system
   become?" — the trigger in `ticket-workflow`'s "Design decisions are not
   findings", checked here, when writing next steps, and at the gate — list
   candidates for that question, including the existing owner, with what
   you tried to invalidate each plausible one ("untested" and why is a valid
   entry; no preference doesn't waive it; a cost or blocker you haven't
   verified is written "unverified", not counted); don't pick one. The rest
   of the diagnosis continues as usual. Record every negative finding ("not
   found", "ruled out") with its search boundary, per "Negative claims must
   expose their search boundary".
4. Record findings, evidence, open questions, and next steps into
   `$WORKSPACE_ROOT/tickets/$ARGUMENTS/investigation.md` (create it from
   `$WORKSPACE_ROOT/tickets/_template/investigation.md` if it doesn't
   exist yet, replacing `<TICKET-ID>` with $ARGUMENTS; its `Status:` line
   starts as `draft`).

Do not edit any code in this phase.

5. Before presenting the gate summary, run the draft findings through the
   independent verification process defined in `ticket-workflow`'s
   SKILL.md ("Independent verification at gates"). Give the fresh
   verifier the complete investigation draft — not just facts, root
   cause, and owner, since next steps and other scope-relevant
   conclusions are material too, and a next step that quietly expands
   scope beyond `context.md`'s confirmed boundaries is exactly the
   contradiction source 3 must catch. Also give it full read access to
   the repo — not just the files you cited — and, in workspace mode,
   `$WORKSPACE_ROOT/tickets/$ARGUMENTS/context.md`, so it can also check
   whether the draft contradicts anything already confirmed there —
   reading any `## Correction` section in `context.md` as overriding the
   claim it corrects, not as separate content alongside it. Its
   job is to find evidence that undermines the claims, not just check
   your citations. On HARD_FAIL — including a
   contradiction with `context.md` — first determine which claim the
   evidence actually invalidates: if it's the investigation draft's
   claim, just fix or downgrade the draft; only if `context.md`'s claim
   is the one that no longer holds, fix the draft accordingly and append
   a dated `## Correction (<date>)` note to `context.md` instead of
   rewriting it. Re-verify once with a new fresh verifier instance; if it
   still fails, stop, report the exact unresolved claim, and do not
   present a gate summary. On PASS or SOFT_FLAGS, proceed to the gate
   below and include any flags in the summary.

   If the draft contains negative claims (including "Checked but not
   responsible" entries), tell the verifier to apply "Negative claims must
   expose their search boundary" — coverage independence: try to overturn
   each one with a materially different query or method and a plausible
   surface class the draft didn't search (its "not searched" list is fair
   game), not reconfirm it with the author's own query. If it contains a
   Candidates table or a Decisions entry, tell it to check the
   design-decision HARD_FAIL source: no design choice under Decisions
   without a recorded choice by the decision owner, and none recorded in
   `context.md` (as an answered Open question or an appended update)
   without a matching Decisions entry. Also tell it to check the
   stakeholder-statement HARD_FAIL source: any finding or candidate that
   conflicts with, or could be read as conflicting with, a comment or review
   remark recorded in `context.md` must be raised as a question, not
   resolved by the draft's own reading.

Gate: summarize confirmed facts, likely root cause, owner, and the next
safest action. If any finding or candidate conflicts with, or could be read
as conflicting with, a stakeholder statement in the ticket, quote it, say
what it conflicts with and the possible readings, and ask the user which
applies before treating that conclusion as settled.

If the next action is a design decision:
- Present the candidates and what was tried to invalidate each (or that
  it's untested).
- Ask the user to choose if they own that decision, or to bring back the
  choice from whoever does, and record it under Decisions (who chose, when,
  among which candidates, where it was raised).
- Also draft the question for the user to post in the channel
  `conventions.md`'s "Design decisions" field names (if the field is
  missing, ask once where such questions go and suggest saving it). This is
  a soft prompt for team visibility, not an approval step, and you never
  post, comment, message or push it yourself.
- Do not set `Status: confirmed` while one is unresolved, since
  `/ticket-implement` only checks that literal value.

Wait for confirmation. Once confirmed, update
`$WORKSPACE_ROOT/tickets/$ARGUMENTS/investigation.md`'s `Status:` line to
`confirmed` (workspace mode). If `investigation.md` predates this field
and has no `Status:` line at all, add one directly under the H1 title
reading `Status: confirmed` instead of trying to find a line to replace.
Append a `Verified:` line per the shared verification section.

Tell the user to run `/ai-engineering-workspace:ticket-implement $ARGUMENTS`.
