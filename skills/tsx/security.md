# Security headers and the lockdown script

Values for `SKILL.md` § Security. The server that serves the bundle sends
the headers on every HTML response; the cookie is set at login.

## The header set — static bundle, same-origin API

One `Content-Security-Policy` header, directives joined by `;`:

```http
Content-Security-Policy:
  default-src 'none'; script-src 'self'; style-src 'self';
  img-src 'self' data: blob:; font-src 'self'; connect-src 'self';
  object-src 'none'; base-uri 'none'; form-action 'self';
  frame-ancestors 'none'; require-trusted-types-for 'script';
  upgrade-insecure-requests
Cross-Origin-Opener-Policy: same-origin
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
Strict-Transport-Security: max-age=63072000; includeSubDomains
Set-Cookie: __Host-session=<id>; Path=/; Secure; HttpOnly; SameSite=Lax
```

- `connect-src`: add the API origin when it is not the page's. `data:` in
  `img-src` and `font-src` covers the small assets Vite inlines
  (`build.assetsInlineLimit: 0` removes the need). NEVER `data:` in
  `script-src`.
- `style-src 'self'`: React's `style` prop writes through the CSSOM, which
  CSP allows; a library that injects a `<style>` element or a server-rendered
  `style=` attribute violates it — a nonce covers `<style>`, nothing covers
  the attribute.
- Next.js emits inline scripts: follow its CSP guide — a nonce per request
  in `proxy.ts`, `script-src 'self' 'nonce-…' 'strict-dynamic'`, which forces
  dynamic rendering (no static pages, no PPR). `'unsafe-eval'` only in
  development.
- `Cross-Origin-Opener-Policy: same-origin` severs `window.opener`; an OAuth
  or payment popup needs `same-origin-allow-popups`.
- `Permissions-Policy` has limited browser support (MDN); it is harmless
  where unsupported.
- Roll-out on an existing app: `Content-Security-Policy-Report-Only` first,
  then every page with the devtools console open until no violation logs.

## Lockdown first

Copy `node_modules/ses/dist/ses.umd.js` into the static dir at build; two
classic scripts run in order before the deferred module bundle:

```html
<script src="/ses.umd.js"></script>
<script src="/lockdown.js"></script>
<script type="module" src="/assets/index.js"></script>
```

`lockdown.js` holds the one call `lockdown()`; `lockdown({ overrideTaming:
'severe' })` when Rollup or webpack output trips the override mistake. The
SES README prefers the separate script tag over bundling `ses`: a bundler is
one more supply-chain step.
