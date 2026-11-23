---
name: refresh
description: Checks if .claude/ docs (CLAUDE.md, rules, skills) are in sync with the current codebase. Identifies drift caused by code changes, new modules, or evolved patterns. Presents diff-style suggestions and applies only what you confirm. Use after significant code changes or when Claude seems out of sync with the project.
allowed-tools: Read, Glob, Grep, Bash, Edit
---

# Claude Docs Refresh

Scan for drift between the current codebase and the existing `.claude/` documentation. Present specific, targeted suggestions. **Apply nothing without confirmation.**

---

## Phase 0 — Verify Setup Exists

Look for the files setup manages: `CLAUDE.md`, `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json`, and the skill directories setup generates (`.claude/skills/deploy/`, `.claude/skills/migrate/`) when git does not track them. Other `.claude/` content — tracked skills, `settings.local.json`, worktrees — does not count. If none of the managed files exists, stop:

> No .claude/ infrastructure found. Run /project-context:setup first.

If only some exist, continue and check those; mention the missing ones in the report.

Also re-check `.gitignore` for `CLAUDE.md` and `.claude/`. If either is missing, add it silently and note it in the final report.
Apply the same per-path rule as setup Phase 0: never ignore a path git tracks (ignoring a tracked file does not untrack it) and note in the report that it was left shared. If `.claude/` is partly tracked, check the untracked paths setup owns — `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json`, and generated skill directories — instead of `.claude/` as a whole.

---

## Phase 1 — Read Existing Docs

Read and internalize:
- `CLAUDE.md`
- `.claude/rules/*.md` (all files)
- `.claude/skills/*/SKILL.md` (all skills)
- `.claude/settings.json`

Read only files that exist. Skip missing files and report them as missing; do not create replacement files during refresh unless a report item proposes one and the user confirms it.

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

For each rules file with `paths:` frontmatter, check that every pattern still matches at least one file (`git ls-files ':(glob)<pattern>' | head -1`; without the `:(glob)` prefix `src/**/*.ts` misses `src/a.ts`, and git does not expand `{a,b}` braces, so check each alternative separately). A pattern that matches nothing means the rule never loads: flag it and propose the pattern that matches where those files live now.

If `CLAUDE.md` still has `@.claude/rules/...` import lines (written by an older setup), flag them for removal: rules in `.claude/rules/` load automatically, and an import loads a path-scoped rule in every session, defeating its `paths:`. Propose replacing them with a one-line `## Rules` list of the rule names in backticks.

For each rules file without `paths:` whose content only applies to part of the tree — typically `testing.md`, `api.md`, `styling.md`, `db.md` or a `<language>.md`, often left unscoped by an older setup — propose `paths:` patterns for where those files live, each checked with `git ls-files ':(glob)<pattern>'`. Without them the rule loads in every session. Rules that apply everywhere (`git.md`, `architecture.md`, `security.md`) stay unscoped. If no pattern reliably covers where a rule applies (e.g. API handlers spread across the tree), do not propose one: setup leaves such rules unscoped on purpose, and proposing a pattern there would repeat on every run.

### 2d. Quality gate drift
Re-read where the repo defines its commands — `package.json` scripts, `Makefile` / `justfile` targets, `.github/workflows/*.yml` `run:` steps, `.pre-commit-config.yaml` — and each module root's toolchain (`go.mod`, `pyproject.toml`, `Cargo.toml`), the same way setup Phase 1 does. Compare against the commands listed in CLAUDE.md's Dev Commands (CLAUDE.md is loaded every session, so that is where the git-commit and structured-bug-fix plugins find them) and any hooks in `.claude/settings.json`.
- Flag commands that have been renamed or removed.
- Flag new quality gate commands not yet in Dev Commands.
- Also check the commands, make targets, scripts and flags that rules and skills tell the reader to run (e.g. a skill step "run `make migrate-clean-dry` first"): flag any that no longer exists.
- Flag a change in where checks run (setup Phase 1, "Where checks run"): Docker files added or removed, the repo's commands moving into or out of containers, or a local toolchain that no longer meets the manifest's version. Propose the matching update to the Dev Commands line and the `<language>.md` "verify before finishing" entry.
- If `.claude/hooks/guard-bash.sh` predates the Docker volume checks (no `check_docker` in it), offer to replace it with the current template, then run setup Phase 5's guard self-check.
- If `.claude/hooks/lint-edited-file.sh` predates the exit-code split (no `rc=$?` in it), it reports a missing linter or a broken config as a code error on every edit: offer to replace it with the current template, keeping its `LINT_CMD` and `LINT_EXTS`. Also flag a `LINT_CMD` that starts with `npx `, `uvx ` or `uv run` (can fetch, install or sync packages when the linter is missing), that runs `ruff check` without `--force-exclude`, or that uses a tool outside setup Phase 1's verified exit-code list, and propose what setup Phase 1 describes.
- If the project still has legacy `.claude/skills/fix/` or `.claude/skills/git-commit/` copies from an older setup, flag them for removal — the plugins replace them.
- If `.claude/settings.json` has an inline hook command that reads `$CLAUDE_TOOL_INPUT` (written by an older setup), flag it: that variable does not exist, so the guard never fires. Propose replacing it with `.claude/hooks/guard-bash.sh` from the setup skill's `templates/hooks/`, and replacing a whole-project `... || true` lint hook with `lint-edited-file.sh`. If the user confirms, the migration must:
  - Remove only the old inline entries, so old and new hooks never both run; keep every other hook entry and key in `settings.json` unchanged. Make targeted edits to those entries; do not re-serialize or re-indent the file, so the rest keeps its original formatting.
  - Install the scripts the same way setup Phase 5 does (including its `jq`/`python3` check), then confirm `settings.json` is valid JSON.
  - Run setup Phase 5's guard self-check (force push → exit 2, `git status` → exit 0) and report the result.

