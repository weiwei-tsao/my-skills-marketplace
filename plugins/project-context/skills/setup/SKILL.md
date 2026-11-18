---
name: setup
description: Initializes .claude/ infrastructure for a new project — generates CLAUDE.md, topic-organized rules files, project-specific skills, and hooks configuration. Presents a full plan before creating any files. Use when setting up Claude Code in a repository for the first time.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Project Claude Setup

Initialize a complete `.claude/` development environment tailored to this project's stack. Work through phases in strict order. **Do not create any files before the user confirms the plan in Phase 2** — the only exception is the Phase 0 `.gitignore` update, which runs first.

---

## Phase 0 — Gitignore Check

Read `.gitignore` at the project root (create it if absent). The project context setup writes is local by default, so it should be ignored — but never a path git already tracks: ignoring a tracked file does not untrack it, so the entry would only mislead. Decide per path:

1. **`CLAUDE.md`** — if `git ls-files -- CLAUDE.md` is empty, ensure `CLAUDE.md` is in `.gitignore`. If it is tracked, leave it shared.
2. **`.claude/`** — run `git ls-files -- .claude`:
   - **Nothing tracked** → ensure `.claude/` is in `.gitignore` (the whole directory).
   - **Something tracked** (e.g. a committed `.claude/skills/<name>`) → do **not** ignore `.claude/` as a whole. Instead ensure each path setup owns is ignored, unless git tracks files under it: `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json`. Skill directories setup creates are handled in Phase 4.

Add any missing entries now. Tell the user exactly what was added. This phase runs silently before the plan is presented.

In the plan, say which paths stay shared and why (e.g. "`.claude/skills/travel-planner` is tracked in git — `.claude/` left shared; `.claude/rules/`, `.claude/hooks/`, `.claude/settings.json` ignored").

---

## Phase 1 — Repo Analysis (read-only)

Scan the project. Collect everything needed to fill in the plan. Do not write files.

### Language / runtime
- `package.json` present → Node.js
  - `"typescript"` in deps or `tsconfig.json` → TypeScript
  - `"next"` → Next.js (note App Router if `app/` exists, Pages Router if `pages/`)
  - `"react"` / `"vue"` / `"svelte"` / `"astro"` → frontend framework
  - `"express"` / `"fastify"` / `"hono"` / `"koa"` → Node API server
- `go.mod` → Go
- `requirements.txt` / `pyproject.toml` → Python
- `Cargo.toml` → Rust
- `pom.xml` / `build.gradle` → Java / Kotlin

### Database / ORM
- `prisma/schema.prisma` → Prisma (note provider: sqlite / postgresql / mysql)
- `drizzle.config.*` → Drizzle ORM
- `mongoose` in deps → MongoDB
- `sequelize` / `typeorm` / `knex` → SQL ORM

### Auth
- `next-auth` / `lucia` / `clerk` / `better-auth` in deps → auth library
- `middleware.ts` or `middleware.js` at root → custom auth middleware

### Quality gate commands
Read `package.json` `"scripts"` (or `Makefile` targets). Record the exact command names for:
- Lint: look for `lint`, `eslint`, `biome lint`
- Format check: look for `format:check`, `prettier --check`, `biome format`
- Type check: look for `typecheck`, `type-check`, `tsc --noEmit`
- Test: look for `test`, `jest`, `vitest`, `playwright`

Also record a **per-file lint command** for the edit hook — the linter invoked on a single file, not the project-wide script — and the file extensions it handles. Examples: ESLint → `npx eslint` for `ts tsx js jsx`; Biome → `npx biome lint` for `ts tsx js jsx json`; Ruff → `ruff check` for `py`; golangci-lint → skip (it lints packages, not files). If no linter can run on a single file, record none. The command must be a program plus plain arguments (no quotes, pipes, redirects or `$variables`): the hook splits it on spaces and runs it without a shell.

### Project structure
List top-level directories under `src/` (or root if no `src/`). Note the purpose of each module if inferable from name.

