# AI Engineering Workspace Flow Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rework `plugins/ai-engineering-workspace` so `ticket-workflow`'s phase boundaries are structural (via slash commands + a persisted `Status:` field) instead of relying on the agent voluntarily honoring prose, per `docs/superpowers/specs/2026-08-08-ai-engineering-workspace-flow-redesign-design.md`.

**Architecture:** Four new `commands/*.md` files (one per phase, `disable-model-invocation: true`) replace `ticket-workflow`'s inline three-phase instructions; `ticket-workflow/SKILL.md` shrinks to a router. A `Status: draft`/`confirmed` line in `context.md`/`investigation.md` gives each command a literal string to check instead of judging whether prior content "looks" confirmed. `new-ticket.sh` creates only `context.md` up front; the other five per-ticket files are created lazily by whichever command first writes to them. `conventions.md` gains two fields (`Ticket source`, `Verification commands`) so per-ticket work stops re-deriving them. `pr.md` stops duplicating commit-message rules that the marketplace's `git-commit` skill already owns. `structured-bug-fix` gets one added confirmation paragraph (no command split — it already hard-stops before implementation).

**Tech Stack:** Markdown (skills, commands, templates), bash (`new-ticket.sh`), JSON (`plugin.json`, `marketplace.json`). No new dependencies.

## Global Constraints

- All four new commands must set `disable-model-invocation: true` in frontmatter — this is what makes the phase gate structural on the command path (the mechanism the whole redesign depends on).
- The `Status:` field takes exactly two values, `draft` and `confirmed` — no other values, no state machine.
- `conventions.md`'s "Verification commands" entries must support `N/A`; `/ticket-implement` must skip `N/A`/unset entries rather than asking the agent to invent a command.
- `/ticket-finish` must never run `git commit` without showing the user the exact message and getting explicit confirmation first, and must never run `git push` under any circumstance.
- `new-ticket.sh` creates only `context.md` for a new ticket; the other 5 per-ticket template files (`investigation.md`, `implementation.md`, `test.md`, `pr.md`, `timeline.md`) are created lazily by whichever command first needs to write into them.
- `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color` must be re-run after all files are added/changed and must report no new CRITICAL finding.
- `plugins/ai-engineering-workspace/.claude-plugin/plugin.json` version bumps `0.4.0` → `0.5.0`; `.claude-plugin/marketplace.json`'s mirrored `ai-engineering-workspace` entry bumps the same way (established convention in this repo — the prior `0.3.0` → `0.4.0` bump touched both files together).
- `claude plugin validate .` must pass after `commands/` is added.

---

### Task 1: `Status:` field in `context.md` and `investigation.md` templates

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/context.md`
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/investigation.md`

**Interfaces:**
- Produces: both templates now start with a literal `Status: draft` line immediately after the H1 title. Every later task that references "the `Status:` line" (Tasks 5–8) depends on this exact string and position.

- [ ] **Step 1: Add `Status: draft` to `context.md`**

In `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/context.md`, change:

```markdown
# <TICKET-ID> Context

## Goal
```

to:

```markdown
# <TICKET-ID> Context

Status: draft

## Goal
```

- [ ] **Step 2: Add `Status: draft` to `investigation.md`**

In `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/investigation.md`, change:

```markdown
# <TICKET-ID> Investigation

## Reproduction steps
```

to:

```markdown
# <TICKET-ID> Investigation

Status: draft

## Reproduction steps
```

- [ ] **Step 3: Verify both edits**

Run:
```bash
grep -n "^Status: draft$" plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/context.md plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/investigation.md
```
Expected: one match per file, each on line 3.

- [ ] **Step 4: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/context.md plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/investigation.md
git commit -m "feat(ai-engineering-workspace): add Status field to context/investigation templates"
```

---

### Task 2: `conventions.md` — add Ticket source and Verification commands fields

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/conventions.md`

**Interfaces:**
- Produces: a `## Ticket source` section (with a `Command: <fill in>` line) and a `## Verification commands` section (four `N/A`-aware bullet lines: Typecheck/Lint/Test/Build). Task 6 (`ticket-understand.md`) references "Ticket source" by this exact heading; Task 8 (`ticket-implement.md`) references "Verification commands" by this exact heading.

