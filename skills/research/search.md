# Search — how a knob is tuned

ALWAYS pick the method that fits the knob, and add a new method as its own
section here, NEVER as a variant inside another method.

## Shared rules

NEVER pick a knob's value from one flat grid — ALWAYS search around the best
point. ALWAYS pin each knob's bracket, its hard limits and the pass cap in the
loop-state file (`layout.md` § Rounds) before the first run. Score every point
as its paired gain over the current point, the same paths and dates under both
settings, with its interval. ALWAYS keep a step whose mean gain is above
zero; NEVER gate a step on noise. ALWAYS judge noise once, on the final point
against the baseline: its paired gain's interval must clear zero, else the
search found nothing. When a pick sits on the bracket's edge, ALWAYS extend
the bracket past that edge and search on, up to the hard limit — NEVER report
an edge pick as the optimum. ALWAYS report a pick on a hard limit as
"constrained", naming the limit.

ALWAYS plot the search on its page (`report.md`), one plot per knob: every
point's paired gain with its interval, numbered in run order, with the fitted
curve, the bracket, the hard limits and the pick. NEVER report the pick alone.
Its score on the search window is in-sample (`method.md` § Runs).

## Coordinate Newton from a grid start

For a few smooth knobs, each expensive to evaluate. First run a coarse grid per
knob, each knob alone from the pinned row (`method.md` § Runs); a knob that
cuts a quantity gets its points at that quantity's quantiles. ALWAYS start with
3 points and widen to 5, then 7, only when the Newton steps do not converge
from them. Each knob's best grid point is its start.

Then ALWAYS take Newton steps one coordinate at a time, from the current
point: fit a quadratic through the knob's best point and its two neighbours,
move the knob to the vertex, clamped to its hard limits, and run that point.
The next knob steps from the point that results. When the quadratic has no
maximum, ALWAYS take a Brent or successive-grid step inside the bracket
instead. Pass over the knobs until a full pass keeps no step: that is
convergence.