### Existing Claude files
List every file that already exists among the paths setup can write — `CLAUDE.md`, `.claude/rules/*.md`, `.claude/skills/*/`, `.claude/hooks/*`, `.claude/settings.json` — and for each note whether git tracks it (`git ls-files -- <path>`). Do not write anything and do not ask yet: the decision is made in the Phase 2 plan, where each existing file gets an explicit action. Ignore files setup never writes (e.g. `.claude/settings.local.json`).

---

## Phase 2 — Present Full Plan → Wait for Confirmation

Print the plan below. Use actual detected values. Do not create files yet.

```
## Setup Plan

### Gitignore  [already updated in Phase 0]
  [entries added, and which paths stay shared because git tracks them]

### Existing files  [only if Phase 1 found any — otherwise omit this section]
  path                          tracked?  action
  CLAUDE.md                     no        keep        (default for existing files)
  .claude/rules/git.md          no        overwrite   (only if the user agrees)
  .claude/settings.json         no        merge       (add hooks; existing keys untouched)
  .claude/skills/travel-planner yes       keep        (setup never writes it)
  Overwriting a file git tracks changes shared content — say so next to it.

### Rules  (.claude/rules/ — loaded automatically, no @imports)
  git.md          ✓ always · loads every session
  architecture.md ✓ always · loads every session
  api.md          [✓ if API layer detected / — if not] · paths: [detected API globs, or "every session"]
  testing.md      [✓ if test command detected / — if not] · paths: [detected test globs, or "every session"]
  styling.md      [✓ if frontend framework detected / — if not] · paths: [detected style/component globs, or "every session"]
  db.md           [✓ if ORM/DB detected / — if not] · paths: [detected schema/DB globs, or "every session"]
  security.md     [✓ if auth layer detected / — if not] · loads every session

### Skills  (.claude/skills/)
  (not generated: commits → git-commit plugin; bug diagnosis →
   ai-engineering-workspace:structured-bug-fix — they see Dev Commands via CLAUDE.md)
  [deploy/        if CI/CD config detected: .github/workflows/, Dockerfile, fly.toml, vercel.json]
  [migrate/       if DB migration tooling detected]

### Hooks  (.claude/settings.json → scripts in .claude/hooks/)
  PostToolUse(Write,Edit) → lint-edited-file.sh: [per-file lint command + extensions, else "none — no per-file linter found"]
  PreToolUse(Bash)        → guard-bash.sh: block recursive delete of / or ~, force push to main/master, DROP TABLE/DATABASE/SCHEMA

### CLAUDE.md (root, written last)
  Sections: Tech Stack · Project Structure · Dev Commands · Architecture Notes · Rules (names only, no @imports)

Every file below is marked [new], [overwrite] or [merge]; existing files not listed are kept.
No project context files have been created yet (only .gitignore was updated, in Phase 0). Confirm to proceed?
```

Mark each file in the Rules, Skills, Hooks and CLAUDE.md sections as **[new]**, **[overwrite]** or **[merge]**. An existing file defaults to **keep**: only mark it [overwrite] if the user asks for that, and when existing files are present, ask explicitly which (if any) to overwrite as part of the confirmation question — a plain "proceed" keeps them. `.claude/settings.json` is always [merge].

Wait for explicit confirmation before Phase 3. In Phases 3–6, write only files marked [new] or [overwrite], and merge `.claude/settings.json`; never touch a file marked keep.

---

## Phase 3 — Create Rules Files

Create each file confirmed in the plan at `.claude/rules/<name>.md`. Only create files on the confirmed list.

Claude Code loads every `.claude/rules/*.md` file on its own, so nothing imports them. How each file loads depends on its frontmatter:

- **No frontmatter** → loads at the start of every session. Use this for `git.md`, `architecture.md` and `security.md`, which apply across the codebase.
- **`paths:` frontmatter** → loads only when Claude reads or edits a matching file. Use it for `api.md`, `testing.md`, `styling.md` and `db.md`, built from the directories and extensions actually found in Phase 1, for example:

```markdown
---
paths:
  - "src/app/api/**/*.ts"
  - "src/server/**/*.ts"
---
```

Patterns are relative to the project root. Only use globs that match files that exist now: check each with `git ls-files ':(glob)<pattern>' | head` (the `:(glob)` prefix makes `**` match zero or more directories, as Claude Code does; git does not expand `{a,b}` braces, so check each alternative separately). If no reliable pattern exists (e.g. API handlers spread across the tree), leave the file without `paths:` so it loads every session.

