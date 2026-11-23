---
paths:
  - "apps/api/**/*_test.go"
  - "apps/api/**/testdata/**"
---
# Testing

## Scope
- Only the Go API has tests (12 `_test.go` files). The web app has none and no test runner.
- Unit-test pure logic and services: parsers, address cleaning, backoff, error categorisation, batch handling, validation service, router helpers.
- No test hits real Firestore, Smarty, or the network.

## Conventions
- Tests live next to the code, same package (white-box): `backoff.go` → `backoff_test.go`, `package validation`.
- Table-driven with `t.Run(tt.name, ...)` (e.g. `internal/business/validation/backoff_test.go`).
- HTML fixtures in `testdata/` (`internal/business/crawler/testdata/sample_page.html`).
- Fakes, not mocking libraries: hand-written structs implementing the service's repository interfaces (e.g. `fakeMailboxRepository` in `validation/service_test.go`). Add an interface in the consumer package if you need to fake a dependency.
- Router tests cover pure helpers (`TestGenerateExportFilename` in `internal/platform/http/router_test.go`); `cmd/server/main_test.go` tests revalidation scheduling (`TestNextRevalidationCheck`). Extract logic into helpers to test it without Gin/Firestore.
- Use `t.Errorf` with `got … want …` messages; standard library `testing` only.

## Running
```bash
cd apps/api && go test ./...                                           # all
cd apps/api && go test ./internal/business/validation                  # one package
cd apps/api && go test ./internal/business/validation -run TestCalculateBackoff -v   # one test
```
- Every bug fix should come with a regression test in the relevant package.

Go conventions → go.md
