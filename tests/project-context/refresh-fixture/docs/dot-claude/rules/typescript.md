---
paths:
  - "apps/web/**/*.ts"
  - "apps/web/**/*.tsx"
---
# TypeScript / React (apps/web)

## Verify before finishing
```bash
pnpm build:web                                                    # from repo root (vite build)
pnpm --filter us-virtual-address-verifier exec tsc --noEmit       # optional: type check (vite build doesn't)
```
- pnpm workspace; package name `us-virtual-address-verifier`. No linter or tests are configured.
- After changing `apps/web/Dockerfile` or `pnpm-lock.yaml`: `make docker-build`.

## Conventions
- React 19 function components, named exports (`export const Mailboxes`); `App.tsx` default export only.
- Server state via TanStack Query (`useQuery` / `useMutation` / `useQueryClient().invalidateQueries`) in `pages/*.tsx`; no global store. Toasts via `contexts/ToastContext.tsx`.
- All HTTP through `services/api.ts`; shared types in `types.ts`; constants in `constants.ts`. `services/mockData.ts` is mock data — don't wire it into real pages.
- Env: only `import.meta.env.VITE_*` (currently `VITE_API_BASE_URL`), baked in at build time.
- `tsconfig.json`: `strict` is off, `@/*` alias maps to `apps/web/*`, `allowImportingTsExtensions`.
- Raw API JSON is typed `any` only inside `api.ts` mapping; components consume typed `types.ts` shapes.

Styling → styling.md · API client → api.md
