"""Money helpers. Rounding moved here from format.py on 2026-11-10."""
from decimal import Decimal, ROUND_HALF_EVEN

CENT = Decimal("0.01")


def round_amount(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_EVEN)
