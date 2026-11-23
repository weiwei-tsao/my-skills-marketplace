#!/usr/bin/env bash
# PostToolUse(Edit|Write) lint, installed by project-context:setup.
#
# Lints only the file Claude just edited (path at .tool_input.file_path on
# stdin). The edit itself has already happened and is not undone.
# Linter exit 1 means it found problems in the file: exit 2 so Claude sees the
# output and can fix it. Any other failure (not installed, config error, crash)
# is a setup problem, not the code's: exit 1, which shows the message to the
# user without blocking Claude or telling it to change the code.
#
# setup fills in the two values below for this project.
# LINT_CMD is split on spaces and run directly (no shell): a program plus plain
# arguments only, with no quotes, pipes, redirects or $variables.
LINT_CMD="__LINT_CMD__"      # per-file lint command, the file path is appended, e.g. "node_modules/.bin/eslint"
LINT_EXTS="__LINT_EXTS__"    # space-separated extensions to lint, e.g. "ts tsx js jsx"

# Work from the project root so relative paths and the linter's config resolve.
cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  file=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
elif command -v python3 >/dev/null 2>&1; then
  file=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
else
  exit 0
fi

[ -n "$file" ] && [ -f "$file" ] || exit 0

ext="${file##*.}"
case " $LINT_EXTS " in
  *" $ext "*) ;;
  *) exit 0 ;;
esac

out=$($LINT_CMD "$file" 2>&1)
rc=$?
case $rc in
  0) exit 0 ;;
  1) printf 'Lint failed for %s:\n%s\n' "$file" "$out" >&2
     exit 2 ;;
  *) printf 'Lint hook: %s exited %s (linter not installed, config error or crash), not a problem in %s. Not blocking.\n%s\n' \
       "$LINT_CMD" "$rc" "$file" "$(printf '%s\n' "$out" | head -n 5)" >&2
     exit 1 ;;
esac
