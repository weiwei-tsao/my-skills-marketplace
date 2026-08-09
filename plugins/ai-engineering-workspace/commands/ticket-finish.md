---
description: "Phase 4 of ticket-workflow: PR notes, an implementation-repo commit report, and handoff."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are finishing ticket $ARGUMENTS. This is Phase 4 of 4: Finish.

Precondition (workspace mode): `implementation.md` must contain
`Status: complete`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run
`/ai-engineering-workspace:ticket-implement $ARGUMENTS` first — check the
literal `Status:` value only, not whether PR notes already look ready to
write.

Precondition (standalone mode): require an explicit indication earlier in
this conversation that implementation and verification finished; if there
isn't one, stop and ask before generating PR notes.

1. Generate PR title, PR description, test notes, and a short status
   update (follow `conventions.md`'s style, or repo precedent if unset).
   Save into `pr.md` (create it from `tickets/_template/pr.md` if it
   doesn't exist yet, replacing `<TICKET-ID>` with $ARGUMENTS). Record the
   status update into `timeline.md` too (create it from
   `tickets/_template/timeline.md` if it doesn't exist yet, replacing
   `<TICKET-ID>` with $ARGUMENTS).
2. Implementation repo — report only, never commit or push:
   - Identify the implementation repo(s) touched during Phase 3
     (Implement).
   - For each: report the repo path, the changed files (`git status` /
     `git diff --stat`), and a suggested commit message following
     `conventions.md`'s "Commit / PR title style".
   - Do not run `git commit` or `git push` yourself, and do not invoke
     the `git-commit` skill to execute a commit on your behalf — this
     applies whether or not that skill is installed. The user commits
     and pushes the implementation repo manually.
3. Ticket workspace / notes files (`context.md`, `investigation.md`,
   `implementation.md`, `test.md`, `pr.md`, `timeline.md`, `handoff.md`):
   - If the workspace root is the same git repository as the
     implementation repo from step 2, treat these files under the same
     manual-only rule as step 2 — do not commit them either, since
     they'd get bundled with that repo's pending code changes.
   - If the workspace root is a separate git repository, and
     `conventions.md`'s "Notes repo automation" field allows it, commit
     the workflow file changes (and push them too, only if that field
     also allows push) without asking. If the field is unset or says no,
     leave them uncommitted and say so in the summary.
4. Save a handoff — invoke the `handoff` skill's save flow. A ticket isn't
   finished until the next session could continue it cold.
