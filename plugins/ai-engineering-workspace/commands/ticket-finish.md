---
description: "Phase 4 of ticket-workflow: PR notes, an implementation-repo commit report, and handoff."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are finishing ticket $ARGUMENTS. This is Phase 4 of 4: Finish.

Workspace root: use the `WORKSPACE_ROOT` established in
`/ai-engineering-workspace:ticket-understand` earlier in this
conversation. If it isn't clear from context, re-detect it the same way
(current dir, or ask the user) — never assume it equals the current shell
cwd or the implementation repo from Phase 3.

Precondition (workspace mode):
`$WORKSPACE_ROOT/tickets/$ARGUMENTS/implementation.md` must contain
`Status: complete`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run
`/ai-engineering-workspace:ticket-implement $ARGUMENTS` first — check the
literal `Status:` value only, not whether PR notes already look ready to
write.

Precondition (standalone mode): require an explicit indication earlier in
this conversation that implementation and verification finished; if there
isn't one, stop and ask before generating PR notes.

1. Generate PR title, PR description, test notes, and a short status
   update (follow `$WORKSPACE_ROOT/conventions.md`'s style, or repo
   precedent if unset). Save into
   `$WORKSPACE_ROOT/tickets/$ARGUMENTS/pr.md` (create it from
   `$WORKSPACE_ROOT/tickets/_template/pr.md` if it doesn't exist yet,
   replacing `<TICKET-ID>` with $ARGUMENTS). Record the status update
   into `$WORKSPACE_ROOT/tickets/$ARGUMENTS/timeline.md` too (create it
   from `$WORKSPACE_ROOT/tickets/_template/timeline.md` if it doesn't
   exist yet, replacing `<TICKET-ID>` with $ARGUMENTS).
2. Implementation repo — report only, never commit or push:
   - Identify the implementation repo(s) touched during Phase 3
     (Implement). This is a different directory from `WORKSPACE_ROOT`
     whenever the ticket workspace is a dedicated notes repo.
   - For each: report the repo path, the changed files (`git status` /
     `git diff --stat`), and a suggested commit message following
     `$WORKSPACE_ROOT/conventions.md`'s "Commit / PR title style".
   - Do not run `git commit` or `git push` yourself, and do not invoke
     the `git-commit` skill to execute a commit on your behalf — this
     applies whether or not that skill is installed. The user commits
     and pushes the implementation repo manually.
3. Save a handoff — invoke the `handoff` skill's save flow, targeting
   `$WORKSPACE_ROOT/tickets/$ARGUMENTS/handoff.md` explicitly. Do not let
   the handoff skill's own file-location detection decide the path here:
   that detection is cwd-relative, and if the agent's cwd is still the
   implementation repo from Phase 3, it would resolve against the wrong
   repo and could write `.handoff/HANDOFF.md` into the implementation
   repo instead of the workspace. A ticket isn't finished until the next
   session could continue it cold. Do this before step 4 — `handoff.md`
   must exist before the notes repo is committed, or step 4 will commit
   every workflow artifact except it.
4. Ticket workspace / notes files (`context.md`, `investigation.md`,
   `implementation.md`, `test.md`, `pr.md`, `timeline.md`, `handoff.md`,
   all under `$WORKSPACE_ROOT/tickets/$ARGUMENTS/`):
   - If `WORKSPACE_ROOT` is the same git repository as the implementation
     repo from step 2, treat these files under the same manual-only rule
     as step 2 — do not commit them either, since they'd get bundled with
     that repo's pending code changes.
   - If `WORKSPACE_ROOT` is a separate git repository, and
     `$WORKSPACE_ROOT/conventions.md`'s "Notes repo automation" field
     allows it, commit the workflow file changes (and push them too,
     only if that field also allows push) without asking. If the field is
     unset or says no, leave them uncommitted and say so in the summary.
