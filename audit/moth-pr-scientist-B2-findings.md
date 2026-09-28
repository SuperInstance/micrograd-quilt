# FINDINGS — Scientist B2: detection arena with reference steering

Date: 2026-09-26 · Lane: B's follow-up #1 (detection arena) · `/tmp/pr-b2-lab/`
Nothing pushed. Reuses B's streams/fingerprints/arena verbatim; one steering change.

## 1. Hypothesis under test (B's pre-registered prediction)

Give the moth a reference = ideal-uniform fingerprint; steer on
distance-from-reference instead of cross-window variance. Predicted: matches χ²
on bias detection AND keeps QRNG structural sensitivity that χ² structurally
lacks (1-D marginals of Weyl/vdc are uniform).

## 2. Setup

- Reference = per-fingerprint-type mean vector over **2000 independent pymt
  windows** (W=100, Monte-Carlo uniform ensemble; analytic expectations avoided
  for one machinery path). Frozen in `reference.json` before any arena run.
- Arena identical to B's (blind shuffled slots, real `weightedQuantumPick` from
  quilt-cortex, packets mock:true, W=100, T=25, N=500/stream cap, BINS=10).
- Arms per trial: χ² (B's), moth-variance (B's arena), moth-reference (arena2.mjs).
- K=200 trials × 4 conditions (strong q=0.25, weak q=0.06, qrng, null), paired
  by identical trial IDs → identical stream content across arms.
- Each arm's α=0.05 thresholds calibrated on its OWN null trials (fair).
- **Sanity anchors reproduced:** χ² strong 1.0000 / weak 0.3900 (exactly B's
  published 1.00/0.39); variance-arm FPR 0.0467 (B's 0.045). Harness sound.

## 3. Scoreboard

Bias detection (early-visit flag, power @ α=0.05):

| Arm | strong (q=0.25) | weak (q=0.06) | FPR on uniforms |
|-----|----------------|---------------|-----------------|
| χ² | **1.000** [0.981,1] | **0.390** [0.325,0.459] | 0.050 |
| moth-variance | 0.060 | 0.045 | 0.047 |
| moth-reference | 0.120 [0.082,0.172] | 0.055 | 0.050 |

QRNG (legacy late-detector, as in B's lane): weyl/vdc power var 0.02/0.05,
ref 0.03/0.045 — **all ≈ FPR; χ² 0/0 (structurally blind).**

McNemar (paired, exact): ref vs χ² strong b=0 c=176 p=0; weak b=8 c=75 p=0 —
**χ² wins decisively.** ref vs var strong b=20 c=8 **p=0.036** — reference
steering is a real, significant improvement over variance steering. weak tie
(p=0.81). qrng-late tie (p=1.0).

## 4. The inversion (measured, post-hoc mechanism check — INFERRED)

B's framing assumed QRNG sensitivity would appear as *late* visits (the
variance arm's repulsion idiom). Measured null-trial mean visit positions:

| stream | var arm | ref arm | shift |
|--------|---------|---------|-------|
| weyl | 11.13 | 8.16 | **−3.0 steps earlier** |
| vdc | 13.60 | 9.47 | **−4.1 steps earlier** |
| pymt | 11.73 | 13.97 | +2.2 steps later |

Distance-to-reference **attracts** structural deviation: QRNG streams are
consistently visited earlier under reference steering. Corollary: the legacy
late-detector's FPR on uniform streams jumps to **0.51** under the ref arm —
uniforms get pushed late by the early-arriving structured streams. The signal
didn't disappear; it **inverted polarity**. A post-hoc early-QRNG detector
(α=0.05 on null QRNG positions) shows the shift is real but underpowered at
T=25: power 0.05 var / 0.05 ref — the ~3-step mean shift is smaller than the
trail-order spread.

## 5. Verdicts

1. **B's prediction is REFUTED as stated.** Reference steering does not match
   χ² on bias (0.12 vs 1.00 strong) and its QRNG edge inverts polarity rather
   than manifesting as detectable lateness. Two for two against the moth as a
   *detector at this arena scale* — B's original verdict stands and widens.
2. **The mechanism B hypothesized is CONFIRMED in direction.** Distance-from-
   reference makes structure visible to the moth (weyl −3.0, vdc −4.1 steps,
   bias power ×2 over variance arm, p=0.036). The sensory fix works; the
   decision layer wastes the information.
3. **The arena's budget geometry is the binding constraint, not the sensor.**
   Equal caps (500/stream, T=25×W=100=2500 total) force full drainage of all
   five streams — dwell shares are exactly 0.2 everywhere, the trail's only
   signal is temporal order, and it is diluted by mandatory first-round visits
   plus novelty EMA smoothing (α=0.3). χ² spends all 500 samples in ONE
   statistic; the moth fragments them into five windows of 100 and loses.
4. **The moth-as-detector verdict is now structural, not incidental.** Across
   B and B2: variance steering fails, reference steering fails better. Neither
   closed the 8× power gap to a single-shot χ². Recommend STOPPING detector
   development on the equal-cap arena.
5. **What would actually close the gap (follow-up, one sentence each):**
   (a) adaptive caps — stop draining a stream once its fingerprint distance is
   confidently at reference (sequential SPRT instead of fixed 500); (b) report
   the max per-window reference-distance as the test statistic instead of
   trail order; (c) raise W to 500 so a single window carries the full sample.

## 6. Honest limitations

Post-hoc polarity analysis is INFERRED, not pre-registered. T=25 may be too
short for trail-order statistics in general (B's showcase used T=400; the
stored detection run used T=25 — matched here for anchor compatibility).
Reference ensemble is pymt-only (2000 windows); a multi-generator ensemble
(pymt+platonic+weyl-marginal) might shift absolute distances but not the
polarity result. Simulated steering packets (mock:true) — selection rule under
test, not entropy source.
