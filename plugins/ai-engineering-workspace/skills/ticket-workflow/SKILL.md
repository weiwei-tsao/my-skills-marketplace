---
name: ticket-workflow
description: Phase-gated workflow for working an engineering ticket — read-only investigation first, minimal implementation only after ownership is confirmed, then PR notes and handoff. Use when starting, implementing, or finishing a ticket, or when the user names a ticket ID.
---

# Ticket Workflow

Four gated phases, each with its own slash command for a hard,
user-controlled phase boundary — the agent can't see a later phase's
instructions until the user runs that phase's command, so it can't
self-chain ahead.

| Phase | Command | Purpose |
|---|---|---|
| Router | `/ai-engineering-workspace:ask [ID]` | Read-only: inspect literal `Status:` fields and recommend the next command |
| Setup | `/ai-engineering-workspace:setup [path]` | Create or upgrade the ticket workspace and templates |
| 1. Understand | `/ai-engineering-workspace:ticket-understand <ID>` | Fetch the ticket + comments, confirm the ask, before any code is touched |
| 2. Investigate | `/ai-engineering-workspace:ticket-investigate <ID>` | Read-only: trace flow, confirm root cause + owner |
| 3. Implement | `/ai-engineering-workspace:ticket-implement <ID>` | Minimal change, only after investigation is confirmed; verification must pass before Finish is allowed |
| 4. Finish | `/ai-engineering-workspace:ticket-finish <ID>` | PR notes, implementation-repo commit report (never executed), handoff — only after implementation is verified complete |

**Use the commands for a hard phase boundary.** If the user asks to "work
on ticket X" conversationally instead of invoking a command, walk them
through the same 4 phases and gates in the conversation — but that path is
prose-gated, not structural, so recommend switching to the commands so
understanding gets confirmed before you read any code. All three phase
transitions have a durable backstop: `context.md` and `investigation.md`
carry `Status: draft` → `confirmed` (a human confirmed the restatement or
diagnosis); `implementation.md` carries `Status: draft` → `complete`
(no second human confirmation needed there — the agent sets it once every
configured verification command passed or was `N/A`). Whichever path
reaches a ticket first, a command run later still has a real precondition
to check instead of guessing.

