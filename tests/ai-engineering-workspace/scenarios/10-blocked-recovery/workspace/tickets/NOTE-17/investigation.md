# NOTE-17 Investigation

Status: draft
Verified: 2026-11-17 — BLOCKED: claim 2 (root cause is format_due converting in the wrong direction) — fresh verifier #2 found parser.py:12 drops the offset without converting to UTC, so format_due receives local wall time labelled as UTC; the draft never inspected parser.py

## Reproduction steps

1. `create_reminder(1, {"due": "2026-03-01T09:00:00-05:00"})`
2. `show_reminder(1, "America/Toronto")` returns `2026-03-01 04:00`.

## Facts

- Claim 1: `show_reminder` passes the stored value straight to `format_due` (`notes_app/api.py:12-13`).
- Claim 2: `format_due` treats its input as UTC and converts it to the user's zone (`notes_app/formatter.py:8-9`). This conversion is the root cause: it shifts the time by the user's offset.

## Hypotheses

- (none)

## Root cause

`format_due` converts in the wrong direction (claim 2).

## Owner repo / module

`notes_app/formatter.py`

## Checked but not responsible

| Ruled out | Searched (surface + query) | Not searched |
|---|---|---|
| `notes_app/api.py` | read the whole file | — |

## Open questions

- (none)

## Next investigation steps

- (none)
