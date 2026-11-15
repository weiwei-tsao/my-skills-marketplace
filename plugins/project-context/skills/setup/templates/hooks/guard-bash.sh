#!/usr/bin/env bash
# PreToolUse(Bash) guard, installed by project-context:setup.
#
# Claude Code passes the tool call as JSON on stdin; the command is at
# .tool_input.command. Exit 2 blocks the call and shows stderr to Claude.
# Any other exit code lets the call through.

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | jq -r '.tool_input.command // empty')
elif command -v python3 >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("command",""))')
else
  echo "guard-bash: neither jq nor python3 found; guard is not checking commands" >&2
  exit 0
fi

block() {
  echo "BLOCKED by .claude/hooks/guard-bash.sh: $1" >&2
  exit 2
}

# Recursive force-delete of filesystem root or home directory.
if printf '%s' "$cmd" | grep -qE '(^|[;&|[:space:]])rm[[:space:]]+-[a-zA-Z]*(rf|fr)[a-zA-Z]*[[:space:]]+(/|~|\$HOME)/?([[:space:];&|]|$)'; then
  block "recursive delete of / or home directory"
fi

# Force push that targets main/master (covers `git push -f origin main`,
# `git push --force main`, `git push origin main --force`, `+main` refspecs).
if printf '%s' "$cmd" | grep -qE '(^|[;&|[:space:]])git[[:space:]]+push([[:space:]]|$)'; then
  if printf '%s' "$cmd" | grep -qE '[[:space:]](-f|--force|--force-with-lease)([[:space:]=]|$)|[[:space:]]\+(main|master)([[:space:]]|$)' \
     && printf '%s' "$cmd" | grep -qE '(^|[[:space:]:+/])(main|master)([[:space:]]|$)'; then
    block "force push to main/master"
  fi
fi

# Dropping a table or database.
if printf '%s' "$cmd" | grep -qiE '\bdrop[[:space:]]+(table|database|schema)\b'; then
  block "DROP TABLE/DATABASE/SCHEMA"
fi

exit 0
