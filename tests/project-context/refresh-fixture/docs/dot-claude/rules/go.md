---
paths:
  - "apps/api/**/*.go"
---
# Go (apps/api)

## Verify before finishing
```bash
cd apps/api && go build ./... && go vet ./... && go test ./...
cd apps/api && gofmt -l .     # must print nothing
```
- Checks run locally (go ≥ 1.25.3; go.mod pins `go 1.25.3`).
- After editing `apps/api/Dockerfile`, `docker-compose.yml`, `go.mod`/`go.sum`: `make docker-build`.
- chromedp / Chromium behaviour (musl, `CHROME_NO_SANDBOX`) is only verifiable in Docker: `make docker-up`, then `curl localhost:8080/healthz`.
- Fallback if local Go is missing/too old: `docker run --rm -v "$PWD/apps/api":/src -w /src golang:1.25-alpine go test ./...`

## Errors
- Wrap with context and `%w`: `fmt.Errorf("decode mailbox %s: %w", doc.Ref.ID, err)` (`internal/repository/mailbox_repo.go`). Lowercase, no trailing punctuation.
- Package-level sentinels as `var ErrX = errors.New(...)` (`internal/platform/smarty/client.go`: `ErrCircuitOpen`, `ErrAllCredentialsExhausted`).
- Validation classifies errors via `validation.CategorizeError` (`errors.go`) into Transient / Permanent / QuotaExhausted — route new Smarty failure modes through it.
- `log.Fatalf` only in `main` packages.

## Context
- `ctx context.Context` is the first parameter of every repository/service method that does I/O.
- `cmd/server/main.go` derives the root ctx from `signal.NotifyContext`; background workers stop on `ctx.Done()`.

## Layout
- Binaries: `cmd/<name>/main.go` (server, check-*, migrate-*); ad-hoc ops scripts: `scripts/<name>/main.go`.
- `internal/` for app code (`platform`, `business`, `repository`); `pkg/model`, `pkg/util` for shared types/helpers.
- Constructors `NewX(...) *X`; dependencies passed explicitly (no globals); validation takes interfaces it declares itself.
- Logging: standard `log.Printf`; services receive a `func(msg string)` logger (`[validation]`, `[revalidation]` prefixes).
- Config: env via `godotenv.Load(".env.local", ".env")` + `config.Load()`; runtime tunables in Firestore `system` config and `config.yaml`.

## Tests
- Table-driven, same package, `testdata/` fixtures; run one: `go test ./internal/business/validation -run TestCalculateBackoff`. Details → testing.md

Firestore → db.md · HTTP → api.md
