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

## exp006 — Finding 3 candidate (a): GHZ-prefix seeded restart (VERIFIED)

Two seeded lanes, same seeds/policy as exp005, success = held-out
balance >= 0.45:

| lane | seed | champion | verify balance | first >=0.45 gen |
|---|---|---|---|---|
| A: bare GHZ prefix | [h(0), cx(0,1)] (fitness 0.0) | [h(0), crx(1.0,0,2), cx(0,1)] | **0.482** | **gen 2** |
| B: partial entangler | [h(0), cx(0,1), h(2)] (fitness 0.256) | unchanged | 0.242 | never (8 gens) |

- **Candidate (a) CONFIRMED (VERIFIED):** seeding the bare skeleton —
  zero fitness at birth, but ONE indel/replace move from correlation —
  crosses to near-balanced GHZ in 2 generations. Birth proximity is
  the whole game: exp005's 180 random-local draws found nothing,
  exp006 lane A's 32 draws around the prefix found it twice over.
- **Bonus finding (VERIFIED):** the PARTIAL entangler is a fitness
  TRAP, not a ladder. Lane B never sampled above 0.256 in 120 draws
  (telemetry max = 0.2559): the min-witness rewards the h(2) plateau
  and the single winning replace move (h(2)→cx(1,2), ~1%/draw) is
  too rare under the jitter-dropped policy. More fitness is not more
  reachable — a mid-slope seed can be worse than a zero-fitness seed.
- Harness guard: default lane reproduces exp001 byte-identical (pass).

**Finding 4 (RESOLVED):** seed CHOICE beats seed FITNESS. Seed the
skeleton, not the partial solution. Doctrine update for the lab:
init champions at zero-fitness structural prefixes of the target
class; let promotion earn the slope. INFERRED next: exp007 (below)
— same skeleton-seeding on a 2-qubit Bell balance target to test
whether the trap generalizes (cheap control).

## exp007 — Bell-balance skeleton-seed control at n=2 (VERIFIED)

the exp006 INFERRED control, run: 2-qubit Bell balance,
targets ("01","10") (the psi+ pair), mode="balance", same named
seeds + jitter-dropped policy, success = held-out balance >= 0.45.
Birth balances measured on train seed 101: the WRONG-BELL phi+
skeleton [h(0),cx(0,1)] scores **0.0000** (maximally entangled but
its counts are 00/11 — target mismatch, not weakness; one x(0)
insert converts phi+ to psi+); the product |++> seed [h(0),h(1)]
scores **0.2246** with its slope already present — and |++> is a
fixed point of either cx, a true trap (any cx insert is a no-op;
escape needs two coordinated moves).

| lane | birth balance | champion | verify balance | first >=0.45 gen |
|---|---|---|---|---|
| unseeded random birth | — | [h(1), cx(0,1), h(0)] | 0.234 | **never (12 gens)** |
| A: phi+ skeleton (wrong bell) | 0.0000 | [x(1), h(0), cx(0,1)] | **0.482** | **gen 5** |
| B: \|++> product trap | 0.2246 | unchanged [h(0), h(1)] | 0.234 | **never (12 gens)** |

- **H1 REFUTED (VERIFIED):** the n=2 Bell-balance problem is NOT
  already easy. Unseeded champion-local search never leaves the
  product plateau (12 gens, frozen at 0.234). The exp005 stall was
  not an n=3 artifact — champion-local mutation is the bottleneck
  class on the engine's home turf too. Note the unseeded champion's
  verify (0.234) equals the trap lane's exactly: unaided search
  falls INTO the |++>-class plateau here.
- **Doctrine holds at n=2 (VERIFIED):** the zero-fitness structural
  prefix (phi+ skeleton, balance 0.0 at birth) crosses at gen 5 to a
  real psi+ producer [x(1), h(0), cx(0,1)] — phi+ with the x(1)
  flip — held-out 0.482. Zero fitness at birth, one move from
  correlation: the prescription works at both qubit counts tested.
- **Trap generalizes (VERIFIED):** the |++> mid-slope seed never
  escaped in 12 gens × 16 draws (champion byte-unchanged). Finding
  4's trap class is real at n=2 as well.
