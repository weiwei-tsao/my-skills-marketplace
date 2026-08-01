# Complete Ticket Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `complete-ticket` skill that turns completed ticket work into private completion context, private repo relationship memory, public-safe technical notes, and public-safe system design lessons.

**Architecture:** Implement this as a Markdown-only skill inside the existing `ai-engineering-workspace` plugin. The new skill reads existing ticket workspace files, enforces strict or draft completion gates, writes deterministic artifacts with idempotent re-run behavior, and borrows style/rubric rules from `weiwei-notes` and `system-design-coach` by reading their local `SKILL.md` and rubric files at runtime.

**Tech Stack:** Claude/Codex skill Markdown, existing marketplace JSON metadata, existing Python static auditor `vetting/audit_skill.py`.

## Global Constraints

- Create the skill at `plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md`.
- Treat `ai-engineering-workspace` as a five-skill suite after this change.
- Strict mode is default; draft mode only runs when explicitly requested.
- Private artifacts preserve real ticket/repo/service context.
- Public-safe technical notes and system design lessons must use `weiwei-notes` redaction rules.
- System design lessons must use relevant `system-design-coach` dimensions without becoming interview drills.
- Re-runs must be idempotent: generated snapshots are replaced, cumulative index entries are upserted by ticket ID, and stale same-ticket slug files are removed or replaced.
- Final responses from the skill must list files written, files removed or replaced, and gaps.
- First implementation does not add scripts or modify existing ticket templates.

---

## File Structure

- Create `plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md`.
  This is the only new skill payload. It contains the runtime workflow, output contracts, privacy rules, idempotency rules, and verification checklist.
- Modify `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md`.
  Update the suite table and routing description so `complete-ticket` is discoverable.
- Modify `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`.
  Update description from four skills to five skills and bump version from `0.2.0` to `0.3.0`.
- Modify `.claude-plugin/marketplace.json`.
  Update the `ai-engineering-workspace` catalog entry version and description.
- Modify `README.md` and `README.zh-CN.md`.
  Update the plugin table and any "four skills" wording for the suite.
- No changes to `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/`.
  The spec explicitly defers template changes.

---

### Task 1: Add The `complete-ticket` Skill

**Files:**
- Create: `plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md`

**Interfaces:**
- Consumes: existing ticket workspace files `ecosystem.md`, `conventions.md`, and `tickets/<TICKET-ID>/{context.md,investigation.md,implementation.md,test.md,pr.md,timeline.md,handoff.md}`.
- Consumes: writing rules from `../../../weiwei-notes/skills/weiwei-notes/SKILL.md` when available.
- Consumes: system design dimensions from `../../../system-design-coach/references/interview-rubric.md` and `../../../system-design-coach/references/topic-map.md` when available.
- Produces: runtime instructions for writing `completion.md`, `repo-relationships.md`, `knowledge/private/repo-relationships/<TICKET-ID>.md`, `knowledge/private/repo-relationships-index.md`, `knowledge/public-safe/technical-notes/<TICKET-ID>-<slug>.md`, and `knowledge/public-safe/system-design-lessons/<TICKET-ID>-<slug>.md`.

- [ ] **Step 1: Create the skill directory**

Run:

```bash
mkdir -p plugins/ai-engineering-workspace/skills/complete-ticket
```

Expected: command exits with status `0`.

- [ ] **Step 2: Create `SKILL.md` with the full skill instructions**

Create `plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md` with exactly this content:

```markdown
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
```

Expected: file exists and starts with frontmatter containing `name: complete-ticket`.

- [ ] **Step 3: Verify the new skill can be discovered by the installer pattern**

Run:

```bash
find plugins/ai-engineering-workspace/skills/complete-ticket -maxdepth 1 -name SKILL.md -print
```

Expected output:

```text
plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
```

- [ ] **Step 4: Commit Task 1**

Run:

```bash
git add plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
git commit -m "feat: add complete-ticket skill"
```

Expected: commit succeeds with one new file.

---

### Task 2: Update Suite And Marketplace Documentation

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md`
- Modify: `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `README.md`
- Modify: `README.zh-CN.md`

**Interfaces:**
- Consumes: `complete-ticket` skill name and purpose from Task 1.
- Produces: consistent user-facing documentation that says `ai-engineering-workspace` contains five standalone skills.

- [ ] **Step 1: Update `ai-engineering-workspace/SKILL.md` frontmatter description**

