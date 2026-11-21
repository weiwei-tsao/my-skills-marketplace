# BILL-21 Context

Status: confirmed
Verified: 2026-11-18 — PASS

## Goal

Invoice totals match finance's rounding policy.

## User-visible problem / business need

Since 2026-11-10 some invoice totals are one cent lower than finance's
spreadsheet. Finance's policy is that every money amount rounds half-up to
the cent. Example: one line, qty 1, unit price 0.125, tax rate 0 → finance
expects 0.13, the invoice says 0.12.

## Expected behavior

Every money amount on an invoice rounds half-up to the cent.

## Current behavior

Some totals are 0.01 lower than expected.

## Scope

### In scope

- `billing_app` invoice total calculation.

### Out of scope

- Invoice email content.
- Changing finance's policy.

## Open questions

- None.
