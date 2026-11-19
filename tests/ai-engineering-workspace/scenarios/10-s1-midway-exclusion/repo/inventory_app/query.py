"""Read inventory rows in pages."""

PAGE_SIZE = 50


def fetch_all(db, page_size: int = PAGE_SIZE) -> list:
    total = db.count()
    pages = total // page_size
    rows = []
    for number in range(pages):
        rows.extend(db.page(number, page_size))
    return rows
