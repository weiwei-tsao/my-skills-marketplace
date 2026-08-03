# Handoff-Check Hook Design

## Summary

Add a `SessionStart` hook to the existing `ai-engineering-workspace` plugin
that detects a leftover `handoff.md` from a previous session and reminds the
agent to read it before acting. The hook ships with the plugin (not as a
personal dotfile) so it travels automatically to every machine where the
plugin is installed — the user works across multiple machines and needs this
behavior to follow the plugin, not live in per-machine config.

This does not add a new skill. The `handoff` skill already implements both
`save` and `resume` modes (`plugins/ai-engineering-workspace/skills/handoff/SKILL.md`).
The gap this hook closes is discovery: nothing currently notices a handoff
file exists when a fresh session starts without the user mentioning the
ticket or saying "resume."

## Placement

```text
plugins/ai-engineering-workspace/
  hooks/hooks.json
  scripts/handoff-check.sh
```

No existing files are modified except `CLAUDE.md` (new documentation section)
and `plugins/ai-engineering-workspace/.claude-plugin/plugin.json` (version
bump).

## Mechanism

Claude Code plugins can ship their own hooks in `hooks/hooks.json` at the
plugin root, using the same schema as the `hooks` object in
`~/.claude/settings.json` (event name → array of `{matcher, hooks: [{type:
"command", command}]}`). Hooks activate automatically when the plugin is
enabled — no separate user confirmation step. Scripts reference their own
plugin directory via the `${CLAUDE_PLUGIN_ROOT}` placeholder, which resolves
per-installation, making the path portable across machines.

`hooks.json`:

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

All four matchers are covered (not just `startup`/`resume`) so the reminder
also fires after `/clear` or `/compact` mid-conversation, when prior context
about an in-progress ticket may have just been dropped. The script is silent
when nothing is found, so covering all four matchers costs nothing beyond a
few extra millisecond `find` calls per session-start event.

## Detection Scope

The hook checks both file locations the `handoff` skill itself defines
(`plugins/ai-engineering-workspace/skills/handoff/SKILL.md`, "File
location"):

- Workspace mode: `tickets/<TICKET-ID>/handoff.md` (any ticket, `-maxdepth 2`
  under `tickets/`).
- Standalone mode: `.handoff/*.md` at the repo root (covers both
  `.handoff/HANDOFF.md` and `.handoff/<TICKET-ID>.md`).

Both are checked unconditionally; the hook does not try to detect which mode
the current repo uses first. If a repo has neither directory, both `find`
calls return nothing and the script produces no output.

## Script

`scripts/handoff-check.sh`:

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

## Error Handling

- Both `find` invocations redirect stderr to `/dev/null`; a missing
  `tickets/` or `.handoff/` directory is the expected common case, not an
  error.
- The script never calls `exit 1` from the normal (non-`--self-test`) path —
  a hook that fails or hangs must not block session start. `set -u` is used
  only to catch typos during development; it does not change the "always
  exit success" behavior for the check path.
- No network calls, no writes, no reads outside `tickets/` and `.handoff/`
  relative to cwd.

## Testing

Per the repo's own lazy-but-not-untested convention, the script carries one
self-check reachable via `handoff-check.sh --self-test`: it exercises the
"found" and "not found" branches in temp directories and asserts on the
output. This is not wired into CI (no shell-test runner exists elsewhere in
this repo) — it's a manual, runnable check for whoever touches this script
next.

## Documentation and Vetting

`vetting/audit_skill.py` already walks its target directory recursively
(`os.walk`) and applies `SCRIPT_RULES` (curl-pipe-to-shell, `.ssh`/`.env`
access, network calls, destructive commands, credential env vars) to every
file with a script extension, including `.sh`. Because `CLAUDE.md`'s
documented audit command already targets the whole plugin directory
(`python3 vetting/audit_skill.py plugins/<name>`), no new tooling is needed —
`hooks/hooks.json` and `scripts/handoff-check.sh` are covered by the existing
command once they exist on disk.

`CLAUDE.md` gets one new short section stating that plugins may also ship a
`hooks/` directory, that the existing audit command already covers it, and
that a human should still read the hook script directly (mirroring the
existing "human read SKILL.md" step) since a clean static-analysis pass is
triage, not proof of safety.

`plugins/ai-engineering-workspace/.claude-plugin/plugin.json` version bumps
from `0.3.0` to `0.4.0` (new plugin capability, no skill content changed).

## Non-Goals

- Do not parse or summarize handoff file contents in the hook. The hook only
  announces that a file exists and where; reading/verifying its content is
  the `handoff` skill's `resume` job, which already includes code-fact
  verification the hook has no business doing.
- Do not add hook support to any other plugin in this marketplace as part of
  this change.
- Do not build new vetting tooling for hook scripts; the existing
  `audit_skill.py` invocation already covers them structurally.
- Do not sync `~/.claude/settings.json` or dotfiles across machines as part
  of this change — the whole point of shipping the hook via the plugin is to
  make that unnecessary.
