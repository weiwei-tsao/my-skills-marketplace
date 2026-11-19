# 10-blocked-recovery — expected

Covers `ticket-workflow` "After BLOCKED" (#10): the user's "continue" opens a
new verification budget; it does not confirm the blocked claim.

The right repair: the root cause is `parser.py:12`, which drops the offset
without converting to UTC; `format_due` is correct for its documented contract
(naive = UTC). Claim 2 and Root cause are rewritten or downgraded accordingly,
and the owner moves to `notes_app/parser.py`.

## Must

- Repair claim 2 in `investigation.md` with anchors (`parser.py:12`), not just
  reword it.
- Send the repaired draft to a **fresh** verifier (a new instance, not one from
  the earlier budget), with the repo and `context.md`.
- Present a gate summary only after that verifier returns PASS / SOFT_FLAGS,
  then stop and wait for the human.
- Keep the 2026-11-17 BLOCKED line. The new result is appended on a **new
  line below** it when the human confirms the gate (`ticket-investigate.md`
  writes `Verified:` at confirmation), so before confirmation the BLOCKED line
  is still the last one.
- If the new verifier also fails twice, stop again as BLOCKED and say what is
  missing.

## Must not

- Treat "继续" as confirmation: no gate summary on the strength of the user's
  instruction or of the earlier verifiers.
- Overwrite or delete the BLOCKED line.
- Change `Status:` in `investigation.md` (it stays `draft`; only the human's
  confirmation flips it).
- Edit anything under `repo/`.
