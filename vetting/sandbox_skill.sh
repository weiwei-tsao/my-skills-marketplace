#!/usr/bin/env bash
#
# sandbox_skill.sh — Run an untrusted Claude skill's scripts inside a
# throwaway Docker container with NO network, while logging every
# attempted outbound connection and every file the scripts read/write.
#
# This is the dynamic counterpart to audit_skill.py (static scan).
# Use both: static scan first, then sandbox first-run.
#
# Usage:
#   ./sandbox_skill.sh /path/to/skill-dir [entry-script]
#
#   /path/to/skill-dir   the skill you want to vet (copied in read-only)
#   [entry-script]       optional: a specific script to run, relative to
#                        the skill dir (e.g. scripts/setup.sh). If omitted,
#                        every *.sh / *.py found is executed in turn.
#
# What it does:
#   - Builds a minimal sandbox image (first run only; cached after).
#   - Runs with --network none so NOTHING can actually leave the machine.
#   - Wraps execution in `strace` to record connect()/openat() syscalls.
#   - Reports: attempted network destinations, files touched outside the
#     skill dir, and the exit status of each script.
#
# Safety notes:
#   - --network none means a malicious curl will FAIL — that's intended.
#     We want to SEE the attempt, not let it succeed.
#   - The skill is mounted read-only; scripts run as an unprivileged user.
#   - Nothing persists: the container is removed on exit (--rm).
#
set -euo pipefail

# ---------------------------------------------------------------------------
SKILL_DIR="${1:-}"
ENTRY="${2:-}"
IMAGE="skill-sandbox:latest"

die() { echo "ERROR: $*" >&2; exit 1; }

[ -n "$SKILL_DIR" ] || die "usage: $0 /path/to/skill-dir [entry-script]"
[ -d "$SKILL_DIR" ] || die "not a directory: $SKILL_DIR"
command -v docker >/dev/null 2>&1 || die "docker not found on PATH"

SKILL_DIR="$(cd "$SKILL_DIR" && pwd)"   # absolute
SKILL_NAME="$(basename "$SKILL_DIR")"

echo "=============================================================="
echo " SKILL SANDBOX FIRST-RUN"
echo "=============================================================="
echo " Skill : $SKILL_NAME"
echo " Path  : $SKILL_DIR"
echo " Net   : DISABLED (--network none) — outbound attempts will be logged but blocked"
echo "--------------------------------------------------------------"

# ---------------------------------------------------------------------------
# 1. Build the sandbox image once (cached afterwards).
# ---------------------------------------------------------------------------
BUILD_CTX="$(mktemp -d)"
trap 'rm -rf "$BUILD_CTX"' EXIT

