#!/bin/bash
set -u

check() {
  local files=()
  while IFS= read -r -d '' f; do
    files+=("$f")
  done < <(
    { find tickets -maxdepth 2 -type f -iname 'handoff.md' -print0 2>/dev/null
      find .handoff -maxdepth 1 -type f -iname '*.md' -print0 2>/dev/null
    }
  )
  [ "${#files[@]}" -eq 0 ] && return 0

  # Cap the list and sanitize each path on its own (not the joined stream) so
  # an embedded newline/control byte inside one filename can't be mistaken
  # for a record separator or inject fake lines into the reminder.
  found=""
  local n=0 clean
  for f in "${files[@]}"; do
    [ "$n" -ge 20 ] && break
    clean=$(printf '%s' "$f" | tr -cd '\40-\176')
    found="${found}${clean}
"
    n=$((n + 1))
  done
  found="${found%$'\n'}"

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
