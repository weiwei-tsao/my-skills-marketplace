#!/usr/bin/env python3
"""
audit_skill.py — Static safety auditor for Claude Code skills.

Scans a skill directory BEFORE you install it and flags:
  - Shell/network exfiltration patterns in scripts
  - Secret/credential access (.env, ~/.ssh, env vars, cloud creds)
  - Prompt-injection phrasing in SKILL.md (the skill-specific attack surface)
  - Dangerous frontmatter (allowed-tools: Bash, etc.)
  - Risky install patterns (curl | bash)
  - DATA-FLOW exfiltration in Python scripts via AST taint analysis:
    a value from a sensitive source (os.environ, open('.env'), ~/.ssh ...)
    actually reaching a network/exec sink (requests.post, urlopen, os.system).
    This catches real flows that regex alone would miss, with fewer false
    positives than "any network call" matching.

This is a FIRST-PASS triage tool. A clean report does NOT mean the skill is
safe — it means nothing in these known-bad patterns fired. Always read the
SKILL.md and scripts yourself, and run untrusted skills in a sandbox first.

Usage:
    python3 audit_skill.py /path/to/skill-dir
    python3 audit_skill.py /path/to/skill-dir --json report.json
    python3 audit_skill.py /path/to/skill-dir --quiet     # only HIGH/CRIT

No third-party dependencies. Python 3.8+.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional

# Optional AST taint-analysis layer (taint_python.py sits beside this file).
# If it's missing, the auditor still runs with regex-only analysis.
try:
    from taint_python import analyze_python_source
    _HAVE_TAINT = True
except Exception:
    _HAVE_TAINT = False

# ----------------------------------------------------------------------------
# Severity levels
# ----------------------------------------------------------------------------
CRIT, HIGH, MED, LOW, INFO = "CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"
_RANK = {CRIT: 4, HIGH: 3, MED: 2, LOW: 1, INFO: 0}

# ----------------------------------------------------------------------------
# Pattern definitions.  Each rule: (severity, compiled_regex, label, why)
# Patterns are intentionally broad — false positives are fine, this is triage.
# ----------------------------------------------------------------------------

def _rx(p):
    return re.compile(p, re.IGNORECASE)

# --- patterns to run against script / code files ---------------------------
SCRIPT_RULES = [
    (CRIT, _rx(r"curl[^\n|]*\|\s*(ba)?sh"),
     "pipe-to-shell", "Downloads and executes remote code in one step."),
    (CRIT, _rx(r"wget[^\n|]*\|\s*(ba)?sh"),
     "pipe-to-shell", "Downloads and executes remote code in one step."),
    (CRIT, _rx(r"\beval\s*\(?\s*\$\(.*curl"),
     "eval-remote", "Evaluates content fetched from the network."),
    (HIGH, _rx(r"\b(cat|grep|source|read)\b[^\n]{0,40}\.env\b"),
     "dotenv-access", "Reads a .env file — likely contains secrets."),
    (HIGH, _rx(r"~/\.ssh|/\.ssh/|id_rsa|id_ed25519|authorized_keys"),
     "ssh-access", "Touches SSH private keys / authorized_keys."),
    (HIGH, _rx(r"~/\.aws|AWS_SECRET|AWS_ACCESS_KEY|\.aws/credentials"),
     "aws-creds", "Accesses AWS credentials."),
    (HIGH, _rx(r"(GITHUB_TOKEN|GH_TOKEN|NPM_TOKEN|OPENAI_API_KEY|ANTHROPIC_API_KEY|LLM_API_KEY)"),
     "token-access", "References an API token / secret env var."),
    (HIGH, _rx(r"\bprintenv\b|\benv\s*\|\s*curl|os\.environ.*(post|requests|urllib|http)"),
     "env-exfil", "Reads environment and may send it over the network."),
    (HIGH, _rx(r"(curl|wget|requests\.(post|get)|urllib|fetch|axios|http\.client)"
               r"[^\n]{0,80}(\$\{?[A-Z_]+|os\.environ|process\.env|\.env)"),
     "data-to-net", "Sends local/env data to a network endpoint."),
    (MED,  _rx(r"\b(curl|wget|requests\.(post|get)|urllib\.request|fetch\(|axios|nc\s|netcat)"),
     "network-call", "Makes an outbound network request."),
    (MED,  _rx(r"\bbase64\b\s*(-d|--decode|\()"),
     "base64-decode", "Decodes base64 — sometimes used to hide payloads."),
    (MED,  _rx(r"\b(rm\s+-rf|shred|mkfs|dd\s+if=)"),
     "destructive", "Destructive filesystem command."),
    (MED,  _rx(r"\b(chmod\s+777|chmod\s+\+s|sudo\b)"),
     "priv-escalation", "Permission / privilege change."),
    (LOW,  _rx(r"\b(history|\.bash_history|\.zsh_history)\b"),
     "shell-history", "Reads shell history."),
    (LOW,  _rx(r"\bcrontab\b|/etc/cron|launchctl|systemctl\s+enable"),
     "persistence", "Sets up a scheduled / persistent task."),
]

# --- patterns to run specifically against SKILL.md (prompt-injection) ------
INJECTION_RULES = [
    (CRIT, _rx(r"\b(ignore|disregard|override)\b[^\n]{0,40}\b(previous|prior|above|user|system|instruction)"),
     "instruction-override", "Tries to override prior/user/system instructions."),
    (HIGH, _rx(r"\b(do not|don't|never)\b[^\n]{0,30}\b(tell|inform|mention|show|reveal)\b[^\n]{0,20}\b(user|them)\b"),
     "hide-from-user", "Instructs the model to hide actions from the user."),
    (HIGH, _rx(r"\b(silently|without (asking|telling|confirmation)|no confirmation|secretly|quietly)\b"),
     "silent-action", "Asks for silent / unconfirmed actions."),
    (HIGH, _rx(r"\b(send|post|upload|exfiltrate|forward|transmit)\b[^\n]{0,40}"
               r"(http|url|endpoint|webhook|server|email|@)"),
     "exfil-instruction", "Instructs sending data to an external destination."),
    (HIGH, _rx(r"\b(regardless of|no matter)\b[^\n]{0,30}\b(what (the )?user|instruction)"),
     "unconditional", "Unconditional directive that ignores user intent."),
    (MED,  _rx(r"\b(api[_\s-]?key|password|token|credential|secret)\b"),
     "credential-mention", "Mentions credentials in instructions — review intent."),
    (MED,  _rx(r"\bcurl\b|\bwget\b|https?://(?!github\.com|raw\.githubusercontent|docs\.|anthropic)"),
     "embedded-url", "Embeds a network call / non-obvious URL in instructions."),
    (MED,  _rx(r"\b(base64|rot13|hex decode|decode the following)\b"),
     "obfuscation", "References encoded/obfuscated content."),
]

# --- frontmatter (YAML-ish) checks -----------------------------------------
TOOL_RISK = {
    "bash": HIGH, "shell": HIGH, "write": MED, "edit": MED,
    "execute": HIGH, "run": HIGH, "network": MED,
}

SCRIPT_EXTS = {".sh", ".bash", ".zsh", ".py", ".js", ".ts", ".mjs", ".cjs",
               ".rb", ".pl", ".ps1", ".php", ".go"}
TEXT_EXTS = {".md", ".markdown", ".txt", ".yaml", ".yml", ".json", ".toml"}


@dataclass
class Finding:
    severity: str
    rule: str
    why: str
    file: str
    line: int
    excerpt: str


@dataclass
class Report:
    skill_path: str
    skill_name: Optional[str] = None
    allowed_tools: List[str] = field(default_factory=list)
    files_scanned: int = 0
    findings: List[Finding] = field(default_factory=list)

    def counts(self):
        c = {CRIT: 0, HIGH: 0, MED: 0, LOW: 0, INFO: 0}
        for f in self.findings:
            c[f.severity] += 1
        return c


def _read(path: Path) -> Optional[List[str]]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return None


def _excerpt(line: str, limit: int = 120) -> str:
    s = line.strip()
    return s if len(s) <= limit else s[:limit] + "…"


def parse_frontmatter(lines: List[str]):
    """Pull skill name + allowed-tools out of a SKILL.md YAML frontmatter block."""
    name, tools = None, []
    if not lines or lines[0].strip() != "---":
        return name, tools
    for ln in lines[1:]:
        if ln.strip() == "---":
            break
        m = re.match(r"\s*name\s*:\s*(.+)", ln, re.IGNORECASE)
        if m:
            name = m.group(1).strip().strip('"\'')
        m = re.match(r"\s*allowed[-_]tools\s*:\s*(.+)", ln, re.IGNORECASE)
        if m:
            raw = m.group(1).strip().strip("[]")
            tools = [t.strip().strip('"\'') for t in re.split(r"[,\s]+", raw) if t.strip()]
    return name, tools


def scan_file(path: Path, rel: str, rules) -> List[Finding]:
    findings = []
    lines = _read(path)
    if lines is None:
        return findings
    for i, line in enumerate(lines, 1):
        for sev, rx, label, why in rules:
            if rx.search(line):
                findings.append(Finding(sev, label, why, rel, i, _excerpt(line)))
    return findings


def taint_scan_python(path: Path, rel: str) -> List[Finding]:
    """AST data-flow scan: sensitive source -> network/exec sink. .py only."""
    if not _HAVE_TAINT:
        return []
    try:
        src = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return []
    lines = src.splitlines()
    out = []
    for flow in analyze_python_source(src):
        excerpt = _excerpt(lines[flow.lineno - 1]) if 0 < flow.lineno <= len(lines) else ""
        out.append(Finding(
            CRIT, "taint-flow",
            f"Data from {flow.source} flows into {flow.sink} — likely exfiltration.",
            rel, flow.lineno, excerpt))
    return out


def audit(skill_dir: Path) -> Report:
    rep = Report(skill_path=str(skill_dir))
    if not skill_dir.exists() or not skill_dir.is_dir():
        raise SystemExit(f"Not a directory: {skill_dir}")

    for root, _dirs, files in os.walk(skill_dir):
        for fn in files:
            p = Path(root) / fn
            rel = str(p.relative_to(skill_dir))
            ext = p.suffix.lower()

            is_skill_md = fn.lower() in ("skill.md", "skill.markdown")
            if is_skill_md:
                lines = _read(p) or []
                rep.skill_name, rep.allowed_tools = parse_frontmatter(lines)
                rep.files_scanned += 1
                rep.findings += scan_file(p, rel, INJECTION_RULES)
                # SKILL.md can also embed inline code worth script-scanning
                rep.findings += scan_file(p, rel, SCRIPT_RULES)
            elif ext in SCRIPT_EXTS:
                rep.files_scanned += 1
                rep.findings += scan_file(p, rel, SCRIPT_RULES)
                if ext == ".py":
                    rep.findings += taint_scan_python(p, rel)
            elif ext in TEXT_EXTS:
                rep.files_scanned += 1
                rep.findings += scan_file(p, rel, INJECTION_RULES)

    # frontmatter tool risk -> findings
    for t in rep.allowed_tools:
        sev = TOOL_RISK.get(t.lower())
        if sev:
            rep.findings.append(Finding(
                sev, "allowed-tool", f"Skill grants '{t}' capability.",
                "SKILL.md", 0, f"allowed-tools includes: {t}"))

    rep.findings.sort(key=lambda f: (-_RANK[f.severity], f.file, f.line))
    return rep


# ----------------------------------------------------------------------------
# Output
# ----------------------------------------------------------------------------
_COLOR = {CRIT: "\033[1;91m", HIGH: "\033[91m", MED: "\033[93m",
          LOW: "\033[94m", INFO: "\033[90m"}
_RESET = "\033[0m"


def verdict(counts) -> str:
    if counts[CRIT]:
        return "DO NOT INSTALL — critical patterns found. Manually review before trusting."
    if counts[HIGH] >= 3:
        return "HIGH RISK — multiple sensitive operations. Sandbox-run and read every flagged line."
    if counts[HIGH]:
        return "REVIEW REQUIRED — sensitive operations present. Confirm each is expected."
    if counts[MED]:
        return "CAUTION — nothing critical, but read the flagged lines before installing."
    return "NO KNOWN-BAD PATTERNS — still read SKILL.md yourself; tools catch ~known patterns only."


def print_report(rep: Report, color: bool, min_sev: str):
    counts = rep.counts()
    floor = _RANK[min_sev]

    def c(sev, text):
        return f"{_COLOR[sev]}{text}{_RESET}" if color else text

    print("=" * 70)
    print("CLAUDE SKILL SECURITY AUDIT")
    print("=" * 70)
    print(f"Skill name   : {rep.skill_name or '(unnamed / no frontmatter)'}")
    print(f"Path         : {rep.skill_path}")
    print(f"allowed-tools: {', '.join(rep.allowed_tools) or '(none declared)'}")
    print(f"Files scanned: {rep.files_scanned}")
    print(f"Findings     : "
          + "  ".join(c(s, f"{s} {counts[s]}") for s in (CRIT, HIGH, MED, LOW)))
    print("-" * 70)

    shown = [f for f in rep.findings if _RANK[f.severity] >= floor]
    if not shown:
        print("No findings at or above the selected severity.")
    for f in shown:
        print(f"{c(f.severity, f.severity.ljust(8))} {f.rule:<22} {f.file}:{f.line}")
        print(f"         why: {f.why}")
        print(f"         >>> {f.excerpt}")
    print("-" * 70)
    print("VERDICT: " + verdict(counts))
    print("=" * 70)
    print("Reminder: a clean report is necessary, not sufficient. Read the")
    print("SKILL.md, skim every script, and run untrusted skills in a container")
    print("first (watch network egress + file access) before adding to ~/.claude/skills.")


def main():
    ap = argparse.ArgumentParser(description="Static safety auditor for Claude Code skills.")
    ap.add_argument("skill_dir", help="Path to the skill directory to audit")
    ap.add_argument("--json", metavar="FILE", help="Also write a JSON report to FILE")
    ap.add_argument("--quiet", action="store_true", help="Only print HIGH/CRITICAL findings")
    ap.add_argument("--no-color", action="store_true", help="Disable ANSI colors")
    args = ap.parse_args()

    rep = audit(Path(args.skill_dir).expanduser().resolve())
    min_sev = HIGH if args.quiet else LOW
    color = sys.stdout.isatty() and not args.no_color
    print_report(rep, color, min_sev)

    if args.json:
        payload = asdict(rep)
        payload["counts"] = rep.counts()
        payload["verdict"] = verdict(rep.counts())
        Path(args.json).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nJSON report written to {args.json}")

    counts = rep.counts()
    # exit code: 2 if critical, 1 if any high, else 0 — handy for CI gates
    sys.exit(2 if counts[CRIT] else 1 if counts[HIGH] else 0)


if __name__ == "__main__":
    main()
