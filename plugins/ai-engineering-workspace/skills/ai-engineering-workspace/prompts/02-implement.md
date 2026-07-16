# Prompt: Implement Minimal Fix

Use this only after investigation has enough evidence to identify the likely owner repo and fix scope.

```text
You are implementing <TICKET-ID>.

Read these files first:
- ecosystem.md
- conventions.md
- tickets/<TICKET-ID>/context.md
- tickets/<TICKET-ID>/investigation.md
- tickets/<TICKET-ID>/implementation.md
- tickets/<TICKET-ID>/test.md
- tickets/<TICKET-ID>/handoff.md

Before editing code:
1. Confirm the owner repo.
2. Check current directory.
3. Check current branch.
4. Run git status.
5. Inspect current diff.
6. Summarize the intended minimal change.

Then make the smallest safe code change.

Rules:
- Do not refactor unrelated code.
- Do not change multiple repos unless investigation justifies it.
- Avoid unrelated formatting.
- Preserve existing behavior unless the ticket requires changing it.
- Update implementation.md and test.md after the change.
- Update handoff.md with current status and next steps.
```
