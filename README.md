# my-skills

Private, hand-vetted Claude Code skill marketplace.

This repository is a trusted allow-list for Claude Code plugins and skills. It
keeps the skills you personally approve in one public GitHub repository, so they
can be installed on any machine through Claude Code's plugin marketplace flow.

English is the primary documentation language. A Chinese companion is available
in [README.zh-CN.md](README.zh-CN.md).

## What This Repository Provides

- **Portable installation**: add this marketplace once, then install any listed
  skill from Claude Code without copying files between machines.
- **Controlled admission**: new skills enter `plugins/` only through the local
  vetting workflow in `add-skill.sh`.
- **Static and dynamic checks**: the admission workflow runs a Python auditor,
  an optional no-network Docker sandbox, and a manual `SKILL.md` review.
- **CI protection**: GitHub Actions re-runs the static auditor on every push and
  pull request, and blocks CRITICAL findings.
- **Readable ownership model**: `.claude-plugin/marketplace.json` is the catalog;
  `plugins/<name>/` contains the plugin manifest and skill payload.

## Available Plugins

The current marketplace catalog includes:

| Plugin | Category | Purpose |
| --- | --- | --- |
| `a11y-audit` | quality | Accessibility audit support for WCAG 2.1/2.2 checks. |
| `git-commit` | workflow | Runs quality checks, drafts a Conventional Commits message, and commits staged changes. |
| `setup` | workflow | Initializes and refreshes `.claude/` project infrastructure. |
| `ai-engineering-workspace` | workflow | Ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, and cross-session handoff — four skills, each usable standalone. |
| `system-design-coach` | learning | Supports system design study through roadmaps, drills, and answer review. |

The source of truth for the list is
[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## Install From Claude Code

Add the marketplace once on each machine:

```text
/plugin marketplace add weiwei-tsao/my-skills-marketplace
```

Install a skill:

```text
/plugin install a11y-audit@my-skills
```

Update the marketplace when this repository changes:

```text
/plugin marketplace update
```

This flow assumes the repository is public, because Claude Code fetches the
marketplace from GitHub. Do not store secrets or proprietary private skill
content in this repository.

## Add a New Skill

Use `add-skill.sh` as the only admission path:

```bash
cd my-skills-marketplace
./add-skill.sh /path/to/skill-dir <plugin-name>
```

For example:

```bash
./add-skill.sh ~/Documents/Repositories/plain-dock/.claude/skills/git-commit git-commit
```

The script runs four gates:

1. **Static audit**: `vetting/audit_skill.py` scans for risky patterns and
   Python taint flows. CRITICAL findings stop the process.
2. **Sandbox first run**: `vetting/sandbox_skill.sh` runs the skill in a Docker
   container with networking disabled and logs suspicious access. If Docker is
   unavailable, the script warns loudly and asks before continuing.
3. **Human review**: the script prints the discovered `SKILL.md` for manual
   confirmation.
4. **Admission**: the skill is copied into `plugins/<plugin-name>/`, a minimal
   plugin manifest is generated, and a catalog entry is printed.

After admission, paste the printed entry into the `plugins` array in
`.claude-plugin/marketplace.json`, fill in `description`, `category`, and
`keywords`, then validate and commit:

```bash
claude plugin validate .
git add -A
git commit -m "add <plugin-name> (vetted)"
git push
```

## Marketplace Source Format

For vendored local plugins, each catalog entry must use a relative source path
that starts with `./`:

```json
{
  "name": "git-commit",
  "source": "./plugins/git-commit",
  "version": "0.1.0",
  "description": "Run quality checks and draft a Conventional Commits message, then commit staged changes.",
  "author": { "name": "weiwei-tsao" },
  "category": "workflow",
  "keywords": ["git", "commit", "conventional-commits"]
}
```

Rules that prevent common install failures:

- Use `"source": "./plugins/<name>"`, not `"plugins/<name>"` or `"<name>"`.
- Do not add a top-level `pluginRoot` field.
- Do not add a top-level `strict` field.
- Run `claude plugin validate .` before pushing.

Older Claude Code versions can reject unsupported source shapes with the error:

```text
This plugin uses a source type your version does not support.
```

When that happens, update Claude Code and verify the source path format above.

## Pin an Upstream Skill Instead

If you prefer to reference an upstream repository instead of vendoring a skill,
pin it by commit SHA:

```json
{
  "name": "cool-skill",
  "source": {
    "source": "github",
    "repo": "someone/cool-skill",
    "sha": "<40-character-commit-sha>"
  }
}
```

Use a SHA, not a branch or moving tag. Re-vet the upstream content before
updating the pinned SHA.

## Repository Layout

```text
.claude-plugin/marketplace.json   # marketplace catalog consumed by Claude Code
.github/workflows/vet-skills.yml  # CI static audit gate
CLAUDE.md                         # maintainer guidance for Claude Code
README.md                         # English primary documentation
README.zh-CN.md                   # Chinese companion documentation
add-skill.sh                      # vetting and admission workflow
plugins/<name>/
  .claude-plugin/plugin.json      # plugin manifest
  skills/<name>/SKILL.md          # skill instructions
vetting/
  audit_skill.py                  # static auditor
  taint_python.py                 # Python AST taint analyzer
  sandbox_skill.sh                # Docker sandbox first-run helper
```

## Audit Tool Exit Codes

`vetting/audit_skill.py` returns:

| Code | Meaning | Effect |
| --- | --- | --- |
| `0` | Clean | Continue. |
| `1` | HIGH findings | Warn locally; CI reports a warning. |
| `2` | CRITICAL findings | Stop locally; CI fails. |

Run a manual audit with:

```bash
python3 vetting/audit_skill.py plugins/<name> --no-color
```

Add `--json report.json` if you need a machine-readable report.

## Maintenance Rules

- Keep this public repository free of secrets, tokens, credentials, and private
  company material.
- Admit one skill per commit where practical, with the commit message noting it
  was vetted.
- Re-run the vetting workflow whenever a skill is updated.
- Keep every catalog source path aligned with `plugins/<name>/`.
- Treat a clean audit as "no red flags found", not as proof that a skill is
  safe.
- Remove accidental macOS metadata before committing; `.gitignore` excludes
  `.DS_Store`, but existing files can still appear in a working tree.

## Troubleshooting

**Plugin source type is not supported**

Update Claude Code, then check that the catalog source is exactly
`"./plugins/<name>"`. Remove unsupported `pluginRoot` or `strict` fields, run
`claude plugin validate .`, commit, push, and run `/plugin marketplace update`.

**`git push` fails with permission denied or 403**

The machine may have cached credentials for the wrong GitHub account. Clear the
credential, then authenticate as the repository owner with `gh auth login` or a
Personal Access Token with appropriate repository access.

**`git push` says repository not found**

Create the GitHub repository first, preferably public and empty, then push this
local repository to it.

**The plugin installs, but the skill never triggers**

Review the skill's `SKILL.md` frontmatter. The `description` should clearly say
when the skill should be used, not only what the skill is.

## Security Boundary

This repository reduces risk by combining a private allow-list, static scanning,
sandbox observation, human review, and CI. It does not prove that a skill is
safe. Read unfamiliar skills carefully, especially if they execute scripts,
touch credentials, install dependencies, or require network access.
