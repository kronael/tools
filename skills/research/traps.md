# Traps — plausible wrong numbers, produced silently

Each entry is a mechanism that shipped a believable number with no error, how
it was caught, and the rule. None of them raise; all of them look like a
result.

## Data

- `pd.read_csv(names=..., header=N)` means "row N is the header", not "skip N
  lines": with `names` supplied, row 0 AND row N are discarded, so `header=1`
  eats the first DATA row. It emptied every one-row daily file for a year and
  dropped the first bar of every day, and a "dispersion helps" conclusion — a
  regression that had fit on zero rows and fallen back to a constant — stood
  in three documents before it was retracted. ALWAYS count the rows of one
  raw file by hand and match them against the reader before believing
  anything built on it; ALWAYS one reader per dataset — two readers in one
  process disagree by a bar and nothing says so.
- A bar is labelled by its observation instant, the CLOSE. A bare
  `resample().last()` is left-labelled while carrying the bin's closing price,
  putting the label one bar before the observation; an event stamped at
  `open_time` hands the strategy a one-bar lookahead into the close. ALWAYS
  `closed='right', label='right'`, and ALWAYS pin the convention with a test.
- A unit or power wrong by one step gives a curve of the right shape and the
  wrong amplitude. A log-VARIANCE multiplier deseasonalises returns with
  `exp(0.5*s)` and scales variance with `exp(s)`; `datetime64[us]` turned
  `astype('int64') // 1_000_000` into seconds, every lookup clamped to one row,
  and a signal was exactly zero for three years. A signal that is exactly
  zero, or a score exactly equal to the baseline's, is a unit bug or a dead
  path, NEVER a quiet market.
- A cross-check derived from the series it checks is identical by
  construction: a 5-minute proxy aliased to the model-bar series read
  `rv_5m == rv_1m` for the whole default configuration. ALWAYS derive a check
  from the raw source, never from the thing under test.
- The horizon actually covered is shorter than the one requested when one
  member of a pool has less history, and a stale cache is reused when its key
  omits something that changes the answer. ALWAYS print the effective window
  beside the requested one; ALWAYS key a cache on every input.

## Models

- A model can degenerate into its nested baseline and keep its name. An
  all-NaN covariate column standardised to zero, the extra term vanished, and
  the model scored bit-identical to the plain one under its own name with one
  numpy warning. ALWAYS refuse to fit on a signal with no finite rows; a score
  identical to the baseline is a defect, not a tie.
- A selector that admits everybody, or nobody, is not evidence. In-sample MLE
  returned a positive loading in 100% of 363 windows; the rebuilt selector
  scores candidates on a held-out tail of the fit window with "none" among
  them and records every window's choice. ALWAYS read the selected fraction
  before the score — near 0% or 100% means the selector is degenerate and the
  score means nothing.
- A deployed parameter file that sets only the required fields runs on code
  defaults for the rest, and "zero means skip" switched five of eight live
  gates off with nothing logged. NEVER give a model parameter a default in
  code: the artifact is the authority, an unknown key fails the load, and
  what the artifact does NOT specify is the first thing to read.
- A deployed curve can be a constant on its whole live domain — a clamp band
  entirely inside the blocked region — and three tests passed comparing a
  quantity that cannot move. ALWAYS evaluate a fitted curve across the domain
  it will see and assert that it moves.

## Scoring

- A benchmark computed by different code than the strategy is a different
  benchmark: its sign flipped with the sign of its return, its Sharpe was
  annualised by 20 instead of √252 (+26% on every Sharpe ever reported), its
  daily PnL was bucketed on a different grid. ALWAYS score benchmark and
  strategy through one code path and one bucketing; check the annualisation
  constant once and pin it with a test.
- Winners chosen from rounded point estimates: scores rounded to four decimals
  before ranking, ties resolved by list position, one winner reported over
  spreads of 0.0001-0.0004 with no uncertainty. ALWAYS rank on unrounded
  values and flag a tie when the runner-up sits within a margin an order of
  magnitude above display rounding.
- "Realized" PnL that is mark-to-market: a summary published realized plus
  unrealized at the last mid under `realized_pnl`, and the losing path cleared
  open positions with no fill, so only the worst positions vanished and PnL
  was biased upward. ALWAYS name every PnL by what it is — raw, adjusted,
  marked — and keep operator economics on the ledger only.

## Reports

- Generated text outruns its data. A README asserted "every model
  under-forecasts" unconditionally; a verdict derived from the headline symbol
  read as global while the by-symbol table three paragraphs down contradicted
  it — and had reached the diary, the TODO, the project file and memory before
  it was caught. ALWAYS derive every sentence from the summary frame or scope
  it to what it measured; NEVER hand-copy a number into prose.
- A replay that is not the production path: every risk module off in every
  golden while the README said the full path ran; synthetic books pricing
  every symbol at 1.0 so accounts died on the first fill; one shared book
  making a cross-venue gate unreachable. ALWAYS list what the fixture disables
  beside every result; a real-data replay with negative PnL is a determinism
  gate, not a profitability baseline.
- A recorded result goes stale when the engine is fixed. A one-character
  reader fix shifts every recorded equity curve by one bar per day; the fix is
  not done until the records that depend on it are re-run or marked.