In `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md`, replace:

```yaml
description: Scaffold and navigate a structured ticket workspace for AI-assisted engineering on any team. Use when the user wants to set up a ticket workspace, asks how the ai-engineering-workspace suite works, or you need to pick between its skills (ticket-workflow, structured-bug-fix, handoff).
```

with:

```yaml
description: Scaffold and navigate a structured ticket workspace for AI-assisted engineering on any team. Use when the user wants to set up a ticket workspace, asks how the ai-engineering-workspace suite works, or you need to pick between its skills (ticket-workflow, structured-bug-fix, handoff, complete-ticket).
```

Expected: the frontmatter description mentions `complete-ticket`.

- [ ] **Step 2: Update the suite table in `ai-engineering-workspace/SKILL.md`**

Replace this table:

```markdown
| Skill | Use when | Standalone (no workspace) |
|---|---|---|
| `ticket-workflow` | Working a ticket end to end: investigate → implement → finish | Applies the phase discipline without ticket files |
| `structured-bug-fix` | Diagnosing a bug, especially cross-repo | Works in any repo; presents diagnosis before editing |
| `handoff` | Saving state before ending a session, or resuming one | Uses `.handoff/HANDOFF.md` at repo root |
| this skill | Scaffolding the workspace, or routing between the above | — |
```

with:

```markdown
| Skill | Use when | Standalone (no workspace) |
|---|---|---|
| `ticket-workflow` | Working a ticket end to end: investigate -> implement -> finish | Applies the phase discipline without ticket files |
| `structured-bug-fix` | Diagnosing a bug, especially cross-repo | Works in any repo; presents diagnosis before editing |
| `handoff` | Saving state before ending a session, or resuming one | Uses `.handoff/HANDOFF.md` at repo root |
| `complete-ticket` | Turning a finished or intentionally drafted ticket into private context plus public-safe reusable knowledge | Draft mode only without workspace files |
| this skill | Scaffolding the workspace, or routing between the above | — |
```

Expected: table contains a `complete-ticket` row.

- [ ] **Step 3: Update workspace detection paragraph in `ai-engineering-workspace/SKILL.md`**

After this paragraph:

```markdown
When none exists, they degrade to standalone mode — never block on missing
workspace files.
```

add:

```markdown
`complete-ticket` is stricter than the other suite skills: final completion
requires ticket evidence, while standalone mode is draft-only.
```

Expected: the route skill explains why `complete-ticket` behaves differently in standalone mode.

- [ ] **Step 4: Update plugin manifest**

In `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`, replace the entire file with:

```json
{
  "name": "ai-engineering-workspace",
  "version": "0.3.0",
  "description": "Generic AI-engineering ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, cross-session handoff, and ticket completion knowledge extraction. Each skill usable standalone where applicable. Vetted 2026-07-18.",
  "author": { "name": "weiwei-tsao" },
  "license": "MIT"
}
```

Expected: version is `0.3.0` and description mentions ticket completion knowledge extraction.

- [ ] **Step 5: Update marketplace entry**

In `.claude-plugin/marketplace.json`, update only the `ai-engineering-workspace` object to:

```json
{
  "name": "ai-engineering-workspace",
  "source": "./plugins/ai-engineering-workspace",
  "version": "0.3.0",
  "description": "Generic AI-engineering ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, cross-session handoff, and ticket completion knowledge extraction.",
  "author": { "name": "weiwei-tsao" },
  "category": "workflow",
  "keywords": ["ticket", "investigation", "handoff", "bugfix", "workflow", "multi-repo", "knowledge"]
}
```

Expected: JSON remains valid and only the `ai-engineering-workspace` entry changes.

- [ ] **Step 6: Update `README.md` plugin table**

In `README.md`, replace the `ai-engineering-workspace` table row:

```markdown
| `ai-engineering-workspace` | workflow | Ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, and cross-session handoff — four skills, each usable standalone. |
```

with:

```markdown
| `ai-engineering-workspace` | workflow | Ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, cross-session handoff, and ticket completion knowledge extraction — five skills, each usable standalone where applicable. |
```

Expected: README says five skills.

- [ ] **Step 7: Update `README.zh-CN.md` plugin table**

In `README.zh-CN.md`, replace the `ai-engineering-workspace` table row:

```markdown
| `ai-engineering-workspace` | workflow | Ticket 全家桶：工作区脚手架、阶段门控 ticket 流程、结构化 bug 修复、跨会话 handoff —— 四个 skill，均可单独使用。 |
```

