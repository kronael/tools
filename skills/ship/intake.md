# Owner brief

Use the owner's request, standing preferences and current code to prefill the
brief.

## One question batch

The question tool blocks until the owner answers. ALWAYS launch independent
research in the background first — here and at every later decision point.

ALWAYS ask only the answers the result depends on, together in one call to
the question tool, or one numbered message if none exists. Use real
alternatives from the task, put the recommendation first, and explain each
tradeoff briefly.

1. **Outcome and boundary** — What must the user be able to do? Which
   observable checks prove it? Name exclusions and material product choices.
2. **What to hammer** — Offer two or three risks found in this change, such
   as failure recovery, user flow or performance. Let the owner choose the
   focus and depth, or delegate the choice. Turn it into named cases to
   exercise, measurable thresholds where relevant, and an existing skill.
   ALWAYS ask it in the opening batch unless the owner's words already name
   the focus: the owner is present when ship starts. NEVER ask it again at
   a later decision point.
3. **Run limits and destination** — State the proposed effort, repair and
   review limits and finish line as defaults. Ask only when the request
   leaves one ambiguous. Record external actions requested by the owner
   separately from actions whose final approval is still required.

ALWAYS omit answered questions. If the request already supplies the whole
brief, state it briefly and proceed. NEVER demand a ceremonial reply.

## Defaults to state when preferences are missing

- **Scope:** the requested change, its defects, docs and acceptance checks.
- **Hammer:** the highest-risk changed boundary. One focused review or check
  after normal `refine`, with one further fix-and-check round if needed.
- **Repairs:** three evidence-producing repair attempts per failing gate.
  Escalate the approach before exhausting them. The count survives resumes.
- **Budget:** estimate work from the inspected scope and honor any owner
  time, token or cost ceiling. Do not invent a spend allowance. If none is
  given, use the repair and review bounds, and ask when new work materially
  grows effort.
- **Destination:** verified local commits. A release, PR, merge, push,
  publication or deployment needs the owner's explicit request.

ALWAYS state each open preference as a default in the shown brief and
proceed on it. The owner corrects a default by replying. NEVER infer a
material decision or external-action authorization from silence. It stays
pending.

## Record the agreement

The plan's owner brief contains the original request, scope and exclusions,
acceptance checks, hammer cases and depth, limits, destination, existing
authorizations and unresolved decisions. Each preference says whether it
came from the owner or a stated default. Use `prompt.md` for plan fields.

The main agent answers a worker's routine questions from the brief and code,
without relaying implementation choices to the owner.

An owner correction updates the same brief and affected remaining steps.
ALWAYS preserve unchanged acceptance items and explicit deferments. NEVER
turn a new message into permission to drop unfinished requirements.

## Real decision points after intake

Ask only when evidence reaches one of these boundaries:

- A material product choice, changed contract, conflict or missing fact
  cannot be settled from the accepted brief and code.
- A proposed repair expands scope, reverses an owner choice, or needs a
  destructive action or an external action governed by an approval gate.
- The accepted effort limit is reached, the repair limit is exhausted, or
  the selected hammer checks still fail after the allowed rounds.
- A required tool, credential, environment or manual user check prevents
  acceptance, after independent authorized work is exhausted.

ALWAYS present the concrete evidence, what is blocked, and two or three
choices with a recommendation. State what each costs or leaves incomplete.
Batch decisions sharing the same dependency, and keep unaffected work
running. NEVER ask "continue?" after a passing step — advance the accepted
plan.

For an approval request, finish the reviewable local result first and cite
the exact owning rule that requires approval. `runtime.md` covers goal and
loop behavior at this boundary.