- [ ] **Step 1: Insert "Ticket source" after "Ticket IDs"**

In `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/conventions.md`, change:

```markdown
## Ticket IDs

<!-- e.g. ABC-123. Used in branches, commits, PR titles. -->

Format: `<PREFIX>-<number>`

## Branch naming
```

to:

```markdown
## Ticket IDs

<!-- e.g. ABC-123. Used in branches, commits, PR titles. -->

Format: `<PREFIX>-<number>`

## Ticket source

<!-- Command or tool used to fetch a ticket's raw content and comments,
     e.g. `gh issue view <ID> --comments`, or a Jira/Linear MCP tool name.
     Used by /ticket-understand so it doesn't have to ask every time. -->

Command: <fill in>

## Branch naming
```

- [ ] **Step 2: Insert "Verification commands" after "Commit / PR title style"**

In the same file, change:

```markdown
## Commit / PR title style

```text
fix(<TICKET-ID>): short description
```

Keep the description under ~10 words when possible.

## PR description style
```

to:

```markdown
## Commit / PR title style

```text
fix(<TICKET-ID>): short description
```

Keep the description under ~10 words when possible.

## Verification commands

<!-- Typecheck / lint / test / build commands to run before considering an
     implementation done. Referenced by /ticket-implement — set once here
     instead of re-deriving per ticket. Mark any that don't apply to this
     project as N/A rather than leaving them unset. -->

- Typecheck: `<command or N/A>`
- Lint: `<command or N/A>`
- Test: `<command or N/A>`
- Build: `<command or N/A>`

## PR description style
```

- [ ] **Step 3: Verify both sections exist**

Run:
```bash
grep -n "^## Ticket source$\|^## Verification commands$" plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/conventions.md
```
Expected: two matches, `## Ticket source` before `## Verification commands`.

- [ ] **Step 4: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/conventions.md
git commit -m "feat(ai-engineering-workspace): add ticket source and verification command fields"
```

---

### Task 3: `pr.md` — drop the duplicated commit-message section

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/pr.md`

**Interfaces:**
- Produces: `pr.md` no longer contains a `## Commit message` heading; it contains a `## Commit` heading pointing at the `git-commit` skill / `conventions.md`. Task 9 (`ticket-finish.md`) references this file by name only, no shared symbols.

- [ ] **Step 1: Replace the "Commit message" section**

In `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/pr.md`, change:

```markdown
## Commit message

```text
fix(<TICKET-ID>): short description
```

## Status update — ready for verification
```

to:

```markdown
## Commit

Handled by the `git-commit` skill when `/ticket-finish` runs (or
`conventions.md`'s "Commit / PR title style" if that skill isn't
installed). Never committed without the user confirming the exact message
first.

## Status update — ready for verification
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "^## Commit" plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/pr.md
```
Expected: one match, `## Commit` (not `## Commit message`).

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/pr.md
git commit -m "fix(ai-engineering-workspace): stop duplicating git-commit's job in pr.md"
```

---

### Task 4: `new-ticket.sh` — lazy creation (context.md only) + self-test

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/scripts/new-ticket.sh`

**Interfaces:**
- Consumes: `context.md` template must already contain `Status: draft` (Task 1) — the self-test asserts on it.
- Produces: the script now copies only `context.md` into a new ticket dir (never the other 5 template files), and supports `--self-test` (same convention as `plugins/ai-engineering-workspace/scripts/handoff-check.sh`).

- [ ] **Step 1: Rewrite the script**

