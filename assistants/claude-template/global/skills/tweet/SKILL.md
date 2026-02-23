---
name: tweet
description: Write X/Twitter threads. Dense, narrative, product-focused. No marketing fluff, no emojis, no hashtags.
user-invocable: true
---

# X/Twitter Thread Writing

## Voice

- Dense information, no marketing fluff
- Narrative flow, not presentation bullet points
- Personal "I built/needed" framing
- End with "back to kroning."
- No stories or anecdotes beyond the opening hook
- No emojis, no hashtags (except optionally 2-3 in final tweet)

## Structure (4-8 tweets)

1. **Hook**: Product value proposition + link. What it does in one line.
   Then "Why?" to open the loop.
2. **Motivation**: Personal need that drove building it. Dense, specific.
3. **What it enables**: "Write a..." pattern. Show distinct use cases as
   activities the reader can do. No repetition of the same concept.
4. **Closer**: Punchy one-liner. Then "back to kroning."

## Rules

- One idea per tweet
- No implementation details (no code, no architecture)
- Product-focused: what problems it solves, what it enables
- Lead with value, explain why after
- GitHub link goes in tweet 1 (immediate access)
- Each tweet under 280 chars
- No "What it does:", "Use cases:", etc. headers -- just write it

## Anti-patterns

- Listing the same concept three different ways
- "Here's why this works" / "Let me explain" / "Thread 🧵"
- Technical details (process spawn, cleanup, timeouts)
- Marketing language ("revolutionary", "game-changing", "unlock")
- Starting with "I built this" (start with what the reader gets)

## Process

1. Read examples in `examples/` directory for voice calibration
2. Identify the single core value proposition
3. Write hook: value prop + link + "Why?"
4. Write 2-3 body tweets: motivation, use cases, capabilities
5. Write closer: one punchy line + "back to kroning."
6. Verify each tweet is under 280 chars
7. Read aloud -- if it sounds like a pitch deck, rewrite
