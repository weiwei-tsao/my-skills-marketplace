# Ecosystem

This file gives AI coding agents the repo map and ownership rules.
Keep it updated when the layout changes.

## Repo layout

<!-- List the repos involved and where they live locally. Single-repo
     projects: describe the top-level module layout instead. -->

```text
~/code/
  <app-repo>/
  <shared-lib-repo>/
  <api-repo>/
  <this-workspace>/
```

## Repos and ownership

| Area | Repo / module | Owns |
|---|---|---|
| App | `../<app-repo>` | Pages, routing, app-specific behavior |
| Shared UI/lib | `../<shared-lib-repo>` | Shared components — often owns shared fixes |
| API / data | `../<api-repo>` | Response shape, upstream data |

## Request / data flow

<!-- The typical path a request or piece of data travels. Agents use this
     to trace symptoms back to root cause. -->

```text
Entry (URL / event / job)
→ routing / middleware
→ page / handler
→ data fetch
→ shared components / libraries
→ API / upstream data
→ source system
```

## Ownership rules

<!-- For each common symptom class, the order in which to check owners.
     The point: don't patch the symptom's repo if a shared layer owns the
     behavior. Add/remove classes to match your stack. -->

### UI rendering issue

1. App-level usage
2. Shared component behavior
3. App-specific style overrides
4. Data shape from API, if rendering depends on missing fields

### Missing or malformed data

1. App fetch path
2. API response shape
3. API/service implementation
4. Source content/system
5. Shared code assumptions

## AI safety rules

- Do not edit code before root cause and owner repo/module are reasonably confirmed.
- Do not make broad refactors unless the ticket explicitly requires it.
- Do not change multiple repos unless the investigation explains why.
- Prefer minimal, reviewable diffs.
- Always check current branch and git status before editing.
- Always summarize changed files and test coverage before PR.
