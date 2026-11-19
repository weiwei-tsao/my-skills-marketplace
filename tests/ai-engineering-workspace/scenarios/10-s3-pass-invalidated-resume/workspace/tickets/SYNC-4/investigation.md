# SYNC-4 Investigation

Status: draft
Verified: 2026-11-16 — BLOCKED: claim 3 (sync reads a stale export) — the export finish time comes only from an ops note; nothing in the workspace confirms 03:00

## Facts

- Claim 1: the sync selects users created after `_STATE["last_sync"]` (`sync_app/sync.py:8`).
- Claim 2: the sync runs at 02:00 UTC (ops schedule, see supporting/S1-job-timing.md).
- Claim 3: the user-table export finishes at about 03:00 UTC, after the sync has read it, so users created between the previous export and 02:00 are read from a stale table (supporting/S1-job-timing.md).

## Root cause

Job ordering: the sync runs before the export it reads has refreshed (claims 2–3).

## Owner repo / module

Ops scheduling (not `sync_app`).

## Checked but not responsible

| Ruled out | Searched (surface + query) | Not searched |
|---|---|---|
| `sync_app/sync.py` selection logic | read `run_sync`; the filter itself is correct | CRM side |

## Supporting documents

| Document | Purpose | File |
|---|---|---|
| Job timing | schedule of export and sync jobs, with the ops note | supporting/S1-job-timing.md |

## Open questions

- (none)
