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

Before tracing, run through the checklist that actually surfaces root
causes: read the full error message/stack trace (don't skip past it),
confirm the bug reproduces consistently (if it doesn't, gather more data —
don't guess), and check what changed recently in the suspected area (git
log/diff, new dependencies, config). Jumping straight from "this file looks
suspicious" to a conclusion is how symptom fixes happen.

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

**Trigger scenarios are conjunctions — and a bug can have more than one**: if
the bug only reproduces under specific circumstances, model the trigger as
one or more *scenarios*; within each scenario, every listed condition must
hold — not one variable. Don't collapse everything observed into a single
conjunction: a symptom can have independent sufficient paths (e.g.
`(browser A && cached state) || malformed payload`), and forcing them into
one big AND misrecords the other path's inputs as "immune," which
misdirects diagnosis and drops valid regression cases. List every condition
in each scenario explicitly (→ `investigation.md`'s Trigger conditions
section), then for each one ask: "if this didn't hold, would I still see
the same symptom under this same scenario?" A variable you never isolated
(save count, timing between actions, which UI path was used...) is exactly
as plausible a cause as the one you did isolate. Attributing an intermittent
bug to the one variable you happened to track, without ruling out the
others that also varied between observations, is an unaddressed alternate
explanation, not a diagnosis.

This also governs how to read a negative test: it only rules out one
condition when every *other* known condition in the scenario is held at
its triggering value and only that one condition is flipped. If more than
one condition changes between the reproducing case and the non-reproducing
case, the non-reproduction can't tell you which change mattered — that
comparison has no information value, regardless of how many conditions
were individually driven to a triggering value at some point. To test
necessity: reproduce with every condition at its triggering value, then
flip exactly one back to non-triggering at a time, holding the rest fixed.
A flip that kills the bug confirms that condition's necessity; a flip that
doesn't is itself a finding — that condition wasn't actually required.

**Multiple repos in play**: this chain is causal, so trace it sequentially
in one thread — never split one suspected chain across parallel agents.
Fan out one agent per repo only when `ecosystem.md` shows the ticket
plausibly touches genuinely independent repos/surfaces (no shared state,
either could turn out to own the fix) and you need to triage which one
before committing to a deep trace; converge back to sequential tracing the
moment the owning repo is identified.

## Phase 3 — Present diagnosis, wait for confirmation

Before presenting the diagnosis, run it through the independent
verification process defined in `ticket-workflow`'s SKILL.md ("Independent
verification at gates"). Give the fresh verifier the draft root cause,
evidence, owner, **and the checked-not-responsible list** — an exclusion is
a material claim too, and a broad one by default, per `ticket-workflow`'s
scope-scaled evidence rule — plus full read access to the repo, not just
the cited files,
so it can check both that each material claim has positive traceable
support and that no other part of the codebase contradicts it. This
includes any exclusion reached informally while chasing something else,
not only the ones already written into the diagnosis draft — if you're
about to tell the user a repo/module/theory is ruled out, add it to
checked-not-responsible and verify it before saying so. On HARD_FAIL, fix
or downgrade the flagged claim and re-verify once with a new fresh verifier
instance; if it still fails, stop, report the exact unresolved claim, and
do not present a diagnosis. On PASS or SOFT_FLAGS, include any flags in the
diagnosis below.

Before writing a single line of code, present:

```md
## Diagnosis

**Root cause**: <one sentence>

**Trigger scenario(s)** <omit this field if the bug reproduces unconditionally; list more than one scenario if there are independent sufficient paths>:
- Scenario 1 (all must hold together):
  1. <condition>
  2. <condition>

**Evidence**:
- <file:line> — <what it shows>

**Owner**: <repo/module> — <why it owns the fix>
**Checked, not responsible**: <repos/layers ruled out>

**Files that need changes**:
1. `path/file` — <what and why>

**Verified**: <PASS / PASS — flags: ...>

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

## Common rationalizations

| Rationalization | Correct response |
|---|---|
| "The suspicious file is obvious, so tracing the full flow is waste." | Trace until the owner is confirmed; symptom location is not ownership. |
| "I can patch the UI and come back to root cause later." | Present diagnosis first, then edit only after confirmation. |
| "The user expects this repo to own it." | Follow evidence. If evidence contradicts the user's framing, say so plainly. |
| "Parallel agents will make the investigation faster." | Use parallel triage only for genuinely independent repos; trace a causal chain sequentially. |
| "I found one fix, so I can skip checked-not-responsible notes." | Record what was ruled out so the next session does not repeat dead ends. |
| "The bug reproduces under specific conditions, so once I've found the one that correlates, listing the rest is unnecessary." | Enumerate every conjunct anyway — an unlisted one is an untested variable. A non-reproduction only isolates a condition when the other known conditions in that scenario are held at their triggering values. |

## Red flags

- Starting from a suspected implementation file instead of the symptom and flow.
- Treating a hypothesis as a fact without an anchor.
- Editing before presenting root cause, evidence, owner, and files to change.
- Stopping at the first plausible layer in a multi-layer request/data path.
- Leaving no handoff after a partial diagnosis or failed verification.
- Diagnosing an intermittent bug from one correlated variable without ruling
  out other variables that also varied between the same observations.

## Exit criteria

- The bug is restated and confirmed before code investigation starts.
- Root cause, evidence, owner, checked-not-responsible layers, and files to
  change are presented before editing.
- The implementation changes only the diagnosed owner files.
- Verification results and remaining risks are recorded honestly.
- A handoff exists with next steps that a new session can follow cold.
