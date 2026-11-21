# Prior knowledge lookup in Investigate — design

Tracking: #51 (group B: #36, #37). This is step 1 of the cross-ticket knowledge work: the read side only.

## Problem

`complete-ticket` writes reusable knowledge (`knowledge/private/repo-relationships-index.md` and its cards), and workspaces often keep their own cross-ticket notes as well: a findings index with topic documents organised by domain. No phase command reads any of it. The complete-ticket design (2026-08-01) built the index to help the *user* remember past tickets, not as an agent input. So every ticket starts cold, even when an earlier ticket already established the relevant ownership or flow.

## Goal

At the start of Investigate, the agent consults the workspace's cross-ticket knowledge, opens only the documents relevant to this ticket, and uses what it finds as **leads, not evidence**. Before relying on a lead it re-checks it against the current code, and it records what it consulted and how it turned out.

## Non-goals (this step)

- Writing new knowledge: capturing small repo facts at handoff save, or backfilling them from past tickets. That is step 2.
- Changing workspace layout or ticket-folder resolution.
- Search infrastructure: embeddings, a database, a new skill or command.
- Editing the knowledge documents themselves (marking a card stale, superseding it).
- Reading knowledge during Understand. Understand reads no code, and these documents are claims about code.

## Design

### Where the sources come from: `conventions.md` "Knowledge sources"

A new optional section lists index files, each with a short note on what it indexes and where its entries point:

```markdown
## Knowledge sources

- `knowledge/private/repo-relationships-index.md` — complete-ticket repo relationship index; entries link to `knowledge/private/repo-relationships/<TICKET-ID>.md`
- `FINDINGS.md` — findings index by domain; entries link to topic documents at the workspace root
```

If the section is missing, the agent uses `knowledge/private/repo-relationships-index.md` when it exists, and mentions once that more indexes can be listed. Existing workspaces add the section by hand, since the upgrade never overwrites `conventions.md`.

### Lookup: a new first step in `ticket-investigate`

1. Read every listed index in full. Indexes are short by design.
2. Match their entries against this ticket's repos, components, surfaces and symptom, taken from `context.md` and `ecosystem.md`.
3. Open only the documents the matching entries point to. Never open every document a source covers.
4. If no entry matches, record "none matched" and investigate as usual. Don't stretch a weak match into a relationship.

### Rule: prior knowledge is a lead, not evidence (`ticket-workflow`)

- A document records what was true where and when it was written. Code may have moved since, or the document may have been wrong.
- Before a lead supports a fact, root cause, owner or exclusion, re-check it against the current code and cite the current anchor. Mark the result using handoff's resume vocabulary: ✅ confirmed / ⚠️ changed / ❌ gone or contradicted.
- A material claim whose only support is a knowledge document lacks evidence (HARD_FAIL source 1). An exclusion copied from an earlier ticket is a lead to re-check, even when it recorded a search boundary, because that boundary applied to older code.
- Prior knowledge does not change gates, the verifier budget, or `Status:` rules.
- A lead that turns out ⚠️ or ❌ is recorded in the ticket. The source document is not edited in this step.

### Record: `## Prior knowledge` in `investigation.md`

One row per document opened: source, what it said, how it was re-checked, and the result (✅ / ⚠️ / ❌ / not used). "None matched" is a valid entry. When the draft has this section, the Investigate verifier is told to check that no material claim rests only on a consulted document.

### Scaffolding

`workspace-scaffold` and the suite skill's interview ask where cross-ticket knowledge lives, and record the answer in `conventions.md`.

## Verification

New agent-behaviour scenarios in `tests/ai-engineering-workspace/scenarios/`, all invented:

- `36-mixed-leads`: two matching documents. One is still correct; the other is stale, because the code was refactored after it was written. Followed blindly, the stale one gives the wrong root cause. A third, unrelated entry should not be opened.
- `36-no-match`: the sources cover only other repos. Expected: "none matched", nothing opened, and no invented link.

Run both against 0.10.4 for a baseline, then against the change. The expected baseline is that 0.10.4 never looks at the sources.

The plugin's own checks still apply: the vetting unit tests, the audit with `--strict-reviewed`, and `claude plugin validate .`. Version: 0.11.0.
