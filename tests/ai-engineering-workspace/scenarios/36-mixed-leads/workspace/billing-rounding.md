# Billing: money rounding

Learned on BILL-9 (2026-06-02).

- All money rounding happens in `billing_app/format.py :: to_cents`, which
  rounds half-up (`ROUND_HALF_UP`) as finance requires.
- So a one-cent difference on a total is never a rounding-mode problem; look
  at tax or line quantities instead.
