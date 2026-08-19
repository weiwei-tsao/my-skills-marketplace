---
description: "Phase 3 of ticket-workflow: minimal implementation. Requires investigation already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are implementing ticket $ARGUMENTS. This is Phase 3 of 4: Implement
(minimal).

Workspace root: use the `WORKSPACE_ROOT` established in
`/ai-engineering-workspace:ticket-understand` earlier in this
conversation. If it isn't clear from context, re-detect it the same way
(current dir, or ask the user) — never assume it equals the current shell
cwd. This is separate from the implementation repo you'll edit in this
phase; the two are frequently different directories.

Precondition (workspace mode):
`$WORKSPACE_ROOT/tickets/$ARGUMENTS/investigation.md` must contain
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
- If a fact turns up here that contradicts something
  `investigation.md` already marked `confirmed`, append a dated
  `## Correction (<date>)` note to `investigation.md` — don't rewrite the
  confirmed sections.
- Run verification commands in the confirmed implementation owner
  repository — not `WORKSPACE_ROOT` or ambient cwd. If
  `$WORKSPACE_ROOT/conventions.md`'s "Per-repo overrides" table has a row
  for this repo, use those typecheck/lint/test/build commands; otherwise
  use the default "Verification commands". Skip any entry marked `N/A` or
  left unset. Report results honestly, including failures. If the ticket
  touches multiple repos, repeat this for each repo touched.
- Record what changed and how it was tested into
  `$WORKSPACE_ROOT/tickets/$ARGUMENTS/implementation.md` and
  `$WORKSPACE_ROOT/tickets/$ARGUMENTS/test.md` (create them from
  `$WORKSPACE_ROOT/tickets/_template/implementation.md` and
  `$WORKSPACE_ROOT/tickets/_template/test.md` if they don't exist yet,
  replacing `<TICKET-ID>` with $ARGUMENTS in each; `implementation.md`'s
  `Status:` line starts as `draft`).

Gate: if every verification command that ran passed (or all were `N/A`
or unset), update
`$WORKSPACE_ROOT/tickets/$ARGUMENTS/implementation.md`'s `Status:` line
to `complete` (if `implementation.md` predates this field and has no
`Status:` line at all, add one directly under the H1 title reading
`Status: complete` instead of trying to find a line to replace), then
tell the user to run `/ai-engineering-workspace:ticket-finish $ARGUMENTS`.
If any verification command failed, do not update `Status:` — report the
failure and stop; do not suggest running `/ticket-finish` until it's
fixed and re-verified.
