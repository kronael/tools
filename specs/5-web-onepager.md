# Web One-Pager: README as Terminal-Native Landing

## TL;DR

Turn `README.md` into a dense, single-scroll landing that reads like a TUI in
the browser. Five anchor visuals carry the explanation: a session asciicast
above the fold, a bundle architecture diagram, an install + hook lifecycle
flow, a skill catalog grid, and a dockbox sandbox illustration. No separate
site — GitHub renders it. Eval-style copy at the top (what is it, install in
30 seconds), contributor-style depth below (architecture, lifecycle, extend).

## Goals

- **G1**: A user landing on `github.com/kronael/tools` should know *what it is*
  and *how to try it* within 30 seconds of scrolling.
- **G2**: A contributor scrolling further should see *how it's structured*
  and *where to plug in* without leaving the README.
- **G3**: Aesthetic matches the ratpoison philosophy — mono, dense, ASCII
  boxes, dark by default (GitHub dark mode renders code blocks dark anyway).
- **G4**: All assets live in the repo. No external CDNs, no broken-image
  surprises after a year.
- **G5**: One source of truth per fact. Detailed reference (full skill
  catalog, hook architecture, dockbox internals) lives in
  `skills/README.md`, `hooks/README.md`, etc. The landing teases and
  links — never duplicates and maintains in two places.

## Non-goals

- A separate static site (`docs/`, `website/`, `github.io`). Re-evaluate
  if README grows past ~600 lines.
- A custom domain (kronael.com etc.).
- Interactive demos that require a backend.
- Marketing-style hero copy. Terse, descriptive, technical.

## Constraints (GitHub README renderer)

The renderer enforces what's possible:

| Rule | Implication |
|---|---|
| No `<style>`, no `<script>` | Can't theme; rely on GitHub's dark/light themes |
| `<img>` allowed with sanitized attrs | SVG is in, but inline event handlers stripped |
| Code blocks render mono, themed | ASCII diagrams in fences = free dark-mode TUI feel |
| `<picture>` + `prefers-color-scheme` works | Light/dark image swap is supported |
| Tables render but cap at ~viewport width | Skill catalog grid: prefer ASCII boxes over big tables |
| Anchor links `#section` work | Use a dense TOC for "jump to" navigation |

**Strategy**: ASCII diagrams in fenced code blocks for inline density; SVGs
for the hero asciicast and the architecture/flow figures that need shapes
and color encoding code blocks can't carry. Dual-asset SVGs (light/dark)
under `<picture>` so both GitHub themes look correct.

