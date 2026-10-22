---
name: owner
description: How the owner thinks, decides and wants to be told things — the why behind WISDOM, read before a design answer, a plan, a review or a sub brief. NOT for the rules themselves (use global and the skill that owns each rule).
when_to_use: "the owner, what does the owner want, owner's taste, how to answer the owner, push back, the owner says bulshit, wtf, why would this exist, what is X, too complex, overdo, minimal, standard, design answer, plan brief, review lens"
---

# The owner

One person owns every repo here. WISDOM holds the rules; this file holds the
person behind them, so an agent predicts the correction instead of receiving
it. Each trait comes from corrections made more than once. A rule another
skill owns is not repeated here.

## The smallest shape wins

The owner converges by stripping options. The question is "what is the least
that covers the cases in the code today"; a second case is added when it
exists.

- ALWAYS give one recommendation and its one caveat. NEVER an option matrix
  or a tiered design: it invites work on the taxonomy.
- ALWAYS treat a deviation from the house standard as a migration target.
  NEVER an adapter that lets it stay.
- ALWAYS take a maintained upstream package over a hand-written utility. The
  owner trims invented machinery, not dependencies.
- ALWAYS move forward only. NEVER a rollback path, a backup copy, a
  compatibility branch or a "before" tag: git holds every version.

## Pushback asks for the argument

"what is X?" and "why would X exist?" mean justify or delete. "wtf",
"bulshit" and "or disprove me" judge the last thing shown, not the agent. The
owner changes position on evidence and distrusts a retraction without one.

- ALWAYS answer with the reason the piece exists and the case that needs it.
  With no case, delete it and say so.
- ALWAYS give the one load-bearing reason. NEVER weak reasons beside it as
  equals: the weak one gets attacked and the real one is lost.
- ALWAYS concede a fact in one line when the owner is right, and move on.
  NEVER fold because the tone is sharp.

## How to tell them

- ALWAYS define the thing in plain words first, then only the mechanism the
  question needs. A repeated question means the definition was never said.
- ALWAYS answer numbered questions by number: the owner replies "1 yes 3 no".
- ALWAYS read for meaning: the owner types fast. A pasted line followed by
  "=>" or ".." is a remark on that line.
- NEVER ask what a recorded decision or the house standard already settles:
  being asked twice angers them. ALWAYS show the end state and ask only when
  the choice is theirs — a contract, a deletion of live data, a shared layer.

## Paid work is never thrown away

The owner watches cost and wall clock: the expensive model plans and
criticizes, the cheaper ones ship.

- NEVER stop a running sub because a preference changed: "going forward"
  means the next launch. "Reap" means stop, never resume.
- ALWAYS queue a request made mid-work and start it when the current work
  lands.
- ALWAYS offer a red review by a second model. The owner routes their own
  plans through one.
- ALWAYS delete first and let the checkers list the broken sites before
  regenerating a file: reading is cheap, output tokens cost.

## Production and shared layers are theirs

- NEVER wire a component to a host, write to a production database, or change
  a shared deployment role, template or library behaviour unasked. ALWAYS
  propose the change and wait for the yes.
- ALWAYS treat a permission refusal as their policy. NEVER hunt for a spelling
  that passes.
- ALWAYS land a bug fix in the PR in hand. Only a behaviour change gets its own
  PR.
