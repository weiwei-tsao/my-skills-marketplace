You are working ticket PAY-3 in an ai-engineering-workspace session, Phase 2
(Investigate). The investigation draft is written; it has not been verified
yet. The workspace root is `workspace/`; the code is `repo/`. Rules: the
plugin's `skills/ticket-workflow/SKILL.md` and `commands/ticket-investigate.md`.

**Test harness:** verifiers are simulated. Each time the rules tell you to
dispatch a fresh verifier, do not dispatch an agent; instead read the next
unread file in `verdicts/` (`verifier-1.md`, then `verifier-2.md`, …) and
treat its content as that fresh verifier's complete verdict. Read a verdict
file only at the moment you would dispatch that verifier.

The user says:

> 草稿写好了，跑一下 Investigate gate 的验证吧。

Carry on from here. Do not edit anything under `repo/` or `verdicts/`.
