# SHIP-4 Context

Status: confirmed
Verified: 2026-11-19 — PASS

## Goal

Shipping costs at checkout are correct.

## User-visible problem / business need

Customers report shipping quotes about ten times too high. Example: a 500 g
parcel with standard service is quoted 20.00; the rate card says 4.00 per kg,
so it should be 2.00.

## Expected behavior

Shipping cost = weight in kg × the service's rate per kg.

## Current behavior

Quotes are ten times the expected amount.

## Scope

### In scope

- `shipping_app` rate calculation.

### Out of scope

- The rate card values.
- Label printing.

## Open questions

- None.
