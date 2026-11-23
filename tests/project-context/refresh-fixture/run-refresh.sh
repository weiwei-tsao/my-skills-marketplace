#!/usr/bin/env bash
# Run /project-context:refresh headless on a fixture, using this repo's plugin
# (the installed copy is disabled for this session only), and print the report.
# usage: run-refresh.sh <fixture-dir> <log-file.jsonl>
#
# Needs --permission-mode bypassPermissions to read .claude/ headless; run it only
# on a remote-less fixture copy. Refresh writes nothing until confirmed, so the
# run should leave the fixture unchanged (compare with `diff -r` afterwards).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
PLUGIN=$(cd "$HERE/../../../plugins/project-context" && pwd)
DIR=${1:?usage: run-refresh.sh <fixture-dir> <log-file.jsonl>}
LOG=${2:?usage: run-refresh.sh <fixture-dir> <log-file.jsonl>}
cd "$DIR" || exit 1
claude -p "/project-context:refresh" --plugin-dir "$PLUGIN" \
  --settings '{"enabledPlugins":{"project-context@my-skills":false}}' \
  --permission-mode bypassPermissions --output-format stream-json --verbose \
  < /dev/null > "$LOG"
python3 - "$LOG" <<'PY'
import json, sys
for line in open(sys.argv[1]):
    try:
        e = json.loads(line)
    except ValueError:
        continue
    if e.get("type") == "result":
        print("turns:", e.get("num_turns"), "cost:", e.get("total_cost_usd"))
        print(e.get("result"))
PY
