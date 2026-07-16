# Prompt: Finish Ticket / PR / Handoff

Use this after implementation and testing.

```text
You are finishing <TICKET-ID>.

Read:
- ecosystem.md
- conventions.md
- tickets/<TICKET-ID>/context.md
- tickets/<TICKET-ID>/investigation.md
- tickets/<TICKET-ID>/implementation.md
- tickets/<TICKET-ID>/test.md
- tickets/<TICKET-ID>/timeline.md
- current git diff

Generate and save to tickets/<TICKET-ID>/pr.md:
1. PR title
2. PR description
3. commit message
4. test notes
5. short Slack update in Assembly style

Then update tickets/<TICKET-ID>/handoff.md with:
- current status
- completed work
- branch
- changed files
- diff summary
- test status
- next steps
- blockers
- do-not-do notes
```
