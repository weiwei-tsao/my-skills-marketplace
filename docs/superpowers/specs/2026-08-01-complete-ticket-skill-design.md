# Complete Ticket Skill Design

## Summary

Add a new `complete-ticket` skill to the existing `ai-engineering-workspace`
plugin. The skill turns a completed engineering ticket into durable knowledge:
a private ticket closure record, private repo relationship context, public-safe
technical notes, public-safe system design lessons, and a short cumulative repo
relationship index for fast recall.

The skill extends the lifecycle already started by `ticket-workflow`. It does
not replace investigation, implementation, testing, PR notes, or handoff.
Instead, it runs after those materials exist and converts them into reusable
context.

## Placement

Create the skill at:

```text
plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
```

Update the surrounding catalog and documentation to describe
`ai-engineering-workspace` as a five-skill suite rather than a four-skill suite.

## Modes

`complete-ticket` has two modes:

- **Strict mode** is the default. The skill checks for enough completion
  evidence before producing final artifacts.
- **Draft mode** runs only when the user explicitly asks for a draft, partial
  completion, or interim knowledge extraction. Draft artifacts must clearly
  label missing inputs and unresolved uncertainty.

Strict mode requires evidence for:

- Final outcome or decision.
- Confirmed root cause, or an explicit final decision when no root cause applies.
- Owner repo or module.
- Actual implementation summary.
- Test notes.
- PR, status, or ticket closure notes.
- Acceptance and deploy status, or an explicit reason they are not needed.

If strict mode lacks required evidence, the skill stops and returns a concise
checklist of missing information instead of producing final artifacts.

## Artifact Layout

For ticket `ABC-123`, write two layers of artifacts.

### Ticket-Local Layer

Real ticket, repo, service, and project context is preserved here.

```text
tickets/ABC-123/
  completion.md
  repo-relationships.md
```

`completion.md` is the closure page for the ticket. It records the final
outcome, root cause or final decision, owner repo/module, implementation
summary, tests, acceptance, deploy or rollback notes, knowledge artifact links,
and follow-ups.

`repo-relationships.md` is the ticket-local evidence narrative. It is optimized
for reconstructing what happened in this ticket. It records involved repos,
services, surfaces, request or data flow, ownership boundaries, hidden coupling,
surprising dependencies, evidence links, rejected paths, and the specific lesson
learned from the ticket.

### Workspace Knowledge Layer

By default, use a workspace-local `knowledge/` directory. If the user specifies
an external notes repository or knowledge root, use the same structure under
that root.

