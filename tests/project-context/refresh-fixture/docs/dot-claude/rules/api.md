---
paths:
  - "apps/api/internal/api/**/*.go"
  - "apps/web/services/**/*.ts"
  - "apps/web/hooks/**/*.ts"
---
# API

## Routes (`apps/api/internal/api/router.go`)
- `GET /healthz` → `{"status":"ok"}` (Docker healthcheck depends on it).
- Everything else under `/api`, resource-first, lowercase, slash-separated:
  `/api/mailboxes`, `/api/mailboxes/export`, `/api/stats`, `/api/stats/refresh`,
  `/api/crawl/run|reprocess|status|runs`, `/api/crawl/runs/:runId/cancel`, `/api/crawl/ipost1/run`,
  `/api/validation/run|stats|runs`, `/api/validation/runs/:runId`, `/api/validation/revalidation/check`.
- Actions are `POST` verbs on a sub-path (`/run`, `/refresh`, `/cancel`) rather than REST resources.
- New routes: add to the `api` group in `NewRouter` and a `(r *Router)` handler method in the same package.

## Request / response
- Query params are camelCase (`page`, `pageSize`, `active`, `state`, `cmra`, `rdi`, `source`); parsed with `c.DefaultQuery` + `strconv`.
- JSON bodies use the model's `json` tags (camelCase) from `pkg/model/model.go`.
- List responses wrap arrays in `items`: `/api/mailboxes` → `{ items, total, page, ... }`; run lists → `{ items }`.
- Errors: `c.JSON(status, gin.H{"error": "<context>: " + err.Error()})`.
- Status codes in use: 200, 400 (bad params), 500 (repo/service failure), 503 (`validationSvc` / `revalidationChk` not configured). Preflight `OPTIONS` → 204.
- CSV export sets `Content-Disposition` (exposed via CORS).

## Auth / CORS
- No authentication. CORS allow-list comes from `ALLOWED_ORIGINS` (comma-separated, `*` allowed) in `corsMiddleware`.

## Frontend client
- All calls go through `request()` in `apps/web/services/api.ts`; base URL `import.meta.env.VITE_API_BASE_URL` (default `http://localhost:8080`).
- `request()` throws `Error(text)` on non-2xx; `api.*` maps raw API JSON to `types.ts` shapes (e.g. `addressRaw.street` → `street`). Keep mapping there, not in components.
- `hooks/useCSVExport.ts` also reads `VITE_API_BASE_URL`.

Layering → architecture.md · Handler tests → testing.md
