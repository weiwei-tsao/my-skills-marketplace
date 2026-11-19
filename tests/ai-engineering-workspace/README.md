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

## Runs

| Date | Scenario | Plugin version | Agent | Result | Notes |
|---|---|---|---|---|---|
| 2026-11-18 | 10-blocked-recovery | 0.10.1 | Claude Opus 5.5 (subagent) | pass | Repaired claim 2 to `parser.py:12`; one fresh verifier from a new budget → SOFT_FLAGS; gate summary only after it; BLOCKED line kept, `Status: draft`, `repo/` untouched. EXPECTED first required the new `Verified:` line before confirmation; corrected to match `ticket-investigate.md` (written at confirmation). Freshness of the verifier taken from the agent's own log. |
