# Assembly Repo Ecosystem

This file gives AI coding agents the repo map and ownership rules. Keep this updated when repo layout changes.

## Local repo layout

Assume sibling repositories live under `~/Documents/` unless stated otherwise.

```text
~/Documents/
  pub-todaysparent/
  pub-en-chatelaine/
  pub-fr-chatelaine/
  pub-torontolife/
  pub-macleans/
  pub-shared-react/
  pub-platform-api/
  pub-worker-proxy/
  me-findings-notes/
```

## Brand repos

| Brand | Repo | Notes |
|---|---|---|
| Today’s Parent | `../pub-todaysparent` | TP |
| Chatelaine EN | `../pub-en-chatelaine` | CHE |
| Chatelaine FR | `../pub-fr-chatelaine` | CHF |
| Toronto Life | `../pub-torontolife` | TL |
| Maclean’s | `../pub-macleans` | MAC |

## Shared / platform repos

| Area | Repo | Notes |
|---|---|---|
| Shared React components | `../pub-shared-react` | PSR; often owns shared UI fixes |
| Platform API | `../pub-platform-api` | Go API / upstream JSON / data ownership |
| Worker proxy | `../pub-worker-proxy` | Proxy/worker behavior |

## Common request/data flow

```text
URL
→ brand Express server / middleware / routes
→ brand page / getInitialProps
→ fetchSite / fetchPost
→ shared React components in pub-shared-react
→ upstream JSON / platform API
→ WordPress or other source systems
```

## Ownership rules

### UI rendering issue

Check in this order:

1. Brand page usage
2. `pub-shared-react` component behavior
3. Brand-specific CSS overrides
4. Data shape from API if rendering depends on missing fields

Do not patch a brand repo just to hide symptoms if the shared component owns the behavior.

### Missing or malformed content/data

Check in this order:

1. Brand fetch path
2. API response shape
3. `pub-platform-api`
4. WordPress/source content
5. Shared component assumptions

### Ad / analytics / conversion behavior

Check in this order:

1. Brand integration point
2. Shared component or hook
3. Vendor script timing
4. DataLayer / pixel event shape
5. Environment feature flags

### RSS / feed / syndication

Check in this order:

1. Feed generation path
2. Content transform/sanitize logic
3. Brand-specific feed rules
4. Shared feed utilities
5. MSN / Apple News / external syndication constraints

## AI safety rules

- Do not edit code before root cause and owner repo are reasonably confirmed.
- Do not make broad refactors unless the ticket explicitly requires it.
- Do not change multiple repos unless the investigation explains why.
- Prefer minimal, reviewable diffs.
- Always check current branch and git status before editing.
- Always summarize changed files and test coverage before PR.
