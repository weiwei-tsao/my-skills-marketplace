# AI Engineering Workspace Flow Redesign

## Summary

Rework `plugins/ai-engineering-workspace` based on hands-on usage feedback.
Four pain points, one design each:

1. **Process feels heavy/chatty** — every ticket eagerly creates 7 template
   files even for small tickets, most of which sit empty.
2. **Skill boundaries/triggers are unclear** — `ticket-workflow` bundles all
   phases into one auto-triggered skill; without a hard boundary, the agent
   sometimes reaches Phase 2 (Implement) before the ticket's ask has actually
   been understood and confirmed.
3. **Commit messages are verbose/duplicated** — `ticket-workflow` restates
   commit-message rules that the marketplace's own `git-commit` skill already
   owns.
4. **Ticket understanding isn't a formal, confirmed step** — the workflow
   should read and confirm the raw ticket (including comments) *before*
   starting code investigation, not fold that into the investigation phase.

The core mechanism change is replacing `ticket-workflow`'s single
auto-triggered skill (which relies on the agent voluntarily honoring
"don't skip ahead" prose) with four separate slash commands, one per phase,
with model auto-invocation disabled. The agent cannot see or act on a later
phase's instructions until the user explicitly runs that phase's command —
the gate becomes structural, not a promise.

## Motivation: why prose gating wasn't enough

An earlier iteration of this design kept `ticket-workflow` as a single skill
and added a stronger "wait for confirmation" instruction inside Phase 1.
Investigating a predecessor workspace the user had used previously
(`~/Documents/Repositories/skills/ai_engineering_workspace`) showed why that
predecessor "felt" better-controlled: it didn't rely on one skill governing
every phase. It shipped five standalone prompt files
(`01-start-investigation.md` … `05-update-handoff.md`) that the user
manually selected and pasted. The agent literally never had "implement"
instructions in context until that specific prompt was handed to it.

Claude Code plugins have a first-class equivalent: `commands/*.md`, invoked
as `/ai-engineering-workspace:<name>`. Setting
`disable-model-invocation: true` on each command means the agent cannot
trigger the next phase itself via the SlashCommand tool — only the user
typing the command can. This reproduces the predecessor's hard isolation
inside Claude Code's plugin model, without going back to manual prompt-file
pasting.

`structured-bug-fix` already has a hard stop between diagnosis and
implementation (Phase 3 → 4), so it does not get the command treatment —
it only gains one added confirmation paragraph in Phase 1.

## Architecture overview

```text
plugins/ai-engineering-workspace/
  commands/                         ← NEW
    ticket-understand.md
    ticket-investigate.md
    ticket-implement.md
    ticket-finish.md
  skills/
    ai-engineering-workspace/
      SKILL.md                      ← scaffold interview gains 2 fields
      templates/
        conventions.md              ← +Ticket source, +Verification commands
        scripts/new-ticket.sh       ← only creates context.md
        tickets/
          context.md                ← unchanged
          investigation.md          ← unchanged (created lazily now)
          implementation.md         ← unchanged (created lazily now)
          test.md                   ← unchanged (created lazily now)
          pr.md                     ← Commit message section removed
          timeline.md                ← unchanged (created lazily now)
          handoff.md                 ← unchanged (already created lazily by `handoff` skill)
    ticket-workflow/
      SKILL.md                      ← shrinks to a phase/command router
    structured-bug-fix/
      SKILL.md                      ← +1 confirmation paragraph in Phase 1
    handoff/                        ← unchanged
    complete-ticket/                ← unchanged
  .claude-plugin/plugin.json        ← version bump
```

`handoff` and `complete-ticket` are out of scope — the reported pain points
don't touch them.

## `commands/` — the four hard-gated phases

All four share this frontmatter shape:

```yaml
---
description: <one line>
argument-hint: <TICKET-ID>
disable-model-invocation: true
---
```

`disable-model-invocation: true` is the load-bearing line: it's what stops
the agent from chaining straight into the next phase on its own.

### `commands/ticket-understand.md` — Phase 1 of 4

```text
You are starting ticket $ARGUMENTS. This is Phase 1 of 4: Understand.

1. Detect workspace mode: does a directory with `ecosystem.md` and
   `tickets/` exist (current dir or a notes repo the user points to)?
   - Workspace mode: read `ecosystem.md`, `conventions.md`, and
     `tickets/$ARGUMENTS/context.md` if present. If
     `tickets/$ARGUMENTS/` doesn't exist yet, run
     `./scripts/new-ticket.sh $ARGUMENTS "<title>"` first (ask for a short
     title if the user hasn't given one).
   - Standalone mode: skip file reads; work from what the user has said in
     this conversation.
2. Fetch the ticket's raw content (title, description, all comments):
   - Workspace mode: use the command recorded under "Ticket source" in
     `conventions.md`. If no command is recorded, ask the user for it once
     and suggest saving it to `conventions.md` for next time.
   - Standalone mode: use what the user already provided in conversation;
     ask only for what's missing.
3. Record the raw ask and comments into `context.md` (workspace mode).
4. Output a restatement covering: goal, user-visible problem, expected vs.
   current behavior, explicit in/out of scope, open questions.
5. STOP. Do not read or search any code. Do not create or write
   `investigation.md`. Wait for the user to confirm the restatement.

Once confirmed, tell the user to run `/ticket-investigate $ARGUMENTS`.
```

