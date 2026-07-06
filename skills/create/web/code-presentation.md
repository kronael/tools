# Code presentation (reveal.js)

For **new feature / new work** knowledge-sharing talks. Bug-fix or refactoring
talks need a different structure (leaner, focuses on root cause + diff, not
problem/built/result).

## Repo structure

```
<talks-dir>/YYYYMMDD_<slug>/
  talk.md              ← source content (narrative markdown)
  talk/
    index.html         ← reveal.js slides
    package.json
    Makefile
    vite.config.js
    css/theme/source/theme.scss
```

Scaffold by copying from an existing talk:
```bash
src=<talks-dir>/<existing-talk>/talk
dst=<talks-dir>/YYYYMMDD_<slug>/talk
mkdir -p $dst/css/theme/source
cp $src/package.json $src/Makefile $src/vite.config.js $dst/
cp $src/css/theme/source/theme.scss $dst/css/theme/source/
# update "name" in package.json
```

Build: `cd talk && bun install && make`

## talk.md structure (source document)

Each repo / topic gets 3 themes. Each theme:

```markdown
### Theme N · Title

**What problem this solves**
One paragraph. What was broken/missing/painful. Specific — name the
function, the metric, the support ticket.

**Key commits**
| Hash | Date | Change |
|------|------|--------|
| `abc123` | MM-DD | One-line imperative description |

**What was built**
- `file.ts` — `functionName()`: what it does concretely
- Keep each bullet to one logical unit

**Before / After**
Before: specific broken behavior.
After: specific fixed behavior. Match the Before claim exactly.
```

## Slide structure per theme (index.html)

Use **vertical sections** — one `<section>` per repo, subsections per theme:

```html
<section>                          <!-- repo heading -->
  <section><h1>Repo Name</h1></section>

  <section>                        <!-- theme: problem -->
    <h2>Theme Title</h2>
    <h4>Subtitle</h4>
    <p class="fragment">Problem point 1</p>
    <p class="fragment">Problem point 2</p>
  </section>

  <section>                        <!-- theme: what was built -->
    <h4>Theme Title</h4>
    <h2>What was built</h2>
    <ul>
      <li class="fragment"><code>file.ts</code> — description</li>
    </ul>
  </section>

  <section>                        <!-- theme: before/after -->
    <h4>Theme Title</h4>
    <h2>Before / After</h2>
    <p><strong>Before:</strong> ...</p>
    <p class="fragment"><strong>After:</strong> ...</p>
  </section>
</section>
```

For code diffs or formulas use `<pre><code class="language-text">`:
```html
<pre><code class="language-text">cap = min(60k, max(40k, 50k)) + 10k = 60k ← wrong</code></pre>
```

## Slide rules

- Every content point is a `class="fragment"` — audience controls pace
- `<h4>` = small context label above the slide title (`<h2>`)
- 3–5 fragments per slide; split if more
- No prose paragraphs on slides — bullets and short `<p>` only
- `<strong>Before:</strong>` / `<strong>After:</strong>` always on separate lines,
  After is a fragment
- Code on slides: `<code>` inline for identifiers, `<pre><code>` block for formulas/diffs
- Title slide: `<h1>` + `<h2>` + `<p>` with date and duration
- Agenda slide: `<ul>` with one `<li class="fragment">` per repo
- Close: `<h1>Questions?</h1>`

## Workflow

1. Research: read `talk.md` or run parallel subagents against each repo's git log
2. Write `talk.md` first (narrative source), wrap prose at 90 chars
3. Write `index.html` slides from `talk.md` content
4. `bun install && make` — verify bundle builds
5. Do NOT commit automatically — let the user review first
