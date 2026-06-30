# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A personal, hand-vetted Claude Code skill marketplace. Skills are admitted only through `add-skill.sh`, which runs a three-gate vetting pipeline (static audit → Docker sandbox → human read). The repo _is_ the trusted allow-list.

## Adding a skill

```bash
./add-skill.sh /path/to/skill-dir [plugin-name]
```

The script runs four steps and stops on any failure:
1. **Static audit** (`vetting/audit_skill.py`) — regex + AST taint analysis. Exit code 2 (CRITICAL) = hard stop; exit 1 (HIGH) = prompt to continue.
2. **Sandbox first-run** (`vetting/sandbox_skill.sh`) — Docker container with `--network none`; logs network attempts and sensitive file access. Skipped with a loud warning if Docker is absent.
3. **Human read** — shows `SKILL.md` and asks for confirmation.
4. **Admit** — copies into `plugins/<name>/`, generates `plugin.json`, and prints the `marketplace.json` entry to paste in manually.

After the script finishes:
1. Paste the printed JSON entry into `.claude-plugin/marketplace.json` (fill in `description` and `category`).
2. Validate: `claude plugin validate .`
3. Commit and push: `git add -A && git commit -m "add <name> (vetted)" && git push`

## `marketplace.json` source format — critical

Every plugin entry **must** use `"source": "./plugins/<name>"` (relative path, `./` prefix required). A bare `"<name>"` fails on many Claude Code versions. Do not add `pluginRoot` or `strict` at the top-level metadata — older versions break on these.

Validate locally before pushing: `claude plugin validate .`

## Vetting tool exit codes (for CI)

`vetting/audit_skill.py` returns:
- `0` — clean
- `1` — HIGH findings (CI warns, does not fail)
- `2` — CRITICAL findings (CI fails the build)

CI (`.github/workflows/vet-skills.yml`) re-audits every plugin under `plugins/*/` on every push and PR. A CRITICAL finding blocks merge.

## Auditing an existing plugin manually

```bash
python3 vetting/audit_skill.py plugins/<name> [--quiet] [--json report.json]
```

## Plugin layout

Each plugin follows this structure:

```
plugins/<name>/
  .claude-plugin/plugin.json   # manifest (name, version, author, license)
  skills/<name>/SKILL.md       # the skill payload
```

The root catalog is `.claude-plugin/marketplace.json`.

## Pinning upstream skills (alternative to vendoring)

Instead of copying a skill in, point `source` at a GitHub SHA:

```json
{
  "source": { "source": "github", "repo": "owner/repo", "sha": "<40-char-sha>" }
}
```

Pin by SHA, not branch — re-vet and bump the SHA on updates.
