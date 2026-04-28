---
name: tsx
description: Frontend React/Next.js. USE when editing .tsx files or writing React components with JSX. hooks, server/client components, Tailwind theming, forms, a11y. NOT for plain TypeScript without JSX (use ts).
requires: ts
---

# Frontend (React / Next.js)

Requires `ts` skill for base TypeScript rules.

## Components
- ALWAYS default to server components (no directive)
- `"use client"` only on smallest interactive leaf, NEVER at page level
- One component per file, filename matches export
- Colocate with route (`app/dashboard/components/`), shared at root `components/`

## Props & State
- Props as `interface` above component, destructured in signature
- NEVER pass >5 props — split into composition
- `useState` only for UI state (open/closed, selected tab)
- NEVER store derived data or sync props into state
- Complex client state: `useReducer` over multiple `useState`

## Data & Forms
- Fetch in server components, pass down as props
- NEVER fetch in `useEffect` — use server components or React Query/SWR
- Server Actions for form submission, `useActionState` for validation
- Forms SHOULD work without JS (progressive enhancement)

## Accessibility
- Semantic HTML (`button` not `div onClick`)
- `aria-label` on icon-only buttons
- NEVER suppress focus outlines without replacement
- Form inputs ALWAYS have labels
