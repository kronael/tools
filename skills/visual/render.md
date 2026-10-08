# Render — commands and format gotchas

Read from `SKILL.md` in this directory before the first render.

## Web UI

Headful is required for faithful rendering — fonts, subpixel AA, real layout,
hover and focus states. On a server with no display:

```bash
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99
```

Then, through the `browse` skill's CLI:

```bash
agent-browser open http://localhost:3000/route   # or file:///abs/path.html
agent-browser hover @e1                          # exercise states before the shot
agent-browser screenshot /tmp/ui.png [--full]
```

## Non-browser renders

```bash
rsvg-convert -w 400 -h 400 logo.svg -o /tmp/preview.png
pdftoppm -png -f 1 -l 1 file.pdf /tmp/out
```

## SVG gotchas

- NEVER use `<text>` elements — unreliable across contexts, favicons above
  all. Convert text to paths or skip it.
- NEVER use a gradient without a unique id — two SVGs on one page break each
  other. Prefer solid colours.
- NEVER use SVG for `og:image`/`twitter:image` — X's card crawler does not
  render SVG and drops the image silently, no error, just no card. Ship a
  rasterized PNG/JPG (1200x630), generated from the same SVG at build time so
  it cannot drift.
- Stroke widths for a 100x100 viewBox: thin details `stroke-width="2"`, main
  elements `4-5`, `stroke-linecap="round" stroke-linejoin="round"` for smooth
  joins.

## Email templates

- Inline CSS only, no external stylesheets.
- Table layouts, not flexbox or grid.
- Max 600px width.
- Touch targets 44px minimum.
