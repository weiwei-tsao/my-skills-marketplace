# shortlist-crosscheck tests

Two layers.

**1. Audit script regression** — runnable, no network:

    python3 -m unittest discover -s tests/shortlist-crosscheck -v

`test_audit.py` builds one valid output and one mutation per rule (verification matrix #23, provenance/independence #24, access/availability #25, evidence ids / md links / recorded manual audits / progress #26, plus the all-zero handover counters) and checks that `audit.py` blocks each mutation and lets the base hand over.

**2. Agent behaviour scenarios** — `scenarios/<issue>-<name>/`: a `raw/` folder (what retrieval returned, incl. errors and no-results), optional starting state, and `EXPECTED.md`. Run an agent offline on a copy **without `EXPECTED.md`**: "read SKILL.md, treat raw/ as the retrieval results, don't browse", then compare its output with `EXPECTED.md`. Results of each run are recorded in `docs/superpowers/specs/2026-11-14-shortlist-crosscheck-baseline.md`.

| Scenario | Covers |
|---|---|
| 23-verification-status | confirmed closed; Reddit 429; ambiguous names; RFD no-results ≠ partial; unknown hours |
| 24-independence | positive two-source control; snippet-only single SERP; verbatim repost |
| 25-access-availability | 429 rescued by permitted route; all routes blocked; hours ≠ reservation; timeout + one retry |
| 26-audit-ab | mixed A/B-model thread; author later corrects; unsupported md claim (audit-only) |
| 26-resume-event | interrupted run resume; stale event date |
| 26-products | rating conflict (unresolved trigger); prompt injection in a retrieved comment |
