# Onepager — one public page

One page. A stranger decides in 60 seconds whether this matters to them.
Everything else is a link. ALWAYS read the project's record first — README,
plan/specs, BUGS.md, `.claude/plans/critique-*.md`; NEVER let the page assert
what a critique on file already refuted.

## Sections — this order; cut any with nothing true to say

1. **Name + one sentence.** What it does, plain words, no metaphor. A reader
   who stops here still knows what the thing is. The status line sits
   directly under it, worded as `sync.md` step 3 requires.
2. **The problem** — two or three sentences, stated as the reader's problem,
   never as the project's motivation.
3. **How it works** — 3–5 numbered steps or one diagram. The only section
   allowed domain vocabulary, and it defines each term inline.
4. **What is different** — comparison against real alternatives, named. A
   comparison against nobody reads as marketing.
5. **Limits** — what works today, what does not, what is assumed —
   from the bug queue and open questions, not imagination. A page with no
   limits is not believed.
6. **Numbers** — cost, effort, scale, latency, with cost stated by
   `sync.md` § Rules. Only numbers a run, file, or recorded estimate
   produced; NEVER invent one.
7. **Next step** — the one action a convinced reader takes, with the link. A
   negative critique verdict on file is named here, not hidden.

## Rules

- ALWAYS cap body prose near 500 words — longer material links out.
- ALWAYS lead each section with its conclusion, then support it.
- NEVER present planned behavior as shipped — a project with no code says so
  in its first sentence, and "How it works" is labeled as the design.
- Craft and presentation — one self-contained dark-mode-safe file, one font,
  one accent, measure ≤70ch, prose over bullet soup, boxes, sources and links —
  are the `writing` skill: ALWAYS read `writing/page.md` before writing.
- ALWAYS reread the rendered page as a stranger before handing over: the
  first sentence says what it is, every claim is backed in its section's
  sources note (`writing/page.md` § Sources and links), a skeptic survives it.
- NEVER publish through Claude Artifacts — ALWAYS write into the web root
  the owner's local setup names (`~/.claude/LOCAL.md`) and hand back the
  public URL, unless the request names a different destination; then write
  exactly there.
