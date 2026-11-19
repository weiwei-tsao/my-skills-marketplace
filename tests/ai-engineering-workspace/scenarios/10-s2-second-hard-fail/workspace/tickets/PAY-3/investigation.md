# PAY-3 Investigation

Status: draft

## Facts

- Claim 1: `apply_discount` subtracts the percentage twice (`shop_app/discount.py:20`).
- Claim 2: `cart_total` calls `apply_discount` once on the subtotal (`shop_app/cart.py:8`).

## Root cause

`apply_discount` applies the percentage twice (claim 1).

## Owner repo / module

`shop_app/discount.py`

## Checked but not responsible

| Ruled out | Searched (surface + query) | Not searched |
|---|---|---|
| `shop_app/cache.py` (claim 3) | read the file | — |

## Open questions

- (none)
