---
paths:
  - "apps/api/internal/repository/**/*.go"
  - "apps/api/internal/platform/firestore/**/*.go"
  - "apps/api/cmd/migrate-*/**/*.go"
  - "apps/api/firestore.indexes.json"
---
# Firestore

## Access
- Client created once in `internal/platform/firestore` (`firestoreclient.New(ctx, cfg)`; creds from `FIREBASE_CREDS_BASE64` or `FIREBASE_CREDS_FILE`) and injected into repositories in `cmd/server/main.go`.
- Only `internal/repository` reads/writes collections at runtime. Collections: `mailboxes`, `crawl_runs`, `validation_runs`, `system` (crawler config).
- Repos are structs holding `*firestore.Client` with `NewXRepository(client)` constructors; methods take `ctx context.Context` first.

## Patterns
- Model fields carry both tags: `json:"x,omitempty" firestore:"x,omitempty"` (`pkg/model/model.go`). Keep them in sync when adding fields.
- Iterate with `iter.Next()` until `iterator.Done`; wrap errors `fmt.Errorf("iterate mailboxes: %w", err)`.
- Fill `m.ID = doc.Ref.ID` when the stored ID is empty.
- Writes go through batches capped at 400 ops (`BatchUpsert`); Firestore's batch limit is 500.
- Use `.Select(...)` to skip the large `RawHTML` field when it isn't needed (`FetchAllMetadata`).
- Free-tier budget is 50K reads / 20K writes per day — avoid full-collection scans in loops or polling.

## Queries and indexes
- `OrderBy` on a field silently excludes docs missing that field (see commit 84bb5bd, removed OrderBy on `nextRetryAt`). Only order by fields every document has.
- Composite indexes are declared in `apps/api/firestore.indexes.json`; add one there for any new multi-field query.

## Migrations
- Data migrations are Go programs in `cmd/migrate-*` with Makefile targets; support `--dry-run` where they rewrite data. See the `migrate` skill.

Layering → architecture.md
