# Skill: Structured Bug Fix

Use this skill for cross-repo bug diagnosis and resolution.

## Principle

Diagnose fully before touching code. A symptom in one brand repo may have a root cause in a sibling repo.

## Phase 1: Gather context

Read:

- `ecosystem.md`
- `conventions.md`
- `tickets/<TICKET-ID>/context.md`
- `tickets/<TICKET-ID>/handoff.md`, if present

Ask for missing information only if necessary. Do not ask for information already present in the ticket files.

## Phase 2: Trace flow across repos

Trace the relevant path:

```text
URL
→ server/middleware/route
→ page/getInitialProps
→ fetchSite/fetchPost
→ shared component
→ platform API/upstream JSON
→ source system
```

Record findings in `investigation.md`.

## Phase 3: Confirm owner repo

Before editing, state:

- owner repo
- why it owns the fix
- repos checked but not responsible
- evidence

## Phase 4: Minimal implementation

Before editing:

- check current directory
- check current branch
- run `git status`
- inspect current diff

Then make the smallest safe change.

## Phase 5: Test and handoff

Update:

- `implementation.md`
- `test.md`
- `pr.md`
- `handoff.md`

Do not leave a session without a useful handoff.
