# Engineering Conventions

Team conventions AI should follow when generating code, PR notes, test
notes, and status updates.

## General working style

- Keep changes small and focused; avoid unrelated formatting.
- Avoid broad refactors in bug-fix tickets.
- Prefer evidence over assumptions; separate facts, hypotheses, decisions.
- Confirm ownership before editing.
- Keep environment/acceptance status explicit.

## Ticket IDs

<!-- e.g. ABC-123. Used in branches, commits, PR titles. -->

Format: `<PREFIX>-<number>`

## Ticket source

<!-- Command or tool used to fetch a ticket's raw content and comments,
     e.g. `gh issue view <ID> --comments`, or a Jira/Linear MCP tool name.
     Used by /ai-engineering-workspace:ticket-understand so it doesn't have
     to ask every time. -->

Command: <fill in>

## Branch naming

```text
fix/<TICKET-ID>-short-description
feature/<TICKET-ID>-short-description
chore/<TICKET-ID>-short-description
```

## Commit / PR title style

```text
fix(<TICKET-ID>): short description
```

Keep the description under ~10 words when possible.

## Verification commands

<!-- Typecheck / lint / test / build commands to run before considering an
     implementation done. Referenced by /ai-engineering-workspace:ticket-implement — set once here
     instead of re-deriving per ticket. Mark any that don't apply to this
     project as N/A rather than leaving them unset. -->

- Typecheck: `<command or N/A>`
- Lint: `<command or N/A>`
- Test: `<command or N/A>`
- Build: `<command or N/A>`

## PR description style

```md
## Summary
- ...

## Test
- ...

## Notes
- ...
```

Concise and evidence-based.

## Status updates

<!-- Where updates go (Slack / Teams / issue comments) and the tone. -->

Channel: <where>

Style: short, friendly, direct, clear about status and next action.
Examples:

```text
Fixed and tested on <staging env>. No longer seeing <issue> on <surface>.
```

```text
Deployed to production. Please flag if anything looks off.
```

## Stages / acceptance

<!-- Adjust to your pipeline. -->

- Validate on <staging/UAT env> before production.
- Record acceptance (who, when) in `timeline.md` and `test.md`.
- If a deploy carries other people's accepted work, mention only what is
  relevant; don't claim ownership of their work.

## AI instructions

When asked to work on a ticket:

1. Read `ecosystem.md` and `conventions.md`.
2. Read the ticket's `context.md` and `handoff.md`.
3. If debugging, update `investigation.md` before code changes.
4. Before editing: current repo, branch, `git status`, current diff.
5. Make the smallest safe change.
6. Update `implementation.md`, `test.md`, `handoff.md`, and `pr.md`.
