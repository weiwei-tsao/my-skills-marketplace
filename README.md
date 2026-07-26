# my-skills

Private, hand-vetted skills collection for Claude Code and Codex.

This repository is a trusted allow-list for reusable agent skills. It has two
installation paths:

- **Claude Code** installs the approved bundles through the repository's
  `.claude-plugin/` marketplace catalog.
- **Codex** uses the same skill payloads as local filesystem skills by symlinking
  `plugins/*/skills/*` into a Codex skill directory.

The goal is to keep the skills you personally approve in one public GitHub
repository, with clear vetting and update steps for both environments.

English is the primary documentation language. A Chinese companion is available
in [README.zh-CN.md](README.zh-CN.md).

## What This Repository Provides

- **Portable Claude Code installation**: add this marketplace once, then install
  any listed bundle without copying files between machines.
- **Codex local install and update**: link the same skill payloads into Codex's
  local filesystem skill directory for personal use.
- **Controlled admission**: new skills enter `plugins/` only through the local
  vetting workflow in `add-skill.sh`.
- **Static and dynamic checks**: the admission workflow runs a Python auditor,
  an optional no-network Docker sandbox, and a manual `SKILL.md` review.
- **CI protection**: GitHub Actions re-runs the static auditor on every push and
  pull request, and blocks CRITICAL findings.
- **Readable ownership model**: `.claude-plugin/marketplace.json` is the Claude
  Code catalog; `plugins/<name>/` contains the plugin manifest and one or more
  skill payloads that Codex can link directly.

## Available Plugins and Skills

The current catalog includes these plugin bundles. For Claude Code, each row is
installed as a plugin from the marketplace. For Codex, `install-codex-skills.sh`
discovers and links the individual `skills/*` directories inside those bundles.

| Plugin | Category | Purpose |
| --- | --- | --- |
| `a11y-audit` | quality | Accessibility audit support for WCAG 2.1/2.2 checks. |
| `git-commit` | workflow | Runs quality checks, drafts a Conventional Commits message, and commits staged changes. |
| `setup` | workflow | Initializes and refreshes `.claude/` project infrastructure. |
| `ai-engineering-workspace` | workflow | Ticket suite: workspace scaffolding, phase-gated ticket workflow, structured bug fix, and cross-session handoff — four skills, each usable standalone. |
| `system-design-coach` | learning | Supports system design study through roadmaps, drills, and answer review. |
| `weiwei-notes` | writing | Turns discussions, debugging sessions, or ticket analysis into notes/blog articles in Weiwei's writing style. |

The source of truth for the list is
[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json).

## Install Through Claude Code Marketplace

Add the marketplace once on each machine:

```text
/plugin marketplace add weiwei-tsao/my-skills-marketplace
```

Install a plugin bundle:

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

## Install or Update For Codex

Codex can load local filesystem skills from directories such as
`$HOME/.agents/skills` and repository-scoped `.agents/skills` folders. The skill
payloads in this repository already live under `plugins/*/skills/*`, so the
safest local Codex setup is to symlink those payload directories into Codex's
user-level skill directory. The same installer is used for the first install and
for later updates when this repository changes.

Preview the install plan:

```bash
./install-codex-skills.sh
```

Create the symlinks:

```bash
./install-codex-skills.sh --apply
```

Update an existing Codex install after pulling repository changes:

```bash
git pull
./install-codex-skills.sh
./install-codex-skills.sh --apply
```

Install into a different Codex skill scope:

```bash
./install-codex-skills.sh --apply --target /path/to/.agents/skills
```

You can also set `CODEX_SKILLS_DIR` instead of passing `--target`.

The script is intentionally conservative:

- It defaults to a dry run.
- It links skill directories instead of copying them.
- It is idempotent for links that already point to the current repository.
- It does not overwrite existing files, directories, or symlinks that point
  somewhere else.
- It validates that each discovered skill has a simple `name` in `SKILL.md`.
- It does not prune stale links for skills that were removed or renamed; inspect
  and delete those symlinks manually if needed.

After installing, restart Codex or start a new session if the skills do not
appear. In Codex CLI or the IDE extension, run `/skills` or type `$` to mention a
skill explicitly, such as `$weiwei-notes` or `$ticket-workflow`.

If you moved this checkout or cloned it into a new path, existing symlinks may
still point at the old location. The installer will skip those as "already links
elsewhere" so you can inspect them before replacing them.

This is not the same as installing this repository as a Codex plugin
marketplace. The repository currently uses the Claude Code marketplace layout
under `.claude-plugin/`; Codex plugin distribution uses its own plugin manifest
and marketplace structure. Use the symlink installer for local personal use, and
create Codex plugin packaging only when you want marketplace-based distribution.

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

Codex does not need a separate catalog update for vendored skills. Once the
skill is under `plugins/<plugin-name>/skills/<skill-name>/`, re-run
`./install-codex-skills.sh --apply` to link it into the selected Codex skill
directory.

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
install-codex-skills.sh           # symlink installer for Codex local skills
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
