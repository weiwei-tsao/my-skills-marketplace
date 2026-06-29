# my-skills — a private, hand-vetted Claude skill marketplace

A single GitHub repo that holds the skills you trust, installable on any machine
with two commands. Every skill in here has passed a vetting pipeline, so the
"convenient everywhere" and "safe" goals are solved by the same structure: a
white-list you control.

## Why this exists

- **Use anywhere**: add the marketplace once per machine, then `/plugin install`
  anything in it. No copying files around, no re-cloning, versioned in git.
- **Safe by construction**: nothing enters `plugins/` until it passes
  `add-skill.sh` (static audit → sandbox first-run → your own read). The repo
  *is* your trusted source.

## One-time setup on each machine

```text
/plugin marketplace add USERNAME/my-skills-marketplace
/plugin install a11y-audit@my-skills
```

Later, to pick up new/updated skills:

```text
/plugin marketplace update
```

To auto-trust this marketplace in a project, add to its `.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "my-skills": { "source": { "source": "github", "repo": "USERNAME/my-skills-marketplace" } }
  }
}
```

## Adding a new skill (the only way in)

```bash
git clone https://github.com/someone/cool-skill /tmp/cool-skill   # never curl|bash
./add-skill.sh /tmp/cool-skill cool-skill
```

`add-skill.sh` will:
1. Run `vetting/audit_skill.py` — CRITICAL findings hard-stop.
2. Run `vetting/sandbox_skill.sh` — no-network container, logs real network +
   file access (skipped with a loud warning if Docker is absent).
3. Show you the SKILL.md to read and confirm.
4. Copy it into `plugins/<name>/` and print the marketplace.json entry to paste.

Then commit and push. CI (`.github/workflows/vet-skills.yml`) re-runs the static
audit on every plugin so nothing compromised lands on `main`.

## Pinning upstream skills instead of vendoring

If you'd rather reference an upstream repo than copy it in, use a plugin entry
that points at it pinned by commit SHA (reproducible even if the branch moves):

```json
{
  "name": "cool-skill",
  "source": { "source": "github", "repo": "someone/cool-skill", "sha": "<40-char-commit-sha>" }
}
```

Pinning by `sha` (not just `ref`) means an upstream force-push or tag move can't
silently change what you install. Re-vet and bump the SHA when you choose to update.

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
.github/workflows/vet-skills.yml  # CI gate
```

## Repo hygiene

- Keep the repo **public** (Claude Code fetches marketplaces from GitHub) but put
  nothing secret in it — it only holds skills you're willing to expose.
- One skill = one commit, with a message noting it was vetted and the date.
- Re-run `add-skill.sh` (or at least the auditor) whenever you bump a skill.

## Limits worth remembering

The vetting tools catch known-bad patterns and observe one sandboxed run. They
don't replace reading the code. Treat a green pipeline as "no red flags found,"
not "proven safe" — especially for skills that fetch dependencies or need network.
