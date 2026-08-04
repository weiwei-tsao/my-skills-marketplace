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
