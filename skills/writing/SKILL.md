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
- NEVER stack qualifying nouns ("bond coverage reserve guarantee") — ALWAYS pick the one noun that does the work.
- NEVER preamble ("It is important to note that…", "This section shows…") — ALWAYS start with the noun or verb the reader cares about.
- NEVER write "this X" referring to the page/card/section you're on — the reader knows where they are. ALWAYS name what the thing does.
- ALWAYS prefer plain verbs ("keep stake", "grow stake") over Latinate nouns ("retention", "expansion").
- NEVER use jargon when a 13yo could read the plain version. ALWAYS test: would a smart non-expert understand this in one read?
- ALWAYS finish longer prose with a de-slop pass: the `humanize` skill strips AI-isms and restores voice.
