---
name: handoff
description: >
  Persist and restore working context across sessions on a single ticket. Use when
  starting work and a HANDOFF.md exists (resume), or when ending/pausing work to save
  findings before the session closes (save). Preserves four things: verified code facts,
  decisions/rationale, execution progress, and dead-ends already ruled out. Triggers:
  "resume", "pick up where I left off", "save handoff", "wrap up this session",
  "hand off", or when the user references prior findings not in the current context.
---

# Handoff: cross-session context persistence

## What this solves

A new session starts with zero memory of prior work on the same ticket. This skill
serializes the working state into a single `HANDOFF.md` at the end of a session and
restores it at the start of the next one, so no findings, decisions, or dead-ends are lost.

**Why this saves context:** the token savings come not from *writing* the document but
from *using it to replace the old session's history*. The next session starts from a small
file instead of dragging along tens of thousands of tokens of prior conversation. This one
fact drives every design choice below — the file must stay far smaller than the history it
replaces, or the skill defeats its own purpose.

Scope: **one ticket, one person, sequential sessions.** Not for multi-model semantic
handoff or external tools. Keep it simple.

## The core principle

The four kinds of saved information decay at different rates. Treat them differently:

| Section        | Decay      | Rule on resume                                  |
|----------------|------------|-------------------------------------------------|
| Code Facts     | Fast       | **Verify before trusting.** Code may have moved.|
| Decisions      | Slow       | Trust unless the requirement changed.           |
| Progress       | Per-session| Update every save; this is the cursor.          |
| Dead-ends      | Append-only| Never delete; this is the "don't retry" list.   |

A handoff file that only compresses tokens but records unverifiable claims is worse than
no file — it launders uncertainty into false confidence. Every code fact MUST carry an
anchor (path + symbol) so it can be re-checked, not just re-read.

## Two commands

### `resume` — start of session

Run when the user asks to continue, or whenever a `HANDOFF.md` exists at session start.

1. Read `HANDOFF.md`.
2. **Verify the Code Facts section first.** For each fact with an anchor, confirm the
   file and symbol still exist and the described relationship still holds. Use grep/read,
   not memory. Mark each fact as one of:
   - ✅ confirmed
   - ⚠️ changed (note what changed)
   - ❌ gone (file/symbol no longer exists)
3. Report a short recovery summary to the user: where things stand, what's next, and
   flag any ⚠️/❌ facts that need attention before proceeding.
4. Do NOT silently act on stale facts. If a next-step depends on a ❌ fact, surface it.
5. **Follow references, don't assume.** Where the file points to a commit/diff/PR/ADR/
   issue rather than copying it, open that artifact if the next step needs its content.
6. **Load suggested skills.** If the Next-session setup section names skills/tools,
   surface them so they can be loaded before work resumes.

### `save` — end of session

Run when the user wraps up, or proactively when the session is clearly ending.

1. Read the existing `HANDOFF.md` (if any) so you append rather than overwrite history.
2. Update each section per its rule (see table above).
3. For every code fact, include a concrete anchor: `path/to/file.py :: function_name`
   and a one-line description of the relationship. No anchor → don't record it as a fact,
   record it under Dead-ends or Decisions as inference.
4. **Separate fact from inference.** Anything you didn't directly verify goes in as
   "(inferred)" — never dressed up as confirmed.
5. Write the Progress section as: done / in-progress / next. Keep "next" actionable
   enough that a cold session can pick it up.
6. **Reference existing artifacts — don't re-transcribe them.** If the content already
   lives in a commit, diff, PR, PRD, ADR, issue, or plan file, record its path/ID and a
   one-line pointer, not a copy. The handoff file captures what's *only in your head*
   (decisions, dead-ends, current cursor), not what's already durable elsewhere.
7. **Suggest skills for next session.** If the "next" step clearly calls for specific
   skills or tools, name them in the Next-session setup section so a cold start knows
   what to load.
8. **Stay within budget.** Target ~1500–2500 tokens for a normal ticket (about one
   screen when read back). This is a persistence file, not a log. If a section outgrows
   its share, replace detail with a reference to the file / commit / PR / log that already
   holds it. Budget by section, because they differ in nature:
   - **Decisions & Dead-ends** get the space — they exist nowhere else.
   - **Code Facts** stay terse: anchor + one line each, no prose.
   - **Progress** is a cursor, not a history — keep only the live frontier; prune
     superseded items on every save.
   If the file can't fit the budget without losing something that lives nowhere else,
   that's the signal to split the ticket, not to grow the file.

## File location

`HANDOFF.md` lives in a dedicated handoff dir, not scattered per-topic. Default:
`.handoff/HANDOFF.md` at repo root (one file per ticket-branch). If multiple tickets are
active, name by ticket: `.handoff/<TICKET-ID>.md`.

## Template

See `TEMPLATE.md` in this skill directory. On first `save` for a ticket, copy it and fill in.

## What NOT to do

- Don't overwrite Dead-ends or old Decisions — append.
- Don't record a code fact without an anchor.
- Don't present inferred/unverified claims as confirmed.
- Don't re-transcribe content that already exists in a commit/diff/PR/PRD/ADR/issue —
  link to it instead.
- Don't let the file grow unbounded — on `save`, prune Progress items that are fully
  superseded, but keep Decisions and Dead-ends.
