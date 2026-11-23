#!/usr/bin/env bash
# PreToolUse(Bash) guard, installed by project-context:setup.
#
# Claude Code passes the tool call as JSON on stdin; the command is at
# .tool_input.command. Exit 2 blocks the call and shows stderr to Claude.
# Exit 0 means "checked and allowed".
#
# This is a safety net against common accidents, not a security boundary: it
# reads the command text, it does not run a shell parser, so commands built at
# run time (eval, variables holding commands, scripts) are not inspected.
#
# Blocks:
#   - recursive rm whose target is / or the home directory
#   - force push that targets main/master, including HEAD or no refspec while
#     main/master is checked out (and when the current branch can't be read)
#   - DROP TABLE / DATABASE / SCHEMA
#   - Docker commands that delete volumes: compose down -v/--volumes,
#     docker volume rm/prune, docker system prune --volumes
#     (a Makefile target that runs them is not inspected)
# If the input can't be parsed, the guard blocks instead of allowing.

fail_closed() {
  echo "guard-bash: could not check this command ($1), so it was blocked. Fix the hook setup (.claude/hooks/guard-bash.sh) or run the command yourself." >&2
  exit 2
}

block() {
  echo "BLOCKED by .claude/hooks/guard-bash.sh: $1" >&2
  exit 2
}

input=$(cat)

if command -v jq >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | jq -er '.tool_input.command | strings' 2>/dev/null) \
    || fail_closed "input is not JSON with a tool_input.command string"
elif command -v python3 >/dev/null 2>&1; then
  cmd=$(printf '%s' "$input" | python3 -c '
import json, sys
try:
    c = json.load(sys.stdin)["tool_input"]["command"]
except Exception:
    sys.exit(1)
if not isinstance(c, str):
    sys.exit(1)
sys.stdout.write(c)
' 2>/dev/null) || fail_closed "input is not JSON with a tool_input.command string"
else
  fail_closed "neither jq nor python3 is installed"
fi

# DROP statements can sit inside quoted SQL, so check the raw text.
if printf '%s' "$cmd" | grep -qiE '(^|[^[:alnum:]_])drop[[:space:]]+(table|database|schema)([^[:alnum:]_]|$)'; then
  block "DROP TABLE/DATABASE/SCHEMA"
fi

# Split into simple commands on ; & | ( ) and newlines, and drop quotes so
# "$HOME" and '/' compare as plain words. Words are never glob-expanded.
segments=$(printf '%s' "$cmd" | tr -d "\"'" | tr ';&|()\n' '\n\n\n\n\n\n')

is_root_or_home() {
  # Root: "/", "//", "/.", "/*" (words are not glob-expanded, so "/*" is literal).
  case "$1" in
    /. | '/*') return 0 ;;
  esac
  [ -n "$1" ] && [ -z "${1//\//}" ] && return 0   # only slashes
  case "$1" in
    "~" | "~/" | "~/*" | '$HOME' | '$HOME/' | '$HOME/*' | '${HOME}' | '${HOME}/' | '${HOME}/*') return 0 ;;
  esac
  [ -n "$HOME" ] && { [ "$1" = "$HOME" ] || [ "$1" = "$HOME/" ] || [ "$1" = "$HOME/*" ]; } && return 0
  return 1
}

current_branch() {
  git -C "${CLAUDE_PROJECT_DIR:-.}" symbolic-ref --quiet --short HEAD 2>/dev/null
}

check_rm() {   # args: words after "rm"
  local recursive=0 opts_done=0 w
  local -a targets=()
  for w in "$@"; do
    if [ $opts_done = 0 ]; then
      case "$w" in
        --) opts_done=1; continue ;;
        --recursive) recursive=1; continue ;;
        --*) continue ;;
        -*) case "$w" in *[rR]*) recursive=1 ;; esac; continue ;;
      esac
    fi
    targets+=("$w")
  done
  [ $recursive = 1 ] || return 0
  for w in "${targets[@]}"; do
    is_root_or_home "$w" && block "recursive delete of / or home directory ($w)"
  done
  return 0
}