### `commands/ticket-investigate.md` — Phase 2 of 4

```text
You are investigating ticket $ARGUMENTS. This is Phase 2 of 4: Investigate
(read-only).

Precondition: ticket understanding was already confirmed via
`/ticket-understand`. If `context.md` looks empty/unconfirmed and nothing in
this conversation confirms it, stop and ask the user to run
`/ticket-understand $ARGUMENTS` first.

1. Read `ecosystem.md`'s flow map if present; otherwise trace from the
   entry point by reading the actual code.
2. Identify the most likely owner repo/module.
3. Separate facts (evidence-backed), hypotheses (unconfirmed), decisions.
4. Record findings, evidence, open questions, and next steps into
   `investigation.md` (create it from the template if it doesn't exist yet).

Do not edit any code in this phase.

Gate: summarize confirmed facts, likely root cause, owner, and the next
safest action. Wait for confirmation before implementing.

Once confirmed, tell the user to run `/ticket-implement $ARGUMENTS`.
```

### `commands/ticket-implement.md` — Phase 3 of 4

```text
You are implementing ticket $ARGUMENTS. This is Phase 3 of 4: Implement
(minimal).

Precondition: investigation confirmed root cause and owner. If
`investigation.md` is missing/empty, stop and ask the user to run
`/ticket-investigate $ARGUMENTS` first.

Before editing:
1. Confirm the owner repo/module.
2. Check current directory, branch, `git status`, and current diff.
3. Summarize the intended minimal change.

Then make the smallest safe change.

Rules:
- No unrelated refactors or formatting.
- Don't touch multiple repos/modules unless the investigation justifies it.
- Preserve existing behavior unless the ticket requires changing it.
- Run the "Verification commands" from `conventions.md` (typecheck/lint/
  test/build as configured); report results honestly, including failures.
- Record what changed and how it was tested into `implementation.md` and
  `test.md` (create them from the template if they don't exist yet).

Once checks pass, tell the user to run `/ticket-finish $ARGUMENTS`.
```

### `commands/ticket-finish.md` — Phase 4 of 4

```text
You are finishing ticket $ARGUMENTS. This is Phase 4 of 4: Finish.

1. Generate PR title, PR description, test notes, and a short status update
   (follow `conventions.md`'s style, or repo precedent if unset). Save into
   `pr.md` (create it from the template if it doesn't exist yet).
2. Commit:
   - If the `git-commit` skill is installed, invoke it to run checks, draft
     the commit message, and commit. Do not restate commit-message rules
     here.
   - Otherwise, fall back to `conventions.md`'s "Commit / PR title style"
     and commit directly.
3. Save a handoff — invoke the `handoff` skill's save flow. A ticket isn't
   finished until the next session could continue it cold.
```

## `ticket-workflow/SKILL.md` — becomes a router

Replaces the current three-phase inline instructions with:

- A table mapping phase → command → purpose (the four rows above).
- A note that commands are the way to get a hard phase boundary; if the user
  talks about a ticket conversationally instead of invoking a command, the
  skill still walks the same 4 phases and gates in the conversation, but
  recommends switching to the commands so understanding gets confirmed
  before any code gets read.
- Workspace-mode / standalone-mode file-location notes carried over
  unchanged from the current SKILL.md.
- The existing "Golden rules" section carried over unchanged.

The router doc's auto-trigger description in frontmatter is unchanged — it
still surfaces via description-matching for discovery; the commands are
what actually gates execution.

## `structured-bug-fix/SKILL.md` — one added paragraph

At the end of Phase 1 ("Gather context"), add:

```text
Before tracing the flow, output a one-line restatement: "My understanding
of the bug is: ...". Wait for the user to confirm before starting Phase 2.
```

No other changes to this skill — its existing Phase 3 → 4 hard stop
(diagnosis before implementation) already does the job the new commands do
for `ticket-workflow`.

## Lazy ticket-file creation

`templates/scripts/new-ticket.sh` changes from copying all of
`tickets/_template/*.md` to copying only `context.md`:

```bash
mkdir -p "$TICKET_DIR"
cp "$TEMPLATE_DIR/context.md" "$TICKET_DIR/"
sed -i.bak "s/<TICKET-ID>/$TICKET_ID/g" "$TICKET_DIR/context.md"
rm -f "$TICKET_DIR/context.md.bak"
```

