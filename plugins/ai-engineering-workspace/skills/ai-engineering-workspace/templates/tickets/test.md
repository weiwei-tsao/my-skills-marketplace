# <TICKET-ID> Test Plan

## Local checks

- [ ] `git status` checked before testing
- [ ] Typecheck
- [ ] Unit tests, if relevant
- [ ] Lint, if relevant
- [ ] Affected page/component checked locally, if possible

## Environment checks

<!-- One row per environment/surface that must be verified. -->

| Environment / surface | URL | Checked | Notes |
|---|---|---|---|
|  |  | [ ] |  |

## Trigger-scenario coverage

<!-- Only if investigation.md has a Trigger conditions section. Both tables
     are required — per-condition rows can each pass independently without
     ever combining the conditions, which proves nothing about the
     scenario (e.g. one test with only condition A active, another with
     only B active, neither reproducing an A-&&-B bug). -->

### Per-condition (boundary checks)

<!-- For each condition, confirm a test actually drives it to its
     triggering value — not a neutral/empty value that runs the code path
     without exercising the condition. A test that "saves twice" with an
     empty payload both times is not testing "second save with stale
     data"; it's a structural no-op. -->

| Scenario | Condition | Test that drives it to the triggering value | Confirmed |
|---|---|---|---|
|  |  |  | [ ] |

### Full scenario (all conditions simultaneously)

<!-- One test per scenario that activates every condition in that scenario
     at once — the only test that can actually reproduce the bug. -->

| Scenario | Test that activates the complete conjunction | Confirmed |
|---|---|---|
|  |  | [ ] |

## Regression checks

- [ ] Existing behavior still works
- [ ] No new console/log errors
- [ ] No obvious visual regression
- [ ] No unrelated area affected

## Acceptance

| Person | Role | Status | Date | Notes |
|---|---|---|---|---|
|  |  | Pending |  |  |

## Production deploy check

- [ ] Accepted on staging
- [ ] Safe for production
- [ ] Deployed
- [ ] Ticket marked done
- [ ] Status update sent, if needed

## Final test notes for PR

```text
- 
```
