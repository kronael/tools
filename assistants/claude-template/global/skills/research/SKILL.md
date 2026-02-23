---
name: research-hub
description: Deep research hubs on technical topics. Use when asked to "research thoroughly", "deep research", "create research hub", or build a comprehensive knowledge page on a frontier topic (biotech, AI, crypto, etc).
---

# Research Hub

Build single-page research hubs by running parallel deep-research
agents, then distilling and assembling into a web page.

## Workflow

### 1. Plan Tasks

Create `tasks.md` in the project directory with numbered tasks,
dependencies, and status checkboxes. Update throughout.

### 2. Parallel Deep-Research Agents

Launch one `deep-research` subagent per topic using Task tool:
- `run_in_background: true` for parallelism
- Each agent does 5 iterative loops (search, read, refine)
- 3 agents max in parallel (avoids rate limits)
- Save each agent's output to `./tmp/<topic>.md`

```
Task: "Research <topic>. Do 5 iterative deepening loops:
  loop 1: broad landscape, key companies, terminology
  loop 2: specific technologies, mechanisms, challenges
  loop 3: key papers, researchers, recent breakthroughs
  loop 4: companies, funding, clinical stage
  loop 5: cross-references, gaps, synthesis
  Save comprehensive findings."
```

### 3. Prepare Web Directory While Agents Run

While research agents run in background:
- Check existing site patterns (look at sibling pages)
- Create the app directory: `/srv/data/takopi/web/<name>/`
- Scaffold `index.html` with the page structure

### 4. Distill Agent

After research agents complete, launch `distill` subagent:
- Input: all research outputs
- 5/3 recursive summarization (5 passes, keep top 3 insights)
- Output: TLDRs, cross-cutting patterns, key tensions

### 5. Assemble Web Page

Single-page HTML with all research organized into sections:
- TLDR (distilled summary at top)
- Topic deep-dives (one card per research area)
- Companies table (name, stage, funding, focus)
- Key papers (title, authors, year, one-line takeaway)
- Guidebooks / learning path (ordered progression)
- Key people (researchers, founders)
- Cross-cutting patterns (from distill agent)

### 6. Deploy

Drop `index.html` into `/srv/data/takopi/web/<name>/`.
Available at `https://takopi.fiu.wtf/<name>/`.

## Page Design

- Dark monospace theme (consistent with takopi.fiu.wtf)
- Sticky nav with section links
- Cards for topic deep-dives
- Tables for structured data (companies, papers)
- Tags for status (clinical stage, funding round, etc.)
- No external dependencies (inline CSS, no JS frameworks)
- Mobile-responsive

## Rules

- ALWAYS save raw research to ./tmp/ before assembling
- ALWAYS run research agents in parallel (not sequential)
- ALWAYS distill before final assembly (raw research is too long)
- NEVER put the full research text on the page (summarize)
- NEVER skip the iterative deepening (shallow research is useless)
- ALWAYS update tasks.md as work progresses
- ALWAYS check existing takopi pages for style consistency

## Research Agent Prompt Template

```
You are researching <TOPIC> for a comprehensive knowledge hub.

Do 5 iterative deepening loops. Each loop builds on the previous.

Loop 1 - Landscape: What is the field? Key terminology. Major
  players. Current state of the art. Market size.

Loop 2 - Mechanisms: How does it work technically? Key challenges.
  Current approaches and their tradeoffs.

Loop 3 - Literature: Important papers (title, authors, year,
  one-line summary). Key researchers. Recent breakthroughs (last
  2 years).

Loop 4 - Companies: Who is building what? Funding. Clinical/
  development stage. Differentiation.

Loop 5 - Synthesis: Cross-references between loops. Gaps in the
  field. Emerging trends. Contrarian takes.

Output format: structured markdown with clear sections.
```

## Distill Agent Prompt Template

```
Distill <N> research documents into:

1. TLDR (3-5 sentences, the most important things)
2. Cross-cutting patterns (themes that appear across topics)
3. Key tensions (where experts disagree or tradeoffs exist)
4. What surprised you (non-obvious findings)

Use 5/3 recursive summarization:
- Pass 1: summarize each document to 1 page
- Pass 2: merge related summaries
- Pass 3: extract top 3 insights per merged group
- Pass 4: synthesize across groups
- Pass 5: final distillation
```
