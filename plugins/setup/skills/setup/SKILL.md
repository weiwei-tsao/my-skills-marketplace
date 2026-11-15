---
name: setup
description: Initializes .claude/ infrastructure for a new project — generates CLAUDE.md, topic-organized rules files, project-specific skills, and hooks configuration. Presents a full plan before creating any files. Use when setting up Claude Code in a repository for the first time.
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Project Claude Setup

Initialize a complete `.claude/` development environment tailored to this project's stack. Work through phases in strict order. **Do not create any files before the user confirms the plan in Phase 2** — the only exception is the Phase 0 `.gitignore` update, which runs first.

---

## Phase 0 — Gitignore Check

Read `.gitignore` at the project root (create it if absent). Verify these two entries exist:

```
CLAUDE.md
.claude/
```

Add any missing entries now. Tell the user exactly what was added. This phase runs silently before the plan is presented.

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

### Project structure
List top-level directories under `src/` (or root if no `src/`). Note the purpose of each module if inferable from name.

### Existing Claude files
Check for `CLAUDE.md` at root and `.claude/` directory. If either exists, flag it and ask the user whether to overwrite or skip before continuing.

---

## Phase 2 — Present Full Plan → Wait for Confirmation

Print the plan below. Use actual detected values. Do not create files yet.

```
## Setup Plan

### Gitignore  [already updated in Phase 0]

### CLAUDE.md (root)
  Sections: Tech Stack · Project Structure · Dev Commands · Architecture Notes
  @imports: [list each rules file that will be created]

### Rules  (.claude/rules/)
  git.md          ✓ always
  architecture.md ✓ always
  api.md          [✓ if API layer detected / — if not]
  testing.md      [✓ if test command detected / — if not]
  styling.md      [✓ if frontend framework detected / — if not]
  db.md           [✓ if ORM/DB detected / — if not]
  security.md     [✓ if auth layer detected / — if not]

### Skills  (.claude/skills/)
  (not generated: commits → git-commit plugin; bug diagnosis →
   ai-engineering-workspace:structured-bug-fix — they see Dev Commands via CLAUDE.md)
  [deploy/        if CI/CD config detected: .github/workflows/, Dockerfile, fly.toml, vercel.json]
  [migrate/       if DB migration tooling detected]

### Hooks  (.claude/settings.json)
  PostToolUse(Write,Edit) → [lint command if detected, else "none — no lint command found"]
  PreToolUse(Bash)        → block: rm -rf /, force push to main, DROP TABLE/DATABASE

### Refresh routine
  Will offer a weekly scheduled check after setup completes.

No files have been created yet. Confirm to proceed?
```

Wait for explicit confirmation before Phase 3.

---

## Phase 3 — Create CLAUDE.md

Create `CLAUDE.md` at the project root. Keep it under 60 lines. Only include sections that have real content.

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

@.claude/rules/git.md
@.claude/rules/architecture.md
[one line per additional rules file being created]
```

---

## Phase 4 — Create Rules Files

Create each file confirmed in the plan at `.claude/rules/<name>.md`. Only create files on the confirmed list.

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
- Key Pitfalls: non-obvious gotchas worth remembering (start empty; `/refresh` proposes entries from recent fix commits)

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

## Phase 5 — Create Skills

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

## Phase 6 — Create Hooks Configuration

Write `.claude/settings.json`. If the file already exists, merge — do not overwrite existing keys.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "[detected lint command, e.g. npm run lint] || true"
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
            "command": "echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'rm -rf /|git push --force[[:space:]]+main|git push -f[[:space:]]+main|DROP TABLE|DROP DATABASE' && echo 'BLOCKED: dangerous command' >&2 && exit 1 || exit 0"
          }
        ]
      }
    ]
  }
}
```

If no quality gate command was detected, omit the `PostToolUse` block entirely.

---

## Phase 7 — Offer Refresh Routine

After all files are created, print a summary of what was created, then ask:

```
Setup complete.

Created:
  ✓ CLAUDE.md
  ✓ .claude/rules/ ([n] files)
  ✓ .claude/skills/ ([n] skills)
  ✓ .claude/settings.json

Would you like a weekly scheduled check (every Monday 09:00) that scans
for doc drift and sends a push notification with suggested updates?
Requires Claude Code Remote (CCR). [y/N]
```

If yes, create a trigger:
- `cron_expression`: `0 9 * * 1`
- `name`: `claude-docs-refresh`
- `prompt`: `Run /refresh to check if .claude/ documentation is in sync with the current codebase and suggest any needed updates.`
- `create_new_session_on_fire`: false
- `notifications`: `{ "push": true }`
