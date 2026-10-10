---
name: solve
description: Universal entry point — invoke BEFORE any domain skill. Classifies the request, recalls context, then picks the best-matching skill from every skill's frontmatter instead of the first fit. NOT for first-time skill authoring (use wisdom).
when_to_use: "which skill, what should I use, start of task, before acting, route this request, new task, first message, no skill matched"
user-invocable: true
---

# Solve

Triage every incoming message. Internal only — NEVER emit the section
headings below or words like "Classification:". Wrap reasoning in
`<think>…</think>`.

## 1. Classify

**Continuation** — a follow-up to current work (yes, ok, a correction, a
reference to something just discussed). Skip steps 2 and 3: the skills
that matched the prior turn still apply until the entity changes.

**New task** — a distinct request, or the first message in the session.
If unsure, treat as new task.

## 2. Recall (new task only)

- First task of the session: read the 2-3 newest `<cwd>/.diary/*.md` and
  `~/.claude/projects/<slug>/memory/MEMORY.md` (slug = CWD with every non-alphanumeric character → `-`).
- The user references prior work, a name you do not recognize, or "what
  we decided": `/recall-memories <term>` — it greps the session
  transcripts. NEVER answer from diary + memory alone.

## 3. Dispatch (new task only)

The listing in the system prompt is not the full text: each entry is cut
at 1,536 chars, and when the listing overflows its budget the skills
with the least recent use show as a bare name. ALWAYS scan the
frontmatter from disk:

```bash
for d in ~/.claude/skills/*/ "$PWD"/.claude/skills/*/; do
  n=$(basename "$d")
  desc=$(awk 'NR>1 && /^---$/{exit} /^(description|when_to_use):/{f=1; sub(/^[a-z_]*:[[:space:]]*/,""); print; next} f && /^[^ ]/{f=0} f{print}' "$d/SKILL.md" 2>/dev/null | tr '\n' ' ' | sed 's/^[>[:space:]]*//')
  [ -n "$desc" ] && echo "$n: $desc"
done
```

Match the request against each entry (`description` + `when_to_use`):

- One skill matches → read its SKILL.md and follow it.
- Several match → take the one whose `NOT for` clause does not exclude
  this case; a language skill loads beside a workflow skill when both apply.
- None match → say so in `<think>` and work from the `software` baseline.
  NEVER force the nearest skill.

## 4. Act

Respond to the user. Apply the matched skill workflows. Do not mention
this skill.

A skill reached later by another path — the file-extension hook, the
user naming it, a grep — is a skill whose frontmatter lacks the words
this request used. ALWAYS reconcile the output with it, then add the
missing phrase to its `when_to_use` (`wisdom`).
