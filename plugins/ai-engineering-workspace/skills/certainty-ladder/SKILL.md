---
name: certainty-ladder
description: A three-layer testing standard for web apps, sorted by how certain you can be about a check's result without a human looking at it. Use when deciding whether a check belongs in a unit test, an e2e test, or needs a human/agent to look at the rendered page; when deciding whether a test should gate CI; when a test passes but the bug is still visible to users (DOM-correct but not human-correct); or when asked which layer a given check belongs in.
---

# The Certainty Ladder

*A three-layer testing standard for web apps — sorted not by tooling, but by how certain you can be about the answer without a human looking at it.*

**Applies to:** web apps with a browser-rendered UI
**Layers:** 3

---

## §1 The Principle

Most test pyramids split by tooling — unit, integration, e2e. This one splits by **what kind of correctness is being checked**, because that determines whether a check can be written as code at all, and how often it's worth running.

Each rung down the ladder trades certainty for reach: Layer 1 knows an exact answer instantly; Layer 3 can only ask a human or an agent to look and judge. Skipping a rung — testing visual judgment with a DOM selector, or testing pure logic in a browser — is where most flaky and most wasted test suites come from.

| | Verb | What it checks |
|---|---|---|
| **Layer 1 — Logic** | Verify | An input has exactly one correct output. No browser, no network, no ambiguity. |
| **Layer 2 — Behavior** | Script | Needs a real browser and backend, but the expected result is still one exact, assertable state. |
| **Layer 3 — Perception** | Judge | Correct in the DOM isn't the same as correct to a person looking at the screen. |

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

Golden paths that need a live browser and server to exist at all — login, CRUD, form validation, a paste handler's effect on real DOM — but whose correct outcome is still one fixed, selector-checkable state. If the check can't be written as a fixed pass/fail assertion, it doesn't belong here even if it happens inside a browser.

| | |
|---|---|
| **Tooling** | Playwright or Cypress against a disposable environment |
| **Speed** | Seconds per test, minutes per suite |
| **Trigger** | Per pull request (team) or on demand (small/solo projects) |
| **CI gate** | Recommended once the team is more than one person |

### Layer 3 — Perception *(Judge)*

Everything that's correct in the DOM but not necessarily correct to a person: content clipped by an ancestor's `overflow`, an animation that stutters, a control that's technically focusable but not visibly focused, layout that only breaks at one odd viewport width. Structurally, no selector-based assertion can catch this class of bug — it has to be looked at.

| | |
|---|---|
| **Tooling** | A real browser, driven by a human or an agent (e.g. an attached CDP session) |
| **Speed** | Minutes, exploratory — not scriptable by definition |
| **Trigger** | Before merging UI changes, before a release |
| **CI gate** | Never — automating it defeats its purpose |

**Choosing a Layer 3 tool**: the question is what you're checking, not a fixed default.
- *"Does this look right?"* (visual judgment, a flow feels off, a real logged-in session matters) → a real, already-authenticated browser session a human or agent drives directly.
- *"What is this technical metric?"* (Lighthouse score, accessibility tree, network/console errors, a performance trace or heap snapshot) → a browser-inspection tool that reads the browser's own instrumentation, not just what's visible on screen.
Both stay manual, pre-merge/pre-release, and never CI-gated — that's what makes them Layer 3, not a distinct fourth layer.

---

## §3 Where Does This Check Belong?

Ask the questions in order. Stop at the first one that lands.

1. **Does verifying this require a browser, network, or database at all?**
   - No → **Layer 1, Logic**
   - Yes → continue

2. **Can the correct result be written as one fixed selector or API assertion?**
   - Yes → **Layer 2, Behavior**
   - No → continue

3. **Is correctness ultimately a matter of what a person perceives on screen?**
   - Yes → **Layer 3, Perception**

---

## §4 Automation Policy

The further down the ladder, the more expensive and less repeatable a check gets — so the default posture toward automating it gets more conservative, not less.

| Layer | Default trigger | CI gate | Why |
|---|---|---|---|
| **1 · Logic** | On every change | Always | Near-zero cost, zero flakiness when the function is actually pure. |
| **2 · Behavior** | Per PR, or on demand for solo/small projects | Once >1 contributor regularly touches the UI | Real cost (server + DB + browser), but still deterministic once races are closed. |
| **3 · Perception** | Manual, pre-merge or pre-release | Never | Scheduling it turns a judgment step into a false sense of automated coverage. |

---

## §5 Anti-Patterns

- **Writing a Layer 2 assertion for something that's really a Layer 3 judgment call** — "the button is centered," "the transition feels smooth" — instead of admitting it needs eyes on it.
- **Re-scripting a golden path in Layer 3 that Layer 2 already covers.** If it can be a fixed assertion, it should live in Layer 2 — Layer 3's only job is what Layer 2 structurally can't do.
- **Putting Layer 3 on a schedule or a cron job.** The moment it's unattended, it stops being a judgment step and starts being a false "we checked" checkbox.
- **Running pure Layer 1 logic through a full browser suite** because the project "already has Playwright set up." Slower, and every failure now has to rule out the browser before it can blame the logic.

---

## §6 Worked Example

**The bug:** A search match's `<mark>` tag was rendered exactly where expected — present, correctly positioned, semantically right. But its container used `overflow: hidden; text-overflow: ellipsis`, so the highlighted text sat past the visible clip point. Every DOM assertion would have passed. No user ever saw the highlight.

**Why no lower layer caught it:** Layer 1 tests only checked the highlighting function's output string — correct, and irrelevant to layout. Layer 2 could have asserted `<mark>` exists in the DOM — also correct, also irrelevant. Only looking at a rendered browser surfaced it.

| Metric | Count |
|---|---|
| Layer 1 tests | 73 |
| Layer 2 golden paths | 9 |
| Layer 3 bugs neither caught | 1 |
