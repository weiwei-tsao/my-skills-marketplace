---
description: Create, apply, and roll back Firestore data migrations safely. Use when changing stored mailbox / run data or adding model fields that existing documents need.
---

# Firestore Data Migration

Firestore is schemaless; "migrations" are Go programs that rewrite existing documents. They live in `apps/api/cmd/migrate-*/main.go` (ops one-offs in `apps/api/scripts/*`) and run against the Firestore project in `apps/api/.env.local` / `.env`.

## Existing migrations (Makefile targets)
```bash
make migrate-clean-dry          # preview iPost1 address cleaning (--dry-run)
make migrate-clean              # apply it
make migrate-clean-all-dry      # preview for all sources
make migrate-clean-all
make migrate-add-source         # backfill `source` on mailboxes and crawl_runs
make migrate-validation-fields  # initialise validation status fields
make force-revalidate           # scripts/force_revalidate (--limit, default 1000)
```

## Create
1. New directory `apps/api/cmd/migrate-<what>/main.go`, modelled on `cmd/migrate-clean-addresses` (has `--dry-run`) or `cmd/migrate-add-source`:
   - `godotenv.Load(".env.local", ".env")` → `config.Load()` → `firestoreclient.New(ctx, cfg)`; `defer client.Close()`; log the project ID.
   - Add a `--dry-run` flag that prints what would change without writing.
   - Make it idempotent: skip documents that already have the new value.
   - Write in batches ≤400 ops (Firestore limit is 500); wrap errors with `%w`.
2. If the migration supports a new model field, add it to `pkg/model/model.go` with matching `json` and `firestore` tags, and make code tolerate documents that lack it (don't `OrderBy` it).
3. Add Makefile targets (`migrate-<what>-dry` and `migrate-<what>`) with a `## description` comment, and add them to `.PHONY`.
4. Gate: `cd apps/api && go build ./... && go vet ./...`.

## Apply
1. Confirm which Firestore project `.env.local` points to (the program logs it on start).
2. Run the dry-run target and review counts/samples.
3. Run the real target. Watch the free-tier quota (50K reads / 20K writes per day) — a full `mailboxes` pass costs one read per document plus one write per change.

## Rollback
- There is no automatic down-migration. Before a destructive change, export the affected collection (`gcloud firestore export gs://<bucket>` or a dump script) or have the migration store the old value in a backup field.
- To undo, write a reverse migration program the same way, dry-run it, then apply.

## Safety checklist
- [ ] Migration is additive where possible (new fields optional, code handles missing fields)
- [ ] `--dry-run` output reviewed against the right project
- [ ] Idempotent — safe to re-run after a partial failure
- [ ] Write volume fits the daily Firestore quota
- [ ] No data-destructive steps without a confirmed backup/export
