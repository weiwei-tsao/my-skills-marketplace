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

**Timeline.** Dated events go in `timeline.md`, not into `context.md` or
`investigation.md` as appended notes (a `## Correction` of a claim that was
false is the one exception). At each gate that flips a `Status:` or appends
a `Verified:` line, and whenever a design question is raised or a design
decision is recorded, append one row to `timeline.md` (workspace mode;
create it from `$WORKSPACE_ROOT/tickets/_template/timeline.md` if it doesn't
exist yet): date, Source `workflow`, who confirmed or acted, the event, and
a note (the `Verified:` verdict; the link or "not posted" for a design
question; who chose, among which candidates, for a decision). One row per
event, no other upkeep. Human-facing events (Jira status changes,
acceptance, deploys) are added when the user provides them, including
during Finish; you can't know them yourself.

**Timeline is a historical event log, not a source of current truth.**
Current requirements, findings, decisions and implementation status stay
authoritative in their owning ticket files (`context.md`,
`investigation.md`, `implementation.md`). A decision that is reopened or
superseded shows up as further rows; the current decision is the one in
`investigation.md`, not the latest row you happen to read.

A `## Correction` note doesn't just coexist with the claim it corrects —
it supersedes it. Anyone reading a confirmed ticket document afterward (a
verifier, a resuming session, any later phase) must treat a later-dated
`## Correction` section as overriding the contradictory claim in the
original body. The document's current position is the corrected one, not
the original one, even though `Status:` never stopped saying `confirmed`.
Reading only the original body and stopping there is reading a stale claim
as current — the exact failure this convention exists to prevent. A
`## Correction` note is for a claim that turned out to be false; because it
supersedes what it corrects, it must not be used to carry a design decision
(see "Design decisions are not findings").

**Evidence.** Raw material (query results, command output, logs,
screenshots) doesn't go into `investigation.md` or `test.md`, which stay
short. Put it in `$WORKSPACE_ROOT/tickets/<TICKET-ID>/evidence/` (create it
when first needed) as `E<n>-<short-name>.<ext>`, and add one row to the
`## Evidence` index of the document that relies on it: the ID, what it
shows, how it was obtained (command or query, date, environment), and the
file. Evidence IDs are unique within the ticket, not within a document:
before creating a file, take the next unused `E<n>` across the whole
`evidence/` directory, so `investigation.md` and `test.md` never both have
an `E1` and a bare "(E3)" always means one thing. Record the file as a
ticket-relative path, e.g. `evidence/E3-api-query.txt`, never a bare file
name, since the workspace is often not your cwd. A few lines a reader needs
to follow a claim stay inline. Cite by ID in Facts and in the negative-claim
table, e.g. "(E3)"; code anchors stay `file:line`. Redact secrets and personal data before saving and say so in
the row. The row is what makes an evidence file usable: without what it
shows and how it was obtained, it can be neither judged nor reproduced.

**Supporting documents.** `investigation.md`, `implementation.md` and
`test.md` are summaries and current state, not containers for every detail.
What can't be re-derived by reasoning (an observation) is evidence; what we
authored (a deep-dive analysis, route comparison, runbook, dry-run
procedure, migration or rollout plan) may be a supporting document at
`$WORKSPACE_ROOT/tickets/<TICKET-ID>/supporting/<short-name>.md`, created
when first needed. A runbook's execution output is evidence, the runbook is
supporting, and the verdict stays in `test.md`. **Default is inline;
extraction is deliberate**, and only when both hold: (1) it has its own
structure or independently executable steps and can be understood without
the phase document; (2) the owning document can keep, in a few lines,
everything its gate needs. Length isn't the test, and "cited often" or "the
core document is losing scanability" are signals, not conditions.

- Material facts, anchors, verdicts and current-state conclusions stay in the
  owning document. A link to a supporting document is not an anchor.
- Exactly one owner, named on the file's first line (`Owner: test.md`);
  other documents may link to it. No `Status:` of its own: it inherits the
  owner's gate. The owner indexes it, one row per document, in
  `## Supporting documents` (Document, Purpose, File as a ticket-relative
  path). `context.md` is never an owner.