### git.md
- Commit message convention: describe the pattern this repo's `git log` already uses (prefix form, types/scopes, casing); only if history has no clear pattern, write Conventional Commits `type(scope): description`
- Commit messages are one subject line, ≤12-word description, imperative mood — no body, no `Co-Authored-By:` or other trailers
- Branch naming convention (e.g. `feat/`, `fix/`, `chore/`)
- What must never be committed: `.env*`, secrets, build artifacts, database files, `node_modules/`
- PR checklist: tests pass, no console.log, no hardcoded values

### architecture.md
- Module boundaries: which directories own which concerns, what must not cross layers
- Data flow: trace a typical request from UI action → API → DB → response using actual file paths detected in Phase 1
- Server/client boundary rules (if applicable)
- Key invariants: serialization steps, auth check points, singleton patterns, edge runtime constraints
- Key Pitfalls: non-obvious gotchas worth remembering (start empty; `/project-context:refresh` proposes entries from recent fix commits)

### api.md *(if API layer detected)*
- Endpoint naming convention and URL structure
- Request/response shape and error format
- Auth mechanism (cookie / Bearer token / API key) and where it's verified
- Status codes in use and their meaning
- Anything that deviates from REST conventions

### testing.md *(if test command detected)*
- What to test: integration/unit split, what is too trivial to test
- Test file naming and co-location convention
- Mock strategy: when to use real DB vs. mock, and why
- How to run a single test file or test case

### styling.md *(if frontend detected)*
- CSS approach (Tailwind / CSS Modules / styled-components / etc.) and any constraints
- Component structure: where styles live relative to components
- Responsive breakpoints and mobile-first vs. desktop-first
- Forbidden patterns (e.g., no inline styles for layout, no `!important`)

### db.md *(if ORM/DB detected)*
- ORM usage patterns and what to avoid (raw queries, N+1, etc.)
- Migration convention: how to create, run, and roll back
- Serialization boundary: when Prisma/ORM objects must be converted before leaving the server
- Connection singleton location and import pattern

### security.md *(if auth detected)*
- Where auth is enforced (middleware, route handler, service layer)
- Protected vs. public paths and how they're distinguished
- Session / token storage and expiry
- Forbidden patterns: hardcoded secrets, client-side auth checks, logging sensitive values

**Each file:** ≤80 lines. Add a one-line cross-reference at the bottom to related files (e.g., `Auth details → see security.md`).

---

## Phase 4 — Create Skills

If Phase 0 found `.claude/` partly tracked, add each skill directory you create here (e.g. `.claude/skills/deploy/`) to `.gitignore` as well, unless git tracks files under it.

Do **not** generate `fix` or `git-commit` skills: those come from installed plugins (`git-commit`, and `ai-engineering-workspace:structured-bug-fix`), which run "the repo's checks"; CLAUDE.md is loaded into every session, so its Dev Commands section is where they find them. Only generate the project-specific skills below when their trigger is detected; if none is, skip this phase.

### deploy skill *(if CI/CD config detected)* — `.claude/skills/deploy/SKILL.md`

```markdown
---
description: Guide through the deployment process for this project — pre-flight checks, trigger deploy, verify. Use when preparing to deploy or release.
---

# Deploy

## Pre-flight
[Insert detected quality gate commands — all must pass]
Check for uncommitted changes: `git status`

## Deploy
[Insert detected deploy method: GitHub Actions workflow trigger, fly.toml → `fly deploy`, vercel.json → `vercel --prod`, Dockerfile → docker build/push]

## Verify
[Describe what a successful deploy looks like for this project]

## Rollback
[Describe rollback procedure if known]
```

### migrate skill *(if DB migration tooling detected)* — `.claude/skills/migrate/SKILL.md`

