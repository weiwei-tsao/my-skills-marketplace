---
name: system-design-roadmap
description: >
  Build a personalized system design learning roadmap. Use when the user wants to
  study system design, prepare for interviews, choose what to learn next, or turn
  source repositories into a staged learning plan.
---

# System Design Roadmap

Create a practical study plan from the user's current level, target, and time budget.
Prefer an interview-ready path: fundamentals first, then architecture patterns, then
case drills, then mock interviews.

## Required inputs

Ask only for missing inputs that materially change the plan:

- Current level: beginner, backend/product engineer, senior engineer, or interview-ready.
- Goal: general learning, interview prep, architecture review, or a specific company/level.
- Timeline: days/weeks available and hours per week.
- Preferred language: Chinese, English, or bilingual.

If the user does not know, assume backend engineer preparing for interviews in 6 weeks,
5 hours/week, bilingual explanations with Chinese summaries.

## Workflow

1. Read `../../references/source-map.md` for source boundaries and attribution rules.
2. Read `../../references/topic-map.md` for the topic graph.
3. Pick a plan length:
   - 1 week: survival path, only high-leverage topics and 2 drills.
   - 4-6 weeks: standard path, fundamentals + patterns + 6-8 drills.
   - 8-12 weeks: deep path, full topic graph + repeated mock interviews.
4. Produce a roadmap with these sections:
   - Goal and assumptions.
   - Weekly plan with topics, exercises, and output artifacts.
   - Must-know concepts and "defer for later" concepts.
   - Case drill sequence.
   - Review cadence and flashcard prompts.
   - Source links to consult, not copied content.
5. End with the next concrete session: one concept to learn and one case to drill.

## Roadmap principles

- Teach breadth before depth: latency/throughput, availability, consistency, scalability,
  networking, databases, caching, queues, and observability.
- Pair concepts with cases. Example: learn cache strategies before URL shortener or feed.
- Treat estimation as a repeated habit, not a single chapter.
- Include tradeoff prompts in every week: cost, complexity, operational load, failure mode.
- Prefer diagrams or plain component lists over long prose.

## Output shape

Use concise Chinese by default. Keep the roadmap skimmable:

```markdown
## Assumptions

## Plan
| Week | Focus | Exercises | Done when |

## Case Sequence

## Review Cadence

## Next Session
```

Do not paste upstream article or book text. Link to sources and summarize only what is
needed for the plan.
