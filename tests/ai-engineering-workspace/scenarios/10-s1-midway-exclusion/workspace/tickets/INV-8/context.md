# INV-8 Context

Status: confirmed
Verified: 2026-11-17 — PASS

## Goal

The inventory CSV export contains every item.

## User-visible problem / business need

Since 2026-11-02 every warehouse's export is missing exactly one item: the
last one in the list. 2026-11-02 is also when the vendor switched to its new
nightly file format. Nobody on the team has the new format's spec; the
warehouse lead (Robin) can pull a sample file from the vendor portal on
request.

## Expected behavior

One CSV row per inventory item.

## Current behavior

The last item is missing from every export.

## Scope

### In scope

- `inventory_app`: vendor feed load, query, export.

### Out of scope

- The CSV column layout.

## Repos / modules likely involved

| Area | Module | Team | Why it may be involved |
|---|---|---|---|
| Vendor feed | `inventory_app/feed.py` | Data ingestion | loads the vendor file |
| Query | `inventory_app/query.py` | Platform | reads the rows in pages |
| Export | `inventory_app/exporter.py` | Reports | builds the CSV; drops a trailing row in some cases |

## Important constraints

- Do not edit code until ownership is confirmed.
- Each team is holding time for this ticket until it is told it isn't involved.
