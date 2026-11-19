"""Cart totals."""
from .cache import cached_total
from .discount import apply_discount


def cart_total(cart_id: str, items: list, percent: float) -> float:
    subtotal = sum(i["price"] * i["qty"] for i in items)
    discounted = apply_discount(subtotal, percent)
    return cached_total(cart_id, lambda: apply_discount(discounted, percent))