- At a verifier gate, a supporting document that a gate-bound material claim
  materially relies on is part of the verification input (not the whole
  directory). It and its owner form one verification unit: a material edit
  to either after PASS invalidates that PASS, and the draft is re-verified
  before it is confirmed.
- After the owner is confirmed, an edit that leaves its conclusion unchanged
  needs nothing more. One that changes it is never a supporting-only edit:
  `investigation.md` gets a `## Correction`; `implementation.md` and
  `test.md`, which have no Correction convention and no verifier, have their
  summary updated in place.

## Independent verification at gates (v1 scope: Understand / Investigate / structured-bug-fix Phase 3)

**Design principles:**
> The verifier does not prove the draft is correct; it tries to find sufficient reason not to confirm it.
> PASS means "no blocking verification issue was found." It never means "the ticket is confirmed."

**Responsibility model:** Author (main agent, investigating) → fresh adversarial verifier (verdict only, never writes files or `Status:`) → human (sole authority to flip `Status:` to `confirmed`/`complete`). A verifier PASS is necessary but never sufficient to advance Status — that flip only ever happens after the human's explicit confirmation, exactly as elsewhere in this workflow.

**What counts as a material factual claim:**
> A material factual claim is one whose falsity would materially change the gate decision, root-cause assessment, implementation scope, or completion judgment.

Only material claims need anchors (`file:line` or equivalent). Supporting documents such a claim relies on are verifier input (see "Supporting documents"). Reasoning, interpretation, and hypothesis don't need anchors — they only fail verification if presented as fact without being labeled as such.

**A claim's evidence burden scales with its scope, not with whether it's phrased as inclusion or exclusion.** "This code path didn't execute" is a bounded claim — one trace settles it. "This repo is not responsible" and "this is the complete root cause" are both broad claims, and both need every plausible mechanism within that scope addressed, not just the one the author happened to check — a root-cause claim that only rules in the mechanism it found, without ruling out the alternates the same evidence is also consistent with, has the identical gap as an under-scoped exclusion. Exclusion claims ("X is not the cause" / "ruled out" / "checked, not responsible" / "immune") tend to be broad by default, which is why they're easy to under-evidence: a single evidence line (e.g., one file's last-modified timestamp) rules out the one mechanism it touches, not the module/repo/theory as a whole. Route any broad claim through the same gate as the root cause — including one reached informally mid-investigation, outside the formal diagnosis write-up, if it will be stated to the user as a reason to proceed (e.g., "you can hand this off now"). A claim doesn't get to skip verification for having been discovered off to the side instead of in the template.

