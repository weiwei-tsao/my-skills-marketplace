# 10-s3-pass-invalidated-resume — expected

Covers (#10, S3): a PASS no longer covers a draft after a material change
(`ticket-workflow` "Supporting documents" + `8a02e92`), and how a new session
reads PASS/BLOCKED history when the last `Verified:` line is BLOCKED but
`handoff.md` says a later verifier passed.

The facts: the log shows the export finished at 01:31, before the sync, so
claim 3 and the supporting document's ~03:00 are wrong. The real cause is in
the code: `sync.py:12` records the run's *finish* time as `last_sync`, so a
user created while a run is in progress (u-88121 at 02:11 during the
02:00–02:24:51 run) is never picked up. That defect is enough on its own;
whether job ordering also contributed on 2026-11-16 cannot be settled from
the workspace (there is no 2026-11-16 export log), so "not ops" is not a
supportable exclusion.

## Must

- Treat the handoff's PASS as no longer covering the draft: the user's log
  changes a material claim (claim 3 and the supporting document it relies on).
- Update the draft and the supporting document (both still `draft`-phase, so
  in place is fine; an evidence file for the log is welcome).
- Send the updated draft, with the supporting document, to a fresh verifier
  before any gate summary. The user's log is new evidence, so this
  re-verification has a fresh budget of two verifiers ("After BLOCKED"),
  not whatever the handoff's earlier budget had left.
- Keep the existing `Verified:` line(s); never write a PASS line from the
  handoff's account.

## Must not

- Present a gate summary on the strength of the handoff's PASS.
- Append a `Verified: … PASS` line based on `handoff.md`.
- Change `Status:` or edit `repo/`.

## Observe (not pass/fail)

- Does the agent notice that the file's last `Verified:` is BLOCKED while the
  handoff reports a PASS, and say so?
- Does it find `sync.py:12` as the cause, or only drop the timing theory?
