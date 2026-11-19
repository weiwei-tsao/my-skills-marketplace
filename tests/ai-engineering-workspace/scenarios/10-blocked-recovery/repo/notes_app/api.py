"""Reminder endpoints."""
from .formatter import format_due
from .parser import parse_due

_DB: dict[int, object] = {}


def create_reminder(reminder_id: int, payload: dict) -> None:
    _DB[reminder_id] = parse_due(payload["due"])


def show_reminder(reminder_id: int, user_tz: str) -> str:
    return format_due(_DB[reminder_id], user_tz)
