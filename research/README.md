# Research Hub

Notes, paper summaries, and source links that informed the skill auto-improvement design (`specs/2-hermes-skill-autoimprove.md`).

Each file is a single topic — drop new findings into its own file rather than expanding an existing one. Files are short on purpose so a future reader can pull just what they need.

## Index

| topic | file | one-liner |
|---|---|---|
| Hermes Agent | [hermes-agent.md](hermes-agent.md) | What the Curator actually does (idle-triggered, not per-turn) and why BSWEN's critique matters |
| Library Drift paper | [library-drift.md](library-drift.md) | Empirical: LLM-authored skills underperform human-curated ones by 16 percentage points |
| DSPy MIPROv2 | [dspy-miprov2.md](dspy-miprov2.md) | Offline batch compilation against an eval set — the model we're adopting |
| A-MEM | [a-mem.md](a-mem.md) | Zettelkasten for agent memory: atomic notes, embedding-linked, dedup by similarity |
| Reflexion | [reflexion.md](reflexion.md) | Self-critique helps over episodes; per-turn reflection is a documented anti-pattern |
| Anthropic SKILL.md guidance | [anthropic-skills.md](anthropic-skills.md) | "Explain *why*" > "ALWAYS/NEVER caps" — conflicts with our wisdom skill, worth a call |
| Multi-agent failures | [multi-agent-horror.md](multi-agent-horror.md) | What blows up at scale: no stop conditions, no cost ceilings, no observability |
| Eval-set construction | [eval-sets.md](eval-sets.md) | How to bootstrap a usable eval set from session transcripts |

## How to add a topic

1. Create `research/<slug>.md` with a 1-line title + the source link(s).
2. Summarize the source in your own words (one paragraph).
3. List the specific findings that bear on our design (bullet form).
4. Note what it suggests we should do or avoid.
5. Add a row to the table above.

## Conventions

- Cite the source URL on first mention. Add a footnote-style block at the bottom if you cite many.
- One claim per bullet. If you can't link a claim to a quote or measurement, qualify it ("probably", "anecdotally").
- Keep each file under ~150 lines. If it's longer, split it.
