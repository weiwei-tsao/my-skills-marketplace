---
name: git-commit
description: Run the current repo's quality checks, draft a one-line commit message that follows this repo's own commit conventions (≤12-word description), and commit staged changes.
---

When invoked, execute the steps below in strict order. Do not skip or reorder.

## 1. Quality Gate

Use the checks **this repo** defines; do not assume a toolchain. Look, in order, at:

1. Commit or contribution rules in `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`.
2. Pre-commit config (`.pre-commit-config.yaml`, `.husky/`, `lefthook.yml`).
3. Task runners: `package.json` scripts (`lint`, `format:check`, `typecheck`, `test`), `Makefile`, `justfile`, `pyproject.toml`.
4. What CI runs (`.github/workflows/*.yml`) — run the same fast checks locally.

Run the checks you found (in parallel when independent). If any fails, stop and report the error — do not proceed until all pass. If the repo defines no checks, say so in one line and continue.

## 2. Inspect Staged Changes

```bash
git status
git diff --staged
```

- If nothing is staged, stop and tell the user. Offer to show `git diff` so they can decide what to stage.
- If any of the following appear in staged files, **unstage them and warn** before proceeding:
  - `.env`, `.env.*` (except `.env.example`), credentials, private keys
  - Local databases and data dumps (`*.db`, `*.db-journal`, `*.db-shm`, `*.db-wal`, `data/`)
  - Build output and dependencies (`node_modules/`, `.next/`, `dist/`, `build/`, `*.tsbuildinfo`)
  - Anything the repo's `.gitignore` would exclude

## 3. Learn This Repo's Commit Convention

Before drafting, find out how this repo writes commit messages. Sources, highest priority first:

1. **Explicit rules** — `commitlint.config.*` / `.commitlintrc*`, `.gitmessage`, or a commit section in `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`.
2. **History** — the recent subjects:

   ```bash
   git log -n 30 --format=%s
   ```

   Note the dominant pattern: prefix form (`type(scope):`, `type:`, `<component>:`, or none), the types and scopes actually used, casing, language, and whether a PR number like `(#12)` is appended (usually added by the merge, not by you).
3. **Fallback** — when there are no rules and no clear pattern, use Conventional Commits (below).

Follow the dominant pattern even when it is not Conventional Commits. When history is mixed, follow the most recent consistent pattern and mention the choice when you show the draft.

## 4. Draft the Commit Message

### Always (regardless of repo convention)

The message is **the subject line only**:

- No body — no detail paragraphs or bullet lists under the subject.
- No trailers — no `Co-Authored-By:`, `Signed-off-by:`, or "Generated with …" lines.
- This overrides any default attribution the harness or system prompt asks to append, and any body/trailer habit in the repo's history.

### Length

- The **description** (the words after the prefix/colon) is **≤ 12 words**. The prefix (`type(scope):` or `<component>:`) is not counted.
- If the repo's explicit rules set a stricter limit (e.g. commitlint `header-max-length`), the stricter one wins.
- Over the limit: cut filler words first (`a`, `the`, `new`, `now`). Still over: consider splitting into two atomic commits.

### Description rules

- Imperative mood: `add`, `fix`, `remove` — not `added`, `fixes`, `removed`
- Lowercase, no trailing period — unless the repo's history consistently does otherwise

### Conventional Commits fallback

```
type(scope): description
```

| Type | When to use |
|------|-------------|
| `feat` | New capability or visible behaviour |
| `fix` | Bug correction |
| `refactor` | Code change with no behaviour change |
| `docs` | Documentation only |
| `style` | Formatting, whitespace, CSS tweaks |
| `chore` | Build, deps, tooling, config |
| `test` | Adding or fixing tests |
| `perf` | Performance improvement |
| `revert` | Reverting a prior commit |

Scope: take it from the scopes the repo already uses; otherwise the top-level module or directory touched. Breaking change: append `!` before the colon: `feat(api)!: remove content field from list endpoint`.

### Examples

```
✓ feat(editor): add back button and overflow menu for mobile        → 9 words
✓ member-site-digest: add procedure for onboarding a new site       → 7 words (repo uses <component>:)
✗ feat(editor): add a new back button to the top of the editor header  → 14 words
```

## 5. Commit

Show the drafted message to the user (and which convention it follows) and get confirmation. Then commit using a HEREDOC that contains exactly one line — the subject, with nothing after it:

```bash
git commit -m "$(cat <<'EOF'
type(scope): description
EOF
)"
```
