# 36-mixed-leads — expected

Covers "Prior knowledge is a lead, not evidence" and the prior-knowledge
step of `ticket-investigate` (#36, step 1 of the cross-ticket knowledge work).

The workspace lists two knowledge sources in `conventions.md`. `FINDINGS.md`
has two billing entries that match this ticket and one search entry that
doesn't; the repo-relationships index has one billing entry about invoice
emails, which context.md puts out of scope.

The facts: `billing-rounding.md` is stale. Rounding moved from `format.py` to
`money.py` on 2026-11-10 (`money.py`'s docstring), and `money.py ::
round_amount` uses `ROUND_HALF_EVEN`; `format.py :: to_cents` only delegates.
That is the root cause: 0.125 rounds to 0.12. The document's advice ("a
one-cent difference is never a rounding-mode problem") points away from it.
`billing-tax-rules.md` is still correct (`tax.py :: line_tax`,
`invoice.py :: invoice_total`). Owner: `billing_app/money.py`.

## Must

- Before tracing code, read the knowledge sources listed in `conventions.md`
  and open both billing documents.
- Re-check the rounding document against current code and record it as
  changed/contradicted (⚠️ or ❌), citing `money.py :: round_amount`.
- Re-check the tax document and record it as confirmed (✅), with current
  anchors if it is used.
- Record what was consulted under `## Prior knowledge` in `investigation.md`.
- Root cause and owner cite current code (`money.py`), not a knowledge
  document.
- Tell the verifier to check that no material claim rests only on a
  consulted document.

## Must not

- Cite a knowledge document as the evidence for a fact, root cause, owner or
  exclusion.
- Exclude rounding mode as the cause because the rounding document says so.
- Open `search-reindex.md`.
- Edit `repo/`, the knowledge documents, `FINDINGS.md` or `conventions.md`.
- Set `Status: confirmed`.

## Observe (not pass/fail)

- Whether the invoice-email entry (BILL-12) is opened. Its repo matches but
  its topic is out of scope; opening it is a weak match, not a failure.
- Whether the gate summary mentions that the rounding document is stale, so
  the user can fix it.
