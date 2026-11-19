"""Render inventory rows as CSV."""


def export_rows(rows: list) -> str:
    # Reports append a totals row at the end; it is not an inventory item.
    if rows and rows[-1].get("is_total"):
        rows = rows[:-1]
    lines = ["sku,name,qty"]
    for row in rows:
        lines.append(f"{row['sku']},{row['name']},{row['qty']}")
    return "\n".join(lines)
