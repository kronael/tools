# Onepager — one public page

One page. A stranger decides in 60 seconds whether this matters to them.
Everything else is a link. ALWAYS read the project's record first — README,
plan/specs, BUGS.md, the record dir's `critique-*.md` (`ship` § Work record); NEVER let the page assert
what a critique on file already refuted. ALWAYS name the page's reader and the
decision they face before drafting; the project README records them.

## Sections — this order; cut any with nothing true to say

1. **Name + one sentence.** What it does, plain words, no metaphor. A reader
   who stops here still knows what the thing is. The status line sits
   directly under it, worded as `sync.md` step 3 requires.
2. **The problem** — two or three sentences, stated as the reader's problem,
   never as the project's motivation, each one a problem the record shows is
   real. ALWAYS lead with the reader's cost today and the change the project
   makes; NEVER write it as engineers talking to engineers.
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

## Money offers — a page that asks the reader to spend money

- ALWAYS put what the reader pays and can lose in the same block as what they
  get, the first block included; NEVER only in a footer or disclosures
  section (FCA COBS 4.5.2R(2), FINRA 2210(d)(1)).
- ALWAYS state a return or payout with every cost the reader bears already
  subtracted in that figure (FTC earnings-claim guidance Q13, SEC Marketing
  Rule on net results).
- ALWAYS show every recorded result with its count, or the typical one; NEVER
  the best result or a chosen period as the example (FTC Q13, Q16).
- ALWAYS state a loss as an amount and its condition in the offer's own
  terms; NEVER a generic warning line (FCA risk-warning testing).
- ALWAYS write a past result in the past tense with its dates, and mark an
  estimate as an estimate with its main condition beside it; NEVER word
  either as what the reader will get (FINRA 2210(d)(1)(B), (F)).
- ALWAYS give money in and money out before a percentage, and a rate as a
  count over a named group, "3 of 7 accounts" (Gigerenzer et al. 2007).
- ALWAYS state a reward to the person who shares the link in the body when
  the record shows one (FTC Endorsement Guides).
- These rules govern where facts sit and how they are qualified. The owner's
  headline and pitch stay verbatim (WISDOM § Documentation).

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
