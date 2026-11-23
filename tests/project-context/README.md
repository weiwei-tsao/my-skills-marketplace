# project-context tests

Two layers. Results of each run go in the PR that changes the plugin; the
original refresh E2E is recorded in
`docs/superpowers/specs/2026-11-19-project-context-refresh-e2e.md`.

## 1. Lint hook scenarios — runnable, no API calls

    tests/project-context/lint-hook/run-scenarios.sh <work-dir>

Runs setup's `templates/hooks/lint-edited-file.sh` against real ESLint 9.17.0
and Ruff 0.8.4 (installed into `<work-dir>` on the first run; needs node/npm,
uv and python3), feeding stdin JSON the way Claude Code does. 18 scenarios,
each with the expected hook exit; the script exits non-zero if any fails.

| Hook exit | Meaning | Scenarios |
| --- | --- | --- |
| 0 | nothing to report | clean, warning only, ESLint-ignored file, Ruff-excluded file (`--force-exclude`), other extension, path with a space |
| 2 | linter exit 1: findings, fed back to Claude | lint error, syntax error, absolute path |
| 1 | linter failed to run (exit 2 or 127): shown to the user, not blocking | broken or missing config, linter not installed / not on PATH |

Run it whenever the hook template or setup's per-file lint command rules change.

## 2. Refresh fixture — agent runs, ~$0.8 each

A copy of the owner's public repo `weiwei-tsao/virtualbox-non-cmra-verifier`
(Go API + React web app) with planted code drift and planted doc errors. It is
the one exception to "fixture names are invented": the repo is public and the
patches carry no personal data.

    tests/project-context/refresh-fixture/build.sh <dest-dir> [source-clone-or-url]
    tests/project-context/refresh-fixture/run-refresh.sh <dest-dir> <log.jsonl>

`build.sh` clones the source at `e131189` (branch `feat/containerization`),
removes its tracked `CLAUDE.md` / `.claude/` in one commit, applies
`patches/` (10 commits of code drift), then copies `docs/` in as untracked
`CLAUDE.md` + `.claude/`. The docs are stored as `CLAUDE.fixture.md` and
`dot-claude/`: this repo ignores `.claude/`, and a real `CLAUDE.md` here would be
auto-loaded when files in this folder are read.

Put `<dest-dir>` outside Claude Code's temp dir (`/private/tmp/claude-<uid>/…`,
the session scratchpad): Claude Code does not load `CLAUDE.md` or
`.claude/rules/` from there. Refresh reads the files itself, so its results are
not affected, but anything that depends on rules loading is.

Run refresh **3 times** on fresh state (one result says little: what refresh
checks still varies between runs), and check the fixture is unchanged after
each run (`diff -r` against a copy of `docs/`).

### What refresh should report

Planted in code (`patches/`) and stale in the docs:

| Id | Drift | Expected |
| --- | --- | --- |
| D1 | new module `internal/business/notify` (0002) | `[drift]` module list misses it |
| D2 | router moved `internal/platform/http` → `internal/api` (0003) | stale path in `architecture.md` (3 lines) and `testing.md`; `api.md` already updated |
| D3 | `package.json` swaps react-query for zustand, imports unchanged (0004) | reported as a code problem; docs left alone |
| D4 | make target `docker-rebuild-api` → `docker-rebuild` (0005) | `CLAUDE.md` Dev Commands |
| D5 | API tests run in a `golang:1.25-alpine` compose service (0006, 0010) | "where checks run": add `make api-test`, use it as the fallback |
| D6 | two ZIP+4 fixes (0007, 0008) | Key Pitfall candidate; `HashMailboxKey` still hashes the raw ZIP (a real code bug) |
| D7 | 18-line Python helper (0009) | at most a one-line mention; **no** `python.md` |

Planted in the docs (`docs/`):

| Id | Doc says | Code | Expected |
| --- | --- | --- | --- |
| I1 | `make lint-api` | no such target | `[inaccurate]`, remove |
| I2 | scraper flushes every 50 items (`incrementalWriteThreshold`) | 20 in `scraper.go` and `reprocess.go` | `[inaccurate]` value |
| I3 | ZIP normalisation in `pkg/util/zip.go` | no such file | `[inaccurate]` path |
| I4 | migrate skill "Write in batches ≤400 ops" (setup 0.8 output) | migrations use 100; `migrate-validation-fields` uses a literal 50 (fix `0862cc1`) | `[inaccurate]`; the new wording keeps both cases (100 field-only, 50 whole documents with `RawHTML`) |
| U1 | `rules/my-team.md` (user's own): pages use default exports | named exports | flagged, edit only on the user's choice |
| U2 | `CLAUDE.md` "My Notes": router move "mid-review" | already landed | pointed out, not edited unless asked |

Must **not** be reported as wrong:

- `db.md` "batches capped at 400 ops (`BatchUpsert`)": correct, `BatchUpsert`
  enforces 400. A `[gap]` note about the 10 MB payload limit next to it is fine.
- Improvements: equivalent commands, rewording, optional tools.

Also true and acceptable when reported: `CLAUDE.md` "Vite on :5173" vs
`vite.config.ts` port 3000; `git.md` "squash-merge" vs a history of merge
commits; `git.md` types/scopes missing from recent history.

Baselines over the 8 runs from 0.10.0 to 0.11.1: I1–I4, D2, D4 and D5 found in
8/8; D1 in 7/8 (missed by the first 0.10.0 run, before the 0.11.0 rule that a
list read as complete counts as wrong); `db.md` 400 never flagged; I4 wording
keeps both cases in 3/3 runs since 0.11.1; 0 false positives.

## Unchanged repo (no fixture needed)

To check that refresh stays quiet when nothing changed: run setup on a fresh
clone, then refresh straight away. 0.11.0 reported 3 evidence-backed Key Pitfalls
on virtualbox-non-cmra-verifier (0.8.0: 10 items).
