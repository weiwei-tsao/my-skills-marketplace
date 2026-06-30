---
name: refresh
description: Checks if .claude/ docs (CLAUDE.md, rules, skills) are in sync with the current codebase. Identifies drift caused by code changes, new modules, or evolved patterns. Presents diff-style suggestions and applies only what you confirm. Use after significant code changes or when Claude seems out of sync with the project.
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# Claude Docs Refresh

Scan for drift between the current codebase and the existing `.claude/` documentation. Present specific, targeted suggestions. **Apply nothing without confirmation.**

---

## Phase 0 — Verify Setup Exists

Check that `CLAUDE.md` and `.claude/` both exist. If neither is present, stop:

> No .claude/ infrastructure found. Run /setup first.

Also re-check `.gitignore` for `CLAUDE.md` and `.claude/`. If either is missing, add it silently and note it in the final report.

---

## Phase 1 — Read Existing Docs

Read and internalize:
- `CLAUDE.md`
- `.claude/rules/*.md` (all files)
- `.claude/skills/*/SKILL.md` (all skills)
- `.claude/settings.json`

For each file, note what it currently covers — you'll compare this against the live codebase in Phase 2.

---

## Phase 2 — Scan for Drift

Work through each signal below. Collect findings; do not report yet.

### 2a. New or removed modules
Compare the current top-level directory structure under `src/` (or root) against what `CLAUDE.md` and `architecture.md` describe.
- Flag any directory not mentioned in the docs.
- Flag any documented path that no longer exists.

### 2b. Dependency changes
Re-read `package.json` (or `go.mod`, `requirements.txt`, `Cargo.toml`). Compare against what `CLAUDE.md` lists under Tech Stack.
- Flag new major libraries or frameworks not documented.
- Flag removed dependencies still mentioned.
- Pay special attention to: new ORM, new auth library, new test framework, new CSS approach.

### 2c. Stale file path references
Grep all rules and skills files for file paths (patterns like `src/`, `.ts`, `.tsx`, `.go`, `.py`):

```bash
grep -rn "src/" .claude/
```

For each referenced path, verify it still exists. Flag paths that have moved or been deleted.

### 2d. Quality gate drift
Re-read `package.json` scripts (or Makefile). Compare against the commands listed in `.claude/skills/git-commit/SKILL.md` and `.claude/skills/fix/SKILL.md`.
- Flag commands that have been renamed or removed.
- Flag new quality gate commands not yet in skills.

### 2e. Recent fix commits → Key Pitfalls candidates
```bash
git log --oneline -40 --grep="fix"
```
Read the commit messages. For each fix commit, check whether a corresponding entry already exists in `.claude/skills/fix/SKILL.md` under Key Pitfalls.
- Flag patterns that appear 2+ times and are not yet documented.
- Flag any commit message that hints at a non-obvious gotcha (stale closures, serialization, boundary violations, async ordering).

### 2f. Rules coverage gaps
For each rules file, check if new patterns in the codebase fall outside its current scope:
- New API route directories not matching `api.md` conventions.
- New DB models or tables not covered by `db.md`.
- New auth middleware or endpoint patterns not in `security.md`.

---

## Phase 3 — Present Diff-Style Report → Wait for Confirmation

Format the report as below. Show only files with findings. If nothing needs updating, say so and stop.

```
## Refresh Report

### No changes needed
  git.md ✓
  security.md ✓
  skills/git-commit/SKILL.md ✓

### Suggested updates

CLAUDE.md
  + Add module: payments/ (src/payments/ detected — not documented)
  ~ Update tech stack: Redis detected in package.json — not listed

rules/architecture.md
  ~ Stale path: src/lib/old-auth.ts no longer exists (referenced on line 14)

rules/db.md
  + Add: Redis caching pattern (ioredis detected in src/lib/cache.ts)

skills/fix/SKILL.md
  + Key Pitfalls — 3 recent fix commits suggest patterns worth documenting:
    · fix(payments): handle idempotency key collision (abc1234)
    · fix(auth): await params before destructuring route handlers (def5678)
    · fix(db): call serialize() before JSON response (ghi9012)

No files have been changed yet.
Apply all? Or list which items to skip: [all / none / item numbers]
```

Wait for the user's response before Phase 4.

---

## Phase 4 — Apply Selected Updates

For each confirmed item:
- Read the current file first.
- Make the **minimum targeted change**: append a section, fix a stale path, add a pitfall entry.
- Do not rewrite files wholesale.
- Report each change with the file path and a one-line summary of what changed.

After all updates are applied:

```
Refresh complete. [n] files updated.
Next scheduled refresh: [date of next Monday 09:00, if routine is active]
```
