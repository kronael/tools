# Divergence funnel — 4 independent versions per stage, then select

How to actually explore a creative space instead of polishing the first idea.
The unit of iteration is **4 independent versions**, not one refined draft. The
user selects; the selection locks; the next stage fans out again on top of it.

## The core rule

ALWAYS produce **4 independent versions** at each creative stage — never one.
The user picks one to carry forward; the other three are thrown away. One
polished draft hides the design space; four rough ones reveal it.

Independence must be **structural**, not requested. Four agents told "diverge"
but handed the *same* starting assets converge anyway — they take the cheap path
(recolor, retime, one gag) and you get four near-identical outputs. This is the
**germinal v1–v4 failure**: same rig + same source photos + same recording →
skin-deep variation only. Force independence by:

- **BANNING the shared assets.** Forbid reading the prior version's files,
  photos, renderer, recordings. Give each agent ONLY the locked upstream spec
  (see levels) + the skills — nothing else. Isolate each in its own worktree.
- **Seeding different inspiration** into each (below), so they start from
  different corners of the space.

## The four levels (fan out, select, re-extract, repeat)

A finished piece is refined **one level at a time**. At each level you keep what
the user selected upstream and fan out 4 independent takes on THIS level only:

1. **THEME** — the world/subject/tone. 4 independent themes (random-seeded).
   Keep: nothing (or a one-line goal). Vary: everything.
2. **SCENE GRAPH** — the beat map + node hierarchy + motion tracks (the DATA
   graph, see SKILL.md § Principle). 4 independent structures for the chosen
   theme. Keep: theme. Vary: staging, timing, choreography.
3. **VISUALS** — materials, palette, photos/assets, rendering style. 4
   independent looks for the chosen graph. Keep: theme + graph. Vary: craft.
4. **REFINE** — the complete piece. This level does NOT fan out — it progresses
   as **one** version, iterated maker↔critic (SKILL.md § Quality gate) until it
   clears the bar.

Between levels, **re-extract the selected version into a graph/text spec**
(node hierarchy + tracks + beat map as prose/markdown — see
`../../projects/*/schema/demo/germinal-v4.stage.md` for the shape). The next
fan-out builds on that clean skeleton, NOT on the messy artifact — text is
forkable and asset-free, so it transmits structure without dragging craft along.

## Generating random inspiration (to seed divergence)

Two interchangeable methods; both feed one distinct brief per version:

- **RNG → wordlist map (reproducible).** Draw a random 32-bit seed
  (`os.urandom`), record it, and map it deterministically through curated
  wordlists — setting · protagonist · force/twist · material · mood · palette ·
  motion. The seed makes the whole brief reproducible; log seed+words so a run
  can be replayed. (Worked generator: schema `tmp/inspiration.py` pattern.)
- **Sonnet at high temperature.** Ask a `sonnet` agent, temperature ramped up,
  for N deliberately-divergent one-paragraph briefs. Looser and more coherent
  than raw word-salad, but not reproducible — capture the output verbatim.

Hand each version its brief as *inspiration to interpret freely*, not a spec to
execute literally. The brief supplies the corner of the space; the agent fills
it in.

## NEVER

- NEVER ship one "best" version and call it exploration — that's polishing, not
  diverging.
- NEVER let the 4 share mutable assets or a working tree — they'll collide and
  converge. Worktree-isolate; asset-ban.
- NEVER carry the artifact forward between levels when a text/graph extract
  would do — the extract is what keeps the next fan-out independent.
- NEVER fan out the REFINE level — once a complete version is selected, polish
  it single-track.