- **Meta-finding (VERIFIED):** exp001-004's home target (mode="any",
  P("01")) is a product-state lottery — every champion those rounds
  produced, parsimony-minimal [x(0)] included, is a PRODUCT state;
  none ever earned entanglement. Only the balance witness makes the
  target an entanglement gate. Under the honest witness the engine
  has NEVER solved its home problem unaided — the seeded-restart
  doctrine is not a patch for hard lanes, it is the price of honest
  targets.
- Harness guard: default lane reproduces exp001 byte-identical (pass).
- Results: `experiments/exp007.results.json` + per-lane telemetry.

**Finding 5 (RESOLVED):** the exp006 doctrine is engine-general,
not n=3-specific: seed zero-fitness structural prefixes of the
target class; never mid-slope partial solutions; unaided
champion-local search plateaus at product-symmetry balance on any
entanglement-gated target tested (n=2 and n=3).

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

## exp008 — n=4 GHZ balance: doctrine holds, trap class partially REFUTED (VERIFIED)

First experiment the new TICK-witness cell unblocked (stepper.py made
emit O(gates) — n=4+ was the named blocker). Scale test of the
exp005-007 doctrine on the n=4 GHZ balance target {|0000>,|1111>},
mode="balance" (still an entanglement gate: product states score 0.0).
Same named seeds, same jitter-dropped policy, success bar verify>=0.45.

- **Unaided search frozen at n=4 too (VERIFIED):** random-birth
  control: champion train=0.000 verify=0.000, never crossed 12 gens.
  The never-solves-entanglement-unaided meta-finding (Finding 5)
  generalizes across scale.
- **Skeleton-seed doctrine holds at n=4 (VERIFIED):** zero-fitness
  GHZ3 structural prefix [h(0),cx(0,1),cx(1,2)] crosses at gen 5,
  held-out verify 0.482. Champion found a NON-canonical route:
  [h(0),cx(0,1),crx(1.0,1,3),cx(1,2)] — a partial-rotation entangler
  rather than textbook GHZ4 — the seed supplied the correlation
  neighborhood, search supplied the exact gate.
