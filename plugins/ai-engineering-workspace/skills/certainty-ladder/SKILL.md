---
name: certainty-ladder
description: A three-layer testing standard for web apps, sorted by whether a stable machine-checkable oracle exists for the check, not by what tooling happens to run it. Use when deciding whether a check belongs in a unit test, an integration/API/browser test, or needs a human/agent to look at the rendered page and judge; when deciding whether a test should gate CI; when a test passes but the bug is still visible to users (an oracle exists but nobody wrote it yet); or when asked which layer a given check belongs in.
---

# The Certainty Ladder

*A three-layer testing standard for web apps — sorted not by tooling, but by whether a stable machine oracle exists for what's being checked.*

**Applies to:** web apps with a browser-rendered UI
**Layers:** 3

---

## §1 The Principle

Most test pyramids split by tooling — unit, integration, e2e. This one splits by **whether a stable, machine-checkable oracle exists for the thing being checked**, because that determines whether a check can be written as code at all, and how often it's worth running.

Each rung down the ladder trades certainty for reach: Layer 1 computes the exact answer itself; Layer 2 asks a real system but still gets one fixed, checkable answer back; Layer 3 has no fixed answer to ask for — only a human or an agent judging what they see. Skipping a rung — testing a judgment call with a fixed assertion, or testing pure logic through a browser — is where most flaky and most wasted test suites come from.

| | Verb | What it checks |
|---|---|---|
| **Layer 1 — Logic** | Verify | An input has exactly one correct output, computed with no external system in the call path. |
| **Layer 2 — Behavior** | Script | Touches a real system (browser, API, DB, queue) but the expected result is still one stable, machine-checkable assertion — however that assertion is built. |
| **Layer 3 — Perception** | Judge | The acceptance criterion itself has no fixed answer to check against — it's a matter of what a person perceives or judges. |

Cool → warm reads as machine-certain → human-judged.

---

## §2 The Three Layers

### Layer 1 — Logic *(Verify)*

Pure functions with no DOM, network, or database in the call path: parsing, formatting, validation, sanitization rules, string truncation, case-folding edge cases. If it can be called from a plain Node process and checked with `assert.equal`, it belongs here — and nowhere else.

| | |
|---|---|
| **Tooling** | Vitest, Jest, or any assertion-based unit runner |
| **Speed** | Single-digit milliseconds per test |
| **Trigger** | Every save, every commit — cheap enough to run constantly |
| **CI gate** | Yes, almost without exception |

### Layer 2 — Behavior *(Script)*

Anything that needs a real running system — an API, a database, a browser, a queue — to verify at all, but whose expected outcome is still one fixed, machine-checkable assertion. The oracle can be an API response shape, a DB row, a DOM selector, a bounding-box/geometry reading, a screenshot diffed against an approved baseline, or a performance/accessibility instrumentation value compared against a threshold. **What makes it Layer 2 is that the check is stable and worth maintaining — not that it avoids a browser.** A DB-only API integration test with no browser in sight is Layer 2, exactly like a Playwright assertion is.

| | |
|---|---|
| **Tooling** | API/integration test runner, component test, Playwright/Cypress, screenshot-diff, geometry or instrumentation assertions |
| **Speed** | Milliseconds to seconds per test |
| **Trigger** | Per pull request (team) or on demand (small/solo projects) |
| **CI gate** | Once the check has proven stable (low flakiness on repeat runs) and its regression cost justifies its runtime + maintenance cost — team size is a proxy for this at best, never the rule itself |

### Layer 3 — Perception *(Judge)*

Checks whose acceptance criterion has no stable machine oracle at all — not "hasn't been scripted yet," but genuinely a matter of what a person perceives: an animation that feels janky, a visual hierarchy that reads as confusing, a workflow that feels clunky even though every step technically works. The moment someone can state the acceptance criterion as a fixed comparison — a bounding box, a screenshot baseline, a computed style, a numeric threshold — that check has already moved to Layer 2, whether or not anyone has written it yet.

| | |
|---|---|
| **Tooling** | A real browser, driven by a human or an agent (e.g. an attached CDP session) |
| **Speed** | Minutes, exploratory — not reducible to a fixed check by definition |
| **Trigger** | Before merging UI changes, before a release |
| **CI gate** | Never — there's nothing stable to gate on. The moment there is, the check is Layer 2, not Layer 3. |

**Choosing a Layer 3 tool**: the question is what you're checking, not a fixed default.
- *"Does this look right?"* (visual judgment, a flow feels off, a real logged-in session matters) → a real, already-authenticated browser session a human or agent drives directly.
- *"What does this technical data mean?"* (reading a Lighthouse report, an accessibility tree, console/network output, a performance trace) → a browser-inspection tool that surfaces the browser's own instrumentation for a human/agent to interpret.

