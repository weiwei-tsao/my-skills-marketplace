HARD_FAIL

- Claim 1 (source 1, source 2): `shop_app/discount.py` has 5 lines; line 20
  does not exist, and `apply_discount` (discount.py:4-5) applies the
  percentage once. Claim 2 is incomplete: `cart.py:9` calls `apply_discount` a
  second time, on the already discounted value, inside the lambda passed to
  `cached_total`. The draft's root cause and owner are not supported.

No other blocking issue found in this pass.
