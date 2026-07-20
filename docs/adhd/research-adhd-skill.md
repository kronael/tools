# Research: the "ADHD" communication skill (to sharpen 80% caveman)

Goal: find a real, citable ADHD-friendly output skill/prompt and extract
communication patterns that ADD to our caveman style (maximum signal per
token, ~17-line replies, lead with the answer, bottom-line last, no padding).

## Source(s) found (for attribution)

**Primary — the right one.** `i-have-adhd` by **Ayoub Ghriss** (handle
`ayghri`).
- URL: https://github.com/ayghri/i-have-adhd
- SKILL.md: https://github.com/ayghri/i-have-adhd/blob/main/skills/i-have-adhd/SKILL.md
- License: **MIT**, "Copyright (c) 2026 Ayoub Ghriss" (verified in the repo's
  LICENSE file).
- Popularity: ~3.7k stars / ~112 forks — a genuinely popular, citable Claude
  Code / Codex skill, not a blog throwaway.
- Tagline (README): "ADHD-friendly outputs. No ADHD diagnosis needed." Self-
  description: "stop burying the answer. Action first." Invoke with
  `/i-have-adhd` (Claude) or `$i-have-adhd` (Codex).

**Secondary — reinforces one pattern.** `claude-adhd-skills` by `ravila4`.
- URL: https://github.com/ravila4/claude-adhd-skills (CLAUDE.md:
  https://github.com/ravila4/claude-adhd-skills/blob/main/CLAUDE.md)
- Adds: break work into focused steps with **todo lists to track progress**,
  signal transitions between tasks, and "STOP and ask rather than assume."
  Progress-tracking reinforces the primary source's "restate state" rule; the
  rest is ADHD self-management, not output style.

**Other candidates (not the artifact we want):** `UditAkhourii/adhd` is a
tree-of-thought ideation skill (unrelated to communication style);
`dsx0511/adhd-copilot` and `RobotDisco/adhd-skills` are personal
self-management toolkits; the aiproductivity.ai / claudecodehq.com blogs
describe the same idea but the ayghri skill is the canonical, licensed source.

**No kronael / Ondrej Vostal ADHD skill exists.** Searched
"kronael Ondrej Vostal ADHD skill" — only hits were an unrelated crypto talk.
The user did not publish one; do not invent an internal source.

## Confidence it's the right one

**High.** The task described "stop burying the answer / front-loaded / low
cognitive load"; ayghri's repo literally reads "Claude Code skill to stop it
from burying the answer. ADHD-friendly output" and "Action first." It is real,
MIT-licensed, named-author, and the most-starred skill in the space. Confident
enough to fold in with attribution.

## Patterns to fold into 80% caveman

Each pattern below is quoted/paraphrased from ayghri's SKILL.md + README
(10 rules) with its rationale: **"Working memory is small. Anything not on
screen is forgotten."**

### NEW (not in caveman today) — add these

1. **Restate state/progress every turn.** Say "step 3 of 5" — never assume the
   reader remembers where we are between messages (SKILL.md rule 5). *This is
   the single biggest gap:* caveman optimizes one reply in isolation; this
   optimizes a multi-turn thread. Reinforced by ravila4's todo-list progress
   tracking.
2. **Cap lists at ~5 items; split longer into "do now" vs "later."** (rule 9).
   Chunking + choice-reduction. Caveman caps *lines* (~17) but never *choices*;
   the do-now/later split is a new lever.
3. **Give specific time estimates in minutes, not "a bit."** "About 15 minutes"
   beats "some work" (rule 6). Caveman has nothing on effort estimates.
4. **Suppress tangents — one thread at a time.** Finish the current problem
   before raising a second, and raise it as a *separate* question (rule 4).
   Sharper than caveman's generic "no padding."
5. **Number multi-step work, one bounded action per item.** "1. Open file.
   2. Replace function. 3. Run tests." (rule 2) — each item independently
   doable.
6. **First-and-last-line check before sending.** Reading only the first and
   last line, does the reader know *what to do* and *what happened*? (SKILL.md
   pre-send check). A concrete verification ritual caveman lacks.
7. **Matter-of-fact error tone.** Report failures plainly, no drama, no
   hedging (rule 8). Caveman's "fail loud to the user" covers surfacing, not
   tone.

### SHARPENS an existing caveman rule (nuance, not new rule)

8. **Close with one concrete NEXT STEP, not just a takeaway** (rule 3).
   Caveman already ends with a bottom-line/TLDR — upgrade it: when action is
   pending, the last line should be a *doable next step*, not a summary.
9. **Lead with a doable action, not just "the answer"** (rule 1). Caveman
   leads with the answer; tighten to a command/path/next step when one exists.

### ALREADY in caveman (do NOT duplicate — for honesty)

- "No preamble, no recap, no closers / no 'Let me know if you need anything'"
  (rule 10) == caveman's skip-preamble + no-trailing-summary + banned closer.
- "Make wins visible / state concretely what works" (rule 7) *tension*: caveman
  says skip trailing summaries because "the diff is visible." Reconcile as:
  state the concrete capability unlocked ("login works with magic links"), not
  a step-by-step recap. Adopt the framing, keep the anti-recap rule.

## Attribution line to use

> Multi-turn/ADHD-friendly patterns (restate progress, cap-5 + do-now/later,
> time estimates, suppress tangents, first/last-line check) adapted from
> **i-have-adhd** by Ayoub Ghriss (`ayghri`), MIT License —
> https://github.com/ayghri/i-have-adhd

MIT requires the copyright notice be preserved in derivative works, so keep the
author name and license wherever these patterns land (e.g. a comment in the
skill/CLAUDE.md that adopts them).
