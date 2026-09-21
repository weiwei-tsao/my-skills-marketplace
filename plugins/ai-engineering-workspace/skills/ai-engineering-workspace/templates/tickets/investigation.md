# <TICKET-ID> Investigation

Status: draft

## Reproduction steps

1. 

## Facts

<!-- Evidence-backed observations only. A negative finding ("not found",
     "not used") is not a bare fact — record it under "Checked but not
     responsible" with its search boundary. -->

- 

## Hypotheses

<!-- Guesses that still need confirmation. Not design options — those go
     under Candidates, and are never "resolved" by choosing one. -->

- 

## Candidates

<!-- Proposed designs, including ones you lean against. Anything that would
     choose between plausible future system shapes — who should own or be
     authoritative for something (ticket-workflow, "Design decisions are not
     findings") — goes here, never under Decisions.
     List at least two plausible ones; one must be the existing mechanism
     for the same concept, if there is one. If no second plausible candidate
     exists, say why rather than inventing one. For every plausible candidate
     (always for one already proposed by an earlier session, the ticket, or a
     reviewer), record what you looked for that would have invalidated it, or
     write "untested" and why — having no preference doesn't waive this.
     A cost or blocker counts against a candidate only if verified; otherwise
     write "unverified" and what it would take to check, and check it before
     it influences the choice.
     Delete this section if the ticket involves no design choice. -->

| Candidate | Why it could work | What I tried to invalidate it | Result |
|---|---|---|---|
|  |  |  |  |

## Decisions

<!-- Human-confirmed choices only: who chose, when, among which candidates,
     and where it was raised (a link, or "not posted"). Not a place for
     conclusions the investigation reached on its own. -->

- 

## Data / component flow

```text
Entry
→ 
→ 
```

## Files inspected

| Repo | File | Why inspected | Finding |
|---|---|---|---|
|  |  |  |  |

## Root cause

<!-- Fill only when confirmed or highly likely. -->

## Trigger conditions (if intermittent / conditional)

<!-- Model as one or more SCENARIOS. Within a scenario, every condition must
     ALL hold for the bug to reproduce — a scenario is a conjunction, not
     one variable. A bug can have more than one independent sufficient
     scenario (e.g. browser+cache OR malformed payload); don't force them
     into a single conjunction, or the other scenario's inputs get recorded
     as "immune" by mistake. For each condition, ask: if this one didn't
     hold, would the symptom still occur under this same scenario? An item
     you can't answer that for is an untested variable, not a ruled-out one.
     Delete this section if the bug reproduces unconditionally. -->

### Scenario 1

1. 

## Owner repo / module

<!-- Which one should own the fix and why? -->

## Checked but not responsible

<!-- Every entry is a negative claim (ticket-workflow, "Negative claims must
     expose their search boundary"). State what was searched and how (query,
     command, file), and what was plausibly relevant but not searched. An
     entry without a boundary is a lead to re-check, not a closed door. -->

| Ruled out | Searched (surface + query) | Not searched |
|---|---|---|
|  |  |  |

## Evidence

<!-- Index of raw material. Keep a line or a few lines inline only when a
     reader needs them to follow a claim. Put longer output (query results,
     grep output, logs, screenshots) in tickets/<TICKET-ID>/evidence/ as
     E<n>-<short-name>.<ext> and add a row here. IDs are unique across the
     whole ticket (next unused E<n> in evidence/, shared with test.md); the
     File column is a ticket-relative path, e.g. evidence/E3-api-query.txt.
     Cite by ID in Facts and in the negative-claim table, e.g. "(E3)".
     Redact secrets and personal data, and say so in the row. -->

| ID | What it shows | How obtained (command or query, date, environment) | File |
|---|---|---|---|
|  |  |  |  |

## Supporting documents

<!-- Authored structured detail this document OWNS (deep-dive analysis,
     runbook, migration plan, ...) that has its own structure and can be
     read independently. Default is inline. Material facts, anchors, verdicts
     and current-state conclusions stay in THIS document; a link is not an
     anchor. Files live in tickets/<TICKET-ID>/supporting/, first line
     `Owner: investigation.md`; File is a ticket-relative path. A document owned by
     another core document is linked in prose, not listed here. Delete this
     section if there are none. -->

| Document | Purpose | File |
|---|---|---|
|  |  |  |

## Open questions

<!-- Includes any finding or candidate that conflicts with, or could be read
     as conflicting with, a stakeholder's stated intent or design direction
     in the ticket: quote it, give the possible readings, and ask the
     decision-maker. A statement of fact that verified evidence contradicts
     is corrected instead, citing the evidence. -->

- 

## Next investigation steps

- 
