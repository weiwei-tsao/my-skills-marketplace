---
description: "Phase 3 of ticket-workflow: minimal implementation. Requires investigation already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are implementing ticket $ARGUMENTS. This is Phase 3 of 4: Implement
(minimal).

Precondition (workspace mode): `investigation.md` must contain
`Status: confirmed`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run
`/ai-engineering-workspace:ticket-investigate $ARGUMENTS` first — check the
literal `Status:` value only, not whether
the content looks complete.

Precondition (standalone mode): require an explicit confirmation of root
cause/owner earlier in this conversation; if there isn't one, stop and ask
for it before editing.

Before editing:
1. Confirm the owner repo/module.
2. Check current directory, branch, `git status`, and current diff.
3. Summarize the intended minimal change.

Then make the smallest safe change.

Rules:
- No unrelated refactors or formatting.
- Don't touch multiple repos/modules unless the investigation justifies
  it.
- Preserve existing behavior unless the ticket requires changing it.
- Run verification commands in the confirmed implementation owner
  repository — not the notes workspace or ambient cwd. If
  `conventions.md`'s "Per-repo overrides" table has a row for this repo,
  use those typecheck/lint/test/build commands; otherwise use the
  default "Verification commands". Skip any entry marked `N/A` or left
  unset. Report results honestly, including failures. If the ticket
  touches multiple repos, repeat this for each repo touched.
- Record what changed and how it was tested into `implementation.md` and
  `test.md` (create them from `tickets/_template/implementation.md` and
  `tickets/_template/test.md` if they don't exist yet, replacing
  `<TICKET-ID>` with $ARGUMENTS in each; `implementation.md`'s `Status:`
  line starts as `draft`).

Gate: if every verification command that ran passed (or all were `N/A`
or unset), update `implementation.md`'s `Status:` line to `complete`,
then tell the user to run
`/ai-engineering-workspace:ticket-finish $ARGUMENTS`. If any verification
command failed, do not update `Status:` — report the failure and stop;
do not suggest running `/ticket-finish` until it's fixed and
re-verified.
