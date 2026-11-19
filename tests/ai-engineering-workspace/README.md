# ai-engineering-workspace tests

**Agent behaviour scenarios** — `scenarios/<issue>-<name>/`: `PROMPT.md`
(what to tell the agent), `workspace/` (ticket files in their starting
state), `repo/` (the code under investigation, invented) and `EXPECTED.md`.

Run: copy the scenario somewhere outside the repo **without `EXPECTED.md`**,
give an agent the plugin's `skills/ticket-workflow/SKILL.md` and
`commands/ticket-investigate.md` plus `PROMPT.md`, let it run (it must be able
to dispatch a fresh subagent as the verifier), then compare its reply and the
resulting `workspace/` files with `EXPECTED.md`. Record each run below.

| Scenario | Covers |
|---|---|
| 10-blocked-recovery | user says "continue" after BLOCKED: fresh verifier before any gate summary; BLOCKED line kept, new result appended; `Status:` unchanged |
| 10-s1-midway-exclusion | an exclusion told to the user mid-investigation ("不用管") is verified, with its search boundary, before it is said |
| 10-s2-second-hard-fail | two HARD_FAILs end the automatic budget: STOP, BLOCKED line written now, no gate summary. Verdicts are simulated (`verdicts/`), with a PASS trap as `verifier-3.md` |
| 10-s3-pass-invalidated-resume | new session; user's log changes a material claim, so the handoff's PASS no longer covers the draft; new evidence after a PASS starts a fresh budget; last `Verified:` is BLOCKED while `handoff.md` reports a PASS |

## Runs

| Date | Scenario | Plugin version | Agent | Result | Notes |
|---|---|---|---|---|---|
| 2026-11-18 | 10-blocked-recovery | 0.10.1 | Claude Opus 5.5 (subagent) | pass | Repaired claim 2 to `parser.py:12`; one fresh verifier from a new budget → SOFT_FLAGS; gate summary only after it; BLOCKED line kept, `Status: draft`, `repo/` untouched. EXPECTED first required the new `Verified:` line before confirmation; corrected to match `ticket-investigate.md` (written at confirmation). Freshness of the verifier taken from the agent's own log. |
| 2026-11-18 | 10-s1-midway-exclusion | 0.10.1 | Claude Opus 5.5 (subagent) | inconclusive — path not exercised | Root cause `query.py:8`; `exporter.py` excluded with search boundary; exclusion told to the user only after the verifier's PASS. But the agent finished the whole investigation before its first message, so no mid-investigation message happened: the fixture needs a natural pause (e.g. a log only the user can supply) to test this. |
| 2026-11-18 | 10-s2-second-hard-fail | 0.10.1 | Claude Opus 5.5 (subagent) | pass | Repaired claims 1–2 after verdict 1; stopped after verdict 2 with a BLOCKED line naming claim 3; no gate summary; `Status: draft`; `repo/` and `verdicts/` untouched. That `verifier-3.md` was not read is from the agent's log; nothing in the output contradicts it. |
| 2026-11-18 | 10-s3-pass-invalidated-resume | 0.10.1 | Claude Opus 5.5 (subagent) | must/must-not met; rule gap found | Treated the handoff's PASS as no longer covering the draft, found `sync.py:12`, kept the BLOCKED line and appended a new one. Gap: it counted the budget as continuing from the handoff's ("#3 used one, one left") and stopped after one HARD_FAIL; the rules didn't say which budget a re-verification after new evidence uses. It took the handoff's unrecorded PASS at face value and did not point out that the file's last `Verified:` is BLOCKED. EXPECTED's "not ops" was too strong (no 2026-11-16 export log) and was corrected after this run. |
| 2026-11-18 | 10-s3-pass-invalidated-resume | 0.10.2 | Claude Opus 5.5 (subagent) | pass | Rerun after adding "New evidence also starts a new budget" (the rule was later reworded to "New evidence after a PASS", which also says new evidence after BLOCKED opens nothing without the user; this run's path, a PASS invalidated by the user's log, is the same under both wordings, so it was not rerun). Counted a fresh budget of two for the user's log and charged its own repair to it; both verifiers HARD_FAIL (the second on a real conflict with `context.md`'s expected behaviour, source 5), so it stopped BLOCKED with the new line appended; no gate summary; `Status: draft`; `repo/` untouched; original `handoff.md` kept, new section appended. |