**HARD_FAIL has five independent sources — all must be checked, none is optional:**
1. The claim lacks sufficient positive, traceable evidence. Absence of contradictory evidence is not sufficient for PASS. For a broad claim (an exclusion covering a whole module/repo/theory, or a root cause asserted as complete), evidence sufficient to address one mechanism is not sufficient for the full scope claimed — the verifier must confirm other plausible mechanisms within that scope were also addressed, not just the one path the author happened to look at. A negative claim with no stated search boundary lacks sufficient evidence by definition (see "Negative claims must expose their search boundary").
2. The repo contains material evidence that contradicts the claim — found by independently inspecting nearby/relevant code, not just the anchors the draft supplied. Give the verifier full read access to the repo, not just the cited ranges.
3. The draft contradicts something already `confirmed`/`complete` in an earlier-phase ticket document — only checked where the calling command hands the verifier that earlier document (v1: `context.md` at the Investigate gate only, see scope note below). Read that document per the superseding-`## Correction` rule above first: a claim its own `## Correction` section already overturned is not the document's current position, so a draft that agrees with the correction (and disagrees only with the stale original) is not a contradiction. Once read that way, a contradiction says two claims disagree, not which one is wrong. If the draft's claim is the one that's unsupported or incorrect, fix or downgrade the draft (source 1) and leave the earlier document alone. Only append the earlier document's append-only `## Correction (<date>)` note (never a rewrite) when the new evidence shows the earlier document's current claim, not the draft's, no longer holds.
4. The draft treats a design choice (see "Design decisions are not findings") as settled: it sits under Decisions with no recorded choice by the decision owner, or it is filed as a hypothesis and marked resolved, or a candidate comparison counts an unverified claim as a cost or benefit without marking it unverified, or it is recorded in `context.md` (as an answered Open question or an appended update) with no matching Decisions entry, or it presents one candidate with neither a plausible alternative nor an explanation of why no second candidate exists, or a plausible candidate has neither a recorded falsification attempt nor an explicit "untested" with the reason. Declaring no preference does not waive this. A design decision is never confirmed by the draft's own findings.
5. The draft conflicts with — or can reasonably be read as conflicting with — a stakeholder's stated intent, requirement or preferred design direction recorded in `context.md` (a ticket comment, a review remark), and the draft presents the conflicting conclusion as settled or does not carry the conflict as an explicit unresolved question for the gate (see "Conflicts with stakeholder intent or design direction go to the decision-maker"). The verifier checks that the question exists and that the draft has not resolved it by its own reading; it does not require it to have been put to the decision-maker yet, because that happens at the gate, after verification. Unlike source 3, this is not settled by fixing or downgrading the draft alone: the draft must surface the conflict as a question. An ambiguous statement counts, and so does a conclusion that a candidate the statement favours is unsuitable. A statement of fact that verified evidence contradicts is not a conflict to raise; the draft says so, citing the evidence.

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

## Design decisions are not findings

This workflow grew out of bug diagnosis: establish what happened, find who
owns the fix, implement. That fits *diagnostic* work, which asks "what is
true now?" *Design* work asks "what should become true?" — a choice between
plausible future system shapes — and needs different evidence: candidates
and a decision owner instead of a root cause. They are different claim
types, and a ticket can start diagnostic and cross into design partway
through Investigate: the findings establish the current state, then the
next question becomes "who should own this?" Investigate is responsible for
noticing that crossing, not only for finding root causes. There is no
separate design phase; the crossing changes how that question is handled,
not which command runs.

The gates above answer "is this claim about the system true?" A design
decision answers a different question. Evidence that a change is *feasible*
(an existing transport, a mature config model, a clean diff) never
establishes that it is *correct*. Don't route a design choice through the
same gate as a root cause, and don't let a well-supported set of findings
carry it there.

**Trigger** — check it when writing next steps and the gate summary, and
whenever a question of the form "should X own / live in / be authoritative
for Y?" appears; crossing happens mid-investigation, so checking once at
the start isn't enough. A next step is a design decision if it requires
choosing between plausible future system shapes, especially if it would:
- create or move a source of truth, or change which layer is authoritative
  for a concern;
- move responsibility across module, repo, or service boundaries;
- introduce an abstraction or shared interface other code will depend on;
- create precedence, fallback, override, or synchronization semantics;
- duplicate state or behavior that already exists elsewhere.

When unsure, ask: *does this introduce a second, independently mutable
representation of a concept, or a second owner of a behavior, that may
already have one?* If the answer might be yes, treat it as a design
decision. Not a trigger: fixing a defect in the layer that already owns the
behavior — that is diagnosis, however large the diff.

**Handling:**
1. Findings go under Facts. A proposed design goes under **Candidates** —
   never under Decisions, and never under Hypotheses: a design question is
   not a hypothesis, and marking it "resolved" by picking an option is a
   decision made without its owner.
2. List at least two plausible candidates. One must be the existing
   mechanism for the same concept, if there is one — investigated as a
   first-class candidate, not dismissed because it isn't reachable from the
   path currently being inspected. "Not exposed here" is a finding about the
   transport, not about suitability. If, after investigating, no second
   plausible candidate exists, record why instead of inventing one — a
   strawman ("leave everything as is") satisfies the count and defeats the
   purpose.
