#!/usr/bin/env bash
set -euo pipefail

TICKET_ID="${1:-}"

if [[ -z "$TICKET_ID" ]]; then
  echo "Usage: ./scripts/update-handoff-prompt.sh PUB-11743"
  exit 1
fi

cat <<EOF2
Update tickets/$TICKET_ID/handoff.md so a fresh AI session can continue safely.

Include:
- current status
- completed work
- current repo and branch
- changed files
- current diff summary
- tests run and results
- UAT / acceptance / deploy status
- blockers
- next steps
- do-not-do notes

Also update these files if needed:
- tickets/$TICKET_ID/investigation.md
- tickets/$TICKET_ID/implementation.md
- tickets/$TICKET_ID/test.md
- tickets/$TICKET_ID/pr.md
- tickets/$TICKET_ID/timeline.md

Keep it concise but specific. Include file paths and decisions. Link instead of pasting large content.
EOF2