## Page layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. HERO          Title + tagline + asciicast (30s install + use)     │ ABOVE
│ 2. TL;DR         3-line plain-English + 1 install command            │ FOLD
├──────────────────────────────────────────────────────────────────────┤
│ 3. INSTALL       Plugin path + say-install path, both end at same    │
│                  SKILL.md (small ASCII flow diagram)                 │
│ 4. WHAT'S IN     Category teaser (1 line per family) + link to       │ EVAL
│                  skills/README.md for the full catalog               │ ZONE
│ 5. WHY IT HELPS  3-4 toolkit on/off contrasts (session output pairs) │
├──────────────────────────────────────────────────────────────────────┤
│ 6. ARCHITECTURE  Bundle layout: skills/agents/hooks/wisdom →         │
│                  ~/.claude/ + which paths are LLM-procedural         │ DEPTH
│ 7. HOOK CYCLE    UserPromptSubmit / Stop / PreCompact diagram —      │ ZONE
│                  what fires when, what each script does              │
│ 8. DOCKBOX       Sandbox mounts/overmounts illustration; tmpfs vs    │
│                  volume backends                                     │
├──────────────────────────────────────────────────────────────────────┤
│ 9. CLI TOOLS     Compact list — dockbox/rig/tw-fetch/tg-fetch/etc.   │ REF
│ 10. EXTEND       How to add a skill / agent / hook (links into       │ ZONE
│                  wisdom/, skills/README.md, hooks/README.md)         │
│ 11. DOCS         Existing docs table (already in README — move down) │
└──────────────────────────────────────────────────────────────────────┘
```

Reading rhythm: scroll past the hero, you're already deciding. Scroll past
the architecture, you're contributing.

## Anchor visuals — catalog

Five named visuals carry the page. Each gets a name, format, source skill,
and target placement.

### V1: Hero asciicast — "install + first session"

- **Show**: 25–35 seconds. Open empty dir → say "install" → see the install
  procedure run → ask Claude to do something small (commit a fix) → see
  hooks fire (stop hook nudge, commit format) → done.
- **Why**: Convinces the reader the system works without them reading prose.
- **Format**: `asciinema` recording → `agg` (asciinema-gif) for a static
  preview AND `asciinema/asciinema-player` SVG for the click-to-play asset.
  GitHub blocks the player JS, so embed as a linked SVG poster that points
  to an asciinema.org URL OR ship the raw `.cast` and link "download &
  replay with `asciinema play`".
- **Tooling**: asciinema (record), agg (gif convert), `svg-term-cli` for
  static SVG snapshot if `agg` GIF artifacts look bad. All local-only.
- **Asset path**: `assets/hero.svg` (static), `assets/hero.cast` (raw).
- **Placement**: top of README, single `<picture>` tag with light/dark
  variants, wrapped in `<a href="hero.cast">` link.

### V2: Architecture diagram — "what's in the bundle"

- **Show**: A 3-column flow: source repo (left) → install procedure
  (middle) → `~/.claude/` (right). Each lane shows skills, agents, hooks,
  wisdom, settings, RECLAUDE. Arrows annotated with who copies what.
- **Why**: Answers "what does this actually deploy and where".
- **Format**: SVG, hand-drawn-feeling (Excalidraw-style). One light, one
  dark, swapped via `<picture>`.
- **Tooling**: `/create-excalidraw` skill emits Excalidraw JSON → render
  to SVG. Light/dark via Excalidraw theme export.
- **Asset path**: `assets/architecture-{light,dark}.svg`.
- **Placement**: section 6, full-width.

### V3: Install + hook lifecycle — single combined flow

- **Show**: Two parallel install paths converging on `kronael/install/SKILL.md`
  (top half), then a timeline of when each hook fires during a session
  (bottom half): UserPromptSubmit → tool calls → Stop → next prompt →
  PreCompact. Each hook annotated with which script and what it does.
- **Why**: Most-asked questions, answered visually.
- **Format**: ASCII flow in a fenced code block — fits the terminal-native
  brief and stays in source for free.
- **Tooling**: hand-drawn ASCII; `/create-architecture-diagram` can
  produce an SVG companion if the ASCII gets unwieldy.
- **Asset path**: inline in README (no file). Optional
  `assets/hook-lifecycle.svg` if SVG version added later.
- **Placement**: sections 3 (install half) + 7 (hook half) — same diagram
  split, or two halves shown side-by-side.

### V4: Skill category teaser

- **Show**: One line per family with a count and a 3-word tagline:
  `Languages (7)  go/py/rs/ts/sql/sh/tsx — codestyle per language`,
  `Workflow (14)  /commit /ship /refine /diary …`,
  `create-* (12)  HTML mockups, SVG diagrams, ASCII art …` etc. Six
  lines max. Followed by a one-line link: *"Full catalog →
  `skills/README.md`"*.
- **Why**: The eval reader needs to know "yes, lots, organized" — not
  to read 40 names. The catalog itself stays in `skills/README.md` as
  the one source of truth.
- **Format**: 6-line fenced code block, mono spacing aligned. No box
  drawing — just a clean tabular list.
- **Tooling**: hand-written. If a category grows past ~10 entries,
  the counts in the teaser will drift — easy to spot in a review.
- **Asset path**: inline.
- **Placement**: section 4.

### V5: Dockbox sandbox illustration

- **Show**: The container with three mount lanes — read-only host
  (`~/.gitconfig`, etc.), read-write `~/.claude`, ephemeral overmounts
  (`node_modules`, `.next`, `dist`, …). Arrow showing
  `settings.local.json` overmount that disables sandbox inside the
  container even when host has `sandbox.enabled: true`.
- **Why**: Demystifies the "why is this safe" question for the sandboxed
  workflow.
- **Format**: SVG (light/dark pair). The mount geometry is hard to do in
  ASCII without becoming a wall of text.
- **Tooling**: `/create-excalidraw` or
  `/create-architecture-diagram` skill.
- **Asset path**: `assets/dockbox-{light,dark}.svg`.
- **Placement**: section 8.

## Why it helps — toolkit on/off contrasts (section 5)

Three or four short side-by-side pairs showing what a Claude session
looks like *without* the toolkit installed (left) and *with* it
(right). Proof-by-contrast: the reader sees the value without prose.

- **Commit message** — bare Claude: `update stuff`. With toolkit:
  `[skills] Refresh commit hook nudge for amend rule`.
- **Stop check** — bare Claude: silent "done" with uncommitted work.
  With toolkit: `Uncommitted changes detected. Consider running /commit.`
- **Memory recall** — bare Claude: "no access to previous sessions".
  With toolkit: `/recall-memories <topic>` surfaces the actual answer.
- **Diary** — bare Claude: no record across sessions. With toolkit:
  `.diary/YYYYMMDD.md` auto-prompted after significant work.

Each pair is one fenced code block, terminal-session style, two columns
separated by a `│` divider. Each <8 lines. No A/B testing connotation —
purely "Claude alone vs Claude with this toolkit".

## Style guide

- **Mono, dark, dense**. Code fences carry the look on both GitHub themes.
- **Box-drawing chars**: `┌ ─ ┐ │ └ ┘ ├ ┤ ┬ ┴ ┼ ▶ ◀`. Avoid heavy
  Unicode (`╔ ═ ╗`) — clashes with the terminal-native brief.
- **Headings**: H1 once (title). H2 for sections. H3 for sub-callouts.
  Skip H4+ — collapse instead.
- **Inline links**: always relative within the repo (`[CLAUDE.md](CLAUDE.md)`)
  so they work in the rendered README and in cloned-checkout views.
- **Tagline**: a single sentence under H1. Already in `package.json`-ish
  language (`Skills, agents, hooks for daily Claude Code`).
- **No emoji**. Project-wide rule applies to docs.
- **SVG palette**: foreground `#e6e6e6` (dark), `#1a1a1a` (light text on
  light bg). Accent: `#ff9000` or similar single-color highlight, used
  sparingly for arrows/flow direction.

