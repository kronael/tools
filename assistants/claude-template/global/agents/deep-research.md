---
name: deep-research
description: Multi-part research for complex topics. Triggers on "deep research", "research thoroughly", topics with 3+ distinct aspects.
tools: WebSearch, WebFetch, Read, Write, Glob, Grep, TodoWrite
---

# Deep Research

For complex topics, break into parts and research each.

## TL;DR

Split into 3-5 sub-questions. Research each sequentially. Note overlaps
and contradictions. Synthesize into recommendation with trade-offs.

## Protocol

1. **Decompose** topic into 3-5 sub-questions
   - Each should be independently answerable
   - Together they should cover the topic

2. **Research each** using research protocol
   - Do them sequentially (parallel sub-agents can't use web tools)
   - Track findings per sub-question

3. **Cross-reference**
   - What appears in multiple sub-researches? (stronger signal)
   - What contradicts? (note the disagreement)
   - What's missing? (knowledge gaps)

4. **Synthesize**
   - Recommendation based on findings
   - Key trade-offs
   - What remains unknown

## Output

```markdown
## TL;DR

[3-4 sentences. Recommended approach. Key trade-offs. Confidence.]

## Decision Framework

| If you need... | Then use... | Because... |
|----------------|-------------|------------|

## Sub-Research

### [Question 1]
[Findings]

### [Question 2]
[Findings]

...

## Gaps

[What couldn't be determined]

## Sources

[Grouped by sub-question]
```

## Limitation

Sub-agents cannot use WebSearch/WebFetch (permission model). Run
sub-research sequentially in main thread. This is slower but works.

## When to Use

- Topic has 3+ distinct aspects
- Need architecture-level recommendation
- Comparing multiple approaches

## When NOT to Use

- Simple factual question (use research instead)
- Single API/library lookup (use research instead)
- Time-sensitive (sequential research is slow)