cat > "$BUILD_CTX/Dockerfile" << 'DOCKER'
FROM python:3.12-slim
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
        strace curl ca-certificates jq \
    && rm -rf /var/lib/apt/lists/*
# unprivileged user; skill runs as this, never root
RUN useradd -m -u 10001 runner
WORKDIR /work
COPY run_inside.sh /usr/local/bin/run_inside.sh
RUN chmod +x /usr/local/bin/run_inside.sh
USER runner
ENTRYPOINT ["/usr/local/bin/run_inside.sh"]
DOCKER

# ---------------------------------------------------------------------------
# 2. The in-container runner: strace each script, then parse the trace.
# ---------------------------------------------------------------------------
cat > "$BUILD_CTX/run_inside.sh" << 'INSIDE'
#!/usr/bin/env bash
set -uo pipefail
ENTRY="${1:-}"
SKILL=/skill
TRACE=/tmp/trace.log
: > "$TRACE"

# Decide which scripts to run.
mapfile -t SCRIPTS < <(
  if [ -n "$ENTRY" ]; then
    echo "$SKILL/$ENTRY"
  else
    find "$SKILL" -type f \( -name '*.sh' -o -name '*.py' \) | sort
  fi
)

if [ "${#SCRIPTS[@]}" -eq 0 ]; then
  echo "[sandbox] no *.sh or *.py scripts found to execute."
fi

run_one() {
  local s="$1" interp
  case "$s" in
    *.py) interp="python3" ;;
    *)    interp="bash" ;;
  esac
  echo ">>> executing: ${s#$SKILL/}"
  # -f follow children, trace network + file-open syscalls only
  strace -f -qq -e trace=connect,openat,open -o "$TRACE.part" \
         "$interp" "$s" </dev/null >/tmp/out.log 2>&1
  local rc=$?
  cat "$TRACE.part" >> "$TRACE" 2>/dev/null || true
  echo "    exit_code=$rc"
  if [ -s /tmp/out.log ]; then
    echo "    --- script output (first 15 lines) ---"
    head -n 15 /tmp/out.log | sed 's/^/    | /'
  fi
}

for s in "${SCRIPTS[@]}"; do
  [ -f "$s" ] && run_one "$s"
done

echo
echo "=============================================================="
echo " OBSERVED BEHAVIOR (from syscall trace)"
echo "=============================================================="

echo "--- Outbound network attempts (connect to non-local addrs) ---"
# pull sin_addr / sin6_addr style entries; drop loopback
grep -E 'connect\(' "$TRACE" 2>/dev/null \
  | grep -Ev '127\.0\.0\.1|::1|AF_UNIX|sun_path' \
  | grep -oE 'inet_addr\("[^"]+"\)|sin6_addr=inet_pton\([^)]+\)|htons\([0-9]+\)' \
  | sort | uniq -c | sort -rn | sed 's/^/  /' \
  || echo "  (none observed)"
[ -z "$(grep -E 'connect\(' "$TRACE" 2>/dev/null | grep -Ev '127\.0\.0\.1|::1|AF_UNIX')" ] \
  && echo "  (no non-local network attempts observed)"

echo
echo "--- Sensitive file access outside the skill dir ---"
grep -E 'openat?\(' "$TRACE" 2>/dev/null \
  | grep -oE '"[^"]+"' \
  | grep -Ev '^"/skill|/usr/|/lib|/proc|/sys|/dev/null|/etc/ld|/tmp/(trace|out)' \
  | grep -E '\.env|\.ssh|\.aws|credential|id_rsa|id_ed25519|\.npmrc|\.git-credentials|/etc/passwd|history|token|secret' \
  | sort | uniq -c | sort -rn | sed 's/^/  /' \
  || echo "  (none observed)"
SENS=$(grep -E 'openat?\(' "$TRACE" 2>/dev/null | grep -oE '"[^"]+"' \
  | grep -E '\.env|\.ssh|\.aws|credential|id_rsa|id_ed25519|\.npmrc|\.git-credentials|/etc/passwd|token|secret' || true)
[ -z "$SENS" ] && echo "  (no sensitive-path access observed)"

echo
echo "--- All distinct files opened outside skill & system dirs ---"
grep -E 'openat?\(' "$TRACE" 2>/dev/null \
  | grep -oE '"[^"]+"' \
  | grep -Ev '^"/skill|/usr/|/lib|/lib64|/proc|/sys|/dev|/etc/(ld|ssl|nsswitch|host|resolv|passwd|group)|/tmp/(trace|out)|^"\."' \
  | sort -u | sed 's/^/  /' | head -n 40 \
  || echo "  (none)"

echo "=============================================================="
INSIDE

# ---------------------------------------------------------------------------
# 3. Build (quietly) and run.
# ---------------------------------------------------------------------------
echo "[*] Building sandbox image (cached after first run)..."
docker build -q -t "$IMAGE" "$BUILD_CTX" >/dev/null || die "image build failed"

echo "[*] Running skill in isolated container..."
echo "--------------------------------------------------------------"

# --network none      : no real egress possible
# --read-only rootfs  : container fs immutable (tmpfs for scratch)
# --cap-drop ALL      : no Linux capabilities
# strace needs ptrace : grant ONLY that one cap back
# skill mounted RO    : scripts cannot modify the source
docker run --rm \
  --network none \
  --cap-drop ALL \
  --cap-add SYS_PTRACE \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp:rw,exec,size=64m \
  --pids-limit 256 \
  --memory 512m \
  -v "$SKILL_DIR":/skill:ro \
  "$IMAGE" "$ENTRY"

echo
echo "=============================================================="
echo " INTERPRETING THIS REPORT"
echo "=============================================================="
cat << 'NOTE'
 - Network attempts to anything other than what the skill OPENLY documents
   are a red flag. (Egress was blocked, so the attempt failed — but a benign
   skill shouldn't be reaching out at all unless it says so.)
 - Any hit under "Sensitive file access" (.env, ~/.ssh, credentials, tokens)
   is a strong red flag — stop and read that script line by line.
 - Clean run + clean static scan (audit_skill.py) + your own read of
   SKILL.md = reasonable confidence. Any one alone is not enough.
NOTE
