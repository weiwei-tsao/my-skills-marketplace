# my-skills — a private, hand-vetted Claude skill marketplace

A single GitHub repo that holds the skills you trust, installable on any machine
with two commands. Every skill in here has passed a vetting pipeline, so the
"convenient everywhere" and "safe" goals are solved by the same structure: a
white-list you control.

## Why this exists

- **Use anywhere**: register the marketplace once per machine, then
  `/plugin install` anything in it. No copying files around, no re-cloning,
  versioned in git.
- **Safe by construction**: nothing enters `plugins/` until it passes
  `add-skill.sh` (static audit → sandbox first-run → your own read). The repo
  _is_ your trusted source.

---

## One-time setup on each machine

In Claude Code:

```text
/plugin marketplace add weiwei-tsao/my-skills-marketplace
/plugin install a11y-audit@my-skills
```

Later, to pick up new or updated skills:

```text
/plugin marketplace update
```

This works on any machine — your laptop, a work computer — with no GitHub
account configured locally, as long as the repo is **public**.

---

## Adding a new skill (the only way in)

A skill can live anywhere on disk — the default `~/.claude/skills/`, or inside a
project like `some-project/.claude/skills/<name>/`. Point the vetting pipeline at
whatever directory contains its `SKILL.md`.

```bash
cd my-skills-marketplace
./add-skill.sh /path/to/the/skill <plugin-name>
```

For example, vetting a skill that lives inside another project:

```bash
./add-skill.sh ~/Documents/Repositories/plain-dock/.claude/skills/git-commit git-commit
```

`add-skill.sh` will:

1. Run `vetting/audit_skill.py` (regex + AST taint analysis) — CRITICAL findings
   or any taint flow hard-stop.
2. Run `vetting/sandbox_skill.sh` — no-network container, logs real network +
   credential-file access (skipped with a loud warning if Docker is absent).
3. Show you the `SKILL.md` to read and confirm.
4. Copy it into `plugins/<plugin-name>/` and **print a marketplace.json entry**.

Then paste that printed entry into the `plugins` array in
`.claude-plugin/marketplace.json`, fill in `description` and `category`,
**validate**, and push:

```bash
claude plugin validate .                 # catches JSON / format errors locally
git add -A
git commit -m "add <plugin-name> (vetted)"
git push
```

On any other machine: `/plugin marketplace update` then
`/plugin install <plugin-name>@my-skills`.

> For a skill you wrote yourself and already trust, the sandbox step is optional
> — but still run the static auditor; it catches accidentally hard-coded tokens
> or stray network calls.

---

## The plugin `source` format (read this — it's the #1 install failure)

Each entry's `source` must be a **relative path that starts with `./`**:

```json
{
  "name": "git-commit",
  "source": "./plugins/git-commit",
  "version": "0.1.0",
  "description": "…",
  "author": { "name": "weiwei-tsao" },
  "category": "workflow",
  "keywords": ["git", "commit"]
}
```

Rules that matter:

- **Always** write `"source": "./plugins/<name>"`. A bare `"<name>"` (no `./`)
  fails on many Claude Code versions with _"This plugin uses a source type your
  version does not support."_
- **Do not** add a top-level `pluginRoot` in `metadata`, and **do not** add a
  `strict` field — older versions choke on these.
- Relative-path sources only resolve when the marketplace is added **via Git**
  (`owner/repo`), which is exactly how you add this one. (Adding a marketplace by
  a direct URL to the JSON file would NOT download the plugin dirs — avoid that.)

Always run `claude plugin validate .` before pushing; it reports format problems
in seconds instead of after a failed install.

---

## Pinning upstream skills instead of vendoring

If you'd rather reference an upstream repo than copy it in, point `source` at it
pinned by commit SHA (reproducible even if the branch moves):

```json
{
  "name": "cool-skill",
  "source": {
    "source": "github",
    "repo": "someone/cool-skill",
    "sha": "<40-char-commit-sha>"
  }
}
```

Pinning by `sha` (not just a branch ref) means an upstream force-push or tag move
can't silently change what you install. Re-vet and bump the SHA when you update.

---

## Layout

```
.claude-plugin/marketplace.json   # the catalog (what /plugin sees)
plugins/<name>/
  .claude-plugin/plugin.json      # per-plugin manifest
  skills/<name>/SKILL.md          # the skill itself
vetting/
  audit_skill.py                  # static auditor (regex + AST taint analysis)
  taint_python.py                 # AST data-flow engine used by the auditor
  sandbox_skill.sh                # docker sandbox first-run
add-skill.sh                      # the vetting + admit pipeline
.github/workflows/vet-skills.yml  # CI gate (re-audits every plugin on push)
```

---

## Troubleshooting

**"This plugin uses a source type your Claude Code version does not support."**
Two causes: (a) Claude Code is outdated — run `claude update` and check
`claude --version`; (b) the `source` is the wrong format — it must be
`"./plugins/<name>"`, with no `pluginRoot` or `strict` fields. Fix, run
`claude plugin validate .`, commit, push, then `/plugin marketplace update`.

**`git push` → "Permission denied to <other-account>" / 403.**
Your machine has cached credentials for the wrong GitHub account. Clear them
(macOS: `git credential-osxkeychain erase`, or delete the `github.com` entry in
Keychain Access) and re-authenticate as the repo owner. GitHub no longer accepts
account passwords for git — use a Personal Access Token (Settings → Developer
settings → Tokens, `repo` scope) as the password, or `gh auth login`.

**`git push` → "Repository not found."**
The repo doesn't exist on GitHub yet. Create an empty **public** repo (no README/
license) at github.com/new, then push.

**Plugin installs but the skill never triggers.**
The skill activates from its `SKILL.md` frontmatter `description`. Make the
description say _when_ to use it ("Use when reviewing code / writing commits…").

---

## Repo hygiene

- Keep the repo **public** (Claude Code fetches marketplaces from GitHub) but put
  nothing secret in it — it only holds skills you're willing to expose. For
  company-proprietary skills, use a separate **private** marketplace repo instead.
- On macOS, don't commit `.DS_Store` (the `.gitignore` already excludes it;
  `find . -name .DS_Store -delete` before a commit if any slipped in).
- One skill = one commit, message noting it was vetted and the date.
- Re-run `add-skill.sh` (or at least the auditor) whenever you bump a skill.

---

## Limits worth remembering

The vetting tools catch known-bad patterns and observe one sandboxed run. They
don't replace reading the code. Treat a green pipeline as "no red flags found,"
not "proven safe" — especially for skills that fetch dependencies or need network.
