"""In-memory stand-in for the inventory table."""


class InventoryDB:
    def __init__(self, rows):
        self._rows = list(rows)

    def count(self) -> int:
        return len(self._rows)

    def page(self, number: int, size: int) -> list:
        start = number * size
        return self._rows[start:start + size]