### 2e. Recent fix commits → Key Pitfalls candidates
```bash
git log --oneline -40 --grep="fix"
```
Read the commit messages, and the diff where the message is unclear. Propose a Key Pitfall only when it captures a reusable, non-obvious failure mode that is not already covered by existing project rules. Repeated fixes are supporting evidence, not sufficient justification by themselves.
- Check every rules file, not only Key Pitfalls in `architecture.md`, and compare the constraint, not the wording: if `db.md` already says what a fix commit teaches, do not propose it again.
- A single ordinary fix that a pitfall entry would only restate is not a pitfall.

### 2f. Rules coverage gaps
For each rules file, check if new patterns in the codebase fall outside its current scope:
- New API route directories not matching `api.md` conventions.
- New DB models or tables not covered by `db.md`.
- New auth middleware or endpoint patterns not in `security.md`.
- A language with real code but no `<language>.md` rule (e.g. Go added to a TypeScript repo), or a language rule whose gate commands or conventions no longer match the code.
- New directories whose files a path-scoped rule should cover but its `paths:` patterns miss (e.g. a new `src/routes/` when `api.md` only matches `src/api/**`).

### 2g. Values the reader would act on
Do not mark a file ✓ until this check has run on it. First list every value in `CLAUDE.md`, the rules and the skills that a reader would act on: batch sizes, page sizes, timeouts, retry counts, thresholds, intervals, version limits. Skip numbers in plain description that nobody acts on. Then check each one against the code:
- **Find the code it describes.** If the statement names an identifier, constant, config key or file, read that. If it does not — typically a skill step such as "write in batches of N" — read the existing code that does the same operation (for a migrate skill, the existing migration programs; for a deploy skill, the deploy config).
- **Ask whether following the doc goes wrong**, not whether the numbers are literally compatible. "Import up to 1000 rows per request" when every existing importer sends 200, and a fix commit lowered one to 100, is a mismatch: a reader following it would pick a value the repo does not use or has already reverted. A stated upper limit that the code enforces, or a platform limit stated as one, is a match even when callers use smaller values — "`BulkInsert` accepts at most 1000 rows" is correct if `BulkInsert` enforces 1000.
- **Different values at different call sites are not a mismatch by themselves.** Do not infer a universal rule from existing call sites: compare the operation, the data it handles and any documented rationale (a comment, a fix commit) before flagging. Flag only when the doc gives the reader a value for a case where the code, or a fix commit's reason, shows a different one. When proposing new wording, keep the conditions (e.g. "200 for small records, 50 for records with attachments") rather than one number. Before proposing a replacement value, inspect all relevant implementations of the same operation, including literal values and differently named constants. If coverage is incomplete, do not present a single value as a universal rule.
- **Could not check** — the value comes from an environment variable or runtime config that can override the default, or no code does that operation: list it with the reason and propose no edit. Not being able to verify a value does not make it wrong.

Report each mismatch under Suggested updates with the doc's text and the code evidence (file:line, and the fix commit if one changed the value). Add one count line to the report.

---

## Phase 3 — Present Diff-Style Report → Wait for Confirmation

Classify each finding, but only report it if following the current documentation could cause an incorrect action, an incorrect conclusion, or omission of a necessary step. Tag each reported item **[drift]** (the code changed and the doc is now stale), **[inaccurate]** (the doc contradicts the evidence) or **[gap]** (information needed to act correctly is missing). A list the reader takes as complete — modules, Dev Commands — counts as wrong when it misses an entry. Do not report improvements: equivalent commands, rewording, or optional tools and commands the repo does not use. If the user asks for doc improvements, analyse them separately.

Report each finding once, under the file it concerns; list it under several files only when each of them needs its own edit.

Format the report as below. Show only files with findings. If nothing needs updating, say so and stop.

```
## Refresh Report

### No changes needed
  git.md ✓
  security.md ✓

### Suggested updates

CLAUDE.md
  + [drift] Add module: payments/ (src/payments/ detected — the module list omits it)
  ~ [drift] Update tech stack: Redis detected in package.json — not listed

rules/architecture.md
  ~ [drift] Stale path: src/lib/old-auth.ts no longer exists (referenced on line 14)
  + [gap] Key Pitfall: retried payment requests must reuse the idempotency key, or the
    provider charges twice — fixes abc1234, def5678; not covered by api.md or db.md

rules/db.md
  + [gap] Add: Redis caching pattern (ioredis detected in src/lib/cache.ts)

skills/import/SKILL.md
  ~ [inaccurate] Value: "Import up to 1000 rows per request" — existing importers send 200
    (scripts/import_users.py:28); fix jkl3456 lowered import_orders to 100 after timeouts

Values checked (2g): 7 — 6 match, 1 mismatch
[Could not check: only if any — each value with the reason]

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
```