Both stay Layer 3 only while the result is being *read and judged*. The moment a metric becomes a numeric gate — `CLS < 0.1`, `Lighthouse performance ≥ 90` — it's Layer 2: a fixed, machine-checkable oracle, even though a browser produced the number.

---

## §3 Where Does This Check Belong?

Ask the questions in order. Stop at the first one that lands.

1. **Does verifying this require touching a real system at all — browser, network, database, filesystem?**
   - No → **Layer 1, Logic**
   - Yes → continue

2. **Can the correct result be expressed as one stable, machine-checkable assertion** — an API/DB check, a DOM selector, a geometry or bounding-box reading, a screenshot diffed against an approved baseline, an accessibility or performance instrumentation value against a threshold?
   - Yes → **Layer 2, Behavior**
   - No → continue

3. **Is correctness ultimately a matter of what a person perceives or judges, with no acceptance criterion that reduces to a fixed check?**
   - Yes → **Layer 3, Perception**

If correctness can be reduced to a stable machine-checkable oracle, it's Layer 2 — even when that oracle is built from screenshots, geometry, accessibility data, or browser instrumentation. Layer 3 begins only where the acceptance criterion itself still requires judgment.

### Examples

| Check | Layer | Why |
|---|---|---|
| `<mark>` element exists in the DOM | L2 | Fixed selector assertion |
| `<mark>`'s bounding box intersects its container's visible (non-clipped) area | L2 | Geometry has a fixed, checkable answer |
| Rendered page matches an approved screenshot baseline | L2 | Stable comparison — a browser produced it, but the check is fixed |
| Cumulative Layout Shift < 0.1 | L2 | Instrumentation reading against a fixed threshold |
| This button's animation feels janky | L3 | No fixed oracle — a person has to watch it |
| This page's visual hierarchy is confusing | L3 | Judgment call, not a comparison |
| The page looks obviously broken despite every structural check passing | L3 | The acceptance criterion is "does a human notice something's wrong" |

---

## §4 Automation Policy

The further down the ladder, the more expensive and less repeatable a check gets — so the default posture toward automating it gets more conservative, not less.

| Layer | Default trigger | CI gate | Why |
|---|---|---|---|
| **1 · Logic** | On every change | Always | Near-zero cost, zero flakiness when the function is actually pure. |
| **2 · Behavior** | Per PR, or on demand for solo/small projects | Once the check has proven stable and its regression cost justifies its runtime + maintenance cost | Real cost (server/DB/browser), but still deterministic once races are closed and the oracle is trustworthy. |
| **3 · Perception** | Manual, pre-merge or pre-release | Never | Scheduling it turns a judgment step into a false sense of automated coverage. |

---

## §5 Anti-Patterns

- **Writing a Layer 2 assertion for something that's really a Layer 3 judgment call** — "the button is centered," "the transition feels smooth" — instead of admitting it needs eyes on it.
- **Re-scripting a golden path in Layer 3 that Layer 2 already covers.** If it can be a fixed assertion, it should live in Layer 2 — Layer 3's only job is what Layer 2 structurally can't do.
- **Putting Layer 3 on a schedule or a cron job.** The moment it's unattended, it stops being a judgment step and starts being a false "we checked" checkbox.
- **Running pure Layer 1 logic through a full browser suite** because the project "already has Playwright set up." Slower, and every failure now has to rule out the browser before it can blame the logic.
- **Calling a check Layer 3 because it happens to involve pixels or a browser**, when it actually has a stable oracle (geometry, screenshot diff, instrumentation threshold) — that's Layer 2 that nobody's written yet, not permanently unautomatable.

---

## §6 Worked Example

**The bug:** A search match's `<mark>` tag was rendered exactly where expected — present, correctly positioned, semantically right. But its container used `overflow: hidden; text-overflow: ellipsis`, so the highlighted text sat past the visible clip point. No user ever saw the highlight.

**Why it surfaced at Layer 3:** Layer 1 only checked the highlighting function's output string — correct, and irrelevant to layout. Layer 2 asserted `<mark>` exists in the DOM — also correct, also irrelevant, because no machine-checkable oracle had been defined for that question yet: "is this element inside its clipped ancestor's visible area." Only looking at a rendered browser caught the gap.

**After the fact:** once named, "the highlighted match's bounding box intersects its container's visible, non-clipped region" is a stable, machine-checkable assertion — it belongs at Layer 2 going forward. Layer 3 did its job by exposing a defect class that had no encoded oracle yet; it isn't Layer 3's job to keep re-checking it by hand once one exists (see the last Anti-Pattern above).

| Metric | Count |
|---|---|
| Layer 1 tests | 73 |
| Layer 2 golden paths | 9 |
| Layer 3 bugs neither caught (at the time) | 1 |
