# Resume prompt

A copy-pasteable first message for starting a new session, in case the skill doesn't
auto-trigger. Replace the ticket ID and path.

```
Resume PUB-11743 from .handoff/PUB-11743.md.

1. Check the current branch and git status first — this is the ground truth the
   handoff's code facts must be checked against.
2. Read the handoff.
3. Verify every Code Fact against the actual code: grep/read each referenced
   `path :: symbol`. Mark each ✅ confirmed / ⚠️ changed / ❌ gone.
4. Follow any References to commits/PRs/docs only if the next action needs them.
5. Summarize: confirmed state, anything that went stale (⚠️/❌), and the next action.
6. Restate your understanding of the next action and wait — do NOT edit code until
   I confirm.
```

## Why this order

- **git status before the handoff**, not after: the whole reason code facts go stale is
  that the tree moved. Establishing the current state first gives you something to check
  the recorded facts *against*.
- **Verify, don't trust**: a handoff file replaces the old session history, so its claims
  carry no live evidence — they must be re-grounded in the actual code before use.
- **Restate and wait (step 6)**: the cheapest guard against resuming on a misreading.
  A cold session can misinterpret the recorded "next action"; one confirmation turn
  costs almost nothing and stops a wrong-direction run before any code changes.
