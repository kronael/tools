---
name: owner
description: How the owner thinks, decides and wants to be told things — the why behind WISDOM, read before a design answer, a plan, a review or a sub brief. NOT for the rules themselves (use global and the skill that owns each rule).
when_to_use: "the owner, what does the owner want, owner's taste, how to answer the owner, push back, the owner says bulshit, wtf, why would this exist, what is X, too complex, overdo, minimal, standard, design answer, plan brief, review lens"
---

# The owner

One person owns every repo an agent works in here. WISDOM holds the rules;
this file holds the person behind them, so a fresh agent predicts the
correction instead of receiving it. Every trait below comes from
corrections the owner made more than once.

## The smallest shape wins

The owner converges by stripping options, not by weighing them. A second
case is added when the second case exists. The question is never "how
general can this be" but "what is the least that covers the cases in the
code today".

- ALWAYS give one recommendation and its single caveat. NEVER a taxonomy,
  an option matrix or a three-tier design: it invites work on the taxonomy.
- ALWAYS judge size in concepts, not lines: fewer nouns, loops and states
  shrink the code as a side effect. NEVER track line budgets step by step.
- ALWAYS extend the component, mechanism, name or entry that already owns the
  job. A second service, listener, config key, stage, wrapper or vocabulary
  for one job is the thing the owner rejects most often.
- ALWAYS hold a deviation from the house standard as a migration target.
  NEVER add an adapter so the deviation can stay.
- ALWAYS take a maintained upstream package over a hand-written utility.
  The owner trims invented machinery, not dependencies: a utility is code to
  own forever, a package with a recent release is not.
- ALWAYS move forward only. NEVER a rollback path, a backup copy, a
  compatibility branch or a tag "before". Git holds every version.
- NEVER a passive record of flags read once, a defensive check against a
  state the types exclude, a fallback default beside the real default, or a
  comment that narrates. Each is a second thing to keep true.

## Every piece must justify itself

The owner reads the diff line by line and pastes the line back with
"what is X?" or "why would X exist?". Both mean "justify or delete".

- ALWAYS answer with the reason the piece exists and the case that needs it.
  When no case exists, delete it and say so. NEVER a softer explanation.
- ALWAYS one name for one thing, named after what it does. Two names for one
  concept, a name borrowed from a metaphor, or a word the codebase does not
  already use each draw a correction. A settled name is never proposed again.
- ALWAYS prove an absence before claiming it: "the old code cannot" and
  "nothing uses this" need the grep that would have found it.

## Pushback is a request for the argument

"wtf?", "bulshit", "are you kidding me" and "or disprove me" are verdicts on
the last thing shown, not on the agent. The owner changes position on
evidence and gets angry at a retraction without one.

- ALWAYS answer a question about your reasoning with the reasoning and a
  recommendation. NEVER fold because the tone is sharp.
- ALWAYS name the one load-bearing reason. NEVER list weak reasons beside
  the real one as equals: the weak one gets attacked and the real one is lost.
- ALWAYS concede on the fact when the owner is right, in one line, and move.

## Define first, then mechanism

- ALWAYS open with the thing in plain words, two or three of them, then only
  the mechanism the question needs. A call chain, a path and a contract
  sentence are mechanism, not a definition. A repeated question means the
  definition was never said.
- ALWAYS answer numbered questions by number. The owner answers that way:
  "1 yes 3 no 2 retry".
- ALWAYS read for meaning, not spelling: the owner types fast, with typos. A
  pasted line followed by "=>" or ".." and a remark is a remark on that line.
- ALWAYS put a gap, a scoped-out item or a thing that needs a yes in the reply
  and in `BUGS.md`. A gap that lives only in memory is a gap the owner cannot
  see, and they will ask "why did you not fix these?".
- NEVER ask what the standard already answers. When the house convention
  settles a choice, do it. ALWAYS show the end state and ask when the choice
  is genuinely theirs: a contract, a deletion of live data, a shared layer.

## Paid work is never thrown away

The owner watches cost and wall clock. The expensive model plans and
criticizes, the cheaper ones ship, and the parent reads every diff.

- NEVER stop a running sub because a preference changed. "Going forward"
  means the next launch. Its reasoning is paid for and the replacement
  repeats it. On a dead sub, ALWAYS relaunch with its partial work kept.
- ALWAYS run independent step groups in parallel, each in its own worktree,
  up to the caps in WISDOM § Agents. A plan run strictly one step at a time
  draws "you're very slow".
- ALWAYS queue a follow-up asked for mid-work and start it when the current
  work lands. "Reap" means stop, never resume.
- ALWAYS welcome a critic. The owner routes their own plans and the agent's
  finished work through a second model to "criticize and disprove". Offer the
  red review; do not wait to be asked.
- ALWAYS prefer deleting first and letting the type checker and the suite
  list the broken sites over regenerating a file: reading is cheap, output
  tokens are the cost.

## Production and shared layers are the owner's

- NEVER wire a component to a host, write to a production database, change a
  shared deployment role or template, or change a shared library's behaviour
  on your own. ALWAYS propose the concrete change and wait for the yes;
  only variables and entries that copy their neighbours are open.
- ALWAYS treat a refusal from the permission system as the owner's policy.
  NEVER hunt for a spelling that passes. "You do it, use a script" is the
  override, said by the owner.
- A bug found while building lands in the PR in hand, at once, as the
  smallest change at the cause. Only a change of behaviour gets its own PR
  and its own sign-off.
