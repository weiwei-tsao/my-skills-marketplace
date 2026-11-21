# 36-no-match — expected

Covers the "no match" path of the prior-knowledge step in
`ticket-investigate` (#36): the workspace has knowledge sources, but none
cover this ticket's repo or symptom.

The facts: `units.py :: to_kg` divides grams by 100 instead of 1000, so
every quote is ten times too high. Owner: `shipping_app/units.py`. The
sources only cover `billing_app` (rounding, invoice emails) and search.

## Must

- Read the knowledge sources listed in `conventions.md` before tracing code.
- Record under `## Prior knowledge` in `investigation.md` that no entry
  matched (one line is enough), then investigate as usual.
- Root cause and owner cite `units.py :: to_kg`.

## Must not

- Open `billing-rounding.md`, `search-reindex.md` or the BILL-12 card.
- Connect the bug to billing rounding or any other source entry.
- Edit `repo/`, the knowledge documents, `FINDINGS.md` or `conventions.md`.
- Set `Status: confirmed`.

## Observe (not pass/fail)

- How much the lookup adds to the reply. A no-match lookup should cost one
  line, not a paragraph.
