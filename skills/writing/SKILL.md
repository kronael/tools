---
name: writing
description: Router for how prose reads and how a document or page looks — copy rules for docs, UI strings and microcopy, plus the owner's page rules (headers as claims, boxes, layout, colour, sources, links). NOT for PR descriptions (use pr-draft), tweets (use tweet), diary entries (use diary), the AI-tells catalogue (use humanize), or which file a fact belongs in (use readme).
when_to_use: "write a doc, doc prose, tooltip, help text, label, caption, microcopy, UI string, button text, error message, empty-state text, make this clearer, make this page readable, simpler wording, 13yo style, rewrite this copy, explain a metric or formula in plain English; AI slop, fix the slop, card header, box title, figure title, accent stripe, colour legend, status pill on every line, all-caps labels, em-dash chain, wall of text, one narrow column, heading anchor, nav label, name the entity first, sources note, link text in brackets, full address, plain English, Simplified Technical English, ASD-STE100"
---

# Writing — prose and page router

Only this file preloads. Its rules apply to every piece of prose. For a
document or HTML page with any layout, ALSO read exactly ONE matched file
below. Paths are relative to this directory.

| If you need | Read |
|---|---|
| how a document or page is laid out and reads — box and card headers, entities named before use, no stripes, legends, pills or all-caps labels, short lines in cards, a real layout, one name across sidebar, index and title, explicit short anchors on linked headings, one sources note per section, bracketed link text, diagrams, contrast, the one-file craft (font, accent, dark mode), the render check | `page.md` |

The owner's name for a violation of any rule here is "AI slop"; "fix the slop"
routes here. Prose tells with worked fixes are the `humanize` catalogue.

ALWAYS read the Language section of `~/.claude/output-styles/caveman.md` before
writing informational or technical prose. It owns the shared language rules;
its chat budget does not apply to documents. For creative work, ALWAYS follow
an explicitly requested voice or style.

ALWAYS preserve technical names, code, and quotations. Explain technical terms
when the audience needs them; NEVER change a precise term merely to simplify
it — ALWAYS keep the term and explain its meaning instead.

## Rules

- ALWAYS make a heading, a box or card header and a figure title state the most
  important fact under it as a short claim ("One program per deployment", "Only
  the owner can collect") — NEVER a generic label ("Overview", "Details",
  "Notes"), a vague directive ("Change something"), an "X: Y" colon title
  ("The program: one per deployment") or a bold lead-in label (humanize #31).
  In a doc set with navigation, a heading may instead be the reader's
  question ("What it costs", "Run it") when its first sentence answers it,
  and pages of one repeated shape, such as every example page, reuse the
  same section names.
- ALWAYS introduce a program, account, role or term before the prose uses it —
  a plain definition at first use in a doc, its own box on a page — and ALWAYS
  use one name for it throughout; NEVER cycle synonyms (humanize #11).
- NEVER use jargon when a 13yo could read the plain version. ALWAYS test: would
  a smart non-expert understand this in one read?
- NEVER preamble ("It is important to note that…", "This section shows…") —
  ALWAYS start with the noun or verb the reader cares about.
- NEVER write "this X" referring to the page, card or section you are on — the
  reader knows where they are. ALWAYS name what the thing does.
- ALWAYS prefer plain verbs ("keep stake", "grow stake") over Latinate nouns
  ("retention", "expansion").
- NEVER stack qualifying nouns ("bond coverage reserve guarantee") — ALWAYS pick
  the one noun that does the work.
- Parentheses are a style smell in ALL writing. Strength of the rule by genre:
  - Prose, sentences, help text, tooltips, captions, titles — NEVER. ALWAYS
    replace with a comma, two sentences, or at most one em-dash. Parens here
    signal a draft that was not edited down.
  - Deeply technical docs (ARCHITECTURE, SPEC, reference tables) — TOLERATED
    for dense asides, but still prefer the comma rewrite when it reads cleanly.
  - EXCEPTION — leave untouched: compact data tokens and inline UI annotations
    where the parens ARE the formatting, not a sentence aside — `(5ep)` runway,
    `(capped)` tag, `(+2)` rank delta, `(N)` counts.
- NEVER chain em-dashes — at most one in a sentence (humanize #14). NEVER chain
  clauses with semicolons, stand a symbol in for a word ("+" for "and"), or mix
  curly quotes into source — ALWAYS separate sentences, the plain word,
  straight quotes (humanize #19, #32, #33).
- A link is not an aside. NEVER a parenthesised link after a sentence,
  "(queue test)", "(SDK README)". ALWAYS give a link short visible text in
  square brackets, "[queue test]" as the reader sees it, so adjacent links
  read as separate items, and put the full path or test name in the href or
  title. In a document, citations go in the section's one sources note
  (`page.md` § Sources and links), NEVER inside the explanation.
- ALWAYS finish longer prose with the `humanize` pass: it strips AI-isms and
  restores voice. For informational and technical prose, ALWAYS keep the
  shared language rules when that pass suggests fragments, idioms, or slang.
- Three WISDOM § Documentation rules apply to every surface, code comments
  included — point at them, NEVER restate: no history or counterfactual
  framing, no marketing language, every address, signature and hash in full.
