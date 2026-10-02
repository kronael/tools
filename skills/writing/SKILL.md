---
name: writing
description: Copywriting rules for tooltips, help text, UI strings, captions, labels, microcopy, prose in docs. NOT for PR descriptions (use pr-draft), tweets (use tweet), diary entries (use diary), or syncing existing docs (use readme).
when_to_use: "writing a tooltip, help text, label, caption, microcopy, UI string, button text, error message, empty-state text, make this clearer, simpler wording, 13yo style, rewrite this copy, explaining a metric or formula in plain English, plain English, Simplified Technical English, ASD-STE100"
---

# Writing

Copy rules for any user-facing string.

ALWAYS read the Language section of `~/.claude/output-styles/caveman.md` before
writing informational or technical prose. It owns the shared language rules;
its chat budget does not apply to documents. For creative work, ALWAYS follow
an explicitly requested voice or style.

ALWAYS preserve technical names, code, and quotations. Explain technical terms
when the audience needs them; NEVER change a precise term merely to simplify
it — ALWAYS keep the term and explain its meaning instead.

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
- ALWAYS finish longer prose with the `humanize` skill to remove AI-isms.
  For informational and technical prose, ALWAYS keep the shared language rules
  when that pass suggests fragments, idioms, or slang.
- NEVER marketing language — ALWAYS cut fluff.
- NEVER reference an earlier version, prior design, or counterfactual in a comment, doc, skill, or agent definition — no "used to be", "previously", "renamed from", "as before", "instead of X", "no longer", "matching the old <name>", or backwards-compat framing. Same bar for temporary-inside-permanent: NEVER narrate a transient artifact (a one-off backfill script) into a permanent one (a migration, a long-lived module) — that belongs in the transient file itself, if anywhere. ALWAYS state only what is true now and its genuine quirks; history lives in `.diary/`.
