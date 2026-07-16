# Engineering Conventions

This file records team conventions that AI should follow when generating code, PR notes, test notes, and Slack updates.

## General working style

- Keep changes small and focused.
- Avoid unrelated formatting.
- Avoid broad refactors in bug-fix tickets.
- Prefer evidence over assumptions.
- Separate facts, hypotheses, and decisions.
- Confirm repo ownership before editing.
- Keep UAT/PROD/acceptance status explicit.

## Branch naming

Suggested format:

```text
fix/PUB-11743-short-description
feature/PUB-11743-short-description
chore/PUB-11743-short-description
```

## Commit message style

Use concise conventional commits when possible:

```text
fix(PUB-11743): hide top-right nav fallback text
chore(PUB-11743): remove invalid border declaration
feat(PUB-11743): add article engagement conversion event
```

Keep the message under roughly 10 words after the ticket scope when possible.

## PR title style

```text
fix(PUB-11743): hide top-right nav fallback text
```

## PR description style

Use:

```md
## Summary
- ...

## Test
- ...

## Notes
- ...
```

Keep it concise and evidence-based.

## Slack style

Assembly-style Slack updates should be:

- short
- friendly
- low-drama
- direct
- not overly apologetic
- clear about status and next action

Good examples:

```text
This is fixed and tested on UAT. I’m no longer seeing the fallback text on desktop or mobile.
```

```text
Thanks! I’ll deploy this with the next PROD push once acceptance is confirmed.
```

```text
Deployed to PROD. Please let me know if anything looks off.
```

## UAT / acceptance / deploy

- UAT validation should happen before PROD.
- PM/editor acceptance should be recorded in `timeline.md` and `test.md`.
- If a PM assigns the ticket back and says it can be deployed/marked done, record that explicitly.
- If deployment carries other people’s accepted work, mention only what is relevant and avoid claiming ownership of their work.

## AI instructions

When AI is asked to work on a ticket:

1. Read `ecosystem.md` and `conventions.md`.
2. Read the ticket’s `context.md` and `handoff.md`.
3. If debugging, update `investigation.md` before code changes.
4. Before editing, run or request:
   - current repo
   - current branch
   - `git status`
   - current diff
5. Make the smallest safe change.
6. Update `implementation.md`, `test.md`, `handoff.md`, and `pr.md`.
