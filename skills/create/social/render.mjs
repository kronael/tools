// render.mjs — HTML file -> crisp PNG at an exact size.
// usage: node render.mjs <in.html> <out.png> [W] [H] [scale]
// Renders at deviceScaleFactor=scale so a WxH design exports (W*scale)x(H*scale) px.
import { chromium } from 'playwright-core'

const [inHtml, outPng, W = '1080', H = '1080', scale = '2'] = process.argv.slice(2)
if (!inHtml || !outPng) { console.error('usage: node render.mjs <in.html> <out.png> [W] [H] [scale]'); process.exit(1) }

const width = parseInt(W, 10), height = parseInt(H, 10), dsf = parseFloat(scale)
const path = inHtml.startsWith('file://') || inHtml.startsWith('http') ? inHtml : 'file://' + inHtml

const browser = await chromium.launch({ executablePath: process.env.CHROME, args: ['--no-sandbox'] })
const page = await browser.newPage({ viewport: { width, height }, deviceScaleFactor: dsf })
await page.goto(path, { waitUntil: 'load', timeout: 15000 })
await page.evaluate(() => document.fonts && document.fonts.ready)
// overflow guard: report if content exceeds the fixed canvas
const over = await page.evaluate((h) => {
  const b = document.body
  return Math.max(b.scrollHeight, document.documentElement.scrollHeight) - h
}, height)
if (over > 2) console.error(`WARN: content overflows canvas by ${over}px (unscaled)`)
await page.screenshot({ path: outPng, clip: { x: 0, y: 0, width, height } })
await browser.close()
console.log(`wrote ${outPng} @ ${width * dsf}x${height * dsf}`)
