# Prompt: Start Ticket Investigation

Use this when starting a new ticket or when the root cause is not confirmed yet.

```text
You are working on <TICKET-ID>.

Read these files first:
- ecosystem.md
- conventions.md
- tickets/<TICKET-ID>/context.md
- tickets/<TICKET-ID>/handoff.md, if it exists

Start with read-only investigation.
Do not edit code yet.

Your goals:
1. Understand the user-visible problem or business need.
2. Trace the likely flow across repos.
3. Identify the most likely owner repo.
4. Separate facts, hypotheses, and decisions.
5. Update tickets/<TICKET-ID>/investigation.md with findings, evidence, open questions, and next steps.

Before finishing, summarize:
- confirmed facts
- likely root cause
- owner repo
- next safest action
```
