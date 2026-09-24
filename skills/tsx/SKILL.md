---
name: tsx
description: Frontend React/Next.js. NOT for plain TypeScript without JSX (use ts).
when_to_use: editing .tsx files or writing React components with JSX
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
- ALWAYS derive prop types from live (non-story/non-test/non-mock) call
  sites — that's the contract's source of truth, not what Storybook/tests
  find convenient
- NEVER keep a prop optional just to ease Storybook/test/mock setup — ALWAYS
  narrow the type and let the support code adapt to it
- NEVER guard an always-rendered affordance with `onX?.()` or `?? []`
  fallbacks for a value every live call site supplies — ALWAYS require it
- Nullable is not optional: prefer `x: T | null` over `x?: T | null` when
  every live call site passes the prop but the value can be empty

## Data & Forms
- Fetch in server components, pass down as props
- NEVER fetch in `useEffect` — use server components or React Query/SWR
- Server Actions for form submission, `useActionState` for validation
- ALWAYS forms work without JS (progressive enhancement)

## Styling
- ALWAYS use theme variables, NEVER hardcoded colours — not HEX, not a Tailwind
  palette entry, not an arbitrary value: `bg-card text-foreground border-border`,
  never `bg-[#1C1C1C] text-gray-50 border-gray-800`
- Theme variables live in `globals.css` as HSL without the wrapper;
  `tailwind.config.ts` extends from them
- When a colour looks wrong, ALWAYS fix the theme — NEVER reach for a hardcoded
  workaround at the call site

## Accessibility
- Semantic HTML (`button` not `div onClick`)
- `aria-label` on icon-only buttons
- NEVER suppress focus outlines without replacement
- Form inputs ALWAYS have labels
