---
name: humanize
description: "Humanize text: strip AI-isms and add real voice. NOT for drafting new copy (use writing)."
when_to_use: "humanize text, strip AI-isms, de-AI this writing, remove the AI voice, make it sound human, add real voice, less robotic"
license: MIT
metadata:
  version: "2.5.1"
  author: "Siqi Chen (@blader, https://github.com/blader/humanizer), ported by Hermes Agent"
  homepage: "https://github.com/blader/humanizer"
  platforms: "linux, macos, windows"
  tags: "writing, editing, humanize, anti-ai-slop, voice, prose, text"
  category: "creative"
  related_skills: "songwriting-and-ai-music"
---

# Humanizer: Remove AI Writing Patterns

Identify and remove signs of AI-generated text to make writing sound natural and human. Based on Wikipedia's "Signs of AI writing" guide (maintained by WikiProject AI Cleanup), derived from observations of thousands of AI-generated text instances.

**Key insight:** LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely completion, which is how the telltale patterns in `patterns.md` get baked in.

## When to use this skill

Load this skill whenever the user asks to:
- "humanize", "de-AI", or "un-ChatGPT" a piece of text
- rewrite something so it doesn't sound like it was written by an LLM
- edit a draft (blog post, essay, PR description, docs, memo, email, tweet, resume bullet) to sound more natural
- match their voice in writing they're producing
- review text for AI tells before publishing
- finish the prose of a document or page the `writing` skill sent here — its layout and look are `writing/page.md`

Also apply this skill to **your own** output when writing user-facing prose — release notes, PR descriptions, documentation, long-form explanations, summaries. Hermes's baseline voice already strips most of these, but a focused pass catches what slips through.

## How to use it in Hermes

The text usually arrives one of three ways:
1. **Inline** — user pastes the text directly into the message. Work on it in-place, reply with the rewrite.
2. **File** — user points at a file. Use `read_file` to load it, then `patch` or `write_file` to apply edits. For markdown docs in a repo, a targeted `patch` per section is cleaner than rewriting the whole file.
3. **Voice calibration sample** — user provides an additional sample of their own writing (inline or by file path) and asks you to match it. Read the sample first, then rewrite. See the Voice Calibration section below.

Always show the rewrite to the user. For file edits, show a diff or the changed section — don't silently overwrite.

## Scope for informational and technical prose

ALWAYS read and follow the Language section of
`~/.claude/output-styles/caveman.md` for informational and technical prose.
Those rules take precedence over personality, fragments, idioms, and slang
suggested below. ALWAYS preserve technical names, code, and quotations.
Override for rewrites: ALWAYS preserve factual claims and uncertainty from
the input. NEVER invent measurements, sources, interviews, or personal
experiences to add voice — ALWAYS change the wording using the supplied facts.
When this skill is a finishing pass within another writing task, ALWAYS keep
the draft and audit internal and return the result that task requests.

## Your task

ALWAYS read `patterns.md` in this directory in full before the first edit — the 34 patterns, the voice section and the worked example live there; this file is the workflow only.

When given text to humanize:

1. **Identify AI patterns** — scan for the patterns in `patterns.md`.
2. **Rewrite problematic sections** — replace AI-isms with natural alternatives.
3. **Preserve meaning** — keep the core message intact.
4. **Maintain voice** — match the intended tone (formal, casual, technical, etc.). If a voice sample was provided, match it specifically.
5. **Add soul** — don't just remove bad patterns, inject actual personality. See PERSONALITY AND SOUL in `patterns.md`.
6. **Do a final anti-AI pass** — ask yourself: "What makes the below so obviously AI generated?" Answer briefly with any remaining tells, then revise one more time.


## Voice Calibration (optional)

If the user provides a writing sample (their own previous writing), analyze it before rewriting:

1. **Read the sample first.** Note:
   - Sentence length patterns (short and punchy? Long and flowing? Mixed?)
   - Word choice level (casual? academic? somewhere between?)
   - How they start paragraphs (jump right in? Set context first?)
   - Punctuation habits (lots of dashes? Parenthetical asides? Semicolons?)
   - Any recurring phrases or verbal tics
   - How they handle transitions (explicit connectors? Just start the next point?)

2. **Match their voice in the rewrite.** Don't just remove AI patterns — replace them with patterns from the sample. If they write short sentences, don't produce long ones. If they use "stuff" and "things," don't upgrade to "elements" and "components."

3. **When no sample is provided,** fall back to the default behavior (natural, varied, opinionated voice from PERSONALITY AND SOUL in `patterns.md`).

### How to provide a sample
- Inline: "Humanize this text. Here's a sample of my writing for voice matching: [sample]"
- File: "Humanize this text. Use my writing style from [file path] as a reference."


---

## Process

1. Read the input text carefully (use `read_file` if it's a file).
2. Identify all instances of the patterns in `patterns.md`.
3. Rewrite each problematic section.
4. Ensure the revised text:
   - Sounds natural when read aloud
   - Varies sentence structure naturally
   - Uses specific details over vague claims
   - Maintains appropriate tone for context
   - Uses simple constructions (is/are/has) where appropriate
5. Present a draft humanized version.
6. Prompt yourself: "What makes the below so obviously AI generated?"
7. Answer briefly with the remaining tells (if any).
8. Prompt yourself: "Now make it not obviously AI generated."
9. Present the final version (revised after the audit).
10. If the text came from a file, apply the edit with `patch` (targeted) or `write_file` (full rewrite) and show the user what changed.

## Output Format

Provide:
1. Draft rewrite
2. "What makes the below so obviously AI generated?" (brief bullets)
3. Final rewrite
4. A brief summary of changes made (optional, if helpful)

## Attribution

This skill is ported from [blader/humanizer](https://github.com/blader/humanizer) (MIT licensed), which is itself based on [Wikipedia: Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing), maintained by WikiProject AI Cleanup. The patterns documented there come from observations of thousands of instances of AI-generated text on Wikipedia.

Original author: Siqi Chen ([@blader](https://github.com/blader)). Original repo: https://github.com/blader/humanizer (version 2.5.1). Ported to Hermes Agent with Hermes-native tool references (`read_file`, `patch`, `write_file`) and guidance for when to load the skill; the patterns and personality/soul section, in `patterns.md`, are adapted from the source. The scope rules and worked example are local changes. Original MIT license preserved in the `LICENSE` file alongside this `SKILL.md`.

Key insight from Wikipedia: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases."
