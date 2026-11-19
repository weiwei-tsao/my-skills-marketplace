"""Parse reminder payloads coming from the client."""
from datetime import datetime


def parse_due(value: str) -> datetime:
    """Return the due time as a naive datetime.

    Callers treat the result as UTC.
    """
    dt = datetime.fromisoformat(value)
    # Drop the offset so the value can be stored in the naive DB column.
    return dt.replace(tzinfo=None)
