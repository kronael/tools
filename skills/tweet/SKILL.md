---
name: tweet
description: Write X/Twitter posts and threads about a project, a release or a finding. NOT for UI strings or doc prose (use writing), de-slopping an existing draft (use humanize), or the image or GIF for the post (use create or demo).
when_to_use: "tweet, X post, Twitter thread, launch thread, release announcement on X, viral hook, numeric hook, banger, tweetstorm, make this shareable, promote this project on X"
user-invocable: true
---

# Tweet

A tweet is a verified claim with a hook, read by a peer who scrolls past
marketing. Voice and vocabulary come from the `writing` skill, which
points at the Language section of `~/.claude/output-styles/caveman.md`; its
one-clause sentences and named actors are also what fits in 280 characters.
An explicitly requested voice wins over both.

## Workflow

1. Material: collect one to three claims, each traced to its source with
   date, denominator and caveat (§ Claims).
2. Hooks: draft three, keep the one with the clearest tension, not the
   loudest adjective (§ Hook).
3. Write one tweet or a 4–8 tweet arc; reveal the project late (§ Arc).
4. Gate every tweet: plain text, measured under 280 (§ Platform).
5. DISTILL, `humanize`, REVIEW-ON-WISDOM (§ Close).
6. Return each tweet in its own fenced block with its measured count on the
   next line, then the source notes — claim, source, caveat — outside the
   copy.

## Claims

- ALWAYS verify every number, date and comparison against the primary source
  before drafting. For a project the primary source is the code or a run —
  the README and CHANGELOG state the intent, so NEVER take a number or an
  absolute from them alone.
- ALWAYS keep the source's denominator, date, causality, uncertainty and
  wording. NEVER a comparison, a rounding or a unit the source does not make.
- NEVER an absolute the source does not state in those words — "no escape",
  "cannot", "zero", "never fails". ALWAYS name the mechanism ("its own
  kernel") and let the reader draw the consequence.
- NEVER a superlative or marketing word — the number and the consequence
  carry the impact, and an adjective marks the claim that is missing. The
  word list is `humanize` § 4 and § 7.

## Hook

- ALWAYS open on the reader's outcome or the belief that changes. NEVER open
  with "I built", "Introducing", the project name, a link, "🧵" or "a thread".
- ALWAYS anchor on a unit the reader already holds — 100 people, one team,
  one hour, money — and on the one measured number when the source has one.
- ALWAYS land the surprise or contradiction by line two; the reader decides
  there whether to stop scrolling.
- ALWAYS end the hook on the consequence, NEVER on a teaser question.

## Arc

One tweet: hook, one proof clause, consequence. The material caveat rides
inside the tweet or in the first reply next to the link — NEVER only in the
notes to the user, which the reader never sees.

A thread, 4–8 tweets, one new fact per tweet:

1. Hook — anchor, number, tension, consequence.
2. Proof — what was measured, the source, and the material caveat. The
   caveat lives here, NEVER in the close and NEVER omitted.
3. Reframe — the bottleneck or belief that changed.
4. Reasons — one concrete reason per tweet.
5. Reveal — the project, as the response to the proven problem.
6. Close — the memorable line, the action, then the project and source links.

- ALWAYS make each tweet stand alone — a reader meets it quoted or
  screenshotted without the thread, so NEVER open one with "This", "It" or
  "That's why" pointing at the tweet before.
- NEVER restate a claim to fill a slot — ALWAYS cut the tweet instead.
- NEVER a link in the hook — ALWAYS the close or the first reply, unless the
  user asks for immediate clicks.

## Platform

- Plain text only. NEVER markdown — backticks, bold, headers and bullets
  render literally on X. A command goes inline as plain text, a code sample
  into an image.
- ALWAYS measure every tweet with `wc -m` on the text without its trailing
  newline, then count each URL as 23 and each emoji as 2 whatever `wc -m`
  says — X weighs characters that way. ALWAYS show the measured count with
  the copy; NEVER an estimate.
- NEVER lean on the Premium long-post allowance — the timeline folds it
  behind "Show more", so the hook still has to land within 280.
- NEVER hashtags or decorative emoji — both read as a bot to the reader.
- Attribution for Claude's authorship, when the user wants it shown, is a
  bare `🤖` closing the last tweet (WISDOM § Git) — NEVER "Generated with
  Claude Code", a claude.ai link, a session URL or a hashtag.
- An image or GIF for the post: the `create` skill's social-image mode for a
  meme or code-shot, the `demo` skill for a terminal recording. The tweet
  text never describes the image.

## Close

Three passes before any copy is shown, the first and last as WISDOM § Git
defines them:

1. DISTILL — the first draft is never the deliverable. Cut every word that
   does not change the claim.
2. `humanize` — the finishing pass, draft and audit kept internal. For the
   claim tweets the Language section outranks the personality it suggests.
3. REVIEW-ON-WISDOM — re-read the result against: every number traced in the
   source notes; no absolute the source does not state; the caveat visible to
   the reader; no marketing word, markdown, hashtag or teaser; the link out
   of the hook; the attribution form; each count re-measured and under 280.
   Done = every check passes on the copy shown, and the reply names what the
   review changed.
