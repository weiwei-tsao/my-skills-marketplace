# SYNC-4 Context

Status: confirmed
Verified: 2026-11-14 — PASS

## Goal

Every new user reaches the CRM after the nightly sync.

## User-visible problem / business need

A few users created each night never appear in the CRM.

## Expected behavior

All users created since the previous sync are synced.

## Scope

### In scope

- `sync_app` nightly sync.

### Out of scope

- Backfilling users already missed.
