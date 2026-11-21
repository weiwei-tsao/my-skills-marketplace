# Ecosystem

## Repos and ownership

| Area | Repo / module | Owns |
|---|---|---|
| Billing | `repo/billing_app` | Invoice totals, tax, money rounding and formatting, invoice emails |

## Request / data flow

```text
Invoice job → invoice.invoice_total → money / tax helpers → stored total → notify.invoice_email
```
