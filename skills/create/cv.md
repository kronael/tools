# Create CVs

Build or revise CVs and resumes without confusing content work, evidence work,
and visual design.

## Governing rules

- ALWAYS preserve before improving. Treat an existing CV as the visual source
  of truth. NEVER redesign typography, colors, margins, spacing, contact
  treatment, section styling, or page rhythm unless the user explicitly asks
  for a redesign.
- ALWAYS lead with defensible impact. Put the strongest attributable outcome
  first, ownership second, and implementation detail last.
- ALWAYS minimize disclosure. Prefer a large, NDA-safe business result over
  the confidential mechanism that produced it.
- ALWAYS verify meaning and rendering. Correct source text is insufficient;
  inspect the compiled artifact and confirm each displayed number means what
  the user intended.
- NEVER leave working material in the deliverable. Keep measurement scripts,
  cloned references, draft specs, previews, and audit notes in temporary
  storage unless the user asks to retain them.

## Workflow

### 1. Establish the source of truth

- ALWAYS identify the original visual artifact and the latest approved text.
- ALWAYS save approved text in context or temporary storage before restoring
  an original file.
- ALWAYS record immutable constraints: target length, required sections,
  prohibited content, personal wording, and metric presentation.
- NEVER overwrite the only copy of either the visual baseline or approved
  content.

### 2. Build a claim ledger

For every material claim, record its evidence, causality, confidentiality,
status, and display form.

- ALWAYS distinguish measured results, estimates, targets, and work in
  progress. NEVER present a target or intended migration as achieved.
- ALWAYS attribute individual results only when evidence supports causality.
- ALWAYS use a user-specified conversion rate for currency calculations and
  retain the source quantity in the wording when useful.
- ALWAYS state an NDA-safe outcome and ownership. NEVER expose confidential
  parameters, thresholds, or operational mechanics merely to sound technical.

### 3. Build the content hierarchy

- ALWAYS give the strongest and most recent role the most space.
- ALWAYS lead each role or project with impact, then scope and ownership, then
  supporting implementation evidence.
- ALWAYS categorize work accurately: integrations belong with APIs, GraphQL,
  notifications, and frontend surfaces; auction engines, liquidation, and
  failure paths belong with trading or execution infrastructure.
- ALWAYS end each position with a compact, accurate technology line.
- NEVER list a business domain as a technology. Write `futures-trading models`
  in the result instead of listing `futures` as a skill.
- ALWAYS compress older roles before shrinking the global visual system.

### 4. Present metrics semantically

- ALWAYS display the number the user chose as the headline. Treat calculation
  inputs as internal unless requested.
- For LLM-assisted code output, ALWAYS preserve the agreed baseline as the
  main number and put the multiplier second:

  `Python 150k LOC · ×1.23 with LLMs`

- NEVER headline total LLM-inflated output when the user asked for historical
  hand-written experience.
- NEVER print internal labels such as `pre-LLM`, reverse the multiplier to
  `1.23×`, or expose human/LLM decomposition unless explicitly requested.
- ALWAYS label repository measurements, lifetime estimates, and targets so
  readers cannot confuse them.

### 5. Apply content-only edits

- ALWAYS restore the approved visual baseline before merging revised content
  when a redesign has drifted from the original.
- ALWAYS change one semantic area at a time and preserve the original preamble,
  commands, fonts, colors, and layout conventions.
- When content does not fit, ALWAYS remove repetition, shorten technology
  lines, collapse older roles, and reuse established multi-column patterns
  before changing type size or margins.
- NEVER add new documentation, scripts, or repository structure to a CV
  workspace without explicit approval.

### 6. Verify the artifact

- ALWAYS compile with the document's intended engine.
- ALWAYS confirm the required page count, links, overflow, clipping, glyphs,
  and readable density.
- ALWAYS render every page and visually compare it with the original style.
- ALWAYS extract and reread text from the final PDF; NEVER validate wording
  only in source.
- ALWAYS inspect the final diff and remove temporary artifacts before handoff.

## Visual critique mode

- ALWAYS audit without editing when the user asks for critique or a plan.
- ALWAYS report what works before listing issues.
- ALWAYS prioritize scan path, hierarchy, density, alignment, typography,
  emphasis, and page balance.
- ALWAYS recommend the smallest changes that preserve the existing visual
  identity. NEVER use a critique request as permission for a redesign.
