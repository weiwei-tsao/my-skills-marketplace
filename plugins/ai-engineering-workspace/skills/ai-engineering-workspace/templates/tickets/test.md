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

## Trigger-condition coverage

<!-- Only if investigation.md has a Trigger conditions section. For each
     condition, confirm a test actually drives it to its triggering value —
     not a neutral/empty value that runs the code path without exercising
     the condition. A test that "saves twice" with an empty payload both
     times is not testing "second save with stale data"; it's a
     structural no-op. -->

| Trigger condition | Test that drives it to the triggering value | Confirmed |
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
