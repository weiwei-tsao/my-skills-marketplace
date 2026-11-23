#!/usr/bin/env bash
# Rebuild the refresh fixture: virtualbox-non-cmra-verifier at a pinned commit,
# its tracked Claude context removed, the planted code drift applied as commits,
# and the planted docs copied in as untracked CLAUDE.md + .claude/.
#
# usage: build.sh <dest-dir> [source]   (source: a local clone or a git URL)
#
# Put <dest-dir> OUTSIDE Claude Code's temp dir (/private/tmp/claude-<uid>/...,
# i.e. a session scratchpad): Claude Code does not load CLAUDE.md or .claude/rules
# from there.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DEST=${1:?usage: build.sh <dest-dir> [source]}
SRC=${2:-https://github.com/weiwei-tsao/virtualbox-non-cmra-verifier.git}
BASE=e131189   # "fix(crawler): reactivate links that reappear" on branch feat/containerization

[ -e "$DEST" ] && { echo "refusing: $DEST already exists" >&2; exit 1; }
git clone -q "$SRC" "$DEST"
cd "$DEST"
git checkout -q -B fixture "$BASE"
git remote remove origin
G=(git -c user.name=t -c user.email=t@t)
"${G[@]}" rm -rq CLAUDE.md .claude
"${G[@]}" commit -qm "test: remove existing context"
"${G[@]}" am -q "$HERE"/patches/*.patch
cp "$HERE/docs/CLAUDE.fixture.md" CLAUDE.md
cp -R "$HERE/docs/dot-claude" .claude
chmod +x .claude/hooks/*.sh
git log --oneline -1
git status --short --ignored | grep -E 'CLAUDE.md|\.claude' || true
echo "fixture ready: $DEST"
