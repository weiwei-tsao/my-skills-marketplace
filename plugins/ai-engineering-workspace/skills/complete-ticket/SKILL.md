---
name: complete-ticket
description: Complete an engineering ticket by turning ticket workspace files into a private closure record, private repo relationship memory, public-safe technical notes, and public-safe system design lessons. Use after ticket-workflow finish, when closing a ticket, when rerunning completion with new evidence, or when the user asks to complete/summarize a ticket into durable knowledge.
---

# Complete Ticket

Turn a finished or intentionally drafted engineering ticket into durable
knowledge. This skill is a closure and knowledge-extraction step. It does not
implement code, run deploys, create PRs, or replace `ticket-workflow`.

## Source Skills And References

Before writing public-safe artifacts:

1. Read the local `weiwei-notes` skill if available:
   `../../../weiwei-notes/skills/weiwei-notes/SKILL.md`.
2. Read the local system design references if available:
   `../../../system-design-coach/references/interview-rubric.md` and
   `../../../system-design-coach/references/topic-map.md`.

If those files are unavailable, continue with the rules in this skill. Do not
block ticket completion solely because companion skill references are missing.

## Modes

Default to **strict mode**.

Strict mode requires evidence for:

- Final outcome or decision.
- Confirmed root cause, or an explicit final decision when no root cause applies.
- Owner repo or module.
- Actual implementation summary.
- Test notes.
- PR, status, or ticket closure notes.
- Acceptance and deploy status, or an explicit reason they are not needed.

If strict mode lacks required evidence, stop before writing final artifacts and
return a concise missing-evidence checklist.

Use **draft mode** only when the user explicitly asks for a draft, partial
completion, interim writeup, or pre-completion knowledge extraction. Draft mode
may write artifacts, but every artifact and the final response must clearly
label unresolved gaps.

## Workspace Discovery

Workspace mode exists when a directory contains both:

- `ecosystem.md`
- `tickets/`

In workspace mode:

1. Read `ecosystem.md`.
2. Read `conventions.md` when present.
3. Identify the ticket directory from the user request, current path, branch
   name, or existing `tickets/<TICKET-ID>/` folders.
4. Read the selected ticket files when present:
   - `context.md`
   - `investigation.md`
   - `implementation.md`
   - `test.md`
   - `pr.md`
   - `timeline.md`
   - `handoff.md`

If no workspace exists, operate in standalone draft mode only. Use the current
conversation and user-provided files as source material, and explain that final
strict completion requires a ticket workspace or equivalent evidence.

## Evidence Package

Build a compact evidence package before writing artifacts. Separate:

- Facts: evidence-backed observations.
- Hypotheses: still unresolved guesses.
- Decisions: confirmed choices or product/engineering decisions.
- Final outcome.
- Root cause or final decision.
- Owner repo/module.
- Request or data flow.
- Repos, services, surfaces, and modules involved.
- Files inspected and changed.
- Tests and acceptance checks.
- Risks and follow-ups.
- Links back to ticket evidence.

Do not invent repo relationships, implementation details, acceptance status, or
system design lessons to make the output feel complete.

## Artifact Layout

For ticket `ABC-123`, write:

```text
tickets/ABC-123/
  completion.md
  repo-relationships.md

knowledge/
  private/
    repo-relationships/
      ABC-123.md
    repo-relationships-index.md
  public-safe/
    technical-notes/
      ABC-123-<slug>.md
    system-design-lessons/
      ABC-123-<slug>.md
```

If the user specifies an external notes repository or knowledge root, use the
same `knowledge/` substructure under that root.

## Privacy Boundaries

Private artifacts preserve real context:

- `tickets/<TICKET-ID>/completion.md`
- `tickets/<TICKET-ID>/repo-relationships.md`
- `knowledge/private/repo-relationships/<TICKET-ID>.md`
- `knowledge/private/repo-relationships-index.md`

Public-safe artifacts must be redacted:

- `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
- `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

Public-safe bodies must not expose company names, customer names, internal
project names, real repo names, ticket IDs, PR links, Slack links, people, file
paths, URLs, domains, table names, queue names, service names, environment
names, internal constants, API routes, feature flags, exact incident
identifiers, or uniquely identifying timing and scale details.

Public-safe writing should preserve the transferable technical idea: product
goal, generic system roles, tradeoffs, data flow, ownership boundaries, failure
modes, observability, and migration or rollback implications.

## Relationship Artifact Boundaries

`tickets/<TICKET-ID>/repo-relationships.md` is the ticket-local evidence
narrative. It is optimized for reconstructing what happened in this ticket. It
includes evidence links, rejected paths, hidden coupling, and the exact ticket
lesson.

`knowledge/private/repo-relationships/<TICKET-ID>.md` is the reusable
relationship card. It is optimized for future recall. It must not mirror the
ticket-local evidence narrative. Include the mental model, repos/surfaces,
ownership boundary, request or data flow, when to consult the note again, and
links back to ticket evidence. Omit step-by-step investigation history, rejected
debugging paths, raw command output, and PR/process details unless they directly
explain a system relationship.