**Workspace mode**: if a ticket workspace exists (a directory with
`ecosystem.md` and `tickets/` — not `tickets/<TICKET-ID>/`; a new
ticket's own directory won't exist yet, and that must not be read as "no
workspace"), call it `WORKSPACE_ROOT` and read
`$WORKSPACE_ROOT/ecosystem.md`, `$WORKSPACE_ROOT/conventions.md`, and the
ticket's files before starting. If
`$WORKSPACE_ROOT/tickets/<TICKET-ID>/` doesn't exist yet, create it with
`$WORKSPACE_ROOT/scripts/new-ticket.sh <TICKET-ID> "<title>"` — the same
thing `/ticket-understand` does — rather than falling back to standalone
mode. Record results into the ticket files as you go — always via an
explicit `WORKSPACE_ROOT`-relative path, since it's frequently a
different directory from your cwd or the implementation repo you're
working in.
**Standalone mode**: no workspace — follow the same phases, keep the
records in your responses (or a scratch file if the user wants
persistence), and infer conventions from the repo (recent commits, PR
history). There's no `Status:` file to check in this mode — an explicit
confirmation earlier in the conversation satisfies the gate instead.

## Keeping records in sync without over-documenting

Records don't need continuous upkeep — sync happens at the phase gates
that already exist, not on every turn. If Implement (Phase 3) turns up a
fact that contradicts something `investigation.md` already marked
`confirmed`, append a dated `## Correction (<date>)` note to
`investigation.md` instead of rewriting it — the same append-only
discipline the `handoff` skill uses for dead-ends. Never run a standalone
"update the docs" pass outside a gate transition; if nothing changed since
the last gate, there's nothing to sync.

A `## Correction` note doesn't just coexist with the claim it corrects —
it supersedes it. Anyone reading a confirmed ticket document afterward (a
verifier, a resuming session, any later phase) must treat a later-dated
`## Correction` section as overriding the contradictory claim in the
original body. The document's current position is the corrected one, not
the original one, even though `Status:` never stopped saying `confirmed`.
Reading only the original body and stopping there is reading a stale claim
as current — the exact failure this convention exists to prevent.

## Independent verification at gates (v1 scope: Understand / Investigate / structured-bug-fix Phase 3)

**Design principles:**
> The verifier does not prove the draft is correct; it tries to find sufficient reason not to confirm it.
> PASS means "no blocking verification issue was found." It never means "the ticket is confirmed."

**Responsibility model:** Author (main agent, investigating) → fresh adversarial verifier (verdict only, never writes files or `Status:`) → human (sole authority to flip `Status:` to `confirmed`/`complete`). A verifier PASS is necessary but never sufficient to advance Status — that flip only ever happens after the human's explicit confirmation, exactly as elsewhere in this workflow.

**What counts as a material factual claim:**
> A material factual claim is one whose falsity would materially change the gate decision, root-cause assessment, implementation scope, or completion judgment.

Only material claims need anchors (`file:line` or equivalent). Reasoning, interpretation, and hypothesis don't need anchors — they only fail verification if presented as fact without being labeled as such.

**HARD_FAIL has three independent sources — all must be checked, none is optional:**
1. The claim lacks sufficient positive, traceable evidence. Absence of contradictory evidence is not sufficient for PASS.
2. The repo contains material evidence that contradicts the claim — found by independently inspecting nearby/relevant code, not just the anchors the draft supplied. Give the verifier full read access to the repo, not just the cited ranges.
3. The draft contradicts something already `confirmed`/`complete` in an earlier-phase ticket document — only checked where the calling command hands the verifier that earlier document (v1: `context.md` at the Investigate gate only, see scope note below). Read that document per the superseding-`## Correction` rule above first: a claim its own `## Correction` section already overturned is not the document's current position, so a draft that agrees with the correction (and disagrees only with the stale original) is not a contradiction. Once read that way, a contradiction says two claims disagree, not which one is wrong. If the draft's claim is the one that's unsupported or incorrect, fix or downgrade the draft (source 1) and leave the earlier document alone. Only append the earlier document's append-only `## Correction (<date>)` note (never a rewrite) when the new evidence shows the earlier document's current claim, not the draft's, no longer holds.

**SOFT_FLAGS** (surfaced with the gate summary, never blocking): an unaddressed alternate explanation; scope introduced in a restatement that the source material didn't state; a conclusion reachable with fewer intermediate assumptions (fact A → guess B → assumption C → explanation D → conclusion E, when A → E would suffice).

**Flow:**

```text
Author -> draft
   |
Fresh verifier #1
   +-- PASS / SOFT_FLAGS -> gate summary -> human decides
   +-- HARD_FAIL -> author repairs or downgrades the claim
                       |
                   Fresh verifier #2 (a new instance -- never verifier #1 again,
                   so it isn't anchored on its own first hypothesis)
                       +-- PASS / SOFT_FLAGS -> gate summary -> human decides
                       +-- HARD_FAIL -> STOP, report the exact unresolved claim,
                                        do not present a gate summary
```

Dispatch each verifier as a fresh agent with no shared context from the authoring
session — it must not be told the conclusion is expected to be correct.

**Recording** (one line on the ticket's `Status:`-bearing file, no new files):
`Verified: <date> — PASS`, `Verified: <date> — PASS — flags: <short list>`, or
`Verified: <date> — BLOCKED: claim 2 (root cause is X) lacks supporting code
evidence`. Keep the specific unresolved claim in the line — a bare `HARD_FAIL`
tells a future session nothing.

**Scope freeze for v1**: only `ticket-understand.md`, `ticket-investigate.md`,
and `structured-bug-fix.md` Phase 3 call this. All three answer "do we
understand this well enough for a human to confirm the next phase" — one
verification contract. Implement/Finish correctness is a different contract
(tests, diff review, acceptance criteria) and stays out of scope until this
version has run on real tickets and the SOFT_FLAGS noise / HARD_FAIL
false-positive rates are known.

**Cross-document contradiction check (v1 scope: Investigate gate only,
against `context.md`)**: HARD_FAIL source 3 above only fires where the
calling command explicitly hands the verifier an earlier confirmed
document. v1 wires this at Investigate only. Understand has no earlier
confirmed document to check against. structured-bug-fix Phase 3 and
Implement are not wired yet — extend only after this pilot has run on real
tickets, same discipline as the scope freeze above, not as a bundled
change.

## Common rationalizations

| Rationalization | Correct response |
|---|---|
| "The change is small, so I can skip Understand or Investigate." | Small changes still need the same gate; use `/ai-engineering-workspace:ask` if unsure where the ticket is. |
| "`context.md` or `investigation.md` looks complete enough." | Check only the literal `Status:` value. `draft` or missing means stop. |
| "I can continue into the next phase while I have momentum." | Stop at the gate and tell the user the next command to run. |
| "Verification failed, but the failure looks unrelated." | Do not mark implementation complete and do not suggest Finish. Report the failure and stop. |
| "The notes repo and implementation repo are basically the same workflow." | Treat them separately. Implementation repos are never auto-committed or pushed. |
| "The verifier passed, so I can mark `Status:` confirmed myself." | PASS only means no blocking issue was found. The human still has to explicitly confirm before `Status:` changes. |
| "I couldn't find evidence against the claim, so it passes." | Absence of contradicting evidence is not evidence for the claim. It still needs positive, traceable support. |

## Red flags

- Reading code during Understand.
- Editing code during Investigate.
- Running Implement before `investigation.md` has `Status: confirmed`.
- Recommending Finish before `implementation.md` has `Status: complete`.
- Rewriting confirmed investigation history instead of appending a correction.
- Losing track of `WORKSPACE_ROOT` when it differs from the implementation repo.
- Treating a verifier's PASS as equivalent to the human's confirmation.
- Re-running a HARD_FAIL through the same verifier instance instead of a fresh one.
- Letting a verifier write to a ticket file or flip a `Status:` value itself.
- Confirming an investigation draft without giving the verifier `context.md` to check for contradictions.

## Exit criteria

- Understand exits only after the ask is restated and `context.md` is confirmed
  in workspace mode.
- Investigate exits only after facts, hypotheses, owner, and next safe action
  are summarized and `investigation.md` is confirmed in workspace mode.
- Implement exits only after the minimal change is made, configured
  verification has passed or is explicitly `N/A`, and `implementation.md` is
  marked `complete`.
- Finish exits only after PR notes, status update, implementation-repo commit
  report, and handoff are present.
