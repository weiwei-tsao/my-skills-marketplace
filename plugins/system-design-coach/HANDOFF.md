# System Design Coach Handoff

## Purpose

This plugin helps the user learn system design through three V1 skills:

- `system-design-roadmap`: personalized study plans.
- `system-design-case-drill`: interactive case practice.
- `system-design-answer-review`: critique of written or spoken design answers.

The plugin intentionally stores workflows, indexes, and rubrics rather than upstream
course/book text.

## Source Boundaries

Primary source links and usage constraints live in `references/source-map.md`.

Important constraints:

- Do not copy substantial text from `karanpratapsingh/system-design`; its license is
  CC BY-NC-ND 4.0.
- Do not package or quote chapter content from `Admol/SystemDesign`; its README states
  the translation is for learning/research reference and not for public distribution or
  commercial use.
- Keep future additions as original prompts, rubrics, short summaries, and links.

## Current State

Created V1 structure:

- `.claude-plugin/plugin.json`
- `skills/system-design-roadmap/SKILL.md`
- `skills/system-design-case-drill/SKILL.md`
- `skills/system-design-answer-review/SKILL.md`
- `references/source-map.md`
- `references/topic-map.md`
- `references/case-catalog.md`
- `references/interview-rubric.md`

Marketplace entry should point to `./plugins/system-design-coach`.

## Extension Ideas

Good next skills:

- `system-design-concept-tutor`: explain one concept with tradeoffs and examples.
- `system-design-mock-interviewer`: stricter one-question-at-a-time interview mode.
- `system-design-flashcards`: generate Anki-style Q/A cards from a completed session.
- `system-design-diagram-review`: critique Mermaid or architecture diagrams.

Good next references:

- `references/concept-cards.md`: terse original concept summaries.
- `references/estimation-cheatsheet.md`: powers of two, latency numbers, sizing patterns.
- `references/case-rubrics/<case>.md`: per-case evaluation rubrics, not copied solutions.

## Validation Cursor

After edits, run:

```bash
python3 vetting/audit_skill.py plugins/system-design-coach
claude plugin validate .
```

If Docker is available and the plugin later gains scripts, run the sandbox vetting flow
before publishing.
