---
name: resolve
description: Triage an incoming request — classify (new task vs continuation), recall context on new tasks, dispatch matching skills, then act. NOT for first-time skill authoring (use wisdom).
when_to_use: start of any non-trivial request, "what was I working on", ambiguous follow-up, picking up after a gap, deciding which skill applies
user-invocable: true
---

# Resolve

Internal triage you run before acting on a request. Reason in `<think>` —
never emit the section headings below or words like "Classification:",
"Continuation —", "New task —".

## 1. Classify

**Continuation** — follow-up to current work (yes, ok, corrections,
references to something just discussed). Skip recall (step 2); go to
dispatch (step 3). Skills that fired on the prior turn usually still
apply for follow-ups on the same entity.

**New task** — a distinct request, or the first request in a session. If
the entity, repo, or deliverable may have changed, treat as new task. If
unsure, treat as new task.

## 2. Recall (new task only)

ALWAYS run `/recall-memories <topic>` on a new task before claiming you
lack context — it searches diary, `MEMORY.md`, and recent session
transcripts. NEVER answer "I don't have context" without recalling first.
It also surfaces unfinished prior-session work to resume.

## 3. Dispatch (new task AND continuation)

```bash
for d in ~/.claude/skills/*/; do
  [ -d "$d" ] || continue
  n=$(basename "$d")
  desc=$(awk '/^description:/{f=1; sub(/^description:[[:space:]]*/,""); print; next} f && /^[^ ]/{exit} f{print}' "$d/SKILL.md" 2>/dev/null | tr '\n' ' ' | sed 's/^[>[:space:]]*//')
  [ -n "$desc" ] && echo "$n: $desc"
done
```

Reads the one-line `description:` from each skill's frontmatter. Match
descriptions against the request. If a skill matches, read its
`SKILL.md` and follow its workflow. On continuations the prior turn's
skills usually still match — keep using them unless the entity changed.

## 4. Act

Respond to the user and apply matched skill workflows. Never mention this
skill ran.
