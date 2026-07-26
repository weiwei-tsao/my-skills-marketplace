#!/usr/bin/env bash
#
# Install this marketplace's skill payloads as local Codex filesystem skills.
#
# By default this script is a dry run. Pass --apply to create symlinks under
# $HOME/.agents/skills, or pass --target <dir> to use another Codex skill scope.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${CODEX_SKILLS_DIR:-$HOME/.agents/skills}"
APPLY=0

usage() {
  cat <<'USAGE'
Usage:
  ./install-codex-skills.sh [--apply] [--target DIR]

Options:
  --apply       Create symlinks. Without this flag, only print planned actions.
  --target DIR  Install into DIR instead of $HOME/.agents/skills.
  -h, --help    Show this help.

Codex scans local skills from locations such as:
  - $REPO_ROOT/.agents/skills
  - $HOME/.agents/skills

This script links each plugins/*/skills/* directory into the target directory.
It does not overwrite existing files, directories, or symlinks that point
somewhere else.
USAGE
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      APPLY=1
      shift
      ;;
    --target)
      [ "$#" -ge 2 ] || { echo "ERROR: --target requires a directory" >&2; exit 1; }
      TARGET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

skill_name_from() {
  awk '
    NR == 1 && $0 == "---" { frontmatter = 1; next }
    frontmatter && $0 == "---" { exit }
    frontmatter && $0 ~ /^name:[[:space:]]*/ {
      sub(/^name:[[:space:]]*/, "")
      print
      exit
    }
  ' "$1"
}

if [ ! -d "$HERE/plugins" ]; then
  echo "ERROR: plugins directory not found: $HERE/plugins" >&2
  exit 1
fi

mode="DRY RUN"
if [ "$APPLY" -eq 1 ]; then
  mode="APPLY"
  mkdir -p "$TARGET"
fi

echo "Codex skills install mode: $mode"
echo "Source repo: $HERE"
echo "Target dir: $TARGET"
echo

seen_names=""
found=0
linked=0
skipped=0
failed=0

while IFS= read -r skill_md; do
  found=$((found + 1))
  skill_dir="$(cd "$(dirname "$skill_md")" && pwd)"
  name="$(skill_name_from "$skill_md")"
  name="${name%\"}"
  name="${name#\"}"
  name="${name%\'}"
  name="${name#\'}"

  if [ -z "$name" ]; then
    echo "SKIP: missing name in $skill_md"
    skipped=$((skipped + 1))
    continue
  fi

  case "$name" in
    *[!A-Za-z0-9._-]*)
      echo "SKIP: unsupported skill name '$name' from $skill_md"
      skipped=$((skipped + 1))
      continue
      ;;
  esac

  case "
$seen_names
" in
    *"
$name
"*)
      echo "SKIP: duplicate skill name '$name' at $skill_dir"
      skipped=$((skipped + 1))
      continue
      ;;
  esac
  seen_names="${seen_names}${name}
"

  dest="$TARGET/$name"

  if [ -L "$dest" ]; then
    current="$(readlink "$dest")"
    if [ "$current" = "$skill_dir" ]; then
      echo "OK:   $name already linked -> $skill_dir"
      linked=$((linked + 1))
    else
      echo "SKIP: $name already links elsewhere: $current"
      skipped=$((skipped + 1))
    fi
    continue
  fi

  if [ -e "$dest" ]; then
    echo "SKIP: $name target already exists and is not a symlink: $dest"
    skipped=$((skipped + 1))
    continue
  fi

  if [ "$APPLY" -eq 1 ]; then
    if ln -s "$skill_dir" "$dest"; then
      echo "LINK: $name -> $skill_dir"
      linked=$((linked + 1))
    else
      echo "FAIL: could not link $name -> $skill_dir" >&2
      failed=$((failed + 1))
    fi
  else
    echo "WOULD LINK: $name -> $skill_dir"
    linked=$((linked + 1))
  fi
done < <(find "$HERE/plugins" -path '*/skills/*/SKILL.md' -type f | sort)

echo
echo "Summary: discovered=$found linked_or_planned=$linked skipped=$skipped failed=$failed"

if [ "$failed" -ne 0 ]; then
  exit 1
fi

if [ "$APPLY" -eq 0 ]; then
  echo "Dry run only. Re-run with --apply to create symlinks."
else
  echo "Restart Codex or start a new session if the new skills do not appear."
fi
