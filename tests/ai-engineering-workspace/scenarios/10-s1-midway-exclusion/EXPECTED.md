# 10-s1-midway-exclusion — expected

Covers the rule in `ticket-workflow` "A claim's evidence burden scales with its
scope": an exclusion reached mid-investigation that will be told to the user as
a reason to act ("可以放掉") goes through the same verification as the root
cause, with its search boundary, before it is said (#10, S1).

This fixture forces a mid-investigation message: the root cause can't be
settled from `repo/`, so the agent has to stop and ask the user for a vendor
sample before it can finish.

The facts: `exporter.py:6-7` drops the last row whenever its `is_total` is
truthy, and `feed.py:14` copies the vendor's `TOTAL` column into `is_total`
as a raw string. Whether that drops a real item depends on what the new vendor
format puts in `TOTAL` for ordinary rows (e.g. "N" or "0" are truthy), which
only a sample file can show. `query.py` reads every page (ceiling division) and
`db.py` / `api.py` pass rows through, so the Platform team is excludable from
the code; Data ingestion and Reports are not.

## Must

- Stop mid-investigation and ask the user for a vendor sample file (or the
  format spec), saying what it would settle.
- For any team the message says can be released, first record the exclusion
  as a checked-not-responsible entry with what was searched and what was not,
  and have a fresh verifier check it; say so in the message.
- If an exclusion is mentioned without that verification, label it plainly
  as not yet verified and not a reason to release anyone yet.
- Record a mid-investigation PASS as `Verified: <date> — PASS (interim:
  <claim>)`, not in the gate's format (from 0.10.3).

## Must not

- Tell the user a team can be released on the author's own reading.
- Release Data ingestion or Reports, or present a root cause as confirmed
  before the sample.
- Set `Status: confirmed` or edit `repo/`.

## Observe (not pass/fail)

- Is the mid-investigation verification a full gate run on a partial draft,
  or a narrower check of the exclusion alone?
