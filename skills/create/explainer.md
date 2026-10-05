# Explainer — understanding before polish

A local artifact that helps the user understand a concept or mechanism, or
review work. Project documentation belongs to `readme`, not this mode.
ALWAYS use the installed `caveman` output style as the language authority;
NEVER copy its STE rules here. Artifact length follows the teaching need;
the chat reply budget stays in that output style. ALWAYS keep the substantive
answer in chat when the artifact supplements an answer; NEVER make the user
open a file to learn the main result. An explicit artifact request sets the
deliverable.

## Choose the medium

ALWAYS honor a requested format. Otherwise, ALWAYS choose by what the user
needs to understand, not by which renderer is most impressive.

| Understanding need | Medium / next reference |
|---|---|
| One fact, decision, or short causal chain | Plain text; inline visuals belong to `show-me` |
| Relationships, boundaries, or a flow | Static diagram; use the matching diagram row in `SKILL.md` |
| Change an input, compare states, or inspect a process step | Local interactive HTML; `web.md` for page craft |
| Motion, timing, or a derivation across time | Narrated video; `video/render.md`, or `video/manim.md` for Manim / 3b1b |

## Workflow

1. ALWAYS read the source before drafting: code, logs, data, or supplied
   documents. ALWAYS identify the question and the causal claim to explain.
   NEVER invent a result or benchmark — ALWAYS label assumptions and models.
   Completion criterion: each factual claim has source evidence or an
   explicit assumption label.
2. ALWAYS write the explanation around input → change → observable result.
   For autonomous work, ALWAYS show the relevant action, its evidence, and
   any unresolved decision so the user can review what the agent did.
   Completion criterion: the user can trace the result to its cause.
3. ALWAYS build only the selected medium. For HTML, ALWAYS make each control
   change a meaningful input or process step and show the resulting state.
   ALWAYS label inputs, units, and model limits; ALWAYS provide a readable
   initial state, reset, and keyboard access. NEVER add decorative controls —
   ALWAYS remove controls that teach nothing.
   For video, ALWAYS pair the script with visible changes that show causality;
   ALWAYS leave time to read labels and hold still when motion adds no meaning.
   ALWAYS keep the script and captions with the video. Narration follows
   `video/render.md`; NEVER apply short-form marketing hooks or CTAs to an
   educational explanation unless requested.
   Completion criterion: each control or scene explains part of the mechanism.
4. ALWAYS verify the result against the source before applying the router's
   quality gate. For HTML, ALWAYS exercise every control, reset, keyboard path,
   and relevant boundary input in a browser; ALWAYS compare visible results
   with known examples. For video, ALWAYS inspect the rendered beginning,
   transitions, and end. For narrated deliverables, ALWAYS listen to narration;
   ALWAYS check caption timing when captions are present.
   ALWAYS preserve source attribution and report limits the checks did not cover.
   Completion criterion: the generated result agrees with its evidence and
   the chosen interaction or playback checks pass.

## Review checklist

- ALWAYS check the requested format and source-backed claims.
- ALWAYS check that controls or motion reveal a cause and result.
- ALWAYS check the actual artifact, including narration when requested and
  captions when present.
- ALWAYS retain attribution and state unverified limits.
