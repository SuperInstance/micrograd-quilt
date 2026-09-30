# labs/egate — E-gate: e-calibrated conformal over shape space

Two experiments (2026-10-01, main session) built from scouting another agent's
report `SELF-DECOMPOSITION — the compile_decompose gate, the shuffle control,
and what it does not show.md` (delivered by the captain 02:45).

## What the report claimed (extracted, cited-not-rerun)

- 40 synthetic cases, 8×6 compile/decompose parameter space, JEV directional
  gate at accuracy 1.000 (mean gap +0.0953), shuffle control −0.0092, a
  no-op control bug (shuffled labels but not pairings), and the rule
  **"a control must vary the thing it audits"**.
- JEV judged-inference numbers elsewhere in the fleet: realm-ml AUC 0.510/0.454
  (near chance); artifact/human pairs 0.750–0.893.

## Experiment 1 — `exp1.mjs` (6/6 tests green)

Gate a routing decision (compiled vs decomposed) by an **e-value** from
calibration distances, not a threshold.

- Shape space R²; "compiled" population = two 2×2 blocks at centers [2,1] and
  [5,4] (so distance-to-boundary has range); novelties jittered iid across the
  hull. 600 iid covered draws calibrate the conformity; covered test draws at
  seed 555.
- `e(x) = min( ((NC−Kp)/Kp) / ENORM, ECAP )`, Kp = #{d_cal ≥ d_x},
  ENORM = NC·(H(NC)−1)/(NC+1) ≈ 5.965 so the truncated conditional mean is
  exactly 1 under exchangeability; ECAP=100 keeps E[min(e,C)] ≤ 1.
- Results: AUC 0.9965; covered mean e 1.5523 ✓ calibrated; frontier:
  - near band [0.75,1.5): mean e 44.7, saturation 26%
  - mid [1.5,2.5): e 100 (capped), saturation 100%
  - far [2.5,∞): e 100, saturation 100%
- **Discrete-saturation finding**: shape-space distances concentrate on
  {1.0, 1.41, 2.0, 2.24, 2.83, …} while the envelope maxes near 1.2 — nearly
  every non-trivial case saturates. With real delta-shape RLE features the
  distance distribution is richer, but this lattice effect is a real property
  of grid-like shape spaces: **the e-gate's dynamic range lives in the first
  ring**. Kp=0 ⇒ structural verdict `needs_reasoning` (outside the e-framework,
  like ewit's envelope).
- Controls made executable (the report's rule, as code):
  - E1.5 real label-shuffle → AUC 0.4782 (gate killed: pairings changed)
  - E1.6 row-shuffle-without-pairing-change → detected as no-op
  (v1 of exp1 failed E1.5/E1.6 exactly the way the report describes — kept in
  the file header as the honest lineage.)

## Experiment 2 — `exp2.mjs` (6/6 tests green)

How often must "was the compiled answer right?" actually run? A Ville
check-sampling scheduler over a 20k-case stream, 85% covered, table rots at
t=10000 (violation rate 0.03→0.25), detect → full audit → repair → resume.

- v1 design (per-check LR wealth) **died measurably**: LR_pass=0.773 digs a
  healthy-era hole ≈ e^−56, detection delay 4952 settled calls (30× theory),
  alarms stacked into perpetual bursts. The experiment caught it; v2 uses
  **block-Ville** (40-audit rolling blocks, alarm at e ≥ 500, union-bound
  α ≤ 1/500 per block).
- Results (30 seeds): detection 30/30, mean delay **401 settled calls**,
  false alarms 0.067/run, healthy-era savings **12.1×** vs CHECK-ALL,
  post-detection escapes 0 (full audit catches all).
- Tradeoff frontier (12 seeds per point):

  | pCheck | delay | escape rate / rot-era call | healthy cost |
  |--------|-------|----------------------------|--------------|
  | 0.04   | 742   | 0.235                      | 4.3%         |
  | 0.08   | 390   | 0.231                      | 8.3%         |
  | 0.16   | 313   | 0.206                      | 16.3%        |

  Escape rate is roughly flat in p: pre-detection the table serves ~0.2
  violations/call at any sampling rate — the lever that matters is **how fast
  the alarm fires**, and that is what block-Ville buys.

## What this does NOT show (the report's discipline, applied to itself)

- No JEV client in this session: judged-gate figures are cited, not re-run.
- Gate confusion rates in exp2 are structural constants standing in for the
  exp1 gate family; claims are about the **scheduling instrument**.
- Simulation only: no production system, no real delta-shape RLE features yet
  (that's the future lane: replay fleet episodes vs witness sheets as the
  compiled table; adaptive-p check policies).

## Run

```
node exp1.mjs   # 6 tests
node exp2.mjs   # 6 tests + summary JSON
```

Honest marks: SYNTHETIC throughout; e-validity holds exactly under the stated
exchangeability; capping (ECAP=100, e ≥ 500 alarm) is disclosed where used.
