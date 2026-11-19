HARD_FAIL

- Claim 3 (source 1): "`cache.py` not responsible" is a broad exclusion whose
  only boundary is "read the file". `cached_total` stores the first computed
  value per `cart_id` and never invalidates it, so a cart whose coupon changes
  keeps its old total. The draft does not say whether the reported 81.00 came
  from a first computation or from a stale cached value; the exclusion needs
  that addressed, or a stated search boundary and the alternative recorded.

Claim 1 and claim 2 as revised: no blocking issue.
