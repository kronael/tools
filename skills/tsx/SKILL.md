---
name: tsx
description: Frontend React/Next.js. NOT for plain TypeScript without JSX (use ts).
when_to_use: "editing .tsx files or writing React components with JSX; web app security, CSP, response headers, Trusted Types, dangerouslySetInnerHTML, cookie flags, SES lockdown, harden, LavaMoat, supply chain"
---

# Frontend (React / Next.js)

ALWAYS Read `../software/code.md` before the first edit — it owns naming,
comments, design and the boring-code rules.
Requires `ts` skill for base TypeScript rules. Its Tooling section governs
here too: a new project runs on Bun with Biome, an existing one keeps its
tooling — scaffold with `bunx create-next-app@latest --biome`, never `npx`.

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

## Security — a deployed app

The browser never protects page code from the device owner: a client-side
check is advice. Header values and the lockdown script order: `security.md`.
A library ships no headers (its host app does); a prototype on localhost may
skip lockdown and Trusted Types, never the first three rules.

- ALWAYS check auth and access on the server, per request; NEVER let a
  client check, a hidden route or an obfuscated bundle stand in for one
- NEVER a secret in the bundle — every `VITE_*` / `NEXT_PUBLIC_*` value ships
  to every visitor; the key lives in a server route (`ops` § Configuration)
- ALWAYS the session in a `__Host-` cookie — `Path=/; Secure; HttpOnly;
  SameSite=Lax`; NEVER a token in `localStorage` or a JS-readable cookie
- ALWAYS send `Content-Security-Policy` as a response header from the server
  that serves the bundle, NEVER `<meta http-equiv>` (`frame-ancestors` is
  header-only): `script-src 'self'` for a static bundle, Next.js its
  per-request nonce with `'strict-dynamic'`; NEVER `'unsafe-inline'` or
  `'unsafe-eval'` in `script-src`
- ALWAYS `require-trusted-types-for 'script'`; `dangerouslySetInnerHTML` takes
  a `TrustedHTML` from a DOMPurify policy (`RETURN_TRUSTED_TYPE: true`), which
  React ≥ 19.3 passes through — NEVER a raw string from outside the bundle
- ALWAYS the rest of the header set with it: `X-Content-Type-Options`,
  `Referrer-Policy`, `Cross-Origin-Opener-Policy`, `Permissions-Policy`, HSTS
- NEVER a dependency a short local function replaces; NEVER a package in Bun
  `trustedDependencies` or pnpm `allowBuilds` whose install script you did not
  read; ALWAYS `minimumReleaseAge` (Bun `[install]`, seconds; pnpm, minutes)
- NEVER a CDN script in production — bundle it; a cross-origin script that
  must stay carries `integrity` and `crossorigin`
- ALWAYS check `event.origin` against the one expected origin in a `message`
  handler and name the target origin when posting; NEVER `'*'`
- NEVER terser `unsafe*` options unless `lockdown()` is on; `unsafe_math` and
  `unsafe_comps` stay off either way — floats and `valueOf`, not built-ins

### Object capabilities (SES)

Code has only the power of the references it is handed. A plain app needs
none of this — CSP, few dependencies and the server-side check suffice.
ALWAYS reach for it when the page runs third-party or plugin code, or holds
a key or token a script could read:

- `lockdown()` (`ses`) freezes the built-ins so no code can rewrite them;
  your own classes and objects stay normal. ALWAYS the first script on the
  page, before the bundle, then the whole test suite — a library that patches
  a built-in breaks. NEVER hand-rolled `Object.freeze(Object.prototype)`: the
  override mistake then throws on every assignment that shadows an inherited
  property; `lockdown` repairs it (`overrideTaming`).
- `harden(api)` freezes the object graph you hand to less-trusted code, so it
  can call the API and not rewrite it.
- `new Compartment(globals)` runs code with only the globals you pass — no
  ambient `fetch` or `document`. LavaMoat does this per package on webpack or
  browserify (no Vite plugin). A Worker or a sandboxed cross-origin iframe
  isolates DOM-free work. NEVER count on ShadowRealm (TC39 stage 2.7) or Wasm
  (its imports are JS the page supplies).
