#!/usr/bin/env bash
set -euo pipefail

TICKET_ID="${1:-}"
TITLE="${2:-}"

if [[ -z "$TICKET_ID" ]]; then
  echo "Usage: ./scripts/new-ticket.sh ABC-123 \"Short ticket title\""
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TICKET_DIR="$ROOT_DIR/tickets/$TICKET_ID"
TEMPLATE_DIR="$ROOT_DIR/tickets/_template"

if [[ -d "$TICKET_DIR" ]]; then
  echo "Ticket already exists: $TICKET_DIR"
  exit 1
fi

mkdir -p "$TICKET_DIR"
cp "$TEMPLATE_DIR"/*.md "$TICKET_DIR"/

for file in "$TICKET_DIR"/*.md; do
  sed -i.bak "s/<TICKET-ID>/$TICKET_ID/g" "$file"
  rm -f "$file.bak"
done

if [[ -n "$TITLE" ]]; then
  {
    echo ""
    echo "## Short title"
    echo ""
    echo "$TITLE"
  } >> "$TICKET_DIR/context.md"
fi

cat <<MSG
Created ticket workspace:
$TICKET_DIR

Next step:
Open tickets/$TICKET_ID/context.md and fill Goal / Current behavior / Expected behavior.
MSG
