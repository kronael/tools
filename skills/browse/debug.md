# Debugging a web app through Playwright

Read from `SKILL.md` when the question is what the page logged, fetched,
or leaked, not what it shows.

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

Always `npx tsc`/build first if testing your own changes — a stale dev/preview build silently serves old code (a common "my fix didn't work" trap).
