# Research: High-Retention Single-Image Social Posts for Technical Projects

Methodology for turning ONE claim about a technical open-source project into ONE
square image that stops a skeptical engineer mid-scroll on the X/Twitter timeline.
Every rule below is grounded in a named source; see **Sources**.

**In scope:** one static square (~1:1, 1080x1080) image, posted natively to the
X timeline. **Explicitly out of scope:** multi-image threads, video/GIF,
carousels, full landing pages, print posters, and paid-ad creative specs. Those
have different mechanics and are not covered here.

## Persona & context

The target viewer is a senior engineer scrolling X: skeptical, pattern-matching
against marketing, and allergic to hype. They do not read; they scan. Nielsen
Norman Group's eye-tracking work shows users read *at most* 28% of the words on a
page and more realistically ~20%, scanning in an F-shaped pattern rather than
reading linearly (NN/g, "How Little Do Users Read?"; NN/g, "F-Shaped Pattern").
On a fast-moving feed the budget is smaller still — roughly **0.5-2 seconds** per
image before the thumb keeps moving.

Worse, this viewer has *banner blindness*: NN/g's repeated eye-tracking studies
find people actively skip elements that look like ads — generic, decorative,
templated blocks get filtered out before they are read (NN/g, "Banner Blindness
Revisited"). An image that looks like a marketing template is not neutral; it is
a signal to look away. What earns this viewer's attention and their retweet is
the opposite of a brochure: a concrete, falsifiable, slightly opinionated claim
that reads as *something a real engineer would say*. swyx's "Learn in Public"
and Kent C. Dodds's "teach in public" both converge on the same currency with
this audience — you earn credibility by showing real work and "doing cool shit,"
not by polishing adjectives (swyx, "Learn In Public"; Kent C. Dodds).

## Principles

**Scroll-stop: one idea per image.** The image must carry exactly one claim. If a
viewer cannot state the point after a 1-second glance, it is too complex. Buffer's
guidance is blunt: every post should have *one* clear goal — provoke a comment,
a save, or a share (Buffer, "State of Social Media Engagement"). Facebook's
now-retired 20%-text rule was dropped in 2021, but the finding behind it holds:
images with *less* overlay text measurably outperform text-crowded ones because
users process visuals faster than dense text (Search Engine Journal; HubSpot).
One idea, minimal text.

**Legibility at thumbnail size.** A 1080px image renders at roughly ~500px wide
in-feed, so on-canvas type must be oversized. Sprout Social / Hootsuite guidance
is that text meant to be read on a phone should land at ~16-18px *in its final
on-screen render* (Sprout Social; Hootsuite, "Social Media Design"). Working
backward from the ~500/1080 downscale, that means the **smallest text on the 1080
canvas must be ≥40px; the headline ≥90px.** Keep to ≤3 fonts and set text bold
(Sprout Social). Contrast is not optional: WCAG 1.4.3 requires **4.5:1** for
normal text and **3:1** for large text (≥24px, or bold ≥18.66px), and WCAG 1.4.5
holds *images of text* to the same standard (W3C WAI). Treat 4.5:1 as the floor
ALWAYS.

**Avoid the ad-shaped template.** Because banner blindness filters ad-like blocks
(NN/g), the layout itself must not read as generic marketing. This is the
mechanism behind the "AI slop" complaint: a gradient background + three equal
cards + hedged copy *is* the banner-blindness trigger. The counter-move is a
point of view and asymmetric, editorial layout (see Anti-slop tells).

## Modes

Pick exactly one mode per image based on what kind of proof you hold.

**1. HOT-TAKE card.** *Use when* you have a sharp, falsifiable opinion about the
project or its space. Layout: a large left-aligned statement filling most of the
canvas, ONE word or phrase set in the accent color, tiny project handle/logo
bottom-left. No subtitle unless it adds a concrete fact. The POV is the product;
Harry Dry's rule that copy be *falsifiable* is what separates a hot-take from a
platitude (Harry Dry / Marketing Examples).

**2. CODE-SHOT.** *Use when* the code itself is the punchline — a tiny API, a
surprising one-liner, a diff. Style it like Carbon/ray.so: syntax-highlighted
monospace on a dark card with generous padding. This aesthetic works because the
artifact keeps its semantic structure (syntax tokens, line numbers) and reads as
*real code*, not a marketing mock; Carbon has ~34k GitHub stars precisely for
this (Carbon; ray.so). Keep to **≤12 lines**, one accent-colored line or token,
and a single one-line caption above or below stating the takeaway.

**3. BEFORE/AFTER comparison.** *Use when* you can show a concrete delta —
lines of code, latency, step count, dependency count. Layout: two stacked or
side-by-side panels, muted/red "before", accent "after", and the numeric delta
as the largest element. Developer-viral analyses repeatedly flag before/after
and side-by-side comparisons as high-engagement because they show a shared
struggle resolving (SupaBird, "What Makes Developer Posts Go Viral").

**4. STAT / PUNCHLINE.** *Use when* you have ONE concrete, credible number. Layout:
the number as the hero element (≥300px tall), a single line of context beneath,
and a micro-caption naming the source of the figure. Numeric hooks beat vague
ones — "10 tools" outperforms "some tools" (SupaBird) — but the number must be
concrete and credible, never a vague "scales to 100k customers" with no basis.

*Meme templates (Drake, expanding-brain, "nobody: / me:") are deliberately not a
default mode.* By the time a format reaches a marketing roundup it is past peak,
and forcing a project into a borrowed format is the most common way brand memes
read as cringe (Superside; Flickmeme). Use one ONLY if it is genuinely current
and self-aware; otherwise prefer the four modes above.

## Per-image protocol

1. **State the claim in one sentence.** Write the single thing this image must
   land. If you cannot, you have more than one idea — split or cut.
2. **Make it concrete and falsifiable.** Run Harry Dry's zoom-in: rewrite until
   the claim names a concrete object, number, or outcome, not an adjective
   (Harry Dry). "1,000 songs in your pocket," not "huge capacity."
3. **Pick the mode** by proof type: opinion → HOT-TAKE; code is the point →
   CODE-SHOT; measurable delta → BEFORE/AFTER; one number → STAT.
4. **Write the hook.** ≤8-10 words, one strong verb, a specificity or
   curiosity gap that makes the viewer want the *how* (Julian Shapiro).
5. **Cut to the word budget.** Total on-image words ≤20-25 excluding code (see
   Copy rules). Delete every hedge and filler subtitle.
6. **Choose ONE accent color** plus a neutral background and near-white/near-black
   text. Assign the accent to the single most important word/number only.
7. **Lay out on the 1080 grid.** Left-align or offset the hero; do NOT center
   everything. Keep critical text/logo ≥64px from every edge and within the
   central horizontal band as crop insurance.
8. **Render at 1080x1080 PNG.**
9. **Validate** against the template below (thumbnail test, contrast, alt text)
   before posting.

## Copy rules

- **Hook ≤ 8-10 words.** One idea, one verb. Lead with the specific benefit or
  the surprising fact (Julian Shapiro; SupaBird).
- **Total on-image words ≤ 20-25** (excluding a code snippet). Fewer words render
  larger and survive the thumbnail. Less text also outperforms dense text on
  engagement (Search Engine Journal).
- **Numbers over adjectives, ALWAYS.** A concrete figure ("47ms p99", "12 lines",
  "3 deps") beats "fast", "simple", "lightweight" (Harry Dry; SupaBird).
- **Make it falsifiable.** The claim should be checkable, not a vibe. Vague scale
  claims ("scales to 100k customers") without a concrete, credible basis read as
  marketing and lose the skeptical engineer (Harry Dry; NN/g banner blindness).
- **NEVER hedge.** Kill "can help", "designed to", "aims to", "one of the best".
  State the claim plainly and take the position.
- **Talk in benefit to the reader, not self-congratulation** (Julian Shapiro).
- **No emoji sprinkler.** At most zero-to-one emoji, and only if it carries
  meaning.

## Output & validation template

- **Dimensions:** 1080x1080 px, 1:1, PNG, sRGB. (Alternative for maximum mobile
  footprint: 4:5 at 1080x1350, which occupies more vertical feed space than a
  square, per Sked Social / Sprout Social — use only if the deliverable is not
  fixed at square.)
- **Safe area:** all essential text and logo within a ~952px central square
  (≥64px margins); keep the message inside the central horizontal band since some
  render/crop contexts favor a ~16:9 view.
- **Type scale:** headline ≥90px, secondary ≥48px, smallest text ≥40px on the
  1080 canvas (so it clears ~16-18px on-screen at feed size — Sprout Social).
- **Thumbnail-legibility test:** downscale the image to 500px wide (or view it at
  arm's length / squint). If the hook is not readable and the one idea not
  obvious in ~1 second, cut words and enlarge type. This operationalizes the
  0.5-2s scan budget (NN/g).
- **Contrast check:** verify hook and body text at ≥4.5:1 against their
  background (WCAG 1.4.3 / 1.4.5, W3C WAI). ONE accent + neutral only.
- **Alt text:** ALWAYS supply alt text that transcribes the on-image text and
  names the visual, so the claim survives for screen-reader users (WCAG images
  of text principle, W3C).
- **Link placement:** keep the repo/external link OUT of the image-bearing post
  and put it in a reply. X's open-sourced ranking reportedly cuts reach 50-90%
  for posts with off-platform links, while native media gets roughly a ~2x boost
  (X open-source algorithm, via Sprout Social / SocialPilot, 2026). Treat these
  figures as directional, not exact.

## Anti-slop tells → fixes

| AI-slop tell | The opposite move |
| --- | --- |
| Generic gradient / glow background | Flat neutral or one solid brand color; let type carry the design |
| Three equal cards / pillar grid | ONE hero element; asymmetric, editorial layout |
| Everything centered and symmetric | Left-align or offset the hook; break the axis |
| Hedged copy ("helps you", "designed to") | Plain, falsifiable claim with a POV |
| Filler subtitle restating the title | Delete it, or replace with one concrete fact/number |
| Emoji sprinkler | Zero-to-one meaningful emoji max |
| Vague adjectives ("fast", "powerful") | Concrete number or code (Harry Dry) |
| Multiple accent colors competing | ONE accent on the single key word/number |
| Tiny paragraph of body text | ≤20-25 words, ≥40px, thumbnail-legible |
| Borrowed meme template, forced | Native hot-take / code-shot; meme only if current & self-aware |

## Pitfalls

- **Two ideas in one image.** The most common failure. One image = one claim.
- **Code screenshot too dense.** >12 lines becomes an unreadable gray block at
  feed size; trim to the lines that *are* the point (Carbon aesthetic works
  because it stays a focused artifact).
- **Font too small "because it fits".** If it fits at 24px it fails the
  thumbnail test — cut words, do not shrink type (Sprout Social).
- **Uncredible numbers.** A big round number with no basis reads as marketing and
  the skeptical viewer disengages (NN/g banner blindness; Harry Dry falsifiable).
- **Link in the image post.** Costs reach; move it to a reply (X algorithm).
- **Stale meme format.** Drake/expanding-brain past peak reads as out-of-touch
  (Superside; Flickmeme).
- **Optimizing for claps.** swyx's warning: chase the artifact's quality, not the
  vanity metric; a real, useful claim compounds (swyx).

## Corrections (post-codex)

Adversarial critique in `codex-critique.md` corrected this doc; the SKILL
embodies the corrected version, not the numbers as first stated:

- **Evidence gate added.** The doc had no step forcing a real, checkable fact
  before design — the single biggest slop hole. The SKILL adds Gate 0: pull a
  concrete artifact from the repo (command output, LOC, binary size, real API,
  benchmark) or stop.
- **Folklore cut.** The "50–90% link-reach loss / ~2× native boost" figures are
  not stable measurements — removed. Kept only: post native media, link in a reply.
- **Thresholds are defaults, not laws.** ≥40px/≥90px follow only from a fixed
  1080→~500 downscale (40×500/1080 = 18.5px); real X render varies. The 0.5–2s
  dwell, ≤12 code lines, 8–10 hook words, 20–25 total, 64px margins are house
  defaults — useful floors, not findings.
- **Hedging rule split.** Kill *marketing* hedges ("helps", "designed to");
  keep *technical* qualifiers (version, workload, hardware). Precision ≠ hedging.
- **Modes collapsed 4 → 3** (CODE / DELTA / TAKE), keyed by hero element; a
  numeric delta lives in DELTA, so STAT/BEFORE-AFTER no longer overlap.
- **Transferability test added.** If the hook fits any other project, it is slop.
- **4.5:1** kept as an opinionated floor, noted stricter than WCAG (3:1 for large text).

## Sources

- Nielsen Norman Group — "How Little Do Users Read?" (users read ~20-28% of words)
  https://www.nngroup.com/articles/how-little-do-users-read/
- Nielsen Norman Group — "F-Shaped Pattern For Reading Web Content"
  https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content/
- Nielsen Norman Group — "Banner Blindness Revisited: Users Dodge Ads on Mobile and Desktop"
  https://www.nngroup.com/articles/banner-blindness-old-and-new-findings/
- W3C WAI — Understanding SC 1.4.3 Contrast (Minimum)
  https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- W3C WAI — SC 1.4.5 Images of Text (contrast/accessibility of text in images)
- Sprout Social — "Always Up-To-Date Guide to Social Media Image Sizes" (font legibility, safe zones, ≤3 fonts, aspect ratios)
  https://sproutsocial.com/insights/social-media-image-sizes-guide/
- Hootsuite — "10 Social Media Design Tips To Stand Out on the Feed"
  https://blog.hootsuite.com/social-media-design/
- Sked Social — "X (Twitter) Image Size Guide" (1:1 = 1200x1200, 4:5 = 1080x1350, 16:9 crop behavior)
  https://skedsocial.com/blog/twitter-post-size-guide
- Buffer — "The State of Social Media Engagement" / content-format analysis (one clear goal per post)
  https://buffer.com/resources/state-of-social-media-engagement-2026/
- Julian Shapiro — "Startup Handbook: Landing Page Copywriting" (specificity, curiosity, benefit over self-congratulation)
  https://www.julian.com/guide/startup/landing-pages
- Harry Dry / Marketing Examples — concrete, visual, falsifiable; "1,000 songs in your pocket"; zoom-in technique
  https://marketingexamples.com/
- swyx — "Learn In Public" (do cool shit; don't chase claps)
  https://swyx.io/learn-in-public
- Kent C. Dodds — teach in public / high-quality content for experienced devs
  https://kentcdodds.com/about
- Carbon — "Create and share beautiful images of your source code" (~34k stars; artifact fidelity)
  https://github.com/carbon-app/carbon  /  https://carbon.now.sh/
- ray.so — code-to-image tool (Raycast)
  https://www.ray.so/
- Superside — "15 Best Meme Marketing Examples" (formats past peak; forced memes backfire)
  https://www.superside.com/blog/meme-marketing-examples
- Flickmeme — "Meme Marketing 101: How Brands Use Memes Without Cringe"
  https://flickmeme.com/blog/meme-marketing-for-brands
- SupaBird — "What Makes Developer Posts Go Viral on X (Twitter)" (hooks, numbers, before/after, visuals)
  https://supabird.io/articles/what-makes-developer-posts-go-viral-on-x-(twitter)
- Search Engine Journal — "Facebook Removes the 20% Text Limit on Ad Images" (less text outperforms)
  https://www.searchenginejournal.com/facebook-removes-the-20-text-limit-on-ad-images/381844/
- Sprout Social / SocialPilot — X open-source algorithm coverage (native media boost; external-link reach penalty). Directional, not exact.
  https://sproutsocial.com/insights/twitter-algorithm/  /  https://www.socialpilot.co/blog/twitter-algorithm
