---
name: htmx
description: Server-rendered HTML with htmx attributes. USE when editing .html templates with hx-* attributes (Jinja, Go html/template, Tera, Rails ERB, Phoenix HEEx) or when the project lists htmx in deps. NOT for React/JSX (use tsx). NOT for plain TypeScript (use ts).
user-invocable: false
---

# htmx (server-rendered HTML)

State lives on the server; DOM is a projection. For React, use `tsx`.

## Stack
- ALWAYS no client build step — `<script src="htmx.min.js">` (CDN or vendored), nothing to bundle
- Server: any language (Go/Python/Rust/Bun/etc.); template engine renders HTML fragments
- CSS: plain CSS, Pico.css, or Tailwind via CDN — no PostCSS pipeline by default
- NEVER reach for vite/webpack/JSX — if you find yourself wanting them, you're building React, use `tsx`

## Core attributes

| Attribute       | Use                                                    |
|-----------------|--------------------------------------------------------|
| `hx-get`        | GET, swap response                                     |
| `hx-post`       | POST                                                   |
| `hx-put` / `hx-patch` / `hx-delete` | Other HTTP verbs                   |
| `hx-target`     | Selector to swap (default: this element)               |
| `hx-swap`       | `innerHTML` (default), `outerHTML`, `beforeend`, `afterbegin`, `delete`, `none` |
| `hx-trigger`    | Event (default: `click` on buttons, `change` on inputs, `submit` on forms) |
| `hx-vals`       | Extra payload (`{...}` JSON or `js:...`)               |
| `hx-include`    | Extra elements to include in payload                   |
| `hx-push-url`   | Update browser URL on swap                             |
| `hx-boost`      | Progressive-enhance `<a>` / `<form>`                   |
| `hx-confirm`    | `confirm()` dialog before firing                       |
| `hx-indicator`  | Loading spinner selector                               |

## Server
- ALWAYS return HTML fragments, NEVER JSON for swap routes
- ALWAYS detect `HX-Request: true` header — fragment if present, full page otherwise (every endpoint works as nav fallback)
- `HX-Trigger: eventName` (or JSON map) response header fires client events post-swap (close modal, refresh sibling list)
- `HX-Redirect: /url` for full redirects, `HX-Refresh: true` to reload, `HX-Location` for client-side nav
- 4xx/5xx are NOT swapped by default — use `hx-target-4xx="..."` or global `htmx:responseError` listener

## DOM & swapping
- Swapped fragments are auto-processed for `hx-*`; no rebinding needed
- `hx-swap="outerHTML"` replaces the element itself — use when behaviour changes (Edit → Save button)
- `hx-swap-oob="true"` swaps an out-of-band element by id elsewhere on the page in same response
- `hx-preserve="true"` keeps an element across swaps (open details panel)

## Forms
- `hx-post` sends `application/x-www-form-urlencoded` (or multipart) — NEVER JSON
- Validation errors re-render the same form fragment with inline messages — no client-side validation duplication
- ALWAYS `hx-disabled-elt="this"` (or selector) to disable submit while in flight

## Progressive enhancement
- Every interactive element falls back to nav if JS disabled — `<a href>` or `<form action method>`; htmx hijacks when available
- `hx-boost="true"` on parent makes child `<a>`/`<form>` use AJAX swaps with `hx-push-url`

## Accessibility
- Swaps don't move focus — handle in response template (`autofocus`) or `hx-on::after-swap`
- Wrap async-updated content in `<div aria-live="polite">` for screen readers
- `hx-confirm` uses native `confirm()` (accessible); custom dialogs use `<dialog>` opened via `HX-Trigger`

## Performance
- Cache fragment GETs with normal HTTP cache headers — htmx respects them
- Debounced search: `hx-trigger="keyup changed delay:500ms"`
- Lazy-load: `hx-trigger="revealed"`; polling: `hx-trigger="every 10s"` (prefer SSE/WebSocket for real-time)

## Styling
- Read project `CLAUDE.md` for token system
- Tailwind: semantic classes (`bg-card`, `text-foreground`); scoped CSS: same rule
- NEVER raw hex literals in templates
