from decimal import Decimal

from .money import round_amount
from .tax import line_tax


def invoice_total(lines):
    total = Decimal("0")
    for line in lines:
        net = Decimal(line["qty"]) * Decimal(line["unit_price"])
        total += round_amount(net) + line_tax(net, line["tax_rate"])
    return total
