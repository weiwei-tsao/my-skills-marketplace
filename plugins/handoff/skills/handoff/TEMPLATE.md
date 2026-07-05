# Handoff — <TICKET-ID>: <short title>

> Last updated: <date> · Session: <n>
> Goal of this ticket (1 sentence): <what "done" looks like>

---

## 1. Code Facts  (verify on resume — code may have moved)

Format: `path :: symbol` — relationship. Mark verification status on resume.

- [ ] `src/auth/session.py :: refresh_token()` — called by `login()` and the middleware; issues new JWT. _(verified <date>)_
- [ ] `src/api/routes.py :: /session/refresh` — the only route hitting `refresh_token()`. _(verified <date>)_

> On resume, prefix each: ✅ confirmed / ⚠️ changed / ❌ gone.
> Do NOT record a fact here without a `path :: symbol` anchor. Un-anchored observations
> go under Decisions (as inference) or Dead-ends.

---

## 2. Decisions & Rationale  (stable — trust unless requirement changed)

Why we're doing it this way. This is what lives only in your head, not in the code.

- **Decision:** <what was decided>
  **Why:** <reason>
  **Alternatives rejected:** <what and why not>
  **(inferred / confirmed):** <mark which>

---

## 3. Progress  (the cursor — update every save)

**Done**
- <completed step>

**In progress**
- <what's half-finished, and exactly where it stands>

**Next**
- <next concrete action — actionable enough for a cold start>

---

## 4. Dead-ends  (append-only — never retry these)

Failed attempts and ruled-out paths. Highest value, easiest to lose.

- **Tried:** <approach>
  **Result:** <why it failed>
  **Lesson:** <what to avoid / what it implies>

---

## 5. References  (point, don't copy)

Durable artifacts that already hold the detail — link, don't transcribe.

- PR / commit: <#id or sha> — <what it contains>
- PRD / ADR / issue: <path or url> — <relevance>
- Plan / design doc: <path> — <relevance>

---

## Next-session setup

- **Skills/tools to load:** <e.g. the test-runner skill, the migration skill>
- **First action on resume:** <the single thing to do after verifying code facts>

---

## Open questions / risks

- <anything unresolved that the next session should decide or watch>
