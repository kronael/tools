---
name: browse
description: Browser automation via the agent-browser CLI. USE when a real browser is needed (login flows, screenshots, page interaction, DOM extraction). NOT for plain HTTP fetches. ALWAYS invoke via Bash tool — this is NOT an Agent subagent type, never pass it to Agent(subagent_type=...).
when_to_use: "login flow, screenshot, fill form, click button, DOM extraction, scrape page, interact with web app, browser automation, headless browser, Playwright"
allowed-tools: Bash(agent-browser:*)
---

# Browser Automation with agent-browser

## Core workflow

1. `agent-browser open <url>`
2. `agent-browser snapshot -i` (interactive elements with refs like `@e1`)
3. Interact using refs
4. Re-snapshot after navigation or significant DOM changes

## Commands

```bash
# Navigation
agent-browser open <url> | back | forward | reload | close

# Snapshot
agent-browser snapshot [-i interactive] [-c compact] [-d depth] [-s selector]

# Interact (use @refs from snapshot)
agent-browser click|dblclick|hover @e1
agent-browser fill @e2 "text"          # Clear and type
agent-browser type @e2 "text"          # Type without clearing
agent-browser press Enter
agent-browser check|uncheck @e1
agent-browser select @e1 "value"
agent-browser scroll down 500
agent-browser upload @e1 file.pdf

# Get info
agent-browser get text|html|value @e1
agent-browser get attr @e1 href
agent-browser get title|url
agent-browser get count ".item"

# Screenshot/PDF
agent-browser screenshot [path.png] [--full]
agent-browser pdf output.pdf

# Wait
agent-browser wait @e1 | 2000 | --text "Success" | --url "pattern" | --load networkidle

# Semantic locators (alternative to refs)
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"

# Auth state
agent-browser state save|load auth.json

# Storage
agent-browser cookies [set name value | clear]
agent-browser storage local [set k v]
agent-browser eval "document.title"
```

## Rules

- ALWAYS `agent-browser wait --load networkidle` (or wait --text/--url) BEFORE snapshot on dynamic pages; NEVER snapshot directly after `open` on SPAs — refs will be stale
- ALWAYS prefer `find role --name`, `find text`, `find label` over numbered `@eN` refs; `@eN` refs are valid only within one snapshot — NEVER reuse across navigations
- ALWAYS `agent-browser screenshot ./tmp/err.png --full` before reporting an unexpected failure

## Coordinate clicks (canvas, maps, custom renderers)

ALWAYS use `mouse` for coordinate-based clicks. JS `MouseEvent` has
`isTrusted=false` and is blocked by security-conscious apps; `mouse` sends
real CDP input events with `isTrusted=true`.

```bash
agent-browser mouse move 930 120
agent-browser mouse down
agent-browser mouse up
```

## Debugging: console, page errors, network, perf, memory

`agent-browser` snapshots and clicks but does NOT stream console logs, network,
or performance/heap. For DEBUGGING (console errors, "does scroll/interaction
refetch?", UI freezes, leaks) drive Playwright directly from a node script —
it exposes the CDP event streams `agent-browser` hides.

Setup once (browsers may be root-locked at the default `/opt` path → use a
writable local path):

```bash
export PLAYWRIGHT_BROWSERS_PATH=$PWD/tmp/pw
npx playwright install chromium-headless-shell   # ~2MB, no sudo needed
```

Capture everything in one script (`tmp/debug.mjs`, run `node tmp/debug.mjs`):

```js
import { chromium } from '@playwright/test'
const browser = await chromium.launch()             // headless OK for logs
const page = await browser.newPage()

page.on('console', m => console.log(`[${m.type()}]`, m.text()))   // console.* + warnings
page.on('pageerror', e => console.log('PAGEERROR', String(e)))    // uncaught throws
page.on('requestfailed', r => console.log('REQFAIL', r.url()))
const net = []
page.on('request', r => net.push(r.url()))          // count/inspect to test "refetch on X?"

await page.goto('http://localhost:5173/route', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('tbody tr', { timeout: 60000 })
const before = net.length

// Reproduce the interaction; TIME each step — a hang shows as a long step.
const steps = []
for (let i = 0; i < 12; i++) {
  const t0 = Date.now()
  await page.mouse.move(720, 450); await page.mouse.wheel(0, 1200)
  await page.waitForTimeout(120)
  steps.push(Date.now() - t0)
}
console.log('step ms', steps, 'requests during interaction', net.length - before)
await browser.close()
```

- **"Is it refetching on scroll/interaction?"** — count `net.length` before vs after; filter to the app's API hosts. Zero new requests ⇒ not a fetch problem.
- **UI freeze / jank** — time each interaction step (above); or a CDP perf trace: `const cdp = await page.context().newCDPSession(page); await cdp.send('Performance.enable')` then read `Performance.getMetrics` before/after, or `page.evaluate(() => performance.getEntriesByType('longtask'))`.
- **Memory / leak growth** — `const cdp = await page.context().newCDPSession(page); await cdp.send('Performance.enable'); const m = await cdp.send('Performance.getMetrics')` → read `JSHeapUsedSize`; sample it across repeated navigations to see if it climbs and never drops (a leak) vs plateaus (bounded). `page.goto` between samples.
- **Real APIs vs fixtures** — a Vite dev server (`pnpm start:dev`, :5173) hits live APIs, so network capture is meaningful; `/test-*` fixture routes issue no network. Pick the route that matches what you're testing.

Always `npx tsc`/build first if testing your own changes — a stale dev/preview build silently serves old code (a common "my fix didn't work" trap). Save artifacts under `./tmp`.