Replace the full contents of `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/scripts/new-ticket.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

create_ticket() {
  local ticket_id="$1" title="$2" ticket_dir="$3" template_dir="$4"

  if [[ -d "$ticket_dir" ]]; then
    echo "Ticket already exists: $ticket_dir"
    return 1
  fi

  mkdir -p "$ticket_dir"
  cp "$template_dir/context.md" "$ticket_dir/"
  sed -i.bak "s/<TICKET-ID>/$ticket_id/g" "$ticket_dir/context.md"
  rm -f "$ticket_dir/context.md.bak"

  if [[ -n "$title" ]]; then
    {
      echo ""
      echo "## Short title"
      echo ""
      echo "$title"
    } >> "$ticket_dir/context.md"
  fi
}

self_test() {
  tmp=$(mktemp -d)
  mkdir -p "$tmp/tickets/_template"
  cat > "$tmp/tickets/_template/context.md" <<'EOF'
# <TICKET-ID> Context

Status: draft

## Goal
EOF
  cat > "$tmp/tickets/_template/investigation.md" <<'EOF'
# <TICKET-ID> Investigation

Status: draft
EOF

  create_ticket "ABC-123" "Test title" "$tmp/tickets/ABC-123" "$tmp/tickets/_template"

  local file_count
  file_count=$(find "$tmp/tickets/ABC-123" -maxdepth 1 -type f | wc -l | tr -d ' ')
  [ "$file_count" = "1" ] && echo "PASS: only one file created" || { echo "FAIL: expected 1 file, found $file_count"; exit 1; }

  [ -f "$tmp/tickets/ABC-123/context.md" ] && echo "PASS: context.md created" || { echo "FAIL: context.md missing"; exit 1; }
  [ -f "$tmp/tickets/ABC-123/investigation.md" ] && { echo "FAIL: investigation.md should not be created eagerly"; exit 1; } || echo "PASS: investigation.md not created (lazy)"

  grep -q "ABC-123 Context" "$tmp/tickets/ABC-123/context.md" && echo "PASS: TICKET-ID substituted" || { echo "FAIL: TICKET-ID not substituted"; exit 1; }
  grep -q "^Status: draft$" "$tmp/tickets/ABC-123/context.md" && echo "PASS: Status: draft present" || { echo "FAIL: Status: draft missing"; exit 1; }
  grep -q "Test title" "$tmp/tickets/ABC-123/context.md" && echo "PASS: title appended" || { echo "FAIL: title not appended"; exit 1; }

  rm -rf "$tmp"
  echo "self-test OK"
}

main() {
  local ticket_id="${1:-}" title="${2:-}"

  if [[ -z "$ticket_id" ]]; then
    echo "Usage: ./scripts/new-ticket.sh ABC-123 \"Short ticket title\""
    exit 1
  fi

  local root_dir ticket_dir template_dir
  root_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  ticket_dir="$root_dir/tickets/$ticket_id"
  template_dir="$root_dir/tickets/_template"

  create_ticket "$ticket_id" "$title" "$ticket_dir" "$template_dir"

  cat <<MSG
Created ticket workspace:
$ticket_dir

Next step:
Run /ticket-understand $ticket_id to fetch the ticket and confirm
understanding before any code is touched.
MSG
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
else
  main "$@"
fi
```

- [ ] **Step 2: Confirm it's still executable**

Run: `test -x plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/scripts/new-ticket.sh && echo "executable"`
Expected: `executable` (the file already had the exec bit before this edit; `Write`/`Edit` tools preserve file permissions).

- [ ] **Step 3: Run the self-test**

Run: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/scripts/new-ticket.sh --self-test`

Expected output (exact):
```
PASS: only one file created
PASS: context.md created
PASS: investigation.md not created (lazy)
PASS: TICKET-ID substituted
PASS: Status: draft present
PASS: title appended
self-test OK
```
Expected exit code: `0`. If any line reads `FAIL: ...`, fix `create_ticket()` before continuing.

- [ ] **Step 4: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/scripts/new-ticket.sh
git commit -m "feat(ai-engineering-workspace): make new-ticket.sh create context.md only"
```

---

### Task 5: `commands/ticket-understand.md` (Phase 1)

**Files:**
- Create: `plugins/ai-engineering-workspace/commands/ticket-understand.md`

**Interfaces:**
- Consumes: `conventions.md`'s "Ticket source" field (Task 2); `context.md`'s `Status:` line (Task 1).
- Produces: the `/ai-engineering-workspace:ticket-understand` command. Its final instruction ("Tell the user to run `/ticket-investigate $ARGUMENTS`") is what Task 6's precondition prose assumes was followed.

- [ ] **Step 1: Create the command file**

