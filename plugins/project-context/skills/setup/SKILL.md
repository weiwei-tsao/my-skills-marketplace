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
List every manifest git tracks, not just the root: `git ls-files ':(glob)**/package.json' ':(glob)**/go.mod' ':(glob)**/go.work' ':(glob)**/pyproject.toml' ':(glob)**/setup.py' ':(glob)**/setup.cfg' ':(glob)**/requirements*.txt' ':(glob)**/Pipfile' ':(glob)**/Cargo.toml'` (skip vendored and `node_modules` paths). Each manifest's directory is a **module root**: its commands run from there (e.g. `cd apps/api && go test ./...`). A repo with several roots is a monorepo; record each root with its language.

- `package.json` present → Node.js
  - `"typescript"` in deps or `tsconfig.json` → TypeScript
  - `"next"` → Next.js (note App Router if `app/` exists, Pages Router if `pages/`)
  - `"react"` / `"vue"` / `"svelte"` / `"astro"` → frontend framework
  - `"express"` / `"fastify"` / `"hono"` / `"koa"` → Node API server
- `go.mod` → Go (`go.work` → multi-module workspace). Note the Go version, the module path, and the layout in use: `cmd/<name>/` binaries, `internal/` packages, `pkg/`, `testdata/`
- `pyproject.toml` / `setup.py` / `setup.cfg` / `requirements*.txt` / `Pipfile` → Python. Note the package manager from its lock file (`uv.lock`, `poetry.lock`, `Pipfile.lock`) and the Python version (`requires-python`, `.python-version`). Tracked `.py` files with no manifest → a standard-library script project
- `Cargo.toml` → Rust (`[workspace]` → note its `members`). Note the edition and whether `unsafe` appears in the code
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
Repository conventions first: take the commands the repo already uses, from `package.json` `"scripts"`, `Makefile` / `justfile` / `Taskfile.yml` targets, the `run:` steps in `.github/workflows/*.yml`, `.pre-commit-config.yaml`, and the README's development section. Record each command exactly, with the module root it runs from. Then fill gaps from the stack's own toolchain:
- Node: lint (`lint`, `eslint`, `biome lint`), format check (`format:check`, `prettier --check`, `biome format`), type check (`typecheck`, `tsc --noEmit`), test (`test`, `jest`, `vitest`, `playwright`)
- Go: `go build ./...` (compile and type check), `go vet ./...` (static analysis), `go test ./...`, and `gofmt -l .` (format check: it lists unformatted files and exits 0, so it passes only when it prints nothing). Add `golangci-lint run` only if a `.golangci.*` config or a CI step uses it
- Python: the test runner the repo actually uses — `pytest` only if it is configured or installed (`[tool.pytest.ini_options]`, `pytest.ini`, `conftest.py`, a dev dependency), otherwise `python -m unittest` (with the module or `discover` arguments the README or CI uses). Add ruff, flake8, black, mypy or pyright only if configured (`pyproject.toml` `[tool.*]`, `setup.cfg`, `tox.ini`, `.pre-commit-config.yaml`) or listed as a dev dependency
- Rust: `cargo build`, `cargo test`, `cargo clippy -- -D warnings`, `cargo fmt --check` (add `--workspace` in a workspace)

Never present a tool the repo does not have as a required gate; if one would help, list it in the plan as optional.

Also record a **per-file lint command** for the edit hook — the linter invoked on a single file, not the project-wide script — and the file extensions it handles. Examples: ESLint → `npx eslint` for `ts tsx js jsx`; Biome → `npx biome lint` for `ts tsx js jsx json`; Ruff (if configured) → `ruff check` for `py`; Python with no linter → `python3 -m py_compile` for `py` (syntax only — say so in the plan); Rust → `rustfmt --check --edition <edition>` for `rs`; Go → none (`go vet` and golangci-lint work on packages, and `gofmt -l` exits 0 even when a file is unformatted). If no linter can run on a single file, record none. The command must be a program plus plain arguments (no quotes, pipes, redirects or `$variables`): the hook splits it on spaces and runs it without a shell. It always runs locally, never through Docker (starting a container on every edit is too slow); if the linter only exists inside a container, record none.

