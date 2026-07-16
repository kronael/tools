---
name: resolve
description: >
  Universal entry point — invoke BEFORE any domain skill. Loads diary/facts
  context first, then picks the best-matching skill instead of jumping at the
  first fit. NOT for first-time skill authoring (use wisdom).
when_to_use: "which skill, what should I use, start of task, before acting, route this request"
user-invocable: false
---

# Resolve

Triage every incoming message. Internal only — never emit the section
headings below or words like "Classification:", "Continuation —", "New
task —". Wrap reasoning in `<think>…</think>`.

## 1. Classify

**Continuation** — follow-up to current work (yes, ok, corrections,
references to something just discussed). Skip recall (step 2);
proceed to dispatch (step 3). The skills that fired on the prior turn
usually still apply for follow-ups on the same entity.

**New task** — distinct request, or first message in session. If unsure,
treat as new task.

## 2. Recall (new task only)

```bash
ls -t ~/diary/*.md 2>/dev/null | head -2 | xargs cat 2>/dev/null
ls ~/facts/ 2>/dev/null | head -20
```

Read the 2 most recent diary files. Scan fact filenames; read any
relevant to the topic. If the user references an unrecognized name:

```bash
grep -ril "<term>" ~/diary/ ~/facts/ ~/users/ 2>/dev/null | head -5
```

If a fact's `verified_at` is >14 days old and the task needs accurate
data, refresh via `/find <topic>`. Delete facts that are wrong.

## 3. Dispatch (every turn — new task AND continuation)

```bash
for d in ~/.claude/skills/*/; do
  n=$(basename "$d")
  desc=$(awk 'NR>1 && /^---$/{exit} /^(description|when_to_use):/{f=1; sub(/^[a-z_]*:[[:space:]]*/,""); print; next} f && /^[^ ]/{f=0} f{print}' "$d/SKILL.md" 2>/dev/null | tr '\n' ' ' | sed 's/^[>[:space:]]*//')
  [ -n "$desc" ] && echo "$n: $desc"
done
```

Match each entry (`description` + `when_to_use`) against the request.
If a skill matches, read its SKILL.md and follow its workflow. On continuations, the same skills
that matched the prior turn typically still match — keep using them
unless the entity has clearly changed.

## 4. Act

Respond to the user. Apply matched skill workflows. Do not mention this
skill.
