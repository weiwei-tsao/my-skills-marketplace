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
Run /ai-engineering-workspace:ticket-understand $ticket_id to fetch the
ticket and confirm understanding before any code is touched.
MSG
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
else
  main "$@"
fi