Create `plugins/ai-engineering-workspace/commands/ticket-understand.md`:

```markdown
---
description: "Phase 1 of ticket-workflow: fetch and confirm understanding of a ticket before any code investigation starts."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

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
3. Record the raw ask and comments into `context.md` (workspace mode). The
   template's `Status:` line starts as `draft` — leave it as `draft`.
4. Output a restatement covering: goal, user-visible problem, expected vs.
   current behavior, explicit in/out of scope, open questions.
5. STOP. Do not read or search any code. Do not create or write
   `investigation.md`. Wait for the user to confirm the restatement.
6. Once the user confirms, update `context.md`'s `Status:` line to
   `confirmed` (workspace mode only — standalone mode has no file to
   update; the user's confirmation in this conversation is the only
   record).

Tell the user to run `/ticket-investigate $ARGUMENTS`.
```

- [ ] **Step 2: Verify the frontmatter and the hard-stop mechanism**

Run:
```bash
grep -n "disable-model-invocation: true\|^5\. STOP\." plugins/ai-engineering-workspace/commands/ticket-understand.md
```
Expected: two matches — the frontmatter line and the STOP step.

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/commands/ticket-understand.md
git commit -m "feat(ai-engineering-workspace): add /ticket-understand command"
```

---

### Task 6: `commands/ticket-investigate.md` (Phase 2)

**Files:**
- Create: `plugins/ai-engineering-workspace/commands/ticket-investigate.md`

**Interfaces:**
- Consumes: `context.md`'s `Status:` line, expected to be `confirmed` by the time this command runs (Task 5's last step).
- Produces: the `/ai-engineering-workspace:ticket-investigate` command; writes/updates `investigation.md`'s `Status:` line, which Task 7's precondition checks.

- [ ] **Step 1: Create the command file**

Create `plugins/ai-engineering-workspace/commands/ticket-investigate.md`:

```markdown
---
description: "Phase 2 of ticket-workflow: read-only code investigation. Requires ticket understanding already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are investigating ticket $ARGUMENTS. This is Phase 2 of 4: Investigate
(read-only).

Precondition (workspace mode): `context.md` must contain
`Status: confirmed`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run `/ticket-understand $ARGUMENTS`
first — do not use judgment about whether the content "looks" confirmed;
check the literal `Status:` value only.

Precondition (standalone mode): no file to check. Require an explicit
confirmation of the ticket understanding earlier in this conversation; if
there isn't one, stop and restate the ask for confirmation before tracing
code.

1. Read `ecosystem.md`'s flow map if present; otherwise trace from the
   entry point by reading the actual code.
2. Identify the most likely owner repo/module.
3. Separate facts (evidence-backed), hypotheses (unconfirmed), decisions.
4. Record findings, evidence, open questions, and next steps into
   `investigation.md` (create it from the template if it doesn't exist
   yet; its `Status:` line starts as `draft`).

Do not edit any code in this phase.

Gate: summarize confirmed facts, likely root cause, owner, and the next
safest action. Wait for confirmation. Once confirmed, update
`investigation.md`'s `Status:` line to `confirmed` (workspace mode).

Tell the user to run `/ticket-implement $ARGUMENTS`.
```

- [ ] **Step 2: Verify the frontmatter and precondition wording**

Run:
```bash
grep -n "disable-model-invocation: true\|Status: confirmed\|check the literal" plugins/ai-engineering-workspace/commands/ticket-investigate.md
```
Expected: at least 3 matches, including the "check the literal `Status:` value only" phrase that rules out impressionistic judgment.

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/commands/ticket-investigate.md
git commit -m "feat(ai-engineering-workspace): add /ticket-investigate command"
```

---

### Task 7: `commands/ticket-implement.md` (Phase 3)

**Files:**
- Create: `plugins/ai-engineering-workspace/commands/ticket-implement.md`

**Interfaces:**
- Consumes: `investigation.md`'s `Status:` line (Task 6); `conventions.md`'s "Verification commands" section (Task 2).
- Produces: the `/ai-engineering-workspace:ticket-implement` command; writes `implementation.md` and `test.md`.

- [ ] **Step 1: Create the command file**