Closing message updates to point at `/ticket-understand` instead of a raw
"open context.md" instruction.

The other five per-ticket files (`investigation.md`, `implementation.md`,
`test.md`, `pr.md`, `timeline.md`) are created lazily by the command that
first needs to write into them (see command bodies above), copying from
`templates/tickets/<name>.md` and substituting `<TICKET-ID>` the same way
`new-ticket.sh` does today. `handoff.md` is unaffected — the `handoff`
skill already creates it lazily at save time.

A 2-ticket workspace goes from 14 mostly-empty files to as few as 2
(`context.md` each) plus whatever each ticket actually reached in its
lifecycle.

## `conventions.md` — two new fields

Added near the existing "Ticket IDs" and "Commit / PR title style"
sections:

```markdown
## Ticket source

<!-- Command or tool used to fetch a ticket's raw content and comments,
     e.g. `gh issue view <ID> --comments`, or a Jira/Linear MCP tool name. -->

Command: <fill in>

## Verification commands

<!-- Typecheck / lint / test / build commands to run before considering an
     implementation done. Referenced by /ticket-implement and test.md — set
     once here instead of re-deriving per ticket. -->

- Typecheck: `<command>`
- Lint: `<command>`
- Test: `<command>`
- Build: `<command>`
```

## Scaffold interview update (`ai-engineering-workspace/SKILL.md`)

The existing 6-question interview gets these two folded in (not new
top-level questions — extending existing related items):

- Question 3 ("Ticket IDs") gains a follow-up: "How do you fetch a ticket's
  raw content and comments? (command or MCP tool)" → **Ticket source**.
- Question 5 ("Conventions") gains a follow-up: "What are your typecheck/
  lint/test/build commands?" → **Verification commands**.

## `pr.md` template — drop the duplicated commit-message section

Remove the "Commit message" heading and its code block (duplicated
`conventions.md`'s "Commit / PR title style" and, now, the `git-commit`
skill's job). Replace with a one-line pointer:

```markdown
## Commit

Handled by the `git-commit` skill when `/ticket-finish` runs (or
`conventions.md`'s "Commit / PR title style" if that skill isn't installed).
```

## File-change summary

| File | Change |
|---|---|
| `commands/ticket-understand.md` | new |
| `commands/ticket-investigate.md` | new |
| `commands/ticket-implement.md` | new |
| `commands/ticket-finish.md` | new |
| `skills/ticket-workflow/SKILL.md` | rewritten as router |
| `skills/structured-bug-fix/SKILL.md` | +1 paragraph in Phase 1 |
| `skills/ai-engineering-workspace/SKILL.md` | scaffold interview: 2 fields folded into existing questions |
| `skills/ai-engineering-workspace/templates/conventions.md` | +Ticket source, +Verification commands |
| `skills/ai-engineering-workspace/templates/scripts/new-ticket.sh` | only creates `context.md` |
| `skills/ai-engineering-workspace/templates/tickets/pr.md` | Commit message section → pointer |
| `.claude-plugin/plugin.json` | version bump (0.4.0 → 0.5.0) |
| `CLAUDE.md` | no change expected (plugin layout doc doesn't need to enumerate `commands/`; it's a standard plugin directory Claude Code already recognizes) |

## Testing / verification

- `claude plugin validate .` after adding `commands/` and editing
  `plugin.json`.
- `python3 vetting/audit_skill.py plugins/ai-engineering-workspace` — no new
  script files are added (commands are `.md`, not executable scripts), so
  this is a sanity check, not expected to surface new findings.
- Manual dry run: scaffold a throwaway workspace in a scratch dir, run
  `/ticket-understand`, `/ticket-investigate`, `/ticket-implement`,
  `/ticket-finish` in sequence against a fake ticket, and confirm each
  command stops where it's supposed to and the lazy files appear only when
  expected.
- Confirm `disable-model-invocation: true` actually prevents the agent from
  self-chaining commands (the mechanism the whole redesign depends on) —
  this is the one behavior worth explicitly re-checking after
  implementation, since it's asserted here from Claude Code's documented
  command frontmatter behavior rather than from a passing test in this repo.

## Non-goals

- Not touching `handoff` or `complete-ticket` — no reported pain points
  there.
- Not converting `structured-bug-fix` into commands — its existing Phase
  3→4 stop already provides the hard gate that mattered.
- Not building new vetting tooling for `commands/*.md` — the existing audit
  command's script-extension rules don't apply to them (they're prompt
  text, not executable scripts), same reasoning already applied to
  `hooks.json` in `CLAUDE.md`.
- Not adding commands for `handoff` save/resume — that skill already
  triggers reliably off phrases like "pick up where I left off," and wasn't
  named as a pain point.
