---
paths:
  - "apps/web/**/*.tsx"
  - "apps/web/index.html"
---
# Styling

- Tailwind CSS loaded from the CDN (`<script src="https://cdn.tailwindcss.com">` in `apps/web/index.html`); no PostCSS build, no `tailwind.config.js` file.
- Theme extensions live in the inline `tailwind.config` in `index.html`: font `Inter`; colours `primary` #4F46E5, `secondary` #64748B, `success` #10B981, `warning` #F59E0B, `danger` #EF4444. Use these names (`bg-primary`, `text-danger`) instead of new hex values.
- Global CSS is only the scrollbar styles in `index.html`; there are no CSS files or CSS modules.
- Styles are utility classes in `className` on the component itself; conditional classes via template literals (see `components/ui/StatCard.tsx`).
- Component layout: `pages/` (screens), `components/` (shared), `components/ui/` (primitives like `StatCard`), `components/badges/` (CMRA/RDI/Source badges, re-exported from `badges/index.ts`).
- Icons from `lucide-react`; charts from `recharts`.
- Avoid inline `style={{}}` for layout and `!important`; prefer existing Tailwind utilities and the default breakpoints (`sm`/`md`/`lg`, mobile-first).

TypeScript conventions → typescript.md
