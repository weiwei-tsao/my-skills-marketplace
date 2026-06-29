#!/usr/bin/env bash
#
# add-skill.sh — Vet an untrusted skill and, only if it passes, admit it into
# this personal marketplace as a plugin.
#
# Pipeline:
#   1. STATIC   : vetting/audit_skill.py   (regex scan; CRITICAL → hard stop)
#   2. DYNAMIC  : vetting/sandbox_skill.sh (no-network container first-run)*
#   3. HUMAN    : opens SKILL.md for you to read and confirm
#   4. ADMIT    : copies into plugins/<name>/ and adds a marketplace.json entry
#
#   * sandbox step is skipped automatically if Docker isn't available, with a
#     loud warning — never silently.
#
# Usage:
#   ./add-skill.sh <path-to-cloned-skill> [plugin-name]
#
# Example:
#   git clone https://github.com/someone/cool-skill /tmp/cool-skill
#   ./add-skill.sh /tmp/cool-skill cool-skill
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC="${1:-}"
NAME="${2:-}"

c_red(){ printf '\033[91m%s\033[0m\n' "$*"; }
c_grn(){ printf '\033[92m%s\033[0m\n' "$*"; }
c_yel(){ printf '\033[93m%s\033[0m\n' "$*"; }
die(){ c_red "ERROR: $*"; exit 1; }

[ -n "$SRC" ] || die "usage: $0 <path-to-cloned-skill> [plugin-name]"
[ -d "$SRC" ] || die "not a directory: $SRC"
SRC="$(cd "$SRC" && pwd)"

# find the SKILL.md to derive a default name
SKILL_MD="$(find "$SRC" -maxdepth 3 -iname 'SKILL.md' | head -n1 || true)"
[ -n "$SKILL_MD" ] || die "no SKILL.md found under $SRC — is this a skill?"

if [ -z "$NAME" ]; then
  NAME="$(awk -F': *' 'tolower($1) ~ /name/ {print $2; exit}' "$SKILL_MD" \
          | tr -d '"'\''' | tr ' ' '-' | tr '[:upper:]' '[:lower:]')"
  NAME="${NAME:-$(basename "$SRC")}"
fi
c_grn "Vetting skill '$NAME' from $SRC"
echo "=================================================================="

# ---- 1. STATIC SCAN ------------------------------------------------------
echo "[1/4] Static audit (audit_skill.py)…"
set +e
python3 "$HERE/vetting/audit_skill.py" "$SRC" --no-color
RC=$?
set -e
echo
if [ "$RC" -eq 2 ]; then
  die "Static audit found CRITICAL patterns. Refusing to admit. Read the report above."
elif [ "$RC" -eq 1 ]; then
  c_yel "Static audit found HIGH findings. Review them carefully before continuing."
  read -r -p "Continue to sandbox step anyway? [y/N] " a
  [ "$a" = "y" ] || { c_yel "Stopped at your request."; exit 1; }
else
  c_grn "Static audit clean."
fi
echo

# ---- 2. SANDBOX FIRST-RUN ------------------------------------------------
echo "[2/4] Sandbox first-run (sandbox_skill.sh)…"
if command -v docker >/dev/null 2>&1; then
  set +e
  "$HERE/vetting/sandbox_skill.sh" "$SRC"
  set -e
  echo
  read -r -p "Did the sandbox behavior look clean (no surprise network / no credential access)? [y/N] " a
  [ "$a" = "y" ] || die "Sandbox behavior not approved. Refusing to admit."
else
  c_yel "!! Docker not found — SKIPPING dynamic sandbox. This is a real gap."
  c_yel "!! Install Docker and re-run, OR manually read every script before trusting."
  read -r -p "Proceed WITHOUT sandbox verification? [y/N] " a
  [ "$a" = "y" ] || { c_yel "Stopped — good call."; exit 1; }
fi
echo

# ---- 3. HUMAN READ -------------------------------------------------------
echo "[3/4] Human review. Opening SKILL.md — read it fully."
echo "------------------------------------------------------------------"
sed 's/^/  | /' "$SKILL_MD"
echo "------------------------------------------------------------------"
read -r -p "Does the SKILL.md match what the skill claims to do, with no hidden directives? [y/N] " a
[ "$a" = "y" ] || die "Human review not approved. Refusing to admit."
echo

# ---- 4. ADMIT ------------------------------------------------------------
echo "[4/4] Admitting '$NAME' into the marketplace…"
DEST="$HERE/plugins/$NAME"
[ -e "$DEST" ] && die "plugins/$NAME already exists. Pick another name or remove it first."

mkdir -p "$DEST/.claude-plugin" "$DEST/skills/$NAME"
# copy the skill payload (everything from source) under skills/<name>/
cp -R "$SRC"/. "$DEST/skills/$NAME/"
# minimal plugin.json
cat > "$DEST/.claude-plugin/plugin.json" << JSON
{
  "name": "$NAME",
  "version": "0.1.0",
  "description": "Vetted $(date +%Y-%m-%d). Source: $SRC",
  "author": { "name": "Weywey" },
  "license": "MIT"
}
JSON

c_grn "Copied into plugins/$NAME/"
c_yel "Final manual step: add this entry to .claude-plugin/marketplace.json"
cat << JSON
    {
      "name": "$NAME",
      "source": "$NAME",
      "strict": false,
      "version": "0.1.0",
      "description": "TODO: one-line description",
      "author": { "name": "Weywey" },
      "category": "TODO",
      "keywords": []
    }
JSON
echo
c_grn "Then: git add -A && git commit -m \"add $NAME (vetted)\" && git push"
c_grn "On any machine: /plugin marketplace update  →  /plugin install $NAME@my-skills"
