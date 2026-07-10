---
name: system-design-answer-review
description: >
  Review a user's system design answer or architecture proposal. Use when the user
  provides a design for critique, asks whether an answer is interview-ready, or wants
  gaps, risks, tradeoffs, and next improvements.
---

# System Design Answer Review

Review like a senior interviewer: findings first, then fixes. Be direct and specific.

## Inputs

Accept any of:

- Written answer.
- Mermaid/diagram description.
- Notes from a mock interview.
- Architecture proposal from real work.

If the design lacks the problem statement, ask for it. If the user wants fast feedback,
infer the likely prompt and mark it as an assumption.

## Workflow

1. Read `../../references/interview-rubric.md`.
2. Identify the intended system and constraints.
3. Review in this order:
   - Requirement gaps.
   - Estimation gaps or impossible numbers.
   - API and data model issues.
   - Scalability bottlenecks.
   - Consistency and failure-mode risks.
   - Security, abuse, privacy, or compliance gaps where relevant.
   - Observability and operations gaps.
   - Communication clarity.
4. Separate critical blockers from polish.
5. Provide a revised answer outline, not a full copied solution.

## Output shape

```markdown
## Verdict

## Findings
- Severity: file/section/quote if available - issue - why it matters - fix.

## Missing Questions

## Strong Parts

## Revised Outline

## Score
```

Use severity labels: `Critical`, `High`, `Medium`, `Low`.

If the user is practicing for interviews, include a short 2-minute final answer they can
say out loud, written in their preferred language.
