"""Export endpoint."""
from .exporter import export_rows
from .query import fetch_all


def export_inventory(db) -> str:
    return export_rows(fetch_all(db))
