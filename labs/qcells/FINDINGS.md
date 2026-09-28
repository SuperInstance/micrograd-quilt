# FINDINGS — qcells local lab

Lab for novel experimentation on SuperInstance/MicroMoth-quilt, run
locally per directive 2026-09-28 ("actually using it… iterate locally…
learning system like the many in quilt"). Claim tags: **VERIFIED**
(measured this date, real output), **INFERRED** (proposed next).

## Provenance

- Engine: `micromoth.py` vendored at `bbd10ac2ffd4…` (matches the
  import-baseline manifest pin on MicroMoth-quilt main).
- Choreography: CELL-MAPPING receipts (PR #2 merged; PR #3 stacked).
  Rows use the fleet WAL canonical key set; hashes fnv1a-64 chain,
  state witnesses sha256 (PROOF form).
- Nothing unseeded is ever written as a result. Seeds are named in
  every WORLD row: root 7, train 101, verify 202, shots 512.

## exp001 — champion-seeded bias search toward |01⟩ (VERIFIED)

8 generations × pop 16, gate budget 6, train/verify seed split.

| gen | train P(01) | verify P(01) | |
|---|---|---|---|
| 0 | 0.225 | 0.234 | PROMOTE |
| 1 | 0.502 | 0.518 | PROMOTE |
| 2–3 | 0.502 | 0.518 | plateau |
| 4–7 | **1.000** | **1.000** | PROMOTE |

- **Prelude A:** mid-circuit `m` does not collapse — statevector VIEW
  byte-identical with/without a mid-circuit measure. Confirms the
  honest-limit gap posted on MicroMoth-quilt#3: micromoth sampling is
  deferred `|ψ|²` over the final state; EFFECT "collapse" cells are
  sampling events, never state mutations.
- **Prelude B:** fixed circuit `x(0),h(1)` across 32 seeds: P(01) ∈
  [0.453, 0.543], spread **0.090** at 512 shots — the train/verify
  split is load-bearing, measured not assumed.
- **Champion:** `[["h",1],["h",1],["x",0]]` → deterministic |01⟩ on
  both seeds. Replay-verified witness ledger: 12 rows, PROOF head
  `7417f8a8ad75a2aa`, `replay_ledger → OK` (chain, per-gate state
  witnesses, seeded histogram all reproduced).

## exp002 — parsimony pressure kills the degenerate champion (VERIFIED)

Same search, same named seeds (root 7 / train 101 / verify 202 /
shots 512), per-gate penalty on the TRAIN selection score only; the
held-out verify promotion gate untouched. Sweep 0.00 / 0.02 / 0.05.

| parsimony | champion | len | verify P(01) | first perfect gen |
|---|---|---|---|---|
| 0.00 (control) | `[h(1),h(1),x(0)]` | 3 | 1.000 | 4 |
| 0.02 | `[x(0)]` | 1 | 1.000 | 3 |
| 0.05 | `[x(0)]` | 1 | 1.000 | 3 |

- **Control reproduces exp001 byte-for-byte** (curve + champion equal
  to `exp001.results.json`) — the pressure is purely additive, no
  drift in the baseline lane. FAIL-first by construction: the runner
  refuses to write results if the control mismatches.
- Parsimony at 0.02 suffices: the dead `h;h` pair is shed and the
  minimal deterministic champion `x(0)` wins on both held-out seeds.
  Convergence MOVES EARLIER (gen 3 vs gen 4), not later — shorter
  genomes are easier to cross to determinism, so parsimony is not a
  tax on search speed here.
- Lesson for the fleet tile: charge parsimony on selection only, never
  on the promotion gate, or the held-out-seed honesty dies with it.
- Results: `experiments/exp002.results.json` + per-penalty telemetry.

## Finding 1 — correct-but-degenerate champion (RESOLVED by exp002)

The champion carries a dead gate pair: `h;h` = identity. Fitness alone
rewarded it — nothing penalizes genome length. A parsimony pressure
(small penalty per gate, or MDL: bits to encode genome + KL to target)
should select `x(0)` alone. Exp-002: add parsimony, re-run, check the
champion genome shrinks while P(01) stays 1.0, and measure whether
convergence generation moves.

## Finding 2 — plateau before breakthrough (INFERRED → exp003)

Gens 1–3 stalled at 0.502 while single-mutation moves couldn't cross
to 1.0; gen 4 crossed via (likely) an insert/replace that completed
the deterministic path. Theta-jitter mutations dominated early
(continuous angles, small effect); discrete gate moves are the
load-bearing class. Exp-003: ablate mutation classes (replace-only,
insert/delete-only, jitter-only) and record which class crosses the
plateau — tells the fleet whether quantum-cell search wants discrete
or continuous neighborhoods, a reusable tile for other search lanes.

## Next iterations (queued to snowball-queue)

- exp002 parsimony/MDL pressure; exp003 mutation-class ablation.
- n=3 qubits, target a 3-bit distribution (entangled target —
  current target is product-state easy).
- Champion ledger currently emits per-gate prefixes O(gates²) sims;
  n=4+ needs the PROOF-witness-at-TICK subset, not full prefixes.
- When MicroMoth-quilt#3 lands: seal exp001 as
  `receipts/exp001-bias-search.json` in-repo (the lane's first
  experiment receipt) + PR.
