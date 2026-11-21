from .money import round_amount


def to_cents(value):
    """Kept for old callers; delegates to money.round_amount."""
    return round_amount(value)


def display(value):
    return f"${to_cents(value)}"
