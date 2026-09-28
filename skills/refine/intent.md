# Settling the ask

The misreadings that cost whole investigations, and the one cheap exchange that
would have caught each. Read before step 1 of the workflow.

The user writes fast and misspells. Density is not ambiguity: the words are
precise, the typing is not. NEVER read a typo as a vague instruction, and
NEVER resolve one by picking the reading that fits the work already in flight.

## The referent, not the word

A name the user corrects is one used for ONE thing while you are using it for a
category. Resolve it against the tree — the config file, the layout metadata,
the ansible flavour — print the path you resolved it to, and carry on.

- ALWAYS settle a contested name from the artifact that defines it, not from
  the conversation; the conversation is where the two meanings drift apart.
- ALWAYS write a settled name where the next session reads it — the project
  `CLAUDE.md`, a spec's vocabulary section, `MEMORY.md`. A name settled in a
  reply is unsettled by the next `/clear`, and the same correction arrives
  again days later.
- NEVER answer a naming correction by explaining that both names denote the
  same product. The user knows, and is naming which one.
- A plural — "the specs", "the tests" — names the work in hand as readily as
  the repository's whole set, and resolves to the bigger one by default. ALWAYS
  ask which before sweeping; the sweep's answer is true and useless.

## An unknown word belongs to nothing yet

A noun you have never seen is not a value for whichever slot is currently open.
Mapping it there spends turns proving the wrong thing absent.

- ALWAYS ask "what is X?" — four words — before searching for X or fitting X
  into the task in hand.
- NEVER ask "did you mean X is the <thing I am working on>?". A yes to a
  compound question confirms the half you did not mean.

## Numbers that disagree name a different object

When a stated count and your measurement conflict, the measurement is usually
right and pointed at the wrong tree.

- ALWAYS state what you measured and the path you measured it over, then ask
  which object — NEVER open by refuting the number.

## Every instruction gets a line

A request carries several instructions. One that cannot be carried out — a
label that does not exist, a host that is unreachable — is a result, not a
detail to mention in passing and drop.

- ALWAYS close the reply with each instruction's outcome, including the ones
  you refused and the ones you could not do, and say what would unblock them.
- ALWAYS look where the project keeps things before reporting you lack them:
  credentials in `cfg/`, data on the host, code on an unmerged branch. "I
  can't from here" is a claim about the tree and settles like any other
  (`claims.md`).

## Check the promise, not the state

"Run it as agreed" was answered with a health check on the two containers
already running — which cannot surface the third that was never launched.

- ALWAYS check the agreement against reality, never reality against itself:
  list what was agreed, then diff it against what exists. The other direction
  cannot fail.

## Answer, do not offer

- ALWAYS answer the question asked. "why?" wants the reasoning; a reason
  followed by "shall I?" hands the decision back to someone who already made
  it.
- NEVER present options the user has already chosen between, and NEVER re-ask
  what an earlier turn answered. A question spends the user's attention;
  reserve it for what is irreversible or genuinely theirs to decide.
- ALWAYS defend a challenged position if the evidence still holds, and say what
  would change it. Folding on pushback destroys the one signal the user has
  that the work was checked.
- NEVER argue against a shape the user did not propose. When an instruction
  names the control flow but not the form, ALWAYS write the three lines and ask
  "this shape?" — cheaper than a refutation you then retract.
- NEVER rest a decision on a name the user has not been shown. A term coined
  inside one worktree is not shared vocabulary until its diff has been.

## Repetition is the tell

The same instruction typed twice, or the same correction made in two sessions,
means the first one never landed in anything durable.

- ALWAYS treat a repeat as a defect in where the answer was written, not as
  emphasis — re-answering in the reply reproduces the failure.
