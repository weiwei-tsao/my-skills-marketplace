# Ecosystem

## Repos and ownership

| Area | Repo / module | Owns |
|---|---|---|
| Shipping | `repo/shipping_app` | Shipping rates, unit conversion, labels |

## Request / data flow

```text
Checkout → rates.shipping_cost → units.to_kg → rate table
```
