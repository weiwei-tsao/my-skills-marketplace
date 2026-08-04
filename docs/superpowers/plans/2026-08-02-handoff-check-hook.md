# Handoff-Check Hook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a `SessionStart` hook with the `ai-engineering-workspace` plugin that detects a leftover handoff file and reminds the agent to read it, so the reminder travels with the plugin to every machine instead of living in per-machine `settings.json`.

**Architecture:** A plugin-local `hooks/hooks.json` registers the same shell script against all four `SessionStart` matchers (`startup`/`resume`/`clear`/`compact`). The script does two read-only `find` calls against the current working directory and prints a short reminder to stdout if it finds anything; stdout of a `SessionStart` hook is what Claude Code injects into the session as a system-reminder (confirmed empirically: this is exactly how the existing `cbm-session-reminder` hook already surfaces its output in every session).

**Tech Stack:** POSIX-ish bash (`#!/bin/bash`), JSON (plugin hook manifest). No new dependencies.

## Global Constraints

- SessionStart hook must cover all four matchers: `startup`, `resume`, `clear`, `compact` — spec decision, not partial coverage.
- Detection must cover both file locations the `handoff` skill itself defines: workspace mode `tickets/<TICKET-ID>/handoff.md` (any ticket dir, depth 2 under `tickets/`) and standalone mode `.handoff/*.md` at repo root.
- The script must never `exit` nonzero or hang on its normal (non-`--self-test`) path — a hook must not block session start. Both `find` calls redirect stderr to `/dev/null`.
- No network calls, no writes, no reads outside `tickets/` and `.handoff/` relative to cwd.
- Script paths in `hooks.json` use `${CLAUDE_PLUGIN_ROOT}`, never a hardcoded absolute path.
- `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color` (the command already documented in `CLAUDE.md`) must be re-run after adding the new files and must not report any new CRITICAL finding.
- `plugins/ai-engineering-workspace/.claude-plugin/plugin.json` version bumps from `0.3.0` to `0.4.0`.

---

### Task 1: Handoff-check hook script and manifest

**Files:**
- Create: `plugins/ai-engineering-workspace/scripts/handoff-check.sh`
- Create: `plugins/ai-engineering-workspace/hooks/hooks.json`

**Interfaces:**
- Produces: an executable shell script at `plugins/ai-engineering-workspace/scripts/handoff-check.sh` with two invocation modes — no args (prints reminder or nothing, always exits 0) and `--self-test` (prints `PASS`/`FAIL` lines and exits 0 on success, 1 on failure). Task 2 does not depend on this script's internals, only on its existence at this path for documentation purposes.

- [ ] **Step 1: Write the script**

Create `plugins/ai-engineering-workspace/scripts/handoff-check.sh`:

```bash
#!/bin/bash
set -u

check() {
  found=$(find tickets -maxdepth 2 -iname 'handoff.md' 2>/dev/null; find .handoff -maxdepth 1 -iname '*.md' 2>/dev/null)
  [ -z "$found" ] && return 0
  cat <<EOF
Handoff file(s) found from a previous session:
$found
If continuing this work, read the file and follow the handoff skill's resume steps before acting.
EOF
}

self_test() {
  tmp=$(mktemp -d)
  cd "$tmp" || exit 1

  mkdir -p tickets/ABC-123
  echo "test" > tickets/ABC-123/handoff.md
  out=$(check)
  case "$out" in
    *tickets/ABC-123/handoff.md*) echo "PASS: detects workspace-mode handoff" ;;
    *) echo "FAIL: did not detect tickets/ABC-123/handoff.md"; exit 1 ;;
  esac
  rm -rf tickets

  mkdir -p .handoff
  echo "test" > .handoff/HANDOFF.md
  out=$(check)
  case "$out" in
    *.handoff/HANDOFF.md*) echo "PASS: detects standalone-mode handoff" ;;
    *) echo "FAIL: did not detect .handoff/HANDOFF.md"; exit 1 ;;
  esac
  rm -rf .handoff

  out=$(check)
  [ -z "$out" ] && echo "PASS: silent when no handoff file exists" || { echo "FAIL: expected empty output, got: $out"; exit 1; }

  cd - > /dev/null || exit 1
  rm -rf "$tmp"
  echo "self-test OK"
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
else
  check
fi
```

- [ ] **Step 2: Make it executable**

Run: `chmod +x plugins/ai-engineering-workspace/scripts/handoff-check.sh`

- [ ] **Step 3: Run the self-test and verify it fails loudly if logic is wrong**

Run: `plugins/ai-engineering-workspace/scripts/handoff-check.sh --self-test`