```markdown
---
description: Create, apply, and roll back database migrations safely. Use when changing the database schema.
---

# Database Migration

## Create
[Insert detected migration command — e.g.: `npx prisma migrate dev --name <description>`]

## Apply (production)
[Insert detected production migration command — e.g.: `npx prisma migrate deploy`]

## Rollback
[Describe rollback procedure for detected ORM]

## Safety checklist
- [ ] Migration is additive where possible (new columns nullable or with defaults)
- [ ] Tested on a copy of production data if the table is large
- [ ] No data-destructive steps without a backup confirmed
```

---

## Phase 5 — Create Hooks Configuration

Hook logic lives in script files, not inline in `settings.json`. Claude Code passes each tool call to a hook as JSON on **stdin** (there is no `$CLAUDE_TOOL_INPUT` variable), and only **exit code 2** blocks a PreToolUse call or feeds a PostToolUse failure back to Claude.

1. Copy the templates from this skill's `templates/hooks/` directory into the project's `.claude/hooks/`, unchanged except for the placeholders below, and make them executable (`chmod +x`):
   - `guard-bash.sh` — always.
   - `lint-edited-file.sh` — only if a per-file lint command was detected in Phase 1. Replace `__LINT_CMD__` with that command (e.g. `npx eslint`) and `__LINT_EXTS__` with its extensions (e.g. `ts tsx js jsx`).
2. Write `.claude/settings.json`. If the file already exists, merge — do not overwrite existing keys.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/lint-edited-file.sh"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/guard-bash.sh"
          }
        ]
      }
    ]
  }
}
```

If no per-file lint command was detected, omit the `PostToolUse` block and `lint-edited-file.sh` entirely.

3. Verify the guard before reporting success — both must hold:

```bash
echo '{"tool_input":{"command":"git push -f origin main"}}' | .claude/hooks/guard-bash.sh; echo $?   # expect 2
echo '{"tool_input":{"command":"git status"}}' | .claude/hooks/guard-bash.sh; echo $?              # expect 0
```

The scripts read JSON with `jq`, falling back to `python3`. The guard **fails closed**: if it cannot parse its input or neither parser is installed, it blocks every Bash command. So before installing it, check `command -v jq || command -v python3`; if both are missing, skip the guard and explain to the user why it was skipped.

When reporting, describe the guard as a safety net against common accidents, not a security boundary: it reads command text, so commands built at run time (`eval`, scripts, variables holding commands) are not inspected.

---

## Phase 6 — Create CLAUDE.md (last)

Write `CLAUDE.md` only after Phases 3–5 are done, so it never points at files that were not written. If any earlier write failed (for example, permission to write under `.claude/` was denied), stop and report what is missing instead of writing `CLAUDE.md`; write it once those files exist.

If `CLAUDE.md` already exists and the plan keeps it, do not write it; mention in the summary that its rules list may need updating (`/project-context:refresh` checks it). Otherwise create `CLAUDE.md` at the project root. Keep it under 60 lines. Only include sections that have real content. Do not add `@` imports of rules files: they are loaded automatically, and an import would load a path-scoped rule in every session. Write rule names in backticks (as below) so they are not read as imports.

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
[one line per detected technology, e.g.: Next.js 15 (App Router) · TypeScript · Prisma (SQLite) · Tailwind CSS]

## Project Structure
[top-level modules with one-line purpose — only what isn't obvious from the name]

## Dev Commands
\`\`\`bash
[exact commands from package.json scripts, only those that exist]
\`\`\`

## Architecture Notes
[data flow summary, key module boundaries, invariants that would surprise a reader — nothing derivable from reading the code]

## Rules
Topic rules in `.claude/rules/` load automatically (path-scoped ones when matching files are opened): [backticked names of the rules files actually written, e.g. `git.md` · `architecture.md` · `api.md`]
```

---

## Phase 7 — Summary

After all files are created, print a summary of what was created:

```
Setup complete.

Created:     [new files]
Overwritten: [files replaced, marking any tracked by git]
Merged:      .claude/settings.json ([keys added])
Kept:        [existing files left as they were]
Guard:       verified (force push → 2, git status → 0)

Keep these docs current: run /project-context:refresh after significant
code changes (new modules, dependency or command changes, a run of fixes).
```

Do not offer or create a scheduled cloud routine for refresh: cloud sessions clone the repo, and `CLAUDE.md` / `.claude/` are gitignored, so a remote run cannot see them.
