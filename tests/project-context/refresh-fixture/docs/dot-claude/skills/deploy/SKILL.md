---
description: Guide through the deployment process for this project — pre-flight checks, trigger deploy, verify. Use when preparing to deploy or release.
---

# Deploy

Targets: backend on Render (Go), frontend on Vercel (static Vite build), database Firebase Firestore. Docker Compose is the self-hosted alternative. There is no CI workflow; deploys are manual/platform-triggered.

## Pre-flight
All must pass:
```bash
cd apps/api && go build ./... && go vet ./... && go test ./...
cd apps/api && gofmt -l .          # must print nothing
pnpm build:web                      # from repo root
git status                          # no uncommitted changes
```
If Dockerfiles, `docker-compose.yml`, `go.mod`/`go.sum` or `pnpm-lock.yaml` changed: `make docker-build`.
If a release needs a new Firestore composite index, deploy `apps/api/firestore.indexes.json` first (indexes take time to build).
If a data migration is part of the release, follow the `migrate` skill before enabling new code paths.

## Deploy
- **Backend (Render):** push/merge to the branch Render tracks. Build command: `cd apps/api && go build -o server ./cmd/server/main.go`. Env vars on Render: `FIREBASE_PROJECT_ID`, `FIREBASE_CREDS_BASE64`, `SMARTY_AUTH_ID`, `SMARTY_AUTH_TOKEN`, `ALLOWED_ORIGINS` (the Vercel URL), optional `ENABLE_VALIDATION_WORKERS` / `ENABLE_REVALIDATION_CHECKER`.
- **Frontend (Vercel):** push/merge; Vercel builds the web app. `VITE_API_BASE_URL` must be set to the public Render URL *before* the build (it is baked into the bundle).
- **Docker (self-hosted):** `cp .env.docker.example .env` (fill credentials), then `make docker-up` (`docker compose up -d --build`). API-only change: `make docker-rebuild`.

## Verify
- `curl <api-url>/healthz` → `{"status":"ok"}` (server only starts after Firestore ping succeeds).
- API logs show `connected to Firestore project …` and the expected background-worker state (`make docker-logs` for Docker).
- Open the frontend: Mailboxes list loads, no CORS errors in the browser console (check `ALLOWED_ORIGINS`).

## Rollback
- Render / Vercel: redeploy the previous successful deploy from the dashboard, or `git revert` and push.
- Docker: check out the previous commit and `make docker-up`.
- Data changes are not rolled back by redeploying — see the `migrate` skill.
- Never use `make docker-clean` as a rollback step (it removes volumes).