Expected output (exact):
```
PASS: detects workspace-mode handoff
PASS: detects standalone-mode handoff
PASS: silent when no handoff file exists
self-test OK
```
Expected exit code: `0` (check with `echo $?` immediately after).

If either line reads `FAIL: ...`, the script has a bug — fix `check()` before continuing. Do not proceed to Step 4 on a `FAIL`.

- [ ] **Step 4: Manually verify silent behavior outside a ticket workspace**

Run, from the repo root (`my-skills-marketplace` has no `tickets/` or `.handoff/` dir):
```bash
plugins/ai-engineering-workspace/scripts/handoff-check.sh; echo "exit=$?"
```
Expected: no stdout output, `exit=0`.

- [ ] **Step 5: Write the hook manifest**

Create `plugins/ai-engineering-workspace/hooks/hooks.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/handoff-check.sh" }]
      },
      {
        "matcher": "resume",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/handoff-check.sh" }]
      },
      {
        "matcher": "clear",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/handoff-check.sh" }]
      },
      {
        "matcher": "compact",
        "hooks": [{ "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/scripts/handoff-check.sh" }]
      }
    ]
  }
}
```

- [ ] **Step 6: Validate the JSON parses**

Run: `python3 -m json.tool plugins/ai-engineering-workspace/hooks/hooks.json`
Expected: pretty-printed JSON echoed back, no `json.decoder.JSONDecodeError`.

- [ ] **Step 7: Run the existing vetting tool against the whole plugin**

Run: `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color`
Expected: exit code `0` or `1` (HIGH at most), and specifically **no CRITICAL finding** whose `file` is `hooks/hooks.json` or `scripts/handoff-check.sh`. Confirm by checking the printed report output — if a CRITICAL finding appears against either new file, stop and fix the script/manifest before continuing (do not weaken the vetting tool to pass).

- [ ] **Step 8: Commit**

```bash
git add plugins/ai-engineering-workspace/scripts/handoff-check.sh plugins/ai-engineering-workspace/hooks/hooks.json
git commit -m "feat(ai-engineering-workspace): add handoff-check SessionStart hook"
```

---

### Task 2: Document the hook and bump plugin version

**Files:**
- Modify: `CLAUDE.md`
- Modify: `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: nothing from Task 1's internals — only needs to know Task 1 created `plugins/ai-engineering-workspace/hooks/hooks.json` and `plugins/ai-engineering-workspace/scripts/handoff-check.sh` (paths only, referenced in prose).

- [ ] **Step 1: Add a "Plugin hooks" section to `CLAUDE.md`**

Insert a new section after the existing `## Auditing an existing plugin manually` section (find it with `grep -n "Auditing an existing plugin manually" CLAUDE.md` to get the exact insertion point), containing:

```markdown
## Plugin hooks

A plugin may also ship a `hooks/hooks.json` (Claude Code plugin hook
convention — same schema as the `hooks` object in `~/.claude/settings.json`,
scripts referenced via `${CLAUDE_PLUGIN_ROOT}`). Hooks activate automatically
when the plugin is enabled, with no separate user confirmation, so they get
the same scrutiny as skill content:

- The existing audit command already covers them: `vetting/audit_skill.py`
  walks the whole directory passed to it and applies `SCRIPT_RULES` to every
  script-extension file it finds, including anything under `hooks/` or
  `scripts/`. Running `python3 vetting/audit_skill.py plugins/<name>` (as
  already documented above) is sufficient — no separate command is needed
  for hook scripts.
- A clean static-analysis pass is triage, not proof of safety. Read any new
  or changed hook script by hand before merging, the same way `SKILL.md` gets
  a human read in the `add-skill.sh` pipeline.
```

- [ ] **Step 2: Verify the insertion**

Run: `grep -n "## Plugin hooks" CLAUDE.md`
Expected: one match, at the line where the section was inserted.

- [ ] **Step 3: Bump the plugin version**

In `plugins/ai-engineering-workspace/.claude-plugin/plugin.json`, change:
```json
  "version": "0.3.0",
```
to:
```json
  "version": "0.4.0",
```

- [ ] **Step 4: Verify the version bump**

Run: `python3 -c "import json; print(json.load(open('plugins/ai-engineering-workspace/.claude-plugin/plugin.json'))['version'])"`
Expected: `0.4.0`

- [ ] **Step 5: Re-run the vetting command referenced in the new doc section**

Run: `python3 vetting/audit_skill.py plugins/ai-engineering-workspace --no-color`
Expected: same result as Task 1 Step 7 (no new CRITICAL findings) — this step exists to prove the doc's claim ("running this command is sufficient") is actually true against the current state of the plugin directory.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md plugins/ai-engineering-workspace/.claude-plugin/plugin.json
git commit -m "docs(ai-engineering-workspace): document plugin hooks and bump version"
```
