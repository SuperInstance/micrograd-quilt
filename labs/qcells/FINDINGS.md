# FINDINGS — qcells local lab

Lab for novel experimentation on SuperInstance/MicroMoth-quilt, run
locally per directive 2026-09-28 ("actually using it… iterate locally…
learning system like the many in quilt"). Claim tags: **VERIFIED**
(measured this date, real output), **INFERRED** (proposed next).

## exp005 — n=3 entangled target: engine does NOT generalize as-is (VERIFIED)

Question: same engine, 3 qubits, balanced GHZ {|000>,|111>} target.
Design pin BEFORE running (anti-laundering): a bare counts-set target
is hit at 1.0 by any deterministic product state (|000> is in the
set), so fitness = the **balance witness** min(c[000],c[111])/shots
(`mode="balance"`) — a product state scores 0.0 because its losing
branch never fires; only genuine 3-way correlation scores.

- **Witness gates entanglement (VERIFIED):** hand GHZ
  h(0),cx(0,1),cx(1,2) balance = 0.482 on seed 202; product h(0)
  balance = 0.000.
- **Gradient exists (VERIFIED):** h,cx partial = 0.0, +h(2) = 0.256,
  +cx(1,2) = 0.498. The landscape is a needle WITH slope, not a flat
  desert. Signal density: 52/2000 random genomes score >0 (2.6%).
- **Search FAILED at 12 gens × pop 16 (VERIFIED):** champion frozen at
  balance 0.000 from gen 0 (telemetry: 12/12 promoted rows all 0.0).
  exp004's jitter-dropped replace/indel cloud around a 0-fitness
  champion never sampled the 2.6% signal region — 180 champion-local
  draws, all zero.
- **Harness not at fault (VERIFIED):** default 2-qubit control lane
  inside this harness config reproduces exp001 curve+champion
  byte-identical (runner guard passed).

**Finding 3 (RESOLVED):** the engine that crossed the 2-qubit plateau
in 2 generations cannot reach an entangled target without seed
proximity — champion-local mutation is the bottleneck class, not the
fitness shape. Candidates, ranked: (a) champion-seeded restarts from a
GHZ PREFIX (h + one cx) instead of pure random init — the exp001
lesson (loadCoev seeds around champs, pong-quilt #73) applied at
birth; (b) pop 64 for the n=3 lane; (c) curriculum: balance witness on
2 qubits (Bell min(c00,c11)) before n=3. INFERRED: (a) is the cheapest
first move — it reuses an already-proven doctrine.


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

## Finding 2 — plateau before breakthrough (RESOLVED by exp003)

Gens 1–3 stalled at 0.502 while single-mutation moves couldn't cross
to 1.0. Exp003 ablated mutation classes on identical seeds to find
which class actually crosses the plateau (see below).

## exp003 — mutation-class ablation: gate substitution is the entire
engine (VERIFIED)

Same search, same named seeds, four arms. Ablation is honest at the
sampler level: `mutate_classed` draws the SAME move value from the
same rng stream as `mutate()` and only the APPLICATION is restricted;
a class that cannot apply (indel on a full/short genome, jitter on a
no-rotation genome) is RESAMPLED, never silently replaced. A hard
no-move state raises `MutationDeadlock`, recorded as the arm's result.

| arm | champion | verify P(01) | first perfect gen |
|---|---|---|---|
| control (full mutate) | `[h(1),h(1),x(0)]` | 1.000 | 4 |
| replace-only | `[h(1),h(1),x(0)]` | 1.000 | **1** |
| indel-only | `[cx(0,1),h(0)]` | 0.518 | never |
| jitter-only | — | — | DEADLOCK at gen 0 |

- **Control reproduces exp001 byte-for-byte** (curve + champion) —
  the ablation harness changed nothing about default behavior.
- **Replace-only matches the champion AND crosses at gen 1 instead of
  gen 4.** Gate substitution alone is sufficient, and strictly faster
  than the mixed neighborhood. The gen-1→4 stall in the control was
  the OTHER classes burning candidate draws, not search difficulty.
- **Indel-only never crosses** (stalls at 0.518, below even the
  plateau): with only 3 fixed gates to shuffle, topology changes
  cannot repair wrong gates. Inserts/deletes are genome-length
  plumbing, not fitness engines.
- **Jitter-only deadlocks at birth**: the seed champion has zero
  rotation gates, and jitter can never introduce one (it only nudges
  existing angles). Continuous-only search cannot even leave the
  starting genome here — and in general cannot reach a target whose
  solution needs gates it was never given.
- **Fleet tile:** quantum-cell search wants a DISCRETE gate
  neighborhood as the engine; keep insert/delete for length control,
  drop or heavily down-weight pure angle-jitter when the genome class
  matters more than fine angles. The same ablation seam
  (`mutate_classed` + `MutationDeadlock`) is reusable for any other
  search lane in the fleet.
- Results: `experiments/exp003.results.json` + per-arm telemetry.

## exp004 — jitter-drop policy: convergence 2× faster, champion
unchanged (VERIFIED)

Same search, same named seeds, ONE policy change: the jitter branch is
dropped entirely (`mutate_classed restrict=("replace","indel")`) —
zero harness change, reusing exp003's ablation seam as the policy
knob. Control lane re-run inside this harness still reproduces exp001
byte-for-byte (curve + champion equal to `exp001.results.json`).

| policy | champion | verify P(01) | first perfect gen |
|---|---|---|---|
| full mutate (control) | `[h(1),h(1),x(0)]` | 1.000 | 4 |
| jitter dropped | `[h(1),h(1),x(0)]` | 1.000 | **2** |

- **Same champion, same held-out honesty (verify 1.000), convergence
twice as fast (gen 2 vs gen 4).** The exp003 fleet tile's
recommendation holds at the policy level, not just the ablation level:
jitter was only burning candidate draws in the mixed neighborhood.
- This is a discrete-gate search target; the recommendation is scoped
  to that class (exp003: continuous-only search cannot even leave the
  start genome when the target needs gates it was never given).
- Results: `experiments/exp004.results.json` + per-arm telemetry.

## Next iterations (queued to snowball-queue)

- exp004 DONE (see above): jitter-drop crosses at gen 2 vs control
  gen 4, champion and held-out honesty unchanged.
- exp005 candidate: n=3 qubits, target a 3-bit distribution (entangled target —
  current target is product-state easy); with the exp003 lesson:
  expect discrete gate moves to carry the search there too.
- PROOF statevector witness cell at a TICK (MicroMoth-quilt lane
  follow-on; champion ledger currently emits per-gate prefixes
  O(gates²) sims — n=4+ needs the subset, not full prefixes).
- Seal exp002/exp003 as in-repo experiment receipts
  (`receipts/exp00X-*.json`) once a MicroMoth-quilt PR lane reopens —
  same shape as the exp001 receipt PR (#5, Casey-gated).
