# Architecture

## Modules
- `apps/api` — Go 1.25 + Gin API (module `github.com/weiwei-tsao/virtualbox-verifier/apps/api`).
  - `cmd/server` — entrypoint; wires repos → services → router in `main.go`, starts optional background workers.
  - `cmd/*` (check-*, migrate-*) and `scripts/*` — one-off ops / data-migration programs, each its own `main`.
  - `internal/platform/` — infrastructure: `config` (env + Firestore `system` config), `firestore` client, `http` router (Gin handlers), `smarty` API client.
  - `internal/business/crawler` — ATMB scraping (HTTP fetch + goquery), `crawler/ipost1` (chromedp headless Chrome for Cloudflare), job manager, orchestrator. The scraper flushes to Firestore every 50 items (`incrementalWriteThreshold`).
  - `internal/business/validation` — Smarty validation: quota manager, backoff, batch handler, revalidation checker.
  - `internal/repository` — the only package that talks to Firestore collections.
  - `pkg/model` — shared data types; `pkg/util` — address cleaning, hashing (ZIP normalisation lives in `pkg/util/zip.go`).
- `apps/web` — React 19 + Vite SPA (no router lib: `App.tsx` switches pages by state).
  - `pages/` (Mailboxes, Analytics, Crawler), `components/`, `services/api.ts` (all HTTP calls), `hooks/`, `contexts/`.

## Layering (three-layer architecture)
- HTTP handlers (`internal/platform/http`) → business services (`internal/business/*`) → repositories (`internal/repository`) → Firestore.
- Business packages must not import Gin; handlers must not query Firestore directly (they call repositories/services).
- `validation` depends on repository *interfaces* defined in `validation/service.go`, so tests can use fakes.
- Crawling and validation are separate layers: crawl writes mailboxes, validation later picks them up by `validationStatus`.

## Data flow example — "Run validation" in the dashboard
1. `apps/web/pages/Crawler.tsx` → `api.*` in `apps/web/services/api.ts` → `POST /api/validation/run`.
2. `internal/platform/http/router.go` `runValidation` → `validation.ValidationService` (runs in background, concurrency-locked).
3. Service fetches mailboxes via `MailboxRepository.FetchByValidationStatus`, calls `smarty` client, writes results with `BatchUpsert` / `UpdateValidationStatus`, tracks progress in `validation_runs` via `ValidationRunRepository`.
4. UI polls `GET /api/validation/runs/:runId` / `GET /api/validation/stats` through TanStack Query.

## Invariants
- Startup fails fast: `config.Load()` validation and `firestoreclient.Ping` (5s) must succeed or the server exits.
- Background workers (validation every 5 min, revalidation daily at 02:00) only run when `ENABLE_VALIDATION_WORKERS` / `ENABLE_REVALIDATION_CHECKER` are true.
- Smarty quota is budgeted (daily budget, high/medium priority quotas from Firestore `system` config); respect `QuotaManager` and retry delays.
- `SMARTY_MOCK=true` skips real Smarty calls — use it for local work.
- In Docker, chromedp needs `CHROME_NO_SANDBOX=true` and `CHROME_PATH` (see `crawler/ipost1/client.go`).
- `VITE_API_BASE_URL` is baked in at build time; it must be browser-reachable.
- Reference docs: `docs/ARCHITECTURE.md`, `docs/CONTAINERIZATION.md`.

## Key Pitfalls
<!-- start empty; /project-context:refresh proposes entries from recent fix commits -->

API details → api.md · Firestore → db.md · Go conventions → go.md
