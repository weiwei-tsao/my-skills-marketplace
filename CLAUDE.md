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
4. **Admit** — copies into `plugins/<name>/`, generates `plugin.json` (with a `TODO` description), and prints the `marketplace.json` entry to paste in manually.

After the script finishes:
1. Paste the printed JSON entry into `.claude-plugin/marketplace.json` (fill in `description` and `category`), and copy the same `description` into `plugins/<name>/.claude-plugin/plugin.json`.
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
- `3` — stale `reviewed-findings.json` entries, only with `--strict-reviewed` (CI fails the build)

CI (`.github/workflows/vet-skills.yml`) re-audits every plugin under `plugins/*/` on every push and PR. A CRITICAL finding blocks merge.

## Auditing an existing plugin manually

```bash
python3 vetting/audit_skill.py plugins/<name> [--quiet] [--json report.json] [--no-reviewed]
```

`vetting/reviewed-findings.json` lists findings a human has read and judged expected. A finding is downgraded to INFO only when plugin, file, rule, **the full line text and a fingerprint of the 3 lines on each side** match, so editing that line or its surroundings makes it fire again. CRITICAL and `taint-flow` findings are never downgraded. A downgrade means a human judged it expected, not that the risk is gone — new skills from untrusted sources still need a human read, and `reviewed-findings.json` can change in the same PR as the code it covers, so review both together. CI runs with `--strict-reviewed`: a stale entry (exit 3) fails the build. Tests: `python3 -m unittest discover -s vetting -p 'test_*.py'`. Add an entry only after reading the line in context, with a `reason`. `--no-reviewed` shows every finding at full severity. `silent-action` also skips a keyword directly negated ("never silently", "don't X or silently").

## Plugin hooks

A plugin may also ship a `hooks/hooks.json` (Claude Code plugin hook
convention — same schema as the `hooks` object in `~/.claude/settings.json`,
scripts referenced via `${CLAUDE_PLUGIN_ROOT}`). Hooks activate automatically
when the plugin is enabled, with no separate user confirmation, so they get
the same scrutiny as skill content:

- The existing audit command covers hook *scripts*: `vetting/audit_skill.py`
  walks the whole directory passed to it and applies `SCRIPT_RULES` (the
  curl-pipe-to-shell, network-call, destructive-command checks) to every
  script-extension file it finds, including anything under `hooks/` or
  `scripts/`. It does **not** apply those checks to `hooks/hooks.json`
  itself — `.json` files only get the prompt-injection wordlist, not the
  script-danger patterns. A `"command"` string embedded directly in
  `hooks.json` (rather than calling out to a separate script file) is not
  caught by `SCRIPT_RULES`. Always read `hooks.json`'s `command` values by
  hand; prefer keeping real logic in a separate, audited script file rather
  than inlining shell in the manifest.
- A clean static-analysis pass is triage, not proof of safety. Read any new
  or changed hook script by hand before merging, the same way `SKILL.md` gets
  a human read in the `add-skill.sh` pipeline.

## Plugin layout

Each plugin follows this structure:

```
plugins/<name>/
  .claude-plugin/plugin.json   # manifest (name, version, author, license)
  skills/<name>/SKILL.md       # the skill payload
  commands/*.md                # optional: slash commands
  scripts/                     # optional: scripts called by hooks or skills
  hooks/hooks.json             # optional: lifecycle hooks, see "Plugin hooks" above
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
