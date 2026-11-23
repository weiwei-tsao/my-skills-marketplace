# Git

## Commit messages
- Format used by this repo's history: `type(scope): description`, lowercase, imperative.
  - Types seen: `feat`, `fix`, `docs`, `test`. Scope is optional (`docs: update readme`).
  - Scopes seen: `crawler`, `validation`, `repository`, `frontend`, `containerization`.
  - Examples: `fix(validation): honor quota retry delay`, `fix(crawler): reactivate links that reappear`.
- One subject line, description ≤12 words, imperative mood.
- No body, no `Co-Authored-By:` or other trailers.
- Squash-merge PRs into main; never rebase shared branches.

## Branches
- `feat/<topic>` (e.g. `feat/containerization`, `feat/three-layer-architecture`), `fix/<topic>`, `chore/<topic>`.
- PRs merge into `main`.

## Never commit
- `.env`, `.env.local`, `.env.docker`, any `.env.*.local` (only `.env.docker.example` is tracked).
- `apps/api/service-account.json` or any Firebase / Smarty credentials.
- Build output: `dist/`, compiled `server` binaries, `node_modules/`.
- `CLAUDE.md` and `.claude/` (local-only, gitignored).

## PR checklist
- API gates pass: `cd apps/api && go build ./... && go vet ./... && go test ./...`, `gofmt -l .` prints nothing.
- Web builds: `pnpm build:web`.
- No stray `console.log` in `apps/web`, no debug `log.Printf` left in hot loops.
- No hardcoded credentials, project IDs or API URLs (use env / `config.yaml`).
- Docker files or dependencies changed → `make docker-build` passes.

Architecture → see architecture.md
