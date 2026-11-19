"""Render reminder times for display."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def format_due(due_utc: datetime, user_tz: str) -> str:
    """Render a stored (naive, UTC) due time in the user's time zone."""
    aware = due_utc.replace(tzinfo=timezone.utc)
    return aware.astimezone(ZoneInfo(user_tz)).strftime("%Y-%m-%d %H:%M")
