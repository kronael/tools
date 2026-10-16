---
name: writing
description: Router for how prose reads and how a document or page looks — copy rules and the owner's page rules. NOT for PR descriptions (use pr-draft), tweets (use tweet), diary entries (use diary), the AI-tells catalogue (use humanize), or which file a fact belongs in (use readme).
when_to_use: "write a doc, doc prose, headers as claims, tooltip, help text, label, caption, microcopy, UI string, button text, error message, empty-state text, make this clearer, make this page readable, page layout, simpler wording, 13yo style, rewrite this copy, explain a metric or formula in plain English; AI slop, fix the slop, card header, box title, figure title, accent stripe, colour legend, status pill on every line, all-caps labels, em-dash chain, wall of text, one narrow column, heading anchor, nav label, name the entity first, sources note, link text in brackets, full address, description list, glossary, word budget, text fills the box, five font sizes, brand block, no mechanics, rent noise, faithful diagram, page checklist, keeper test, plain English, Simplified Technical English, ASD-STE100"
---

# Writing — prose and page router

Only this file preloads. Its rules apply to every piece of prose. For a
document or HTML page with any layout, ALSO read exactly ONE matched file
below. Paths are relative to this directory.

| If you need | Read |
|---|---|
| how a document or page is laid out and reads — box and card headers, entities named before use, description lists, no stripes, legends, pills or all-caps labels, short lines in cards, text filling its box, a real layout, one name across sidebar, index and title, the in-page nav block, explicit short anchors on linked headings, the brand block shared with sibling pages, the word budget, no mechanics or rent noise, every term glossed, one sources note per section, bracketed link text, exact-line code links, diagrams faithful to the code, contrast, the one-file craft (font, five sizes, accent, dark mode), the pre-handover checklist and its keeper tests | `page.md` |

The owner's name for a violation of any rule here is "AI slop"; "fix the slop"
routes here. Prose tells with worked fixes are the `humanize` catalogue.

## Language — ASD-STE100 Simplified Technical English

These rules apply to every informational or technical document, page, README
and description. For creative work, ALWAYS follow an explicitly requested voice
or style. ASD-STE100 is guidance here: NEVER claim compliance without checking
the standard and its approved dictionary (53 writing rules and a ~900-word
dictionary, Issue 9, 2025, asd-ste100.org).

- One word, one meaning: pick the familiar word and use it every time. "Start" stays "start", never "kick off", "spin up" or "fire".
- Every term a project's docs use comes from its Glossary, the project's dictionary. A needed technical term stays, with its meaning stated at first use.
- No metaphor, idiom, slang or drama: "the test failed", not "the test blew up".
- Active voice with a named actor: "the router drops the field", not "the field is dropped". Subject, verb, object, or a direct imperative.
- Simple tenses only: present, past, future. NEVER "has been", "would have", "is being".
- One main clause per sentence, plus at most one short if, when or because clause. NEVER nest clauses or insert asides: split them into sentences.
- A warning or a condition comes before the action it controls, NEVER after it.
- One instruction per sentence: at most 20 words in a step, 25 in a description.
- Noun stacks of at most 3 words: "container spawn timeout" is the limit.
- ALWAYS keep articles and full grammar: "run the test", not "run test".
- ALWAYS repeat the noun where "it", "this" or "they" could point at more than one thing.
- ALWAYS keep technical names, code and quotations as written, and keep the technical meaning and every stated uncertainty when you split or rewrite a sentence.

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
- ALWAYS order a list the way the reader meets its items — by index, in the
  user's flow — and keep one order for the same items, the roles or the steps,
  in every doc.
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
