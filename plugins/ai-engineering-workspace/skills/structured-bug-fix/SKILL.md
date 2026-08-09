---
name: structured-bug-fix
description: Structured bug diagnosis and resolution — trace the full data flow, confirm which repo/module owns the fix, present the diagnosis, and only then make the smallest safe change. Use when diagnosing a bug, especially when the symptom may live in a different repo or layer than the root cause.
---

# Structured Bug Fix

Diagnose fully before touching code. A symptom in one place often has its
root cause in a sibling repo, a shared library, or an upstream data source.

## Phase 1 — Gather context

If a ticket workspace exists, read `ecosystem.md`, `conventions.md`, and the
ticket's `context.md` / `handoff.md`. Otherwise ask only for what's missing:

- exact error message or symptom
- reproduction steps
- suspected area, if any

Don't ask for information already provided.

Before tracing the flow, output a one-line restatement: "My understanding
of the bug is: ...". Wait for the user to confirm before starting Phase 2.

## Phase 2 — Trace the flow

Follow the data through every layer — do not stop at the first suspicious
file:

```text
Entry (URL / event / job)
→ routing / middleware
→ handler / page
→ data fetch
→ shared components / libraries
→ API / upstream data
→ source system
```

Use `ecosystem.md`'s flow map if present; otherwise build the chain by
reading the actual code. Verify each hop — never assume. Record findings as
you go (→ `investigation.md` in workspace mode), keeping facts, hypotheses,
and decisions separate.

## Phase 3 — Present diagnosis, wait for confirmation

Before writing a single line of code, present:

```md
## Diagnosis

**Root cause**: <one sentence>

**Evidence**:
- <file:line> — <what it shows>

**Owner**: <repo/module> — <why it owns the fix>
**Checked, not responsible**: <repos/layers ruled out>

**Files that need changes**:
1. `path/file` — <what and why>

No code has been changed yet. Confirm to proceed.
```

## Phase 4 — Minimal implementation

Before editing: current directory, branch, `git status`, current diff.
Then the smallest safe change, applied to **all** files in the diagnosis —
not just the most obvious one. No unrelated refactors.

## Phase 5 — Verify and hand off

Run the repo's checks (typecheck, lint, tests); report results honestly.
Update `implementation.md`, `test.md`, `pr.md` in workspace mode, and leave
a handoff (use the `handoff` skill). Never leave a session without one.
