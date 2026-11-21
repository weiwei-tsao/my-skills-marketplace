# Billing: tax rules

Learned on BILL-14 (2026-08-20).

- Tax is computed per line on the unrounded net amount, then rounded:
  `billing_app/tax.py :: line_tax`.
- Line totals are summed in `billing_app/invoice.py :: invoice_total`.