## Implementation phases

Land in this order — each phase is independently mergeable.

| Phase | Output | Skill / tool |
|---|---|---|
| 1 | README skeleton with the 11-section TOC + placeholders | manual |
| 2 | V4 category teaser + link to skills/README.md | manual |
| 3 | V3 install + hook lifecycle ASCII | manual |
| 4 | V5 callouts | manual |
| 5 | V2 architecture SVG (light/dark) | `/create-excalidraw` |
| 6 | V5 dockbox SVG (light/dark) | `/create-excalidraw` |
| 7 | V1 hero asciicast (raw + static SVG) | `asciinema` + `agg` |
| 8 | Refactor existing README content into new structure | manual |
| 9 | Sweep links + verify GitHub renders correctly | manual |

Each phase commits as `[docs] <phase>` to keep history readable.

## File layout

```
README.md                                     # the landing
assets/
  hero.svg                                    # asciicast static preview
  hero.cast                                   # raw recording
  architecture-light.svg
  architecture-dark.svg
  dockbox-light.svg
  dockbox-dark.svg
specs/5-web-onepager.md                       # this spec
```

`assets/` is new — no existing convention says otherwise. Keep it flat;
prefix files when there are >10 (`hero-*`, `arch-*`).

## Open questions

- **Asciicast hosting**: link to asciinema.org (cleaner UX, click-to-play)
  vs ship only `.cast` (no external dependency, but worse first-time
  experience)? Lean: ship raw `.cast` + a static SVG poster. asciinema.org
  link in the alt text as an optional convenience.
- **Light/dark SVG pairs vs single neutral**: pairs cost 2× the work for
  every figure. Single neutral palette (mid-grey background, high-contrast
  fg) works on both themes — uglier but cheaper. Lean: pairs for the
  hero/architecture, neutral for one-off small figures.
- **Category counts staleness**: the teaser counts (`Languages (7)`,
  `Workflow (14)`, …) drift on every skill add/remove. Lean: accept
  the drift — a review-time grep catches mismatches and the full
  catalog stays in `skills/README.md`, which is the source of truth.
- **README length**: target ~500 lines max. Current README is ~94 lines.
  We'll roughly 5× it. If a section starts to dominate, split out to a
  dedicated `docs/<topic>.md` and link from the one-pager.
- **`docs/` vs `assets/`**: GitHub Pages convention names the published
  dir `docs/`. We're not publishing yet, so `assets/` avoids confusion.
  If we ever stand up a Pages site, asset dir gets symlinked/migrated.
