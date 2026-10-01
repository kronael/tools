# Onepager — one public page

One page. A stranger decides in 60 seconds whether this matters to them.
Everything else is a link. ALWAYS read the project's record first — README,
plan/specs, BUGS.md, `.ship/critique-*.md`; NEVER let the page assert what a
critique on file already refuted.

## Sections — this order; cut any with nothing true to say

1. **Name + one sentence.** What it does, plain words, no metaphor. A reader
   who stops here still knows what the thing is.
2. **The problem** — two or three sentences, stated as the reader's problem,
   never as the project's motivation.
3. **How it works** — 3–5 numbered steps or one diagram. The only section
   allowed domain vocabulary, and it defines each term inline.
4. **What is different** — comparison against real alternatives, named. A
   comparison against nobody reads as marketing.
5. **Status and limits** — what works today, what does not, what is assumed —
   from the bug queue and open questions, not imagination. A page with no
   limits is not believed.
6. **Numbers** — cost, effort, scale, latency. Only numbers a run, file, or
   recorded estimate produced; NEVER invent one.
7. **Next step** — the one action a convinced reader takes, with the link. A
   negative critique verdict on file is named here, not hidden.

## Rules

- ALWAYS cap body prose near 500 words — longer material links out.
- ALWAYS lead each section with its conclusion, then support it.
- NEVER use marketing words — "revolutionary", "seamless", "powerful",
  "next-generation"; state the capability and let it stand.
- NEVER present planned behavior as shipped — a project with no code says so
  in its first sentence, and "How it works" is labeled as the design.
- ALWAYS one self-contained file: inline CSS, inline SVG, no CDN, no external
  fonts, no build step — it renders from `file://`. Dark-mode-safe via
  `prefers-color-scheme`, explicit background on `body`.
- Craft: one font family, at most five font sizes, generous line height,
  measure ≤70ch; one accent colour — links plus at most one divider, nothing
  else; prose over bullet soup. A diagram only for a mechanism words handle
  badly — inline SVG or `<pre>`, never an image file. NEVER design past
  this — a taste-driven page is `create/web.md`'s job.
- ALWAYS reread the rendered page as a stranger before handing over: the
  first sentence says what it is, every claim has a source linked on the
  claim's own words (`page.md` § Evidence), a skeptic survives it.
- NEVER publish through Claude Artifacts — ALWAYS write into the krons web
  root (`CLAUDE.md` § Publishing) and hand back the public URL, unless the
  request names a different destination; then write exactly there.