### Where checks run (local or Docker)
Only if the repo tracks a `Dockerfile*`, `compose.y*ml` / `docker-compose*.y*ml` or `.devcontainer/`; otherwise checks are local and this step is skipped.

1. **Primary environment — follow the repo.** Docker is primary only when the repo's own commands run checks in a container: a Makefile / justfile / `package.json` script or CI `run:` step like `docker compose run --rm <svc> <cmd>` or `docker run … <test cmd>`, a Dockerfile stage named `test` / `ci` that runs tests, or a `.devcontainer/` that the README says to develop in. A Dockerfile or compose file that only builds or starts the app does not make Docker primary. Note the evidence (file and line).
2. **Check what is actually available — run, don't guess:**
   - Local toolchain for each module root: the tool exists and meets the manifest's version — `go version` against `go.mod`'s `go` line, `python3 --version` against `requires-python` / `.python-version`, `node --version` against `engines.node`, `rustc --version` against `rust-version`. For Go, run `GOTOOLCHAIN=local go version` so an older Go does not download the required toolchain during this read-only phase; if `go env GOTOOLCHAIN` is `auto` (the default), record that the local Go will fetch the required version on first use, with the Docker fallback for when that download is blocked.
   - Docker: `docker info` succeeds (daemon running) and `docker compose version` works. Never start, build or pull anything in this phase.