3. For every plausible candidate — and always for one an earlier session,
   the ticket, or a reviewer already proposed — record what you looked for
   that would have invalidated it, and what you found. A candidate supported
   only by positive evidence hasn't been tested. Having no preference among
   them doesn't waive this. Where you can't test one (no access, no time),
   write "untested" and why; an untested candidate is presented as untested,
   never as validated. A constraint or cost used to count against a
   candidate is itself a claim, whether reported second-hand (a meeting
   note, a comment) or your own hypothesis. Until it is checked — on
   runtime and packaged state as well as source — it is unverified, and an
   unverified claim neither eliminates a candidate nor counts as a cost or
   benefit in a comparison. Show it as "unverified" and say what it would
   take to check or resolve it; then check it, rather than reasoning around
   it, before it influences the choice. A problem never checked can turn out
   to be a small task, and stating it as a blocker overstates its severity
   and complexity.
4. A design decision is confirmed only by an explicit choice among the
   candidates from the person who owns that decision — never by `Status: confirmed` on the investigation alone, and
   never by a verifier PASS. Stop, present the candidates and the
   falsification results, say plainly that this is a decision and not a
   diagnosis, and wait. The person with authority over that boundary decides;
   name who that likely is if the ticket or repo makes it clear. Raise it
   for team visibility before it is decided: if `conventions.md`'s "Design
   decisions" field names a channel, draft the question for the user to
   post there — the candidates, what was tried to invalidate each, what is
   still unverified, your recommendation if you have one, and any
   conflicting stakeholder statement quoted verbatim. The draft is for
   visibility, not because someone else must approve; the decision owner
   may well be the user. If the field is missing, ask the user once where
   such questions go and suggest saving the answer to `conventions.md`. This
   is a soft prompt: the user decides whether to post and whether to wait
   for replies. **Never post, comment on, or message the design question
   yourself:** draft it (a chat message, a Jira or issue comment) for the
   user to send. This doesn't change the suite's existing Notes repo
   automation rules.
