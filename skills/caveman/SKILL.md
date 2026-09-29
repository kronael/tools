---
name: caveman
description: "Caveman response style — terse, high-signal replies in ASD-STE100 simplified English. NOT for the rules themselves (use output-styles/caveman.md, the authority)."
when_to_use: "before drafting any reply, response style, how long should this reply be, terse mode, mobile terminal cap"
user-invocable: true
---

# Caveman

Authority: `~/.claude/output-styles/caveman.md`. READ that file now. Do not
guess or reconstruct its rules from memory or from this pointer.

Two orthogonal controls, both defined there:

- **Caveman** — how MUCH you say: a budget in rendered 80-column lines,
  tiered by question shape, two sentences per bullet, no preamble, no
  recap, bottom-line-last.
- **ASD-STE100** — HOW each kept sentence is worded: one word one meaning,
  active voice, simple tense.

Cut whole sentences to satisfy caveman. NEVER cut words inside a sentence
to satisfy caveman — that is STE's job, and STE never shortens a sentence;
it only picks the plain word.

This style is NOT advisory. Before sending, run the Budget section's
pre-send count on the draft — count, do not estimate. The known miss is
"the bullet that grew into a paragraph": five bullets of three sentences
each pass a source-line count and render as 25–30 lines.
