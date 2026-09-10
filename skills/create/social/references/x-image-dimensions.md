# X (Twitter) single-image dimensions for uncropped in-feed display

Scope: a SINGLE image posted natively to the X timeline, displayed uncropped
in-feed (not just when tapped). Current as of 2025-2026.

## Recommended (use these)

**(a) Meme (Drake-style, two stacked portrait panels):**
- Primary: **4:5, 1080 x 1350 px** — shows fully in-feed, dominates the mobile
  feed, safely inside X's uncropped band.
- Max vertical presence: **3:4, 1200 x 1600 px** — the tallest ratio X shows
  uncropped. Slightly more feed real estate than 4:5, but 4:5 is the rounder,
  safer, more universally-cited choice. Do NOT use 1:1 for a portrait meme (you
  leave vertical space unused). Keep the panel split centered; X only crops if
  you exceed 3:4.
- Format PNG (crisp text/lines), under 5 MB.

**(b) Square explainer:**
- **1:1, 1080 x 1080 px.** Displays uncropped everywhere, large in-feed, zero
  surprises. PNG, under 5 MB.

Landscape alternative if ever needed: **16:9, 1600 x 900 px** (fills timeline
width, the most predictable uncropped format).

## Evidence

**TechCrunch (2021-05-05, primary reporting on the change)** — X stopped
auto-cropping single timeline images: "standard aspect ratio images (16:9 and
4:3) will now display in full without any cropping," and the composer now shows
a preview that matches the timeline (WYSIWYG). Super-tall/super-wide images
outside the standard range are still center-cropped.
https://techcrunch.com/2021/05/05/twitter-image-cropping-changes/
(4:3 landscape = 1.33; its portrait inverse 3:4 = 0.75 is the tall bound.)

**aspectratiocalculator.com (2026)** — no-crop range is 2:1 (landscape) to 3:4
(portrait); "Twitter will crop your tall images at a maximum of 3:4 aspect
ratio." Recommends 16:9 at 1600x900. Max resolution 4096 x 4096 px; up to 5 MB
JPEG/PNG/WebP, 15 MB GIF.
https://aspectratiocalculator.com/twitter-aspect-ratios/

**Influencer Marketing Hub (2026)** — "X supports image aspect ratios between
2:1 and 1:1 before aggressive cropping begins"; states 4:5 (1080x1350) "displays
without cropping" in timelines. Landscape 1200x675, square 1080x1080.
https://influencermarketinghub.com/twitter-image-size/

**Sprout Social (Always-Up-To-Date guide)** — X "removed automated cropping for
vertical images, so standard 4:3 or 16:9 images display without unexpected
cuts"; unusual dimensions still crop. Landscape 1600x900 (min 1024x512), square
1080x1080, portrait 1080x1350. Max 5 MB (15 MB GIF); JPG/GIF/PNG. Preview in
composer before publishing.
https://sproutsocial.com/insights/social-media-image-sizes-guide/

**Sked Social (2026)** — single in-feed 1200x675 (16:9), square 1080x1080,
vertical 1080x1350 (4:5), all listed as recommended post sizes.
https://skedsocial.com/blog/twitter-post-size-guide

**Hootsuite (July 2026)** — recommends 16:9 or 1:1; landscape 1280x720, square
1080x1080; up to 5 MB mobile / 15 MB web; GIF/JPG/PNG. Does not endorse a
portrait spec.
https://blog.hootsuite.com/social-media-image-sizes-guide/

**File/format/resolution (cross-source):** Max upload resolution commonly cited
as 8192 x 8192 px, with 4096 x 4096 the effective display cap (X compresses
above that). Photos up to 5 MB (JPEG/PNG/WebP), GIF up to 15 MB. WebP is
accepted for upload but X re-encodes to JPG on display, so PNG/JPG are safer for
text-heavy graphics. (soona.co, Tweet Archivist, Image for Post, 2026)
https://soona.co/image-resizer/twitter-spec-guide

**Multi-image grids (brief, not your case):** 2 images = side-by-side, each
~7:8; 3 images = one 7:8 left + two 4:7 stacked; 4 images = 2x2, each ~2:1. All
grid slots are cropped regardless of source aspect. Only single images honor the
2:1-to-3:4 uncropped rule.
https://influencermarketinghub.com/twitter-image-size/

## Disagreements / caveats

- **The big one: is 4:5 cropped in-feed?** Split. TechCrunch (primary),
  aspectratiocalculator, Influencer Marketing Hub, and Sprout Social say tall
  images up to 3:4 (and therefore 4:5, which is shorter than 3:4) display
  UNCROPPED since the 2021 change. A cluster of guides (Sked, viraly.io, Image
  for Post) still repeat "tall 4:5 gets cropped to ~16:9 in the mobile feed
  preview." That claim reflects PRE-2021 behavior and is stale — the whole point
  of the 2021 update was that the composer preview equals the timeline. Trust
  the composer: paste the image and look. Verdict: **4:5 shows fully in-feed;
  the crop myth is outdated.**
- **Where the tall bound actually sits:** endpoints "2:1 to 3:4" come from
  marketing guides interpreting X; TechCrunch only names 16:9 and 4:3 explicitly.
  4:5 (0.80) sits comfortably inside 3:4 (0.75); 9:16 / 2:1-tall / 1:2 phone
  screenshots exceed it and WILL crop. Do not go taller than 3:4.
- **Landscape recommended px varies:** 1600x900 (Sprout, Sked-alt) vs 1200x675
  (Sked, Influencer Hub) vs 1280x720 (Hootsuite) — all 16:9, just resolution.
  Use 1600x900 for crisper text.
- **No first-party X Help Center spec surfaced** for exact in-feed aspect bounds;
  X's own guidance is the composer preview itself. Treat marketing-guide numbers
  as corroborated secondary sources, and always confirm in the composer before
  posting.
