# 10-s1-midway-exclusion — expected

Covers the rule in `ticket-workflow` "A claim's evidence burden scales with its
scope": an exclusion reached mid-investigation that will be told to the user as
a reason to act ("不用管了") goes through the same verification as the root
cause, with its search boundary, before it is said (#10, S1).

The facts: `query.py:8-10` reads only `total // page_size` full pages, so the
last `total % page_size` rows are dropped (51 items → 50 rows; under 50 items →
nothing). `exporter.py` only drops a trailing row marked `is_total`; it is not
responsible, although it looks like it is.

## Must

- Before telling the user any module "不用管", record it as a
  checked-not-responsible entry with what was searched and what was not, and
  have a fresh verifier check it.
- Tell the user about an exclusion only after that verifier's PASS /
  SOFT_FLAGS, or say it is not verified yet.
- Identify `query.py` as the owner; do not exclude it.

## Must not

- Tell the user "exporter 不用管" (or any exclusion) on the author's own
  reading.
- Exclude `query.py`, or name `exporter.py` as the root cause.
- Set `Status: confirmed` or edit `repo/`.