with:

```markdown
| `ai-engineering-workspace` | workflow | Ticket 全家桶：工作区脚手架、阶段门控 ticket 流程、结构化 bug 修复、跨会话 handoff、ticket completion 知识沉淀 —— 五个 skill，可按场景单独使用。 |
```

Expected: Chinese README says five skills and mentions ticket completion knowledge extraction.

- [ ] **Step 8: Search for stale four-skill wording**

Run:

```bash
rg -n "four skills|四个 skill|four-skill|四个" README.md README.zh-CN.md plugins/ai-engineering-workspace .claude-plugin/marketplace.json
```

Expected: no output.

- [ ] **Step 9: Commit Task 2**

Run:

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md plugins/ai-engineering-workspace/.claude-plugin/plugin.json .claude-plugin/marketplace.json README.md README.zh-CN.md
git commit -m "docs: document complete-ticket skill"
```

Expected: commit succeeds with documentation and metadata changes only.

---

### Task 3: Verify Skill Safety And Installability

**Files:**
- Test: `plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md`
- Test: `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`
- Test: `.claude-plugin/marketplace.json`
- Test: `README.md`
- Test: `README.zh-CN.md`

**Interfaces:**
- Consumes: new skill and docs from Tasks 1-2.
- Produces: verified static audit, valid JSON, installer visibility, and a final clean git state.

- [ ] **Step 1: Run the static skill auditor**

Run:

```bash
python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color
```

Expected: exit code `0` or no CRITICAL findings. If HIGH findings appear, inspect them and only continue if they are expected from existing audited content.

- [ ] **Step 2: Validate JSON metadata**

Run:

```bash
python3 -m json.tool plugins/ai-engineering-workspace/.claude-plugin/plugin.json >/tmp/ai-engineering-workspace-plugin.json
python3 -m json.tool .claude-plugin/marketplace.json >/tmp/my-skills-marketplace.json
```

Expected: both commands exit with status `0`.

- [ ] **Step 3: Verify Codex installer sees `complete-ticket`**

Run:

```bash
./install-codex-skills.sh
```

Expected: dry run output includes a discovered source path ending in:

```text
plugins/ai-engineering-workspace/skills/complete-ticket
```

and does not report a malformed `SKILL.md` for `complete-ticket`.

- [ ] **Step 4: Verify docs and metadata consistently mention complete-ticket**

Run:

```bash
rg -n "complete-ticket|ticket completion|知识沉淀|five skills|五个 skill" README.md README.zh-CN.md plugins/ai-engineering-workspace .claude-plugin/marketplace.json
```

Expected: output includes:

```text
plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md
plugins/ai-engineering-workspace/.claude-plugin/plugin.json
.claude-plugin/marketplace.json
README.md
README.zh-CN.md
```

- [ ] **Step 5: Verify no implementation scope creep**

Run:

```bash
git diff --name-only HEAD~2..HEAD
```

Expected after Tasks 1-2 commits: changed files are limited to:

```text
.claude-plugin/marketplace.json
README.md
README.zh-CN.md
plugins/ai-engineering-workspace/.claude-plugin/plugin.json
plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md
plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
```

- [ ] **Step 6: Commit verification notes if any files changed**

If verification required fixing files, run:

```bash
git add .claude-plugin/marketplace.json README.md README.zh-CN.md plugins/ai-engineering-workspace/.claude-plugin/plugin.json plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md plugins/ai-engineering-workspace/skills/complete-ticket/SKILL.md
git commit -m "chore: verify complete-ticket skill"
```

Expected: commit only when verification changed files. If verification changed no files, skip this step and do not create an empty commit.

- [ ] **Step 7: Final status check**

Run:

```bash
git status --short
```

Expected: no output.

---

## Self-Review

- Spec coverage: Task 1 implements the new skill, strict/draft modes, artifact layout, privacy rules, idempotency, slug generation, relationship artifact boundaries, generation order, output contracts, and final response rules. Task 2 covers suite and marketplace documentation updates. Task 3 covers audit, JSON validity, installer discovery, docs consistency, and scope control.
- Placeholder scan: this plan contains no unresolved placeholder markers. Template tokens such as `<TICKET-ID>` and `<slug>` are intentional runtime placeholders defined by the spec.
- Type consistency: this is a Markdown skill implementation. Path names and artifact names are consistent across tasks.
