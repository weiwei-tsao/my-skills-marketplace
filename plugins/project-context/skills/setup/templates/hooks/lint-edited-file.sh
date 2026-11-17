#!/usr/bin/env bash
# PostToolUse(Edit|Write) lint, installed by project-context:setup.
#
# Lints only the file Claude just edited (path at .tool_input.file_path on
# stdin). On lint failure it exits 2 so Claude sees the output and can fix it;
# the edit itself has already happened and is not undone.
#
# setup fills in the two values below for this project.
# LINT_CMD is split on spaces and run directly (no shell): a program plus plain
# arguments only, with no quotes, pipes, redirects or $variables.
LINT_CMD="__LINT_CMD__"      # per-file lint command, the file path is appended, e.g. "npx eslint"
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

if ! out=$($LINT_CMD "$file" 2>&1); then
  printf 'Lint failed for %s:\n%s\n' "$file" "$out" >&2
  exit 2
fi
exit 0
