"""Discount rules."""


def apply_discount(total: float, percent: float) -> float:
    return round(total * (1 - percent / 100), 2)