`knowledge/private/repo-relationships-index.md` is a short cumulative index. It
helps locate the detailed relationship card; it is not the detailed note.

## Idempotency And Re-Runs

This skill must be safe to run more than once for the same ticket.

Regenerate these files as authoritative snapshots:

- `tickets/<TICKET-ID>/completion.md`
- `tickets/<TICKET-ID>/repo-relationships.md`
- `knowledge/private/repo-relationships/<TICKET-ID>.md`
- `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
- `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

When replacing a generated file, preserve only intentional user-owned content if
the file has a clearly marked manual section. This first version does not define
manual sections, so the default is full regeneration from current ticket
evidence.

For public-safe files, treat `<TICKET-ID>` as the stable identity. On re-run,
find existing files in the artifact directory with the same ticket ID prefix and
keep exactly one current file per artifact type. If the regenerated title
changes the slug, remove or replace the stale same-ticket file. Track removed or
replaced files and report them in the final response.

For `knowledge/private/repo-relationships-index.md`, upsert by ticket ID. Find
the existing section for the ticket and replace that section. Append a new
section only when no entry exists for the ticket.

Use this stable heading shape:

```markdown
## <Topic> - <TICKET-ID>
```

Match existing index entries by `<TICKET-ID>` even if `<Topic>` changes.

## Slug Generation

Public-safe artifact filenames use:

```text
<TICKET-ID>-<slug>.md
```

Generate `<slug>` from the final public-safe article title after redaction, not
from raw ticket titles, repo names, service names, branch names, PR titles, or
other private source material.

Slug rules:

- Lowercase.
- ASCII only.
- Replace spaces and punctuation with single hyphens.
- Remove characters outside `a-z`, `0-9`, and `-`.
- Collapse repeated hyphens.
- Trim leading and trailing hyphens.
- Limit to 60 characters.

If the redacted title produces an empty slug, use:

- `technical-note` for technical notes.
- `system-design-lesson` for system design lessons.

Slug uniqueness is scoped by artifact directory. Different tickets may share the
same slug because the ticket ID prefix keeps filenames distinct.

## Generation Order

Generate private artifacts first:

1. `tickets/<TICKET-ID>/completion.md`
2. `tickets/<TICKET-ID>/repo-relationships.md`
3. `knowledge/private/repo-relationships/<TICKET-ID>.md`
4. Upsert `knowledge/private/repo-relationships-index.md`

Then generate public-safe artifacts:

1. `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
2. `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

## Output Contracts

### `completion.md`

```markdown
# <TICKET-ID> Completion

## Final Outcome

## Completion Status

## Root Cause / Final Decision

## Owner Repo / Module

## Implementation Summary

## Test And Acceptance Evidence

## Repo Relationship Takeaways

## Knowledge Artifacts

## Follow-Ups
```

### Ticket-Local `repo-relationships.md`

```markdown
# <TICKET-ID> Repo Relationships

## One-Line Mental Model

## Repos / Surfaces Involved

## Request Or Data Flow

## Ownership Boundaries

## Hidden Couplings Or Surprising Dependencies

## Rejected Paths / Not Responsible

## What This Ticket Taught Us

## Links Back To Evidence
```

### Private Relationship Card

```markdown
# <TICKET-ID> <Relationship Topic>

## Mental Model

## Repos / Surfaces

## Ownership Boundary

## Request Or Data Flow

## Useful When

## Ticket Evidence
```

### Cumulative Index Entry

```markdown
## <Topic> - <TICKET-ID>

- Mental model:
- Repos / surfaces:
- Useful when:
- Detailed note:
```

### Public-Safe Technical Note

Use `weiwei-notes` style: conclusion first, root-cause oriented, concise,
technical English terms preserved in Chinese, no AI-sounding framing, and both
Simplified Chinese and English versions unless the user explicitly asks
otherwise.

```markdown
# <Conclusion-Or-Core-Question>

## 简体中文

## English
```

### Public-Safe System Design Lesson

Use only relevant system design dimensions supported by the ticket evidence:
requirements framing, API/data model, ownership boundaries, architecture and
scalability, reliability/consistency/failure modes, observability/operations,
security/privacy, and tradeoffs. Do not force every dimension into every lesson.
Do not turn the output into an interview drill.

```markdown
# <Public-Safe Lesson Title>

## 简体中文

## English
```

## Final Review

Before the final response, check:

- Strict or draft status is clearly labeled.
- Private files may contain real identifiers.
- Public-safe files are redacted.
- Ticket IDs and real repo/service names do not appear in public-safe article
  bodies.
- Evidence links point back to ticket-local files where useful.
- Missing inputs or unresolved questions are visible.
- The cumulative repo relationship index is short and scannable.
- Re-running the same ticket did not duplicate public-safe files or cumulative
  index entries.
- The final response lists files written, files removed or replaced, and gaps.