3. **Decide where each kind of check runs:**

   | Check | Where |
   | --- | --- |
   | build, vet/lint, unit tests, format | the primary environment. If it is local but the toolchain is missing or too old, fall back to a throwaway container from the Dockerfile's build-stage base image, e.g. `docker run --rm -v "$PWD":/src -w /src golang:1.25-alpine go test ./...` |
   | runtime-dependent behaviour (CGO, musl vs glibc, system libraries such as Chromium) | Docker — the local OS cannot verify it |
   | after changing a Dockerfile, compose file, or dependencies the image installs | `docker compose build` (or the repo's Makefile target for it) |
   | integration tests needing a database or other service | `docker compose run --rm <svc> <cmd>` |

   When Docker is primary, use the repo's own container commands exactly. Every container command must exit by itself: `docker compose run --rm …`, `docker run --rm …`, or `docker compose up -d` followed by a check — never a foreground `docker compose up`, which never returns. Do not offer `down -v` / `--volumes` or other volume-deleting commands as a gate: they destroy data.
4. Record: the primary environment with its evidence, when a Docker re-check is required (with the exact command), and the fallback command if the local toolchain is missing or too old (with the reason, e.g. "local go1.22 < go.mod 1.25").

### Project structure
List top-level directories under `src/` (or root if no `src/`), and in a monorepo under each module root. Note the purpose of each module if inferable from name.

### Language conventions
For each language with real code (Go, Python, Rust, …), read a few representative files and note the conventions the code actually follows — these feed that language's rules file (Phase 3). Look for: error handling (Go `fmt.Errorf("…: %w", err)` wrapping and sentinel errors; Python exception types and where they are caught; Rust `Result` with `thiserror` / `anyhow`), `context.Context` passing in Go, typing (Python type hints and checker; Go/Rust public API shape), package layout and import rules (Go `internal/`; Python package vs single script; Rust crate/module split), logging, and how tests are organised (table-driven tests and `testdata/` in Go; `unittest` vs `pytest` fixtures in Python; `#[cfg(test)]` modules vs `tests/` in Rust). Record only what you saw, with a file path as evidence.

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

### Checks  [only if Phase 1 found Docker files — otherwise omit this section]
  Checks: [local / Docker] ([evidence]) · Docker: [when a container re-check is required, with the command]
  [Fallback: if the local toolchain is missing or too old — reason + the one-off `docker run --rm …` command]
  (change this line if checks should run elsewhere; the lint hook always runs locally)

### Rules  (.claude/rules/ — loaded automatically, no @imports)
  git.md          ✓ always · loads every session
                  commit format: one subject line, ≤12-word description, imperative — no body, no trailers
                  (plugin default, not from this repo's history — change or drop it here)
  architecture.md ✓ always · loads every session
  api.md          [✓ if API layer detected / — if not] · paths: [detected API globs, or "every session"]
  testing.md      [✓ if test command detected / — if not] · paths: [detected test globs, or "every session"]
  styling.md      [✓ if frontend framework detected / — if not] · paths: [detected style/component globs, or "every session"]
  db.md           [✓ if ORM/DB detected / — if not] · paths: [detected schema/DB globs, or "every session"]
  security.md     [✓ if auth layer detected / — if not] · loads every session
  <lang>.md       [one per language with real code, e.g. go.md / python.md / rust.md] · paths: [that language's files, e.g. "apps/api/**/*.go"]

### Skills  (.claude/skills/)
  (not generated: commits → git-commit plugin; bug diagnosis →
   ai-engineering-workspace:structured-bug-fix — they see Dev Commands via CLAUDE.md)
  [deploy/        if CI/CD config detected: .github/workflows/, Dockerfile, fly.toml, vercel.json]
  [migrate/       if DB migration tooling detected]

### Hooks  (.claude/settings.json → scripts in .claude/hooks/)
  PostToolUse(Write,Edit) → lint-edited-file.sh: [per-file lint command + extensions, else "none — no per-file linter found"]
  PreToolUse(Bash)        → guard-bash.sh: block recursive delete of / or ~, force push to main/master, DROP TABLE/DATABASE/SCHEMA, Docker commands that delete volumes

### Suggestions  [only if any — otherwise omit this section]
  [practices or tools the repo does not use yet but that would help, one line each with why]
  Not repo practice: written only if you confirm, and marked as suggestions in the files.

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

**Repository evidence first** — this applies to every file setup writes: rules, skills (Phase 4) and `CLAUDE.md` (Phase 6). A prescriptive statement — a number or limit (batch size, timeout, retry count, page size), a required or forbidden practice, a step the reader must follow — goes in only if the repo shows it (code, config, a comment, a script, a CI step, a commit) or the user chose it in the plan. Before writing one, find where the repo does it and write the repo's value, not the platform's or library's documented maximum: if every migration batches 100 documents and a fix commit lowered one to 50 because of payload size, write that, not "Firestore allows 500". If the repo does it in more than one way, say so instead of picking one. Generic best practice the repo does not follow is not a convention: leave it out, or list it under Suggestions in the plan and write it only if the user confirms, marked as a suggestion. The bullet lists below are topics to look for, not content to fill in — skip a topic the repo gives no evidence for.

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
- Commit message format as the plan's git.md line settled it: the plugin default (one subject line, ≤12-word description, imperative mood — no body, no `Co-Authored-By:` or other trailers) unless the user changed or dropped it; if dropped, describe only what the history shows (body, trailers) across the whole history, not just the latest commits — if it is mixed, say so (e.g. "the last 7 are subject-only; earlier ones have bodies and `Co-Authored-By:`")
- Branch naming convention (e.g. `feat/`, `fix/`, `chore/`)
- What must never be committed: what `.gitignore` already excludes (env files, secrets, build output, dependencies), as listed there
- PR checklist: the repo's own (PR template, `CONTRIBUTING`) if it has one; otherwise only the gate commands that must pass

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
- How tests are split (unit / integration / e2e) and where each kind lives
- Test file naming and co-location convention
- Mock strategy: when to use real DB vs. mock, and why
- How to run a single test file or test case

### styling.md *(if frontend detected)*
- CSS approach (Tailwind / CSS Modules / styled-components / etc.) and any constraints
- Component structure: where styles live relative to components
- Responsive breakpoints and mobile-first vs. desktop-first
- Forbidden patterns that the code or a lint config enforces (e.g. a stylelint rule), not general style advice

### db.md *(if ORM/DB detected)*
- ORM / client usage patterns the code follows, and what the code, a comment or a fix commit shows to avoid — including write limits (batch sizes) as the code sets them
- Migration convention: how to create, run, and roll back
- Serialization boundary: when Prisma/ORM objects must be converted before leaving the server
- Connection singleton location and import pattern

### security.md *(if auth detected)*
- Where auth is enforced (middleware, route handler, service layer)
- Protected vs. public paths and how they're distinguished
- Session / token storage and expiry
- Forbidden patterns: hardcoded secrets, client-side auth checks, logging sensitive values

### <language>.md *(one per language with real code: `go.md`, `python.md`, `rust.md`, …)*
Scope it with `paths:` to that language's files (e.g. `"apps/api/**/*.go"`, `"**/*.py"`, `"**/*.rs"`). Write only conventions found in Phase 1, each with a file path as evidence — never generic advice the code doesn't follow:
- Verify before finishing: the exact gate commands and the module root they run from (e.g. `cd apps/api && go build ./... && go vet ./... && go test ./...`). If the repo has Docker files, add where the checks run (from the confirmed Checks line), which changes need a Docker re-check and its command (e.g. "after editing `apps/api/Dockerfile`, `docker-compose.yml` or `go.mod`: `make docker-build`"), and the fallback command if the local toolchain is missing
- Error handling convention, and for Go how `context.Context` is passed
- Package / module layout and import rules (e.g. Go `internal/` boundaries, where new `cmd/` programs go)
- Typing conventions (Python hints and checker; Go/Rust exported API shape)
- Test conventions: file naming, table-driven tests / fixtures / `testdata/`, how to run one test (`go test ./pkg/x -run TestName`, `python -m unittest tests.test_x.TestY.test_z`, `pytest path::test`, `cargo test name`)
- Language pitfalls actually seen in this repo (e.g. nil vs empty slice in JSON output, mutable default arguments, `unwrap()` in library code)

Topic rules (`api.md`, `db.md`, `testing.md`) still describe the project's own patterns; put language-wide conventions here instead of repeating them in each.

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
[Checks the repo's own migrations or docs show — dry-run first, backup step, ordering — each with where it comes from]

## Safety checklist (suggested — not yet repo practice)
[Only the items below the user accepted under Suggestions; omit this section if none]
- [ ] Migration is additive where possible (new columns nullable or with defaults)
- [ ] Tested on a copy of production data if the table is large
- [ ] No data-destructive steps without a backup confirmed
```

When the plan includes the migrate skill, list under Suggestions each of the three generic safety items above that the repo shows no evidence for, so the user sees them and decides; an item the repo already practices goes in the first checklist instead.

If the repo has no migration CLI and its migrations are programs or scripts, describe how the existing ones are built and run. Batch sizes, limits, dry-run flags and ordering in these steps come from the existing migrations, not from the database's documented maximums.

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
[If the repo has Docker files: one line saying where checks run (local / Docker), when to re-check in Docker and with which command, and the fallback if the local toolchain is missing]

## Architecture Notes
[data flow summary, key module boundaries, invariants that would surprise a reader — nothing derivable from reading the code]

## Rules
Topic rules in `.claude/rules/` load automatically (path-scoped ones when matching files are opened): [backticked names of the rules files actually written, e.g. `git.md` · `architecture.md` · `api.md`]
```

---

## Phase 7 — Summary

Before the summary, re-read every prescriptive statement you wrote (numbers, limits, required or forbidden practices) and confirm its evidence in the repo. Fix or remove any statement without evidence (a choice the user made in the plan, including an accepted suggestion, counts as evidence), and list what you changed in the summary. This check covers only the files this run wrote ([new] or [overwrite]); never edit a file marked keep — note any doubt about one in the summary instead.

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