Create `plugins/ai-engineering-workspace/commands/ticket-implement.md`:

```markdown
---
description: "Phase 3 of ticket-workflow: minimal implementation. Requires investigation already confirmed."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are implementing ticket $ARGUMENTS. This is Phase 3 of 4: Implement
(minimal).

Precondition (workspace mode): `investigation.md` must contain
`Status: confirmed`. If it doesn't (missing file, `Status: draft`, or any
other value), STOP and tell the user to run `/ticket-investigate
$ARGUMENTS` first — check the literal `Status:` value only, not whether
the content looks complete.

Precondition (standalone mode): require an explicit confirmation of root
cause/owner earlier in this conversation; if there isn't one, stop and ask
for it before editing.

Before editing:
1. Confirm the owner repo/module.
2. Check current directory, branch, `git status`, and current diff.
3. Summarize the intended minimal change.

Then make the smallest safe change.

Rules:
- No unrelated refactors or formatting.
- Don't touch multiple repos/modules unless the investigation justifies
  it.
- Preserve existing behavior unless the ticket requires changing it.
- Run every configured "Verification command" from `conventions.md`
  (typecheck/lint/test/build); skip any entry marked `N/A` or left unset.
  Report results honestly, including failures.
- Record what changed and how it was tested into `implementation.md` and
  `test.md` (create them from the template if they don't exist yet).

Once checks pass, tell the user to run `/ticket-finish $ARGUMENTS`.
```

- [ ] **Step 2: Verify the frontmatter and the N/A-skip rule**

Run:
```bash
grep -n "disable-model-invocation: true\|skip any entry marked" plugins/ai-engineering-workspace/commands/ticket-implement.md
```
Expected: two matches.

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/commands/ticket-implement.md
git commit -m "feat(ai-engineering-workspace): add /ticket-implement command"
```

---

### Task 8: `commands/ticket-finish.md` (Phase 4)

**Files:**
- Create: `plugins/ai-engineering-workspace/commands/ticket-finish.md`

**Interfaces:**
- Consumes: `pr.md`'s "Commit" pointer section (Task 3).
- Produces: the `/ai-engineering-workspace:ticket-finish` command. Delegates the actual commit to the `git-commit` skill (`plugins/git-commit/skills/git-commit/SKILL.md`, unchanged by this plan) and the handoff to the `handoff` skill (unchanged by this plan).

- [ ] **Step 1: Create the command file**

Create `plugins/ai-engineering-workspace/commands/ticket-finish.md`:

```markdown
---
description: "Phase 4 of ticket-workflow: PR notes, a user-confirmed commit, and handoff."
argument-hint: <TICKET-ID>
disable-model-invocation: true
---

You are finishing ticket $ARGUMENTS. This is Phase 4 of 4: Finish.