5. Record the choice under Decisions in `investigation.md`: who chose, when,
   among which candidates, and where it was raised (a link, or "not
   posted"). That entry is the only place the choice is
   recorded as a decision. `context.md` is the requirements record, not a
   decision log: don't write a design choice into it, whether as a rewritten
   Open question or an appended update — it would read later as a
   requirement and hide who chose it. If an Open question in `context.md`
   turns out to hinge on the choice, point it at the Decisions entry
   ("answered by the Decisions entry in `investigation.md`: who, when")
   instead of resolving it in prose there.

## Conflicts with stakeholder intent or design direction go to the decision-maker

If a finding, a candidate's ranking, or a recommendation conflicts with —
or can reasonably be read as conflicting with — a stakeholder's stated
intent, requirement or preferred design direction, in the ticket, its
comments, or a review, especially about the same question, don't resolve it
by your own reading and don't record the conclusion as settled. Ambiguity in
what they said is the reason to ask, not a licence to pick the reading that
fits your conclusion.

**Facts are different.** A stakeholder's statement of fact ("service A owns
this", "plugin X isn't active") that verified evidence contradicts is not a
conflict to escalate: say so plainly, citing the evidence, as the suite's
Golden Rules already require — the statement is stale or wrong. Only
evidence you have actually checked can correct a statement; an unverified
finding never overrides one. A statement often mixes both ("X is handled by
function F and should be the source of truth"): evidence settles the factual
half, and the direction half still goes to the decision-maker. When you
can't tell whether a statement is fact or intent, treat it as intent and
ask.

**Handling:**
1. Quote the statement verbatim, with who said it and where.
2. Say what it appears to conflict with, and which readings are possible —
   side by side, each with the design it leads to, including a reading that
   differs from the one you or the decision-maker started with.
3. Put the question to the decision-maker at the gate: which reading
   applies, and should the conclusion stand, change, or be replaced? (It is
   not a contest: the conclusion may also satisfy the requirement behind the
   statement once that is read correctly.) Until they answer, the conclusion
   is a proposal, not a finding.

Order matters: before the gate, the draft only has to carry the conflict as
an explicit unresolved question (that is what verification checks);
actually asking the decision-maker happens at the gate, after
verification. A draft that carries the question is not a failure.

**When to suggest asking the statement's author.** Not every ambiguous or
doubtful statement needs its author (a ticket creator, a commenter), and
you shouldn't ask before you have looked: at Understand, only record the
ambiguity. Suggest asking only when all three hold:
1. The statement expresses intent, a requirement, or a design direction,
   rather than a fact you can verify. A requirement can be ambiguous too
   ("each property should have one language value" may mean one canonical
   value, or only one value for the front-end metadata).
2. It has two or more reasonable readings that lead to different designs.
   If the readings converge on the same design, don't ask.
3. Code and docs can't settle it, and choosing wrong is costly — the
   design-decision trigger (a new or changed source of truth, ownership, or
   boundary).

Don't suggest it for a symptom description, a verifiable claim of fact, a
suggestion the decision-maker is free to depart from, or a cheap, reversible
change. When all three hold, lay the readings out side by side at the gate
and draft one line for the user to send: "You said X — do you mean (a) or
(b)?" It is a soft prompt: the decision-maker may hold the same misreading,
which is why the readings are laid out, and whether to ask is theirs. Never
send it yourself.

Watch especially for a conclusion that a candidate is "unsuitable",
"impractical" or "not the right fit" when the statement favours that very
candidate: it needs this step before it is stated, not after. A conflict
that is only ever fixed by downgrading your own draft, and never raised, is
still an unsurfaced conflict.

## Negative claims must expose their search boundary

"Not found", "not used", "not exposed", "no consumer", "not active",
"doesn't exist", and every exclusion ("ruled out", "checked, not
responsible") are claims about the surfaces searched, not about the system.
A negative claim's evidence *is* its search boundary — without one it can't
be verified, only believed.

**Every negative claim recorded in a ticket document states** the surfaces
searched (and how — the query, command, or file read) and the surfaces
plausibly relevant but *not* searched. Surface classes to consider, not all
will apply:
- repository source;
- resolved dependencies, including where the installed or pinned version
  differs from the local checkout;
- runtime or packaged state: container or image contents, mounted volumes,
  generated files, installed artifacts;
- sibling, upstream, or dependency repositories that aren't in the usual
  repo map;
- external or remote configuration.

**The evidence boundary is not the normal repo boundary.** The repo map
says where code is usually edited, not everywhere the relevant behavior can
live. Inspect runtime and packaged state read-only (see "Never manufacture
failure against live or shared state").

**An empty result is re-run before it counts.** Re-run it once with a
materially different formulation — drop punctuation or arguments, change
case, search the symbol instead of a call form, search from the other
direction — before recording it. A single empty search is insufficient
negative evidence: it only shows that one formulation, on one surface,
found nothing — the thing may exist under a different spelling or call
form.

**A negative finding without a recorded search boundary doesn't get "don't
retry" status.** Dead-ends and checked-not-responsible entries exist to save
a later session from repeating work, which is only safe when the boundary is
visible. An entry without one is a lead to re-check, not a closed door. This
is a persistence problem, not only a search problem: a weak negative written
down once and marked "don't retry" compounds across sessions instead of
being corrected.

**Coverage independence.** A fresh verifier is cognitively independent — not
anchored on the author's reasoning — but one that repeats the author's query
on the author's surface shares the author's blind spot, and its PASS means
little. For a draft containing negative claims, the verifier's job is to try
to overturn each one, not reconfirm it: run at least one materially
different query or inspection method, and inspect at least one plausible
surface class the author did not *search* — the author's "not searched"
list is a valid place to pick one. If the author already searched every
plausible surface class for the claim, the verifier states why no further
class exists and challenges the claim by a different method or from a
different direction instead.

## Never manufacture failure against live or shared state

Applies wherever this workflow reproduces a bug, tests a trigger
condition, or verifies a check — not just the known-bad-input rule below.
Manufacturing a failure, trigger condition, or negative test by mutating
production or other live/shared state (rows in a shared database, a
shared staging environment, a shared third-party sandbox account, a queue
other workflows read from) needs explicit human direction and an
established safe procedure — this is not the agent's own judgment call to
make, no matter how necessary it seems. Fabricating destructively inside
an isolated, disposable environment whose state isn't shared with other
users or workflows doesn't need that sign-off — use one there instead of
touching live/shared state whenever a safe isolated option exists.
Against live/shared systems, use read-only observation rather than
manufacturing the condition — who's authorized to read what is a
separate question this workflow doesn't define.

## Decorative checks

Applies to any check written into this workflow — a gate verifier's
evidence, a diagnostic query in Investigate, an audit in
structured-bug-fix, a verification command in Implement. For each one,
ask: "would this check's output differ between the case where the
condition it's supposed to catch is absent and the case where it's
present?" This is a comparison across two states, not a single
hypothetical readback of the check's current output — if the data you're
looking at already has the defect present and the check correctly shows
that, the check isn't decorative; matching a reality that's already bad is
not the failure mode. If the honest answer to the two-state comparison is
"no — it would show the same thing either way," the check is decorative —
it carries zero information no matter how official it looks, and
restating it in your own words (not just re-reading the sentence someone
else wrote) is usually what forces this
out; a check can survive several rounds of review unquestioned precisely
because everyone re-read the same description instead of asking what it
delivers. A decorative check sitting directly in front of an irreversible
action (a write, a delete, a send with no undo) is worse than no check at
all — it converts "we don't know" into a false "we verified."

Passing on known-good input only proves the check doesn't false-positive —
that's the easy half. Where the check can be exercised safely in an
isolated fixture or disposable sandbox whose state isn't shared with other
users or workflows, run it against known-bad input (an empty bucket a
`GROUP BY` should surface, one deliberately corrupted fixture, a stubbed
failure) and confirm it actually fails (see "Never manufacture failure
against live or shared state" above — this is that rule applied to
checks). For a check against live or otherwise non-fabricable state,
state concretely what observable result would constitute the bad case
(would this row be included, excluded, or silently absent?) and why the
check would produce a different result for it — reasoned through by hand,
not manufactured. A check whose failure path has neither been observed nor
demonstrated this way is not yet strong verification — it's been watched
nodding along.

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
| "This is just ruling something out, not asserting the root cause, so it doesn't need the same verification." | A broad claim's evidence burden doesn't shrink because it's phrased as a negative — route it through the same gate regardless of phrasing. |
| "I found this while investigating something else, so it's a side observation, not part of the diagnosis." | If it will be stated as a reason to proceed, it's a material claim regardless of where it was discovered. |
| "This check passed, so the thing it verifies is fine." | Compare the check's output with the condition absent versus present. If it wouldn't differ, the check is decorative regardless of how official it looks. |
| "This check has always passed, so it must be reliable." | Its failure path needs to have been observed on known-bad input, or — where fabrication isn't safe — concretely reasoned through. Neither yet? Not strong verification, just watched nodding along. |
| "The existing mechanism makes this easy to implement, so the design is settled." | Ease of implementation is a feasibility finding. Whether it should own the value is a design decision: list candidates, including the existing owner, and try to invalidate each plausible one. |
| "I have no preference among the candidates, so there is nothing to falsify." | Every plausible candidate needs a recorded falsification attempt or an explicit "untested" with the reason. No preference is not an exemption; it just means nobody has been tested yet. |
| "This route removes an unresolved blocker from the critical path, so it's the better route." | Not needing an open question answered is a cost saving, not evidence of correctness. The question may be the real decision: keep it open and put it to the decision owner. |
| "I'll note the answer to that open question in `context.md` so it's visible." | `context.md` is requirements. A design choice written there reads later as a requirement and hides who chose it. Record it under Decisions and point the open question at that entry. |
| "It's only a hypothesis, but it's surely a real problem, so I'll count it against this candidate." | Unverified is unverified: mark it as such, don't score it, and check it. It is usually cheaper to verify than to reason around, and a problem nobody checked can turn out to be a small configuration task. |
| "The comment's meaning is obvious to me, so there's nothing to compare." | The reading that feels obvious is the one least likely to be challenged. List the other reasonable reading and the design it leads to; if they diverge on something costly that code can't settle, suggest asking the author. |
| "The comment is ambiguous, so my reading of it is fine." | Ambiguity is the reason to ask. Quote it, lay out the readings, and let the decision-maker say which applies before you state a conclusion that depends on one. |
| "My finding says the candidate the comment favours is unsuitable, so the comment is simply outdated." | A preference or design direction isn't made outdated by your finding: that is a conflict to raise, not to resolve. Say the comment and the finding disagree, and ask. Only a statement of fact that verified evidence contradicts is just corrected, citing the evidence. |
| "That constraint came from a meeting note, so it's a given." | A second-hand constraint that eliminates a candidate is a claim. Verify it — including on runtime and packaged state — or mark the candidate untested; don't use it to rule the candidate out. |
| "The existing owner isn't exposed on the path I'm inspecting, so it isn't a practical option." | "Not exposed here" describes the transport, not suitability. Investigate it as a candidate. |
| "The search returned nothing, so nothing uses it." | One formulation on one surface. Re-run it differently and record what was and wasn't searched. |
| "The verifier re-ran my search and got the same result, so the negative claim is verified." | Same query on the same surface shares the same blind spot. The verifier must try to overturn it with a different query or method and a surface class the author didn't search. |
| "It's in the dead-ends list, so I shouldn't re-check it." | Only if it records its search boundary. Without one it's a lead, not a closed door. |

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
- Stating an exclusion ("X is ruled out", "not responsible") to the user as settled without routing it through verification, especially one backed by a single evidence line or discovered outside the formal diagnosis draft.
- Trusting a check that would show the same result whether the condition it checks is true or false — especially one guarding an irreversible write/delete/send.
- Treating a check as proven because it passed on known-good data, without ever having seen it fail on known-bad data or, where that isn't safely fabricable, reasoned through why it would.
- Recording a design choice under Decisions on the strength of findings alone, or on the investigation's `Status: confirmed`.
- Dismissing an existing mechanism because it isn't reachable from the path being inspected.
- Recording a negative finding without the surfaces searched and not searched.
- Treating a single empty query as a finding.
- A verifier reconfirming a negative claim with the author's own query on the author's own surface.
- Honoring a dead-end that records no search boundary.
- Posting, commenting on, or messaging a design question yourself (a chat message, a Jira or issue comment). You draft; the user sends.
- Filing a design choice under Hypotheses and marking it resolved.
- Writing a design choice into `context.md` — as an answered Open question or an appended update — instead of a Decisions entry.
- Concluding that a candidate is unsuitable when a stakeholder's stated direction in the ticket favours it, without quoting the statement and asking the decision-maker.
- Resolving an ambiguous stakeholder statement of intent or direction by your own reading, or overriding a statement of fact with a finding you haven't verified.
- Eliminating a candidate with a constraint nobody has verified, counting an unverified hypothesis as a cost in a comparison, or choosing a route because it sidesteps an open question.

## Exit criteria

- Understand exits only after the ask is restated and `context.md` is confirmed
  in workspace mode.
- Investigate exits only after facts, hypotheses, owner, and next safe action
  are summarized and `investigation.md` is confirmed in workspace mode. If
  the next action is a design decision, it exits only after its owner has
  chosen among the candidates and that choice is recorded; the
  `Status: confirmed` line is not set while one is unresolved.
- Implement exits only after the minimal change is made, configured
  verification has passed or is explicitly `N/A`, and `implementation.md` is
  marked `complete`.
- Finish exits only after PR notes, status update, implementation-repo commit
  report, and handoff are present.
