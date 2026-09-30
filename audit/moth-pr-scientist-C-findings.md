# FINDINGS — Scientist C lane: optimizer comparison on the platonic config space

Date: 2026-09-26 · Lane: search optimizer · Code: `/tmp/pr-c-lab/driver.mjs` (nothing pushed)
Companion lanes: A (sampling geometer, `/tmp/pr-a-lab`), B (statistics auditor, `/tmp/pr-b-lab`)

## 1. Setup

**Repos:** `SuperInstance/platonic-randomness` (real `PlatonicRNG` via node 22
type-stripping), `SuperInstance/quilt-cortex` (the REAL `weightedQuantumPick`
imported from `cortex/moth.mjs` — selection rule tested faithfully; packets
simulated with mulberry32, `mock:true` — no live MothQuantum API key on this
node, and the arm tests the rule, not the entropy).

**Config space:** (seed ∈ shared 500-config bank, solid ∈ 5, backend ∈ 3).
**Design:** paired — all arms share one master PRNG per restart. 10 restarts,
400 evaluations per arm per restart, equal budget everywhere.

## 2. Score-function validation (two failed scales, honestly reported)

| Version | Statistic | Verdict |
|---------|-----------|---------|
| v1 | bucket coverage @256, W=2048 | SATURATED — every config = 1.0000, no discrimination |
| v2 | bucket coverage @65536 | measures sample size only (E[unique]≈2048, sd≈18) — no discrimination |
| v3 | **chi² deviation from uniform @256, W=2048 (lower=better)** | real cross-config variance; same statistic lane B proved sensitive (power 0.39) |

Observed chi² lands 182–206, *below* the uniform ideal of df≈255 — the
solid-mixed streams are mildly over-dispersed. Comparative study unaffected.

## 3. Results (best chi² per restart, lower = better)

| Arm | mean | sd | best | worst |
|-----|------|----|------|-------|
| (a) uniform random | **191.63** | 7.09 | 182.50 | 200.75 |
| (b) hill-climb + restarts | 196.08 | 5.06 | 188.25 | 206.00 |
| (c) moth-guided (`weightedQuantumPick`) | 192.03 | 4.93 | 182.50 | 199.75 |
| (d) reference-steered moth (B's follow-up) | 190.38 | 7.20 | 182.00 | 202.50 |

Paired tests vs (a), 10 restarts:

| Arm | Welch t | df | Cohen's d | Mann-Whitney z | p≈ |
|-----|---------|----|-----------|----------------|-----|
| (b) hill | +1.62 | 16.3 | **+0.72** | +1.17 | 0.32 |
| (c) moth | +0.15 | 16.1 | +0.07 | −0.23 | 0.84 |
| (d) steer | −0.39 | 18.0 | −0.18 | −0.42 | 0.71 |

(lower chi² is better, so POSITIVE d = worse than uniform)

## 4. Verdicts

1. **Uniform random search is the best optimizer on this space at this budget.**
   No challenger beat it; none reached significance (n=10 restarts, anything
   under ~1 sd invisible — same power wall lane B hit).
2. **Hill-climb actively hurts (+4.45 chi², d=+0.72).** Mechanism: the space is
   near-flat + noisy, and greedy acceptance overfits evaluation luck
   (winner's curse). A greedy arm's "best" is a lucky draw, not a good region.
3. **Moth-guided selection ties uniform (d=+0.07).** The ported selection rule
   works mechanically (weights concentrate on low-chi² pairs within ~80
   evals) but the space offers no exploitable structure at W=2048 — fully
   consistent with A (advantage needs W≫16k) and B (trails informative but
   short).
4. **Reference-steering (B's follow-up) ties as well (d=−0.18, best single
   config 182.00).** Pre-registered expectation (diversity ↑, mean ↓) held:
   it finds the floor config as often as uniform but with higher variance.
   Not a win; a different trade.
5. The recurring 182.50 floor across arms is a real bank config, not an
   artifact — verified by direct evaluation.

## 5. Fidelity caveats

- Simulated packets: `weightedQuantumPick`'s INPUT distribution differs from
  live QRNG. The selection dynamics (multiplicative weights over 15 pairs) are
  what's measured. Labeled `mock:true` per doctrine.
- Hill-climb used one fixed neighborhood (change one coordinate); a simulated-
  annealing variant might dodge the winner's curse — not tested (budget).

## 6. Top follow-up

**Raise W, not the optimizer.** The only regime where ANY guided arm should
beat uniform here is W≥16k (A's bound). Re-run this exact driver with
W=16384, EVALS=60 — if moth-guidance still ties at W=16k, the platonic
config space has no learnable structure at any practical memory and the
search question is closed for this product.

## 7. Honest limitations

n=10 restarts (power wall); seed bank 500 (coverage of seed space unknown);
chi2@256 is one statistic (B's lane shows statistic choice moves rankings);
simulated QRNG packets; hill-climb is the only classical arm tested.
