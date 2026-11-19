"""Nightly user sync from the exported user table to the CRM."""
from datetime import datetime

_STATE = {"last_sync": datetime(2026, 11, 1)}


def run_sync(source, target, now) -> int:
    users = source.users_created_after(_STATE["last_sync"])
    for user in users:
        target.upsert(user)
    # Remember when this run happened so the next run only picks up new users.
    _STATE["last_sync"] = now()
    return len(users)
