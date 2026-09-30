# TENSION FACE — exp029 pooled REFUTED vs exp033/exp035 resolution-RETAINED

Status: SYNTHESIS DOC (no new statistics; every number below is quoted from
sealed receipts). Author: snowball pulse 2026-09-30 06:11 CST. Branch
`qcells-exp004-jitter-drop`. For Casey to read before any further census
spend.

## The two faces, verbatim from their seals

**exp029 (pooled deviance, corpus 16 streams, sealed by exp028):**
verdict_primary_rule = **SHARED-HAZARD-REFUTED**
exact conditional deviance p = 0.0032558 (enumeration over 3,268,760
compositions), alpha 0.05, binding rule = exp028 Q2 seal. Bonferroni
per-stream diagnostic: no stream rejects. Reverse sensitivity rule:
SHARED-HAZARD-RETAINED-UNDER-REVERSE-RULE (both must reject; primary did).

**exp033 (per-stream gates, family of 24, sealed by exp032):**
FAMILY VERDICT = **ALL-SHARE-W_HAT RETAINED** at gate 0.05/24 vs sealed null
hazard w_hat = 10/2009 = 0.0049776. Block E clean operating point (streams
contributed nothing to w_hat): 1069 desert draws, 5 hits, 4 crossers; zero
streams trip; named HOT = none, named FROZEN = none.

**exp035 (paired-stream joint gates, sealed by exp034):**
VERDICT = **FAMILY-PAIR-HAZARD RETAINED** at gate 0.05/552 vs w_pair =
15/3078. 276 pairs x 2 probes: zero trips on both. Closest approach probe A
min p = 0.0051676 (pair k3+k20, h=3/n=71, 57x above gate); probe B min p =
0.0585452 (pair k12+k20, 646x above gate). exp034's structural-silence
prediction for probe B holds exactly.

## Why both faces are honestly sealed

- exp029 pools because the exp028 Q2 seal says pool. Its 10 events live in
  16 streams; a pooled deviance asks "is the aggregate event count
  surprising under one shared hazard?" and gets p=0.0032558 → REFUTED.
- exp033/exp035 ask the decomposition question: "can the excess be NAMED to
  a stream (k) or a pair (k,k')?" and get: no nameable unit at either
  resolution → RETAINED at every resolution finer than pooled.
- Both read the same 24-stream corpus (3078 draws, 15 hits total at exp035
  accounting). Neither contradicts the other's arithmetic; they answer
  different questions.

## Reconciliation reads (all labeled, none sealed)

1. **Smooth low-rate heterogeneity**: the field's per-stream hazards vary
   below pair resolution; pooling feels the sum of small deviations, naming
   cannot find any single carrier. Read: exp029's REFUTED is real but
   unassignable — like detecting a faint extended source with an
   instrument that cannot resolve it.
2. **Small-cluster / interaction signature**: exp033 synthesis explicitly
   allows a cluster of 2-3 streams whose individual gates are underpowered
   (frozen-side blindness: n_zero = 1238 needed vs 169 design). Pair gates
   (exp035) should have caught a 2-stream cluster and did not; a 3+ stream
   cluster at low contrast remains possible and untested (triplet space =
   C(24,3) = 2024 tests, needs its own seal).
3. **Corpus conditioning**: the 16 corpus hits set w_hat, so corpus-stream
   tails shrink toward the middle (conditioning-on-total, labeled post-hoc
   in exp033). Block E is the clean operating point — and block E alone
   (5 hits / 1069 draws) sits inside a 2-sigma envelope of w_hat; no signal.

## What is CLOSED vs OPEN

CLOSED (per seals): pooled lane (exp029); per-stream lane at n=24 (exp033);
per-pair lane at census-n (exp035). Any escalation requires a FRESH
pre-registration before data contact — a new census block (block F, salts
k24+), a triplet-gate seal, or both.

OPEN, Casey decisions:
- **Read the face**: accept reconciliation (1) — retire the hazard question
  at "smooth field, nothing nameable" — or commission block F / triplet
  seal to push resolution once more.
- Budget note: each further resolution doubling costs a sealed batch; the
  last three batches moved no verdict. Absent a new scientific question,
  the marginal information is near zero.
- exp029-vs-033 tension should be cited wherever either verdict is quoted
  from now on; quoting one without the other is a laundering risk.

## Receipts

- exp029: `experiments/exp029.results.json` (verdict SHARED-HAZARD-REFUTED)
- exp032/033: per-stream pre-registration + run (ALL-SHARE-W_HAT RETAINED)
- exp034/035: pair-gate pre-registration + evaluation (FAMILY-PAIR-HAZARD
  RETAINED)
- Cross-check pins: `tests/test_tension_doc.py` (quotes match receipts)
