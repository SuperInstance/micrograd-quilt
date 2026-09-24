**1. The gate**

0.55 on raw u is numerology because u is not a probability under this organ: ECE 0.466 means the map u→P(correct) is broken, and 0.885@0.10 means it inverts off-English. A dAnswer written to `memo2.txt` (777 words):

---

**1. The gate**

0.55 on raw u is numerology because u is not a probability under this organ: ECE 0.466 means the map u→P(correct) is broken, and 0.885@0.10 means it inverts off-English. A defensible threshold lives on a calibrated scale with a cost-derived operating point:

- Derive p*: fallback wins when (1−p)·L > C, where L = cost of a wrong fast verdict, C = cost of the slow path. Gate at p* = 1 − C/L on *calibrated* P(correct), never on u. The replacement for 0.55 comes from the ledger's cost fields and re-derives when they change.
- Calibrate per stratum = (task_type × axis × provider × language bucket), never global. Required receipts: paired dual-run rows — fast score + slow-path verdict on the same input — hash-chained, timestamped, current-season, with n_min such that the Clopper-Pearson lower bound of calibrated accuracy clears p* (shrink toward the global curve below ~30 rows). Cold stratum → fail closed to heuristics. The gate is a lease renewed by receipts, not a constant.
- Evaluate structural-first, because collapse regimes are exactly where self-report lies: (1) lang/script outside the calibration set → fallback before u is consulted; input within ε of the 512 ceiling → typed refusal (§3); (2) router margin < m → escalate; (3) dual-checkpoint disagreement > d → fallback (66ms is still free); (4) calibrated LCB(p̂) < p* → fallback. noul is a calibration feature, never a sole trigger — it is the same organ's trained self-report, barred from the bandit for that exact reason.

Book per gated row: {stratum key, curve hash + fit window + n, raw u, calibrated p̂ + LCB, sub-gate fired + value, decision, parent_receipt_id → slow verdict}. Drift trip: weekly, realized accuracy of gated-through rows vs p* per stratum; shortfall > ε auto-reverts the stratum to fallback until re-earned. The chain must contain the evidence that could falsify the gate.

**2. Seed washout**

Beta(1+2u, 3−2u) carries pseudo-mass 4 (prior mean u). After n pulls at true rate p, posterior mean = (4u + n·p̂)/(4+n): seed bias = 4(u−p)/(n+4). Bias < ε requires n > 4|u−p|/ε − 4. Off-English |u−p| = 0.785 → ~59 pulls at ε=0.05, ~153 at ε=0.02, per (task_type, provider) arm. That is the benign case. Two malignancies: (a) Thompson allocates the pulls, so the seed buys its own evidence budget — poisoned-high serves garbage while self-correcting; poisoned-low starves a good arm forever (zero pulls → infinite washout). Washout is a function of allocation policy, not |u−p| alone, so cap the pseudo-mass and decay it. (b) Farming is trivial: if task_type is a caller string, alias minting is an arm-reset attack; seasonal re-fit re-seeds every arm from laya confidence at once — a drifted laya launders into all arms simultaneously and resets every washout clock.

Ship: (1) canonical task-type registry, hashed; unknown alias → Beta(1,1), no seed, typed row. (2) Seed once per arm lifetime; re-fits re-calibrate the u→p̂ mapping, never re-seed live arms. (3) PRIOR_STRENGTH cap 2.0 with power-prior decay α0·cⁿ, c≈0.9 — the seed dies geometrically (~40 pulls), washout guaranteed. (4) Seed from calibrated p̂, never raw u; seeding forbidden on stale-curve strata. Seed receipt: {arm, taxonomy hash, source u + checkpoint_id + router_score, calibration curve hash, (α0,β0), decay c, expiry pulls, trigger actor}. Retroactive audit = chain replay: per arm, reconstruct the seedless counterfactual posterior, flag arms where ≥k routing decisions flip — that flag is the seed-influence metric MOTH watches.

**3. Truncation**

The receipt is for downstream state machines — the bandit, the §1 calibration fit, the lease evidence — not for humans. A field no consumer is forced to read is a log line; the test is deletion: remove it and see if any output changes. Today nothing changes: decorative.

A truncated-input score is a claim about unseen evidence — a refusal wearing a score's clothes ("scored the visible 2%"). Enforcement: coverage = tokens_seen/tokens_total becomes first-class; truncation ratio > τ (5%) forces a typed refusal row for affected axes (refusal_type: insufficient_context; visibility = span hashes + counts); overall is computed only from surviving axes with an explicit unknown term, never a silent average; the bandit skips truncated axes (they carry zero information about arm quality — same bar as noul); truncated rows are excluded from calibration fits or §1's curves inherit the collapse. Below τ: downweight w = coverage, weight itself receipted.

Minimal demo diff — one branch, moved earlier: the truncation check becomes a precondition inside aggregation, not post-hoc metadata booking: `if coverage < τ ∧ axis ∈ {score, overall}: emit refusal row, skip bandit update; else overall ← Σ coverage-weighted surviving axes`. Load-bearing means overall cannot be produced without disposing of truncation.
