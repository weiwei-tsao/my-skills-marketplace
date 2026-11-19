# INV-8 Context

Status: confirmed
Verified: 2026-11-17 — PASS

## Goal

The inventory CSV export contains every item.

## User-visible problem / business need

A warehouse with 51 items exports 50 rows; the last item is missing. Small
warehouses (under 50 items) export nothing at all, according to one report,
but that report has not been reproduced.

## Expected behavior

One CSV row per inventory item.

## Current behavior

Some items at the end of the list are missing from the export.

## Scope

### In scope

- `inventory_app` export path.

### Out of scope

- The CSV column layout.

## Repos / modules likely involved

| Area | Repo / module | Why it may be involved |
|---|---|---|
| Export | `inventory_app/exporter.py` | builds the CSV; drops a trailing row in some cases |
| Query | `inventory_app/query.py` | reads the rows |

## Important constraints

- Do not edit code until ownership is confirmed.