- **Finding-4 trap PARTIALLY REFUTED at n=4 (VERIFIED, honest):** the
  |++> fixed-point trap that froze 12 gens at n=2 (exp007) ESCAPES at
  n=4: |++++> birth balance 0.0566 crossed at gen 8 (champion
  [h(0),cx(0,1),cx(1,2),cx(0,3)] verify 0.482 — a genuinely
  entangled champion, the balance witness guarantees it). The trap
  slows (gen 8 vs skeleton's gen 5) but does not freeze — the trap
  strength is dimension-dependent, not a universal engine law.
- Doctrine update: seed zero-fitness STRUCTURAL prefixes still the
  fastest lane at every n tested (n=2,3,4); the product-trap caveat
  from exp006/007 is downgraded from 'never escapes' to 'slows
  escape' at n>=4.
- Results: `experiments/exp008.results.json` + per-lane telemetry.

## exp009 — budget>6 length control at n=4: ceiling NOT binding (VERIFIED)

Isolation test for the one structural variable every frozen-unaided
verdict (exp005-008) was recorded under: the 6-gate budget. If the
ceiling ever mattered, 'mutation locality is the bottleneck' would be
confounded by a short leash. Swept budget 6 -> 8 -> 12 on the one
lane that reliably crosses (seedA GHZ3 skeleton, n=4 GHZ balance,
restrict=('replace','indel'), same named seeds).

- **All three budgets byte-identical outcomes (VERIFIED):** same
  champion `[h(0),cx(0,1),crx(1.0,1,3),cx(1,2)]` (the exp008
  non-canonical route), same crossing gen 5, same held-out verify
  0.482. Identical genomes, identical curves.
- **Identical is the honest result, not a harness bug:** champion
  length never exceeded 4 (max_champion_len_seen=4 at every budget;
  a 4-gate champion's indel children top out at 5 gates < 6).
  Budget only enters the move choice at len>=budget, which never
  occurs — a budget sweep can only be a no-op on this lane, and it
  was. Anti-laundering rationale recorded in the exp docstring.
- **Doctrine consequence:** the exp005-008 'frozen unaided' verdicts
  stand as engine laws, not leash artifacts (the unseeded cloud
  already had room to reach 6; a longer leash would not unfreeze
  it). Finding 5/meta gains its first boundary condition: length
  control is NOT the constraint class on entanglement-gated targets
  at n<=4; champion-local mutation locality is.
- Results: `experiments/exp009.results.json` + per-budget telemetry.

## exp010 — pop scaling on the frozen unseeded n=3 lane: pop-invariant FREEZE (VERIFIED)

Finding 3 candidate (b) — 'pop 64 for the n=3 lane' — was ranked but
never run. This experiment runs it: the exact exp005 unaided lane
(no seed, targets ("000","111"), mode="balance", jitter-dropped
replace/indel cloud, same named seeds root7/train101/verify202/
shots512) swept pop 16 -> 32 -> 64, 12 gens each.

- **Frozen at every population (VERIFIED):** all three pops end with
the IDENTICAL champion `[h(1),cx(2,0),x(2)]`, train 0.000, verify
0.000, no generation ever promoted above 0.0 (telemetry: 12/12
champion rows at 0.000 per pop). Byte-identical outcomes across a
4x population range.
- **Why identical is the honest result, not a harness bug:** with a
zero-fitness champion, the cloud's children must beat 0.0 to promote.
exp005 measured the local signal density at 2.6% (52/2000 RANDOM
Genomes) — but the champion-local move distribution never samples
that region (exp005: 180 draws, zero hits). Pop scaling multiplies
DRAWS, not REACH: 4x more children of the same zero-fitness
neighborhood still never draw the winning move class. No promotion
at any pop -> champion never changes -> rng stream differences never
surface -> identical champions.
- **Boundary condition gained (VERIFIED):** the exp005/007/008
'frozen unaided' verdicts now hold across BOTH structural axes
tested — length budget (exp009: not the constraint class) and
population (exp010: not the constraint class). Draws alone do not
fix locality; the working fixes are reach-class — seeding structural
prefixes (exp006 doctrine), curriculum, or a wider mutator.
- Honest limit: telemetry logs promoted (champion) rows only; the
cloud's max child balance is not directly recorded — the verdict
rests on 'zero promotions across 3 pops x 12 gens', i.e. no child
ever beat 0.0 by any margin.
- Results: `experiments/exp010.results.json` + per-pop telemetry.

## exp011 — reach-class mutators: NON-CHAMPION-PARENT cloud crosses UNSEEDED (VERIFIED)

exp009 (budget) and exp010 (pop) both verified the unaided n=3
freeze is not a leash artifact; the remaining reach-class candidates
were a wider mutator. This experiment runs both reach-class arms on
the exact exp005 unaided lane (same seeds root7/train101/verify202/
shots512, pop 16, 12 gens, balance targets ("000","111"),
jitter-dropped replace/indel classes), plus their combination:

  - **A: two-move children** (mutate_classed applied twice per child)
    — doubles the neighborhood diameter per draw.
  - **B: non-champion-parent cloud** — new `parent_pool` run_search
    option (default False, byte-identical): each child mutated from a
    parent sampled uniformly from the candidate list (champion +
    already-generated children), one move each.
  - **C: both** — two-move children off non-champion parents.

- **Arm B CROSSED, UNSEEDED (VERIFIED):** champion
  `[swap(2,1), rx(0.5,2), cx(1,2), cx(2,1), rz(0.5,0), cx(1,0)]`,
  held-out verify balance **0.4824** at **gen 5**, frozen there
  through gen 11 (telemetry: monotonic promotions 0.107 -> 0.115 ->
  0.242 -> 0.4824, never regressing). The engine solved its home
  entanglement problem with NO seed, NO curriculum — the first
  unaided crossing on any balance-gated target.
- **Arms A and C FROZE (VERIFIED):** two-move ends at verify 0.2422
  (champion nonzero 12/12 gens — it MOVES but plateaus at the h(2)
  class); both ends at 0.2422 too. Two-move diversity alone does not
  reach the signal region; and it does not stack with parent_pool.
- **Doctrine update (VERIFIED):** the reach fix is GENEALOGY, not
  move-count. A cloud whose children sample many parents retains
  parallel evolutionary lines (arm B's gen-1 champion is a different
  lineage than the final winner); a two-move cloud around ONE parent
  still collapses onto that parent's neighborhood. 'Birth proximity
  is the whole game' (exp006) gains its boundary: proximity can be
  manufactured at runtime by parent diversity, not only at seed time.
- **Boundary condition on the old verdicts:** exp005/007/008's
  'frozen unaided' verdicts are ENGINE-DEFAULT verdicts — they hold
  for the champion-local mutator. They do not hold for
  parent_pool=True. Any future 'unaided freeze' claim must name the
  cloud genealogy.
- Harness change: `run_search(..., parent_pool=False)` added,
  default byte-identical (exp001 control guard reproduces exp001
  curve+champion in-harness, printed True before results written).
- Honest limit: single root seed; the A/C freeze vs B crossing could
  carry seed variance. A 3-seed replication of arm B is the cheap
  next run before doctrine-hardening.
- Results: `experiments/exp011.results.json` + per-arm telemetry.

## exp012 — arm B replication across root seeds: ROOT-LOTTERY (VERIFIED)

The exp011 honest limit, run before any doctrine-hardening: vary ONLY
the root seed (new 11/23/42; 7 = exp011), everything else on the
named exp005 lane. Per root, TWO arms: the unaided baseline
(parent_pool=False — the freeze control) and arm B (parent_pool=True).

| root | unaided verify | poolB verify | poolB crossed (>=0.45) |
|---|---|---|---|
| 7 (exp011) | 0.0000 | 0.4824 | **gen 5** |
| 11 | 0.0000 | 0.2031 | never |
| 23 | 0.0000 | 0.0000 | never |
| 42 | 0.0000 | 0.0000 | never |

- **Unaided freeze REPLICATES (VERIFIED):** 3/3 new roots frozen at
  0.0000, zero signal sampled. The exp005 freeze verdict is root-robust.
- **Arm B does NOT replicate (VERIFIED):** 0/3 new roots crossed. The
  one unaided crossing in the whole lab (exp011 root 7) is a
  root-LOTTERY, not a reach law. 'Genealogy fixes the freeze' is
  REFUTED as doctrine; it fixes one genealogy in four.
- Root 11 poolB reached 0.2031 — it DID sample the signal region but
  stalled on the partial-plateau (Finding 4 class: min-witness rewards
  half-built correlation, single winning move too rare). Reach without
  crossing = the trap, seen from the other side.
- Harness guard: exp001 default lane reproduces in-harness (printed
  True before results written).

**Doctrine update (VERIFIED):** seeding/curriculum stays the ONLY
replicated crossing path (exp006/007/008 across n=2/3/4). Any future
'unaided crossing' claim in this lab must carry multi-root replication
by design — single-root crossings are lottery tickets until 2+ roots
agree. Results: `experiments/exp012.results.json` + per-arm telemetry.

## exp013 — curriculum (2-q Bell before n=3): CROSSES but ROOT-LOTTERY again (VERIFIED)

The last unreplicated crossing-class idea, run multi-root at birth per
exp012 doctrine. Design pinned pre-run: phase 1 = 2-qubit Bell balance
curriculum (targets ("01","10"), exp007 prescription seed
[["h",0],["cx",0,1]]); phase 2 = the EARNED champion transplanted
op-for-op onto qubits {0,1} of the n=3 GHZ balance lane (exp005
exact lane, targets ("000","111"), jitter-dropped, pop 16, 12 gens),
vs the unaided freeze control. Transplant rule pinned: indices
unchanged, qubit 2 enters as |0> — the transplant births psi+|0>,
balance 0.0, zero-fitness structural prefix earned by solving the
smaller problem.

| root | phase-1 Bell | curriculum n=3 | unaided n=3 |
|---|---|---|---|
| 7 | crossed 0.4824 | 0.2480 plateau | 0.0000 frozen |
| 11 | crossed 0.4824 | 0.2422 plateau | 0.0000 frozen |
| 23 | crossed 0.4824 | 0.2422 plateau | 0.0000 frozen |
| 42 | crossed 0.4824 | **crossed 0.4824, gen 1** | 0.0000 frozen |

- **Phase 1 REPLICATES (VERIFIED):** the Bell curriculum itself crosses
  4/4 roots (3/4 the identical psi+ champion [x(1),h(0),cx(0,1)],
  root 42 a different rx route — curriculum learning at n=2 is
  root-robust).
- **Curriculum transplant = ROOT-LOTTERY (VERIFIED):** 1/4 roots
  crossed (r42, at gen 1 — the fastest crossing in the lab; one move
  from the transplant inserts cx(0,2) and lands 0.4824). 0/3 other
  roots. Per exp012 doctrine, 1/4 is a lottery ticket, not a law.
- **The trap mechanism is visible in the telemetry:** the transplant
  births psi+|0> — a PARTIAL entangler against the GHZ target, i.e.
  exactly the Finding-4 trap manufactured at birth. 3/4 lanes stall at
  the 0.2422 plateau (r11/r23 champions end as |+>-style product
  escapes, not correlations); only r42's first-cloud draw found the
  coordinated second entangling move. exp006's doctrine — 'seed the
  SKELETON, never the partial solution' — predicts this exactly:
  an earned 2-qubit solution IS a partial solution at n=3.
- **Unaided freeze replicates 4/4** (0.0000 every root) — exp005/012
  verdicts stand, again.
- **Doctrine update (VERIFIED):** curriculum-as-transplant REFUTED as
  a replicated crossing path; the only replicated path remains
  HAND-BUILT zero-fitness skeletons (exp006/007/008). The distinction
  is now sharp: seeds must carry NO slope on the target (skeleton),
  not earned slope from a smaller problem (transplant) — earned slope
  at the wrong scale is the trap, not the ladder.
- Harness guard: exp001 default lane reproduces in-harness at every
  root before results are written (the guard re-runs the canonical
  root-7 exp001 lane, matching exp005-012; a first-draft per-root
  guard variant was caught and fixed pre-results).
- Results: `experiments/exp013.results.json` + per-root telemetry.

## exp014 — skeleton-seed multi-root replication: SKELETON IS A RATE (VERIFIED)

The hole in the doctrine chain, named and closed: exp012/013 both
conclude "hand-built zero-fitness skeletons are the ONLY replicated
crossing path" — but every skeleton crossing ever measured ran on
ROOT 7 ONLY (exp006 n=3, exp007 n=2, exp008 n=4). "Replicated"
was replication across TARGETS, never across ROOTS. This experiment
runs the skeleton on 8 fresh roots (3/5/13/17/19/29/31/37) on the
exp005 exact unaided n=3 balance lane, S arm = exp006 prescription
seed [h(0),cx(0,1)] champion-local; P arm = parent_pool unaided
(extends the exp012 rate sample). Verdicts pre-registered: >=7/8
SKELETON ROOT-ROBUST; 3-6/8 SKELETON IS A RATE; <=2/8 ROOT-LOTTERY
TOO.

| root | S: skeleton | P: parent_pool |
|---|---|---|
| 3  | **cross gen 6** (0.4824) | frozen 0.0000 |
| 5  | trapped 0.2422 | **cross gen 6** (0.4824) |
| 13 | **cross gen 0** (0.4824) | **cross gen 11** (0.4824) |
| 17 | **cross gen 3** (0.4824) | trapped 0.2422 |
| 19 | **cross gen 0** (0.4824) | **cross gen 9** (0.4824) |
| 29 | trapped 0.2422 | stalled 0.1055 |
| 31 | trapped 0.2422 | stalled 0.2031 |
| 37 | trapped 0.2422 | frozen 0.0000 |

- **VERDICT: SKELETON IS A RATE — 4/8 fresh roots (5/9 incl exp006
  root 7).** The "only replicated path" was itself a root-7-flavored
  lottery. No crossing mechanism in this engine is root-invariant.
- **The freeze IS the invariant (VERIFIED):** champion-local unaided
  search has now crossed 0/11 independent configs (exp005 r7; exp010
  pops 16/32/64; exp012 r11/23/42; exp013 r7/11/23/42) while every
  seeded/reach mechanism crosses at a measurable rate. Doctrine
  rewrite, pinned: **the freeze is the law; the crossing is always a
  rate.**
- **Crossing-rate table (n=3 GHZ balance, verify >= 0.45):**
  skeleton 5/9 (56%, cross gens 0-6, minimal 3-gate champions) >
  parent_pool 4/12 (33%, cross gens 5-11, 4-6-gate champions) >
  curriculum transplant 1/4 (25%, exp013) >> unaided 0/11 (0%).
  Skeleton keeps the top rate AND the fastest crossings — the
  practical prescription survives, demoted from law to best-measured
  mechanism.
- **Root difficulty classes exist (VERIFIED):** r13/r19 crossed under
  BOTH mechanisms (easy roots); r3/r17 skeleton-only, r5 pool-only
  (mechanism-specific — matching is luck, not fit); r29/r31/r37
  resisted BOTH (hard roots — r31 pool sampled signal 0.2031 and
  stalled, Finding-4 class). A root's difficulty is a property of the
  root x mechanism pair, not of the root alone.
- Every crossed champion held out at 0.4824 — the same near-balanced
  GHZ class, nine independent ways.
- Harness guard: exp001 default lane reproduces byte-identical
  in-harness before results written. Design + verdicts pinned pre-run
  in the runner docstring.
- Results: `experiments/exp014.results.json` + per-arm per-root
  telemetry (17 jsonl files incl control).

**Doctrine update (VERIFIED):** any crossing claim in this lab must
carry its measured rate over named roots ("N/M roots, gens a-b"),
never bare "crosses". Mechanism ranking by rate is real and useful;
mechanism-as-law is dead. Hard roots (r29/31/37 class) are the next
scientific target: what makes a root resist both mechanisms?

## Next iterations (queued to snowball-queue)

- exp004 DONE: jitter-drop crosses at gen 2 vs control gen 4.
- exp005 DONE: balance witness gates entanglement; unaided search
  frozen at n=3 (Finding 3).
- exp006 DONE: GHZ-prefix seeded restart confirmed; partial entangler
  = trap (Finding 4).
- exp007 DONE: doctrine engine-general at n=2; |++> trap confirmed;
  unaided search plateaus on any entanglement-gated target
  (Finding 5, meta: exp001-004 champions were all product states).
- exp010 DONE: pop 16/32/64 all frozen byte-identical — pop scaling
  multiplies draws, not reach (Finding 3 candidate (b) RESOLVED).
- exp011 DONE: reach-class mutators — non-champion-parent cloud
  crossed UNSEEDED (root 7 only); two-move arms froze; reach fix is
  GENEALOGY not move-count.
- exp012 DONE: arm B 3-seed replication = ROOT-LOTTERY (0/3 new roots
  crossed; unaided freeze 3/3 replicated). Multi-root replication is
  now lab doctrine for any 'unaided crossing' claim.
- exp013 DONE: curriculum (Bell->n=3 transplant) = ROOT-LOTTERY
  (1/4; r42 gen 1, others trapped at 0.2422 partial plateau);
  phase-1 curriculum itself replicates 4/4; skeleton-not-transplant
  doctrine sharpened.
- exp014 DONE: skeleton multi-root replication = SKELETON IS A RATE
  (4/8 fresh roots, 5/9 incl root 7). THE FREEZE IS THE LAW; THE
  CROSSING IS ALWAYS A RATE. Rate table: skeleton 5/9 > pool 4/12 >
  transplant 1/4 >> unaided 0/11. Root classes: easy (13/19),
  mechanism-specific (3/5/17), hard (29/31/37). Next target: what
  makes hard roots resist both mechanisms?
- Seal exp003-exp014 as in-repo experiment receipts
  (`receipts/expNNN-*.json`) once a MicroMoth-quilt PR lane reopens —
  exp002 shipped as PR #7 (commit 6746e7c, Casey-gated); same shape
  as the exp001 receipt PR (#5).
- exp015 candidate: HARD-ROOT AUTOPSY — r29/31/37 resisted both
  mechanisms. Birth-cloud telemetry deep-read: did the winning move
  class ever get drawn? (If never drawn = reach problem at that root;
  if drawn-but-not-promoted = fitness/witness problem.) Cheap:
  instrument one run per hard root with full-cloud (not just champion)
  telemetry, or run pool+two_move combined arm on hard roots only.
- PROOF statevector witness cell at a TICK DONE: qcell/stepper.py
  walks the statevector incrementally (one O(gates) pass, bit-identical
  to per-gate prefix simulation — pinned over 25 random circuits);
  TICK rows now carry their own state_sha256 witness, so the clock row
  itself is the re-executable proof cell, not just a counter.  Emit
  dropped from O(gates^2) prefix sims to exactly ONE simulation (WORLD
  sampling) — the n=4+ blocker named here is gone.  Replay verifies
  the TICK witness (tamper caught by seq) while legacy ledgers without
  it stay valid.  exp001 champion ledger re-emitted: every hash
  byte-identical, TICK rows gained witnesses only; replay OK.
  7/7 pins green (tests/test_tick_witness.py).
- exp003+ receipts: seal exp003-exp014 as in-repo experiment
  receipts (`receipts/expNNN-*.json`) — exp002 shipped as PR #7
  (commit 6746e7c, Casey-gated); same shape as the exp001 receipt PR
  (#5). Old 'exp002-exp009' bullet superseded.
