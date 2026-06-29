---
name: a11y-audit
description: Audits frontend code and pages against WCAG 2.1/2.2 Level AA — flags missing alt text, contrast issues, heading hierarchy, form labels, ARIA misuse, keyboard access, and focus management. Use when reviewing or fixing accessibility in a frontend codebase.
allowed-tools: Read, Grep, Glob
---

# Accessibility Audit

Systematically review frontend code against WCAG 2.1/2.2 Level AA and report
violations by severity. This skill is read-only: it inspects and reports, it
does not modify files or run network calls.

## How to run

1. Inventory the components and pages (Glob for `.jsx/.tsx/.vue/.svelte/.html`).
2. For each file, check for:
   - Images without meaningful `alt` text.
   - Heading hierarchy: exactly one `h1`, no skipped levels.
   - Form inputs without an associated `<label>` or `aria-label`.
   - Interactive elements reachable and operable by keyboard.
   - Visible focus styles (no `outline: none` without a replacement).
   - ARIA: valid roles/attributes; no `aria-hidden` on focusable elements.
   - Color contrast called out for manual verification (automation is limited).
3. Produce a summary: total issues by severity, file + line for each, and the
   WCAG criterion it maps to.

## Anti-patterns to flag

- `tabindex` greater than 0 (breaks natural tab order).
- `aria-label` on non-interactive, non-landmark elements.
- `role="presentation"` / `aria-hidden="true"` on elements with focusable children.
- Tooltip content only available on hover (unreachable by keyboard/touch).

## Note

Automated code analysis catches a minority of accessibility issues. Always
recommend a manual keyboard walkthrough and screen-reader pass for full coverage.
