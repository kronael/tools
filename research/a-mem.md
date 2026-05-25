# A-MEM — Zettelkasten for agent memory

A-MEM (Agentic Memory) applies the Zettelkasten note-taking method to LLM agent memory: atomic notes, embedding-linked, with structure that emerges from connections rather than threshold rules.

## Source

- [A-MEM: Agentic Memory for LLM Agents, arXiv 2502.12110](https://arxiv.org/abs/2502.12110)

## Core idea

Don't promote memories by hitting a count threshold ("seen 3 times → save"). Instead:

1. Every new memory is an **atomic note** (one fact, one observation, one preference).
2. Notes are **embedded** and linked to similar prior notes.
3. **Links emerge** from semantic proximity — high similarity = strong link.
4. **Retrieval** walks the graph: pull the query-similar notes plus their strongest links.
5. **Maintenance** is structural: when a cluster of notes gets dense, propose a summary note that links to the cluster (a "hub").

## Why it beats threshold-based promotion

- A pattern repeated 3 times in identical wording is obvious; a pattern across 7 sessions in different wording is the one threshold-based systems miss. Embedding similarity catches both.
- Hubs emerge naturally — no need to decide upfront which categories matter.
- Dedup is built in: a new note that's >0.95 cosine-similar to an existing one gets merged, not appended.

## Relevance to our bundle eval loop

We're not building an agent memory system. But the dedup + hub mechanics apply to skill organization:

- **Dedup proposals**: if a proposed edit to `skills/commit/SKILL.md` is semantically very close to an existing rule in that file, drop the proposal.
- **Detect overlap**: if a proposed new skill embeds within ε of an existing skill's `description` + `when_to_use`, reject as redundant. This is the orthogonality check in our spec.
- **Cluster sibling skills**: `/go`, `/rs`, `/py`, `/ts`, `/tsx` already form a cluster (per-language). A future "umbrella language skill" hub note is reasonable.

## What we don't take

- The runtime memory store. We don't need vector DB infrastructure for a bundle of ~40 markdown files.
- The continuous online update. Our use is batch: at eval-loop time, embed all current skills, embed each proposed edit, compute pairwise similarity, apply the rules above.

## Implementation hint

```python
# during proposal scoring
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('all-MiniLM-L6-v2')
existing_embeddings = m.encode([s.description for s in skills])
proposal_embedding = m.encode([proposal.description])
max_sim = max(cosine_sim(proposal_embedding, e) for e in existing_embeddings)
if max_sim > 0.85:
    reject(proposal, reason=f'overlaps with existing skill (sim={max_sim:.2f})')
```

This is one of several scoring rules, not the whole evaluator.