check_push() {   # args: words after "push"
  local force=0 all=0 w dst
  local -a pos=()
  for w in "$@"; do
    case "$w" in
      -f | --force | --force-with-lease | --force-with-lease=* | --force-if-includes) force=1 ;;
      --all | --mirror) all=1 ;;
      -*) ;;
      *) pos+=("$w") ;;
    esac
  done
  # pos[0] is the remote, the rest are refspecs.
  local -a refspecs=("${pos[@]:1}")
  for w in "${refspecs[@]}"; do
    case "$w" in +*) force=1 ;; esac
  done
  [ $force = 1 ] || return 0
  [ $all = 1 ] && block "force push of all branches (--all/--mirror)"
  # `git push --force main` names a remote called "main", but it is almost
  # always meant as the branch; treat it as a main/master target.
  case "${pos[0]:-}" in
    main | master) block "force push to ${pos[0]}" ;;
  esac

  local needs_branch=0
  [ ${#refspecs[@]} -eq 0 ] && needs_branch=1
  for w in "${refspecs[@]}"; do
    w=${w#+}
    dst=${w##*:}           # src:dst -> dst; plain name -> itself
    dst=${dst#refs/heads/}
    case "$dst" in
      main | master) block "force push to $dst" ;;
      HEAD | @ ) needs_branch=1 ;;
    esac
  done
  if [ $needs_branch = 1 ]; then
    local b
    b=$(current_branch) || block "force push while the current branch can't be determined"
    case "$b" in
      main | master) block "force push of the checked-out $b branch" ;;
    esac
  fi
  return 0
}

check_docker() {   # args: words after "docker" (or "compose" for docker-compose)
  local w compose=0 down=0 vol=0 volume=0 vrm=0 system=0 prune=0
  for w in "$@"; do
    case "$w" in
      compose) compose=1 ;;
      down) down=1 ;;
      -v | --volumes | --volumes=true) vol=1 ;;
      volume) volume=1 ;;
      rm | remove | prune) [ $volume = 1 ] && vrm=1; [ "$w" = prune ] && prune=1 ;;
      system) system=1 ;;
    esac
  done
  [ $compose = 1 ] && [ $down = 1 ] && [ $vol = 1 ] && block "docker compose down with volumes deletes their data"
  [ $vrm = 1 ] && block "docker volume rm/prune deletes volume data"
  [ $system = 1 ] && [ $prune = 1 ] && [ $vol = 1 ] && block "docker system prune --volumes deletes volume data"
  return 0
}

while IFS= read -r seg; do
  read -r -a words <<< "$seg" || true
  [ ${#words[@]} -gt 0 ] || continue
  i=0
  # Skip env assignments and wrapper commands (sudo, rtk, command, env, time, nohup, exec).
  while [ $i -lt ${#words[@]} ]; do
    case "${words[$i]}" in
      *=*) i=$((i+1)) ;;
      sudo | rtk | command | env | time | nohup | exec) i=$((i+1)) ;;
      *) break ;;
    esac
  done
  prog=${words[$i]:-}
  prog=${prog##*/}   # /bin/rm -> rm
  case "$prog" in
    rm)
      check_rm "${words[@]:$((i+1))}"
      ;;
    docker)
      check_docker "${words[@]:$((i+1))}"
      ;;
    docker-compose)
      check_docker compose "${words[@]:$((i+1))}"
      ;;
    git)
      # Find the "push" subcommand, skipping git's global options (-C dir, -c k=v, --git-dir=...).
      j=$((i+1))
      while [ $j -lt ${#words[@]} ]; do
        case "${words[$j]}" in
          -C | -c) j=$((j+2)) ;;
          -*) j=$((j+1)) ;;
          *) break ;;
        esac
      done
      [ "${words[$j]:-}" = push ] && check_push "${words[@]:$((j+1))}"
      ;;
  esac
done <<< "$segments"

exit 0