1. Generate PR title, PR description, test notes, and a short status
   update (follow `conventions.md`'s style, or repo precedent if unset).
   Save into `pr.md` (create it from the template if it doesn't exist
   yet).
2. Commit — never automatic, and never push:
   - If the `git-commit` skill is installed, invoke it. It already runs
     checks, drafts the message, shows it to the user, and waits for
     explicit confirmation before committing — do not restate
     commit-message rules here, and do not skip its confirmation step.
   - Otherwise, draft a commit message using `conventions.md`'s "Commit /
     PR title style", show it to the user, and wait for explicit
     confirmation before running `git commit`.
   - Either way: do not run `git commit` without the user having seen and
     confirmed the exact message first, and do not run `git push` as part
     of this command under any circumstance.
3. Save a handoff — invoke the `handoff` skill's save flow. A ticket isn't
   finished until the next session could continue it cold.
```

- [ ] **Step 2: Verify the frontmatter and the no-auto-commit/no-push rules**

Run:
```bash
grep -n "disable-model-invocation: true\|never push\|do not run \`git push\`" plugins/ai-engineering-workspace/commands/ticket-finish.md
```
Expected: at least 2 matches.

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/commands/ticket-finish.md
git commit -m "feat(ai-engineering-workspace): add /ticket-finish command"
```

---

### Task 9: `ticket-workflow/SKILL.md` — rewrite as router

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ticket-workflow/SKILL.md`

**Interfaces:**
- Consumes: the four command names from Tasks 5–8 (referenced by name only, in a markdown table).
- Produces: no runtime interface — this is documentation the agent reads when the skill auto-triggers.

- [ ] **Step 1: Replace the file body (keep frontmatter unchanged)**

Replace everything in `plugins/ai-engineering-workspace/skills/ticket-workflow/SKILL.md` from the line `# Ticket Workflow` onward (keep the `---`-delimited frontmatter at the top exactly as-is) with:

```markdown
# Ticket Workflow

Four gated phases, each with its own slash command for a hard,
user-controlled phase boundary — the agent can't see a later phase's
instructions until the user runs that phase's command, so it can't
self-chain ahead.

| Phase | Command | Purpose |
|---|---|---|
| 1. Understand | `/ticket-understand <ID>` | Fetch the ticket + comments, confirm the ask, before any code is touched |
| 2. Investigate | `/ticket-investigate <ID>` | Read-only: trace flow, confirm root cause + owner |
| 3. Implement | `/ticket-implement <ID>` | Minimal change, only after investigation is confirmed |
| 4. Finish | `/ticket-finish <ID>` | PR notes, commit (user-confirmed, via `git-commit` skill if installed), handoff |

**Use the commands for a hard phase boundary.** If the user asks to "work
on ticket X" conversationally instead of invoking a command, walk them
through the same 4 phases and gates in the conversation — but that path is
prose-gated, not structural, so recommend switching to the commands so
understanding gets confirmed before you read any code. Both paths write
the same `Status:` field in `context.md`/`investigation.md` (`draft` →
`confirmed`), so whichever path reaches a ticket first, a command run
later still has a real precondition to check instead of guessing.

**Workspace mode**: if a ticket workspace exists (a directory with
`ecosystem.md` and `tickets/<TICKET-ID>/`), read `ecosystem.md`,
`conventions.md`, and the ticket's files before starting, and record
results into the ticket files as you go.
**Standalone mode**: no workspace — follow the same phases, keep the
records in your responses (or a scratch file if the user wants
persistence), and infer conventions from the repo (recent commits, PR
history). There's no `Status:` file to check in this mode — an explicit
confirmation earlier in the conversation satisfies the gate instead.
```

- [ ] **Step 2: Verify the frontmatter survived and the phase table is present**

Run:
```bash
head -4 plugins/ai-engineering-workspace/skills/ticket-workflow/SKILL.md
grep -c "^| [1-4]\." plugins/ai-engineering-workspace/skills/ticket-workflow/SKILL.md
```
Expected: `head -4` shows the unchanged `---`/`name: ticket-workflow`/`description: ...`/`---` block; the `grep -c` count is `4`.

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ticket-workflow/SKILL.md
git commit -m "refactor(ai-engineering-workspace): ticket-workflow becomes a command router"
```

---

### Task 10: `structured-bug-fix/SKILL.md` — add the confirmation paragraph

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/structured-bug-fix/SKILL.md`

**Interfaces:**
- None — self-contained prose addition, no other task depends on it.

- [ ] **Step 1: Insert the confirmation paragraph at the end of Phase 1**

In `plugins/ai-engineering-workspace/skills/structured-bug-fix/SKILL.md`, change:

```markdown
Don't ask for information already provided.

## Phase 2 — Trace the flow
```

to:

```markdown
Don't ask for information already provided.

Before tracing the flow, output a one-line restatement: "My understanding
of the bug is: ...". Wait for the user to confirm before starting Phase 2.

## Phase 2 — Trace the flow
```

- [ ] **Step 2: Verify**

Run:
```bash
grep -n "My understanding" plugins/ai-engineering-workspace/skills/structured-bug-fix/SKILL.md
```
Expected: one match, positioned before the `## Phase 2` heading (confirm with `grep -n "My understanding\|^## Phase 2"` — the "My understanding" line number must be smaller).

- [ ] **Step 3: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/structured-bug-fix/SKILL.md
git commit -m "feat(ai-engineering-workspace): add confirmation gate to structured-bug-fix Phase 1"
```

---

### Task 11: `ai-engineering-workspace/SKILL.md` — scaffold interview + golden rule

**Files:**
- Modify: `plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md`

**Interfaces:**
- None — self-contained documentation edit.

- [ ] **Step 1: Fold "Ticket source" into interview question 3**

Change:

```markdown
3. **Ticket IDs** — format, e.g. `ABC-123`. Used in branch names and commits.
```

to:

```markdown
3. **Ticket IDs** — format, e.g. `ABC-123`. Used in branch names and
   commits. Also: how do you fetch a ticket's raw content and comments —
   a command or MCP tool (e.g. `gh issue view <ID> --comments`)? →
   recorded as `conventions.md`'s "Ticket source".
```

- [ ] **Step 2: Fold "Verification commands" into interview question 5**

Change:

```markdown
5. **Conventions** — branch/commit/PR format; where updates are posted
   (Slack/Teams/issue comments) and the preferred tone.
```

to:

```markdown
5. **Conventions** — branch/commit/PR format; where updates are posted
   (Slack/Teams/issue comments) and the preferred tone. Also: typecheck/
   lint/test/build commands (mark any that don't apply as N/A) →
   recorded as `conventions.md`'s "Verification commands".
```

- [ ] **Step 3: Update the "New tickets" line to point at the command**

Change:

```markdown
New tickets: `./scripts/new-ticket.sh <TICKET-ID> "short title"`.
```

to:

```markdown
New tickets: `./scripts/new-ticket.sh <TICKET-ID> "short title"` creates
`context.md` only; run `/ticket-understand <TICKET-ID>` next — the rest of
a ticket's files are created lazily as each phase command needs them.
```

- [ ] **Step 4: Add the commit/push rule to the Golden rules section**

Change:

```markdown
## Golden rules (all suite skills inherit these)

- Do not edit code before root cause and owner location are reasonably confirmed.
- Always check current repo, branch, `git status`, and diff before editing.
- Smallest safe change; no unrelated formatting or broad refactors.
- Separate facts (evidence-backed), hypotheses (guesses), and decisions.
- Never end a session without a useful handoff.
```

to:

```markdown
## Golden rules (all suite skills inherit these)

- Do not edit code before root cause and owner location are reasonably confirmed.
- Always check current repo, branch, `git status`, and diff before editing.
- Smallest safe change; no unrelated formatting or broad refactors.
- Separate facts (evidence-backed), hypotheses (guesses), and decisions.
- Never end a session without a useful handoff.
- Never run `git commit` without showing the user the exact message and
  getting explicit confirmation first. Never run `git push`.
```

- [ ] **Step 5: Verify all four edits**

Run:
```bash
grep -n "Ticket source\|Verification commands\|ticket-understand <TICKET-ID>\|Never run \`git push\`" plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md
```
Expected: 4 matches (one per phrase).

- [ ] **Step 6: Commit**

```bash
git add plugins/ai-engineering-workspace/skills/ai-engineering-workspace/SKILL.md
git commit -m "docs(ai-engineering-workspace): fold new scaffold fields into interview, add push/commit golden rule"
```

---

### Task 12: Version bump + full-plugin validation

**Files:**
- Modify: `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`

**Interfaces:**
- Consumes: nothing from earlier tasks' internals — only needs Tasks 1–11 to be on disk so validation has something to check.

- [ ] **Step 1: Bump `plugin.json`**

In `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`, change:
```json
  "version": "0.4.0",
```
to:
```json
  "version": "0.5.0",
```

- [ ] **Step 2: Bump the mirrored entry in `marketplace.json`**

In `.claude-plugin/marketplace.json`, find the `"name": "ai-engineering-workspace"` entry and change its `"version": "0.4.0"` to `"version": "0.5.0"`.

- [ ] **Step 3: Verify both version bumps**

Run:
```bash
python3 -c "import json; print(json.load(open('plugins/ai-engineering-workspace/.claude-plugin/plugin.json'))['version'])"
python3 -c "
import json
d = json.load(open('.claude-plugin/marketplace.json'))
entry = next(p for p in d['plugins'] if p['name'] == 'ai-engineering-workspace')
print(entry['version'])
"
```
Expected: `0.5.0` printed twice. (If the second script errors on `d['plugins']` — the top-level key name — inspect `.claude-plugin/marketplace.json`'s structure with `python3 -m json.tool .claude-plugin/marketplace.json | head -20` and adjust the key name to match; do not guess blindly.)

- [ ] **Step 4: Validate the plugin manifest and command files**

Run: `claude plugin validate .`
Expected: no errors reported for `ai-engineering-workspace` (including the new `commands/` directory and its four files).

- [ ] **Step 5: Re-run the vetting audit against the whole plugin**

Run: `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color`
Expected: no CRITICAL finding. `commands/*.md` files are prompt text, not scripts, so `SCRIPT_RULES` won't fire on them; this step confirms that assumption holds against the actual files just written, not just in theory.

- [ ] **Step 6: Confirm the plugin's own template sources are untouched**

Run:
```bash
ls plugins/ai-engineering-workspace/skills/ai-engineering-workspace/templates/tickets/
```
Expected: all 7 master template files are still present — `context.md`,
`investigation.md`, `implementation.md`, `test.md`, `pr.md`, `timeline.md`,
`handoff.md`. This directory is the plugin's own template source (it gets
copied wholesale into a scaffolded workspace's `tickets/_template/` per
`ai-engineering-workspace/SKILL.md`'s scaffold table — that `_template/`
naming only exists inside a deployed workspace, not in this repo). Only
`new-ticket.sh`'s *copying behavior* became lazy (Task 4); none of these 7
source files were removed.

- [ ] **Step 7: Commit**

```bash
git add plugins/ai-engineering-workspace/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "chore(ai-engineering-workspace): bump version to 0.5.0 for flow redesign"
```

---

### Task 13: Manual dry run (documented checklist, not automated)

**Files:** none — this task exercises the plugin end-to-end in a live Claude Code session; there is no file to create or modify.

**Interfaces:** none.

This task can't be executed by a coding agent editing files — slash commands and `disable-model-invocation` only take effect inside a real Claude Code session with the plugin installed/enabled. Whoever runs this plan should perform it manually after Task 12, and report results back before considering the redesign done. Steps:

- [ ] **Step 1: Scaffold a throwaway workspace**

In a scratch directory, run the `ai-engineering-workspace` skill's scaffold flow (or `./scripts/new-ticket.sh` directly against a hand-built `tickets/_template/` copied from the plugin's templates) to create a fake ticket, e.g. `TEST-1`.

- [ ] **Step 2: Confirm `/ticket-investigate` refuses to run before `/ticket-understand`**

With `context.md`'s `Status:` still `draft` (or the file missing), invoke `/ai-engineering-workspace:ticket-investigate TEST-1`. Expected: the command stops and points back at `/ticket-understand`, per Task 6's precondition — even if `context.md` has been hand-filled with realistic-looking content, since the check is on the literal `Status:` value, not content quality.

- [ ] **Step 3: Run the full happy path**

Invoke `/ticket-understand TEST-1`, confirm the restatement, then `/ticket-investigate TEST-1`, confirm the diagnosis, then `/ticket-implement TEST-1`, then `/ticket-finish TEST-1`. Expected: each command stops at its gate and waits; `context.md`'s and `investigation.md`'s `Status:` lines flip to `confirmed` at the right points; `implementation.md`, `test.md`, and `pr.md` appear only once their respective command needs them; `/ticket-finish` shows a drafted commit message and waits for confirmation rather than committing immediately, and never runs `git push`.

- [ ] **Step 4: Confirm the agent cannot self-chain commands**

During the dry run, watch whether the agent ever invokes a later `/ticket-*` command on its own via the SlashCommand tool instead of waiting for the user to type it. Expected: it never does — `disable-model-invocation: true` should block that path entirely. This is the one behavior in this plan asserted from Claude Code's documented command frontmatter rather than verified by a script in this repo, so it's worth confirming directly.

- [ ] **Step 5: Clean up the scratch workspace**

Delete the scratch directory used for the dry run. Nothing in this plan writes outside that scratch directory, so no other cleanup is needed.
