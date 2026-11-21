from decimal import Decimal

from .money import round_amount


def line_tax(net: Decimal, rate: str) -> Decimal:
    """Tax is computed per line on the unrounded net, then rounded."""
    return round_amount(net * Decimal(rate))
