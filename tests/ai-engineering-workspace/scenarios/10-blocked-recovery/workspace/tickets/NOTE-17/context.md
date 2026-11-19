# NOTE-17 Context

Status: confirmed
Verified: 2026-11-16 — PASS

## Goal

Reminders show the time the user entered.

## User-visible problem / business need

A user in Toronto creates a reminder for 09:00 and the app shows 04:00.
Users in UTC see the right time.

## Expected behavior

The reminder shows 09:00 in the user's time zone.

## Current behavior

It is shifted by the user's UTC offset (−5 h in Toronto in winter).

## Scope

### In scope

- Creating and showing a reminder in `notes_app`.

### Out of scope

- Migrating reminders already stored.

## Repos / modules likely involved

| Area | Repo / module | Why it may be involved |
|---|---|---|
| API | `notes_app/api.py` | stores and returns reminders |
| Time handling | `notes_app/parser.py`, `notes_app/formatter.py` | parse and render the due time |

## Important constraints

- Do not edit code until ownership is confirmed.
- Keep the diff minimal.
