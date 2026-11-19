"""Tiny memo cache for computed cart totals."""

_CACHE: dict = {}


def cached_total(cart_id: str, compute):
    if cart_id not in _CACHE:
        _CACHE[cart_id] = compute()
    return _CACHE[cart_id]
