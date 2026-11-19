"""Load the vendor's nightly inventory file into the inventory table."""
import csv


def load_vendor_rows(path: str) -> list:
    rows = []
    with open(path, newline="") as f:
        for raw in csv.DictReader(f):
            rows.append({
                "sku": raw["SKU"],
                "name": raw["NAME"],
                "qty": int(raw["QTY"]),
                # The vendor marks its summary line in the TOTAL column.
                "is_total": raw.get("TOTAL"),
            })
    return rows
