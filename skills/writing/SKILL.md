---
name: writing
description: Copywriting rules for tooltips, help text, UI strings, captions, labels, microcopy, prose in docs. NOT for PR descriptions (use pr-draft), tweets (use tweet), diary entries (use diary), or syncing existing docs (use readme).
when_to_use: "writing a tooltip, help text, label, caption, microcopy, UI string, button text, error message, empty-state text, make this clearer, simpler wording, 13yo style, rewrite this copy, explaining a metric or formula in plain English"
---

# Writing

Copy rules for any user-facing string.

## Rules

- Parentheses are a style smell in ALL writing. Strength of the rule by genre:
  - Prose, sentences, help text, tooltips, captions, **titles** — NEVER. ALWAYS replace with an em-dash, a comma, or two sentences. Parens here signal a draft that wasn't edited down.
  - Deeply technical / detailed docs (ARCHITECTURE, SPEC, reference tables) — TOLERATED for dense asides, but still prefer the em-dash/comma rewrite when it reads cleanly.
  - EXCEPTION — leave untouched: compact data tokens / inline UI annotations where the parens ARE the formatting, not a sentence aside — `(5ep)` runway, `(capped)` tag, `(+2)` rank delta, `(N)` counts.
  - A link is not an aside: ALWAYS put it on the words of the claim it proves — NEVER a parenthesised generic link after the sentence, "(queue test)", "(SDK README)".
- NEVER stack qualifying nouns ("bond coverage reserve guarantee") — ALWAYS pick the one noun that does the work.
- NEVER preamble ("It is important to note that…", "This section shows…") — ALWAYS start with the noun or verb the reader cares about.
- NEVER write "this X" referring to the page/card/section you're on — the reader knows where they are. ALWAYS name what the thing does.
- ALWAYS prefer plain verbs ("keep stake", "grow stake") over Latinate nouns ("retention", "expansion").
- NEVER use jargon when a 13yo could read the plain version. ALWAYS test: would a smart non-expert understand this in one read?
- ALWAYS finish longer prose with a de-slop pass: the `humanize` skill strips AI-isms and restores voice.
- NEVER title a section with a vague directive ("Change something", "Notes") or an "X: Y" colon title ("The program: one per deployment") — ALWAYS name the concrete action or content under it, plainly (humanize #31).
- NEVER chain clauses with semicolons, stand a symbol in for a word ("+" for "and"), or mix curly quotes into source — ALWAYS separate sentences, the plain word, straight quotes (humanize #19, #32, #33).
- NEVER marketing language — ALWAYS cut fluff.
- NEVER reference an earlier version, prior design, or counterfactual in a comment, doc, skill, or agent definition — no "used to be", "previously", "renamed from", "as before", "instead of X", "no longer", "matching the old <name>", or backwards-compat framing. Same bar for temporary-inside-permanent: NEVER narrate a transient artifact (a one-off backfill script) into a permanent one (a migration, a long-lived module) — that belongs in the transient file itself, if anywhere. ALWAYS state only what is true now and its genuine quirks; history lives in `.diary/`.
