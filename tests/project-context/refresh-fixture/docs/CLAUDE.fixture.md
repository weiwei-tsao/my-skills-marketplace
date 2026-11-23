# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack
Go 1.25 + Gin API (`apps/api`) · Firebase Firestore · Smarty Street API (CMRA/RDI validation) · chromedp + goquery crawlers
React 19 + TypeScript + Vite + TanStack Query + Tailwind (CDN) SPA (`apps/web`) · pnpm workspace
Docker Compose (api + nginx web) · deploys: Render (API), Vercel (web)

## Project Structure
- `apps/api/cmd/server` — API entrypoint; `cmd/check-*`, `cmd/migrate-*`, `scripts/*` — one-off ops/data-migration programs
- `apps/api/internal/api` — Gin router and HTTP handlers
- `apps/api/internal/platform` — config, Firestore client, Smarty client
- `apps/api/internal/business/crawler` — ATMB scraper + `ipost1` (headless Chrome for Cloudflare)
- `apps/api/internal/business/validation` — Smarty validation, quota, backoff, revalidation
- `apps/api/internal/business/notify` — webhook notifier for finished runs
- `apps/api/internal/repository` — all Firestore access; `pkg/model` shared types
- `apps/web/services/api.ts` — all HTTP calls from the SPA
- `docs/` — ARCHITECTURE.md, CONTAINERIZATION.md, plans

## Dev Commands
```bash
make start                         # API + web locally (start.sh, creates apps/api/.env.local)
pnpm dev:web                       # Vite on :5173
cd apps/api && go run ./cmd/server # API on :8080
cd apps/api && go build ./... && go vet ./... && go test ./...   # API gates
cd apps/api && gofmt -l .          # must print nothing
pnpm build:web                     # web gate (vite build; no lint/tests configured)
make docker-build | docker-up | docker-logs | docker-rebuild-api
make lint-api                      # golangci-lint over apps/api
make help                          # all targets incl. migrate-* and check-*
```
Checks run locally. After changing a Dockerfile, `docker-compose.yml`, `go.mod`/`go.sum` or `pnpm-lock.yaml`, re-check with `make docker-build`; Chromium/chromedp behaviour is only verifiable in Docker (`make docker-up` → `/healthz`). If local Go is missing or < 1.25.3: `docker run --rm -v "$PWD/apps/api":/src -w /src golang:1.25-alpine go test ./...`. Never run `make docker-clean` casually (deletes volumes).

## Architecture Notes
- Three layers: Gin handlers → business services → repositories → Firestore. Crawl writes mailboxes; validation later processes them by `validationStatus`.
- Server exits at startup unless config validates and Firestore ping succeeds; background workers run only with `ENABLE_VALIDATION_WORKERS` / `ENABLE_REVALIDATION_CHECKER`.
- `SMARTY_MOCK=true` avoids spending Smarty credits; Firestore free tier is 50K reads / 20K writes per day.
- `VITE_API_BASE_URL` is baked into the web bundle at build time.
- No API authentication; access is limited only by CORS (`ALLOWED_ORIGINS`).

## Rules
Topic rules in `.claude/rules/` load automatically (path-scoped ones when matching files are opened): `git.md` · `architecture.md` · `api.md` · `testing.md` · `styling.md` · `db.md` · `go.md` · `typescript.md`
Skills: `deploy`, `migrate` (Firestore data migrations).

## My Notes
- Prefer small PRs; ask before touching apps/api/scripts/.
- The internal/platform/http move is mid-review; see team thread.
