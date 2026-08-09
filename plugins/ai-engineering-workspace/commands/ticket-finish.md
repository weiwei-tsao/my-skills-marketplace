---
description: "Phase 4 of ticket-workflow: PR notes, a user-confirmed commit, and handoff."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are finishing ticket $ARGUMENTS. This is Phase 4 of 4: Finish.

1. Generate PR title, PR description, test notes, and a short status
   update (follow `conventions.md`'s style, or repo precedent if unset).
   Save into `pr.md` (create it from the template if it doesn't exist
   yet).
2. Commit — never automatic, and never push:
   - If the `git-commit` skill is installed, invoke it. It already runs
     checks, drafts the message, shows it to the user, and waits for
     explicit confirmation before committing — do not restate
     commit-message rules here, and do not skip its confirmation step.
   - Otherwise, draft a commit message using `conventions.md`'s "Commit /
     PR title style", show it to the user, and wait for explicit
     confirmation before running `git commit`.
   - Either way: do not run `git commit` without the user having seen and
     confirmed the exact message first, and do not run `git push` as part
     of this command under any circumstance.
3. Save a handoff — invoke the `handoff` skill's save flow. A ticket isn't
   finished until the next session could continue it cold.