```text
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

`knowledge/private/repo-relationships/ABC-123.md` is the reusable relationship
card for future recall. It also preserves real context, but it must not mirror
the ticket-local evidence narrative. It is optimized for explaining what the
ticket taught about how the repos or systems relate. It should include the
mental model, involved repos/surfaces, ownership boundary, request or data flow,
when to consult this note again, and links back to the ticket-local evidence. It
should omit step-by-step investigation history, rejected debugging paths, raw
command output, and PR/process details unless they directly explain a system
relationship.

`knowledge/private/repo-relationships-index.md` is cumulative and short. Each
entry should help Weiwei quickly remember what a past ticket taught and where to
find the detailed note. It is not a full duplicate of the detailed relationship
file.

`technical-notes` and `system-design-lessons` are public-safe by default. They
use `weiwei-notes` redaction and writing style.

## Idempotency And Re-Runs

The skill must be safe to run more than once for the same ticket. Re-runs happen
when new evidence, tests, acceptance notes, or repo relationship details are
added after an earlier completion pass.

Ticket-local generated files are authoritative snapshots and should be replaced
on re-run:

- `tickets/<TICKET-ID>/completion.md`
- `tickets/<TICKET-ID>/repo-relationships.md`

Knowledge detail files are also authoritative snapshots for the ticket and
should be replaced on re-run:

- `knowledge/private/repo-relationships/<TICKET-ID>.md`
- `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
- `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

Because public-safe filenames include a slug, the skill must treat
`<TICKET-ID>` as the stable identity. On re-run, it should find existing
technical note and system design lesson files with the same ticket ID prefix and
keep exactly one current file per artifact type. If the regenerated title changes
the slug, the stale same-ticket file should be removed or replaced so the
knowledge directory does not accumulate multiple public-safe files for the same
ticket.

When replacing a file, the skill should preserve only intentional user-owned
content if the file has a clearly marked manual section. The first version does
not require manual sections, so the default behavior is full regeneration from
the current ticket evidence.

The cumulative index must use upsert behavior, not append-only behavior. For
`knowledge/private/repo-relationships-index.md`, the skill must find the
existing section for the ticket and replace that section. It must not create
duplicate entries for the same ticket.

Index entries should use a stable heading key:

```markdown
## <Topic> - <TICKET-ID>
```

On re-run, the implementation should match by `<TICKET-ID>` even if `<Topic>`
changes, then rewrite the heading and body with the latest evidence. If no entry
for the ticket exists, append a new entry.

## Slug Generation

Public-safe artifact filenames use:

```text
<TICKET-ID>-<slug>.md
```

`<TICKET-ID>` is the stable private identity. `<slug>` is only a readable hint
for humans browsing the knowledge directory.

Generate `<slug>` from the final public-safe article title after redaction, not
from the raw ticket title, repo names, service names, branch names, PR titles, or
other private source material. This prevents sensitive internal terms from
leaking through filenames.

Slug rules:

- Lowercase.
- ASCII only.
- Replace spaces and punctuation with single hyphens.
- Remove characters outside `a-z`, `0-9`, and `-`.
- Collapse repeated hyphens.
- Trim leading and trailing hyphens.
- Limit to 60 characters.

If the redacted title produces an empty slug, use an artifact-specific fallback:

- `technical-note`
- `system-design-lesson`

Slug uniqueness is scoped by artifact directory. Different tickets may use the
same slug because the ticket ID prefix keeps filenames distinct. For the same
ticket, the idempotency rules apply: keep exactly one current file per artifact
type, even if the regenerated title changes the slug.

## Privacy And Redaction Rules

Private artifacts preserve real context:

- `tickets/<TICKET-ID>/completion.md`
- `tickets/<TICKET-ID>/repo-relationships.md`
- `knowledge/private/repo-relationships/<TICKET-ID>.md`
- `knowledge/private/repo-relationships-index.md`

Public-safe artifacts must be redacted:

- `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
- `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

Public-safe documents must not expose company names, customer names, internal
project names, real repo names, ticket IDs in the article body, PR links, Slack
links, people, file paths, URLs, domains, table names, queue names, service
names, environment names, internal constants, API routes, feature flags, exact
incident identifiers, or uniquely identifying timing and scale details.

Public-safe documents should preserve the transferable technical idea:

- Product goal.
- System role names such as "CMS", "API", "SSR page", "upstream system", or
  "downstream consumer".
- Technical tradeoffs.
- Data flow.
- Ownership boundaries.
- Failure modes.
- Observability and operational implications.
- Migration or rollback path when relevant.

## Pipeline

The skill runs in five phases.

### 1. Discover Context

Detect workspace mode by finding `ecosystem.md` and `tickets/`. Read
`ecosystem.md`, `conventions.md` if present, and the selected ticket files when
present:

- `context.md`
- `investigation.md`
- `implementation.md`
- `test.md`
- `pr.md`
- `timeline.md`
- `handoff.md`

If no workspace exists, the skill can operate in standalone draft mode only,
using the current conversation or user-provided files as source material.

### 2. Validate Completion

In strict mode, verify completion evidence before writing final artifacts. If
required evidence is missing, stop and report the missing checklist.

In draft mode, continue with available evidence but label every generated
artifact as partial and list known gaps.

### 3. Build Evidence Package

Extract:

- Facts.
- Hypotheses still unresolved.
- Decisions.
- Final outcome.
- Root cause or final decision.
- Owner repo/module.
- Request or data flow.
- Repos, services, surfaces, and modules involved.
- Files inspected and changed.
- Tests and acceptance checks.
- Risks and follow-ups.
- Links back to ticket evidence.

The skill must separate evidence-backed facts from hypotheses. It must not
invent repo relationships, implementation details, acceptance status, or system
design lessons to make the output feel complete.

### 4. Generate Artifacts

Generate private artifacts first:

1. `tickets/<TICKET-ID>/completion.md`
2. `tickets/<TICKET-ID>/repo-relationships.md`
3. `knowledge/private/repo-relationships/<TICKET-ID>.md`
4. Upsert `knowledge/private/repo-relationships-index.md`

Then generate public-safe artifacts:

1. `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`
2. `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`

The public-safe technical note uses `weiwei-notes` style: conclusion first,
root-cause oriented, concise, technical English terms preserved in Chinese, and
both Simplified Chinese and English versions unless the user explicitly asks
otherwise.

The system design lesson uses relevant dimensions from `system-design-coach`:

- Requirements framing.
- API and data model.
- Ownership boundaries.
- Architecture and scalability.
- Reliability, consistency, and failure modes.
- Observability and operations.
- Security or privacy when relevant.
- Tradeoffs and implications.

The skill should only include dimensions that the ticket actually supports.

### 5. Review Output

Before final response, run a review checklist:

- Strict or draft status is clearly labeled.
- Private files may contain real identifiers.
- Public-safe files are redacted.
- Ticket IDs and real repo/service names do not appear in public-safe article
  bodies.
- Evidence links point back to the ticket-local files where useful.
- Missing inputs or unresolved questions are visible.
- The cumulative repo relationship index is short and scannable.
- Re-running the same ticket replaced generated snapshots and did not duplicate
  the cumulative index entry.
- The final response lists files written and any gaps.

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

For `knowledge/private/repo-relationships/<TICKET-ID>.md`:

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

```markdown
# <Conclusion-Or-Core-Question>

## 简体中文

## English
```

### Public-Safe System Design Lesson

```markdown
# <Public-Safe Lesson Title>

## 简体中文

## English
```

## Documentation Updates

Update:

- `README.md`
- `README.zh-CN.md`
- `.claude-plugin/marketplace.json`
- `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`
- `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md`

The documentation should describe `complete-ticket` as the fifth skill in the
AI Engineering Workspace suite and clarify that it turns ticket closure into
private context plus public-safe reusable knowledge.

## Verification

Because this is a skill-only change, verification is documentation and safety
oriented:

- Run `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color`.
- Inspect the new `SKILL.md` manually for hidden directives, ambiguous gates,
  and mismatch with the intended behavior.
- Confirm README and plugin metadata consistently say the suite has five skills.
- Confirm the public-safe/private artifact distinction is explicit.

## Non-Goals

- Do not modify the existing ticket templates in the first implementation.
- Do not add scripts for automatic Markdown generation in the first version.
- Do not replace `ticket-workflow` Phase 3.
- Do not make `complete-ticket` perform code changes, tests, deploys, or PR
  creation.
- Do not turn system design lessons into interview drills. The skill borrows
  `system-design-coach` dimensions, but the output is knowledge extraction from
  real ticket work.
