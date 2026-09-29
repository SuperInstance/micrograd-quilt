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
- exp015 MAP-Elites illumination (ELITISM-ARTIFACT partial, VERIFIED):
  QD archives (A1: verify-bucket x length, 36 cells; A2: balance x
  entropy, 30 cells) over the exact exp005 unaided lane, 3 configs x
  roots 7/11/23.  Unaided archives DO hold verify>0 elites (max
  0.248, r23) that single-fitness champion search discarded every
  generation - the freeze hides reachable signal; but illumination
  only lifts the unaided ceiling to the Finding-4 partial-plateau
  class (0.2422/0.248); the 0.45 crossing stays skeleton-only 3/3
  (r7 transplant got 0.4355, below bar).  FREEZE verdict REFINED not
  refuted: illumination moves the ceiling 0 -> 0.248; seeding moves
  it 0.248 -> 0.4824.  Selection-regime-invariance holds for the
  crossing claim, fails for the zero-signal claim.  Transplant
  (archive-elite injection) is NOT a third crossing class - 0/3
  roots.  exp001 guard green.  Commit 7368f20, local lab repo.
- exp018 HARD-ROOT AUTOPSY (FITNESS DESERT AT THE BIRTH CLOUD):
  instrumented full-cloud telemetry on the exact exp005 unaided lane,
  hard roots 29/31/37 + control 13 (exp012 ROOT-LOTTERY difference
  read), winning-move class pre-registered from exp016's actual hard-
  root champions (2q gate touching wire 2; all three winners carry
  one).  Reach NOT the binding constraint: win2 drawn 13-17x per hard
  root vs 14x on control.  But all 540 hard-root child-sims sat at
  train=0.0 AND verify=0.0 for all 12 gens - including wire-2-
  entangled birth champions (r37 opens cx(2,0)+swap(2,1)+swap(1,0),
  a structural superset of exp016's r37 winner, and still pays zero
  at both seeds).  Control r13's cloud shows signal from gen 0
  (train 0.1289 -> 0.2559, verify 0.2422 plateau) at identical draw
  counts - the desert is ROOT-SPECIFIC, not lane-global.  Read: the
  hard-class freeze is UPSTREAM of selection (fitness desert, nothing
  to witness); exp016's archive-hybrid hard-root crossing at the same
  seeds unlocked FITNESS ASSEMBLY via multi-parent mixing, matching
  exp015 ELITISM-ARTIFACT.  Harness quirk surfaced by the FAIL-first
  equivalence pin (witness_rng class): search.mutate's indel-insert
  branch calls random_gate(rng) with NO n_qubits - the insert pool is
  hard-wired 2-wire even in n=3 lanes, so insert can NEVER introduce
  wire 2; every observed win2 draw flowed through the ~30% replace
  class.  mutate_telem pinned 800/800 states (genome + rng-state
  equality); exp001 guard green.
- exp022 CROSSING-STREAM CENSUS (TRAIN-VISIBLE, TIE-BREAK-INVARIANT):
  passive census (exp021 Q2 semantics) on the exp021 crossing band
  k3/k5/k6 (seeds 31003/31005/31006) + contrasts k4 (0.418) / k7
  (0.0).  All five replicate exp021 champion values verbatim
  (replicate pins pass) with exp001 guard byte-identical (census
  active).  On every crossing stream the >=0.45 cell appeared with
  train 0.498 / verify 0.482 at a single DESERT-BREAK gen (k3 g0,
  k5 g3, k6 g8) as gen-max: n_tied=1 on k3/k5 (unique max — any tie
  rule picks it), n_tied=2 on k6 (two identical 0.4824 twins).
  Pick window 0 gens everywhere; later bar_gens are the promoted
  champion in the cloud.  READ: 31's resistance is a per-stream
  DESERT-BREAK RATE (5/8 never birth a train-visible high cell;
  k4 near-miss 0.418 under BAR; k7 dead) — NOT a tie-band sampling
  lottery.  exp020 tie-sampling governs 29/37, not 31; exp021
  RATE-NOT-WALL refines to desert-break odds; exp016 archive
  crossing on canonical 31 (desert 12/12 gens) keeps
  RETENTION-ASSEMBLY as the only no-break mechanism.  Local lab
  repo only (push credentials still wiped).
- exp024 BLIND VALIDATION (NOT_SEPARABLE_AT_N8 — exp023 CONFIRMED):
  census of the 3 remaining exp021 Q1 salts k0/k1/k2 (seeds
  31000/31001/31002, never censused before) + frozen-predictor
  test over the enlarged 8-stream panel.  Replicate pins: all
  three finish @0.2422, not crossed — exp021 q1 values verbatim;
  exp001 guard byte-identical with census ACTIVE.  Census facts:
  on all 3 new streams the cloud NEVER holds a >=0.45 cell
  (max_cloud = 0.2422 = the champion itself, zero bar_gens) —
  exp021's DESERT-EXTENDS-TO-CLOUD holds on the full non-crosser
  salt panel (k0/k1/k2/k4/k7 all cloud-barren; k4's 0.418 was
  champion-side, not cloud birth).  Blind predictor reads at n=8:
  C1 win2presence now universal 8/8 at birth AND 6/6 in W2 — the
  reach constraint is dead at panel level, exp018 confirmed on
  every salted stream; C2 trips still only k3 (its break gen IS
  g0); C3 trips 3 crossers + k0/k1/k7 non-crossers (no
  separation); C4 trips nobody in W1, anti-correlates in W2
  (k4 + k6).  No frozen predictor separates 3 crossers from 5
  non-crossers in either window.  VERDICT: exp023's pilot read
  CONFIRMED blind — the desert break is a per-gen BIRTH event
  invisible pre-break; prediction must target birth-cloud
  per-draw odds, not trajectories.  Named next: exp025
  birth-cloud per-draw odds model.  results: experiments/
  exp024.results.json; census: experiments/exp024_blind_validation.py
- exp023 DESERT-BREAK PREDICTOR SCREEN (NOT SEPARABLE AT AVAILABLE N):
  pure analysis of the sealed exp022 telemetry (no re-run, no rng, no
  new sims) answering exp022's named question — what distinguishes
  break streams PRE-break?  Four candidate predictors numbered
  pre-run from named doctrine steps (C1 win2presence/exp018,
  C2 nearbar40/exp022's k4 band, C3 tiewidth4/exp020-022 tie-band
  read, C4 activity3/desert activity), two symmetric windows
  (W1 at-birth gen 0; W2 pre-peak, k3 undefined — peak at g0).
  RESULT: zero separation in either window.  Detail reads: win2
  presence is UNIVERSAL at birth (5/5 streams — reach truly not the
  constraint, exp018 confirmed at stream level); C2 trips only k3
  (its break gen IS gen 0 — at-birth break, no pre-window exists);
  C4 ANTI-CORRELATES in W2 — the non-crossing near-miss stream k4
  was MORE active pre-peak (3+ distinct signal-born cells) than
  crosser k5 (0) — cloud activity does not predict the break, an
  active desert still freezes.  VERDICT: the desert break is a
  per-gen BIRTH event invisible pre-break; exp018 doctrine holds at
  stream level; prediction must target birth-cloud per-draw odds,
  not trajectories.  n=5/n=4 pilot class; validation lane named =
  exp024 (census the 3 remaining exp021 Q1 salts k0/k1/k2, test
  surviving predictors blind).  results: experiments/
  exp023.results.json; screen: experiments/exp023_predictor_screen.py
- exp026 FIRST-BIRTH TIMING + NON-CROSSER HAZARD CEILING
  (HOMOGENEOUS-AT-PILOT-N / CALIBRATED / COMPATIBLE): pure analysis
  of the sealed 8-stream census corpus (exp022 k3-k7 + exp024 k0-k2),
  independent re-derivation from raw telemetry cross-checked against
  sealed exp025 values (74 desert gens / 1037 desert draws / 4 hits —
  match, else abort).  TIMING TABLE sealed as canonical reference:
  k3 breaks AT BIRTH (g0, 16 desert draws in, 1 hit); k5 at g3 (cum
  54 draws); k6 at g8 (cum 121 draws, 2 hits that gen); the five
  non-crossers (k0/k1/k2/k4/k7) run all 12 gens cloud-barren — 846
  desert draws, 0 hits.  Q2 exact homogeneity test under ONE shared
  per-draw hazard (conditional on 4 hits / 1037 draws; per-stream
  exact Binomial(4, n_s/1037) tails, Bonferroni x8): every adjusted
  p >= 0.48 -> HOMOGENEOUS-AT-PILOT-N.  k3's at-birth break carries
  the smallest tail (raw 0.0603) — the least-expected single cell
  under the shared hazard — but is nowhere near significant at n=4.
  Read honestly: 'not distinguishable at this n', never 'rates
  equal'.  Q3 timing calibration under the sealed pooled p
  (1-in-259, never re-estimated): per-stream q_g = 1-(1-p)^D_g
  gives expected birth-stream count 3.02 with exact Poisson-
  binomial 95% prediction interval [1, 5]; observed = 3 ->
  CALIBRATED.  ONE shared hazard predicts ~3 of 8 streams break;
  exactly 3 did.  Per-crosser timing surprises under the shared
  hazard (reported, not verdicted): F_k3(0)=0.0600 (a 1-in-16.7
  event), F_k5(3)=0.1884, F_k6(8)=0.3735 — the early breaks are
  mildly lucky, the late break unremarkable; nothing timing-shaped
  is left unexplained by censoring.  Q4 non-crosser ceiling: 0 hits
  in 846 censored-stream desert draws -> exact 95% upper bound
  0.004351 per draw; COMPATIBLE with the sealed pooled point
  estimate 0.003857 (verdict condition pre-registered on the point
  estimate).  Post-registered observation, labeled as such: the UB
  sits BELOW the pooled CI's upper end (0.00988) — the frozen
  majority rules out the top of the pooled interval, so the pooled
  1-in-259 is best read as 'typical-or-lower for non-crossers,
  carried at the point by crosser-side exposure'.  VERDICT: the
  exp021 RATE-NOT-WALL lottery refines at pilot-n to ONE shared
  desert hazard + heavy censoring; the per-stream 'some hot, some
  frozen' read is NOT distinguishable from shared-hazard luck at
  4 events, and the frozen five are bounded, not rated.  exp016's
  RETENTION-ASSEMBLY on canonical 31 (never births, crosses anyway)
  remains the only no-break mechanism.  Named next: exp027 birth
  ORDER statistics under the shared hazard (joint waiting-time
  distribution of 3 breaks + 5 censored streams — does the OBSERVED
  order k3<=k5<=k6 carry more evidence than the marginals used
  here?) or prospector E3/E4.  results: experiments/exp026.results.json;
  script: experiments/exp026_first_birth_timing.py
- exp027 BIRTH-ORDER + BREAKER-SET STATISTICS (ORDER-AS-EXPECTED /
  SET-SURPRISING / PROCEDURE-DISAGREEMENT-SEALED): pure exact
  analysis of the sealed 8-stream census corpus, no rng, no re-run.
  Q1 ORDER: asked two ways.  Unconditional P(observed order
  k3<k5<k6) = 1.74e-3 SUBSUMES the improbable WHO; the real order
  question is conditional — given the three crossers break at all,
  P(k3 first, k5 second, k6 third) = 0.4126 vs 1/6 order-ignorant:
  the order is the shared hazard's ORDINARY outcome.  ORDER CARRIES
  NOTHING.  Q2 the full configuration sits at percentile 0.357 of
  all 336 ordered breaker triples — below median, not tail (a
  joint WHO+order read).  Q3 SET (the shock): the three breakers
  carry the THREE LOWEST total desert exposures (16/54/121 draws);
  all five non-crossers sit at 163-175.  Under the shared hazard
  the heavy five each break w.p. ~0.47-0.49 (P(none break) =
  0.038) while the observed breakers break w.p. 0.06/0.19/0.37;
  P(break set = exactly the three light streams) = 7.97e-5, ~200x
  below the flat 1/56.  SET CARRIES EVERYTHING.  Q4 CONSISTENCY
  GUARD: exact conditional homogeneity deviance (Multinomial(4; w),
  all 330 compositions enumerated; chi2_7 approximation INVALID at
  expected counts 0.06-1.7) gives G^2 = 14.53, exact p = 0.0053 —
  REJECTING the shared hazard — while exp026's one-stream-at-a-time
  Bonferroni tails (same null, same conditioning) were all >= 0.48.
  TWO EXACT PROCEDURES DISAGREE at pilot-n; the disagreement is
  sealed for Casey, not adjudicated here.  Read: the JOINT set
  statistic puts 'one shared hazard + censoring' in the tail;
  'some salts hot, some frozen' is back on the table as a
  procedure-dependent, n=4 finding — a disagreement to
  adjudicate, never a refutation of exp026.  Honest limits: 4
  events / 8 streams; exposure design-fixed (Q3 descriptive); Q2
  percentile compares exhaustive discrete configurations, not a
  nested alternative.  Named next: Casey adjudicates deviance-vs-
  Bonferroni at this n (or pre-registers the tiebreaker on a
  larger census); qcells lane otherwise awaits credential restore.
  results: experiments/exp027.results.json;
  script: experiments/exp027_birth_order_stats.py
- exp028 PROCEDURE-DISAGREEMENT ADJUDICATION PRE-REGISTRATION
  (OBSERVED-DIRECTION-SURPRISING / RULE-SEALED / POWER-LABELED):
  pure exact analysis, no rng, no new stream runs.  Q1 exact
  disagreement base rate under the shared hazard itself: enumerate
  all 330 Multinomial(4; w) compositions, per-composition exact
  deviance p AND exp026's own procedure (Marginal-Binomial(4, w_s)
  tails, Bonferroni x8 — reproduced live, min tail >= 0.48 guard).
  P(deviance rejects) = 0.0493 (size-calibrated at alpha);
  P(Bonferroni rejects) = 0.0113 (conservative, as constructed);
  P(disagree, either direction) = 0.038 — and the mass is ENTIRELY
  the observed direction (deviance-reject + Bonferroni-retain =
  0.038; reverse = 0.000: at pilot-n the conservative marginals can
  never reject alone).  Verdict per pre-registered threshold:
  OBSERVED-DIRECTION-SURPRISING (0.038 < 0.05) — the exp027 split is
  not the shared hazard's ordinary mood, so it retains genuine
  adjudication urgency, with the honest caveat that 0.038 is
  rare-ish, not vanishing, at 4 events.  Q2 THE RULE, sealed in
  prose BEFORE any power number: enlarged corpus = pilot + b*
  pre-committed salt blocks of 8 census streams (exp024 protocol,
  31000-series seeds, ONE batch, no peeking); shared hazard REFUTED
  iff pooled exact deviance p < 0.05; Bonferroni diagnostic-only;
  reverse sensitivity rule (refute only if BOTH reject) sealed
  alongside so the choice cannot be post-hoc.  Q3 PRE-COMMITTED
  SIZE, LABELED approximation (Patnaik + Wilson-Hilferty, never the
  binding rule): under the design-fixed two-class alternative (3 hot
  at 10x pooled / 5 frozen at 0.1x), b* = 1 block = 8 census streams
  (~1354 draws) already carries approx power 0.9988 — the
  adjudication corpus is ONE pulse of runs away whenever Casey
  commits the batch.  results: experiments/exp028.results.json;
  script: experiments/exp028_adjudication_prereg.py
- exp029 ADJUDICATION CENSUS BLOCK EXECUTED (SHARED-HAZARD NULL
  REFUTED — BACKFILLED from sealed receipt 988428d, appended here
  at exp030 time because the pulse receipt reached the snowball
  queue but not this log): exp028-pre-registered b*=1 block run
  verbatim — salts k8–k15, seeds 31008–31015, exp021 Q1 tiesample
  semantics POP16 GENS12 BUDGET6, ONE committed batch, no peeking;
  determinism verified by in-memory re-run before any statistic.
  Block facts: 972 desert draws / 6 hits; births k8 g4, k9 g7,
  k11 g6 (2 hits), k13 g0 (16 draws — the k3 signature),
  k15 g11; non-crossers k10/k12/k14.  Pooled corpus: 16 streams /
  2009 draws / 10 hits.  SEALED RULE DECISION: pooled exact
  conditional deviance p = 0.003256 < 0.05 → shared-hazard null
  REFUTED; reverse sensitivity rule (refute only if both reject)
  RETAINED — exp027's Bonferroni diagnostic-only lane stays silent
  as constructed.  Guards: pilot re-derivation vs sealed 74/1037/4
  byte-match; exp001 instrument reproduced byte-identical; suite
  7/7 green outside this file.  Local only (push creds wiped).
  results: experiments/exp029.results.json + exp029.telemetry.k8..k15;
  script: experiments/exp029_adjudication_census.py
- exp030 BIRTH-STRUCTURE DECOMPOSITION (MULTIPLICITY-CONSISTENT /
  COUNT-CALIBRATED / TAUTOLOGY-GUARDED): pure exact analysis of the
  pooled 16-stream corpus, no rng, no new stream runs.  DEFINITIONS
  GUARD sealed first: birth = first desert gen with >=1 newborn
  >= BAR(0.45) and the desert regime ENDS at birth, so
  hits>=1 iff birth — any hit-rate test conditioned on crossing
  status is DEFINITIONAL and was BANNED as evidence before any
  rule was written.  RULE-1 multiplicity dispersion: the 8 birth
  events (k3,k5,k6,k8,k9,k11,k13,k15; birth gens carry only
  12–16 newborns by POP16 design; hits 1,1,2,1,1,2,1,1) allocated
  by exact weighted-composition deviance — p = 0.9978 CONSISTENT:
  within birth clouds the shared per-draw hazard predicts the
  multiplicity structure exactly, the two doubles (k6, k11) are
  its ordinary mood.  RULE-2 birth count vs counterfactual
  exposure: p_s = 1-(1-w)^E_s with w = 10/2009 and E_s = FULL
  12-gen newborn count (formula re-verified against exp027's
  sealed table to 1e-9 before use; guard caught this experimenter
  using BAR=0.72 — sealed constant is 0.45 — BEFORE any statistic
  touched the corpus, run aborted and re-run clean).  Every stream
  carries p_s ~ 0.54–0.59; E[births] = 9.08; observed 8;
  exact Poisson-binomial upper tail P(X >= 8) = 0.7889 CALIBRATED.
  RULE-3 birth timing: labeled EXPLORATORY histogram only.
  SYNTHESIS with exp026/027/029: the shared per-draw hazard now
  survives every MARGINAL question the lineage has asked — how many
  births (calibrated), multiplicity within births (consistent) —
  and fails exactly one JOINT question: which streams, given their
  observed exposures (exp027 set p=7.97e-5; exp029 pooled deviance
  p=0.003256).  The two-regime shape (exp025 title claim) sharpens
  to: stream-level Bernoulli(~0.5 over full exposure) birth events,
  allocation across streams NOT the exposure-weighted lottery the
  shared hazard books.  Named next (pre-registration required):
  exp031 non-crosser upper-bound vs pooled w at census-n — 1360
  barren draws, 0 hits; exact UB95 = 0.0022 < w = 0.00498, which
  would pit exp026's frozen-compatible verdict against the enlarged
  corpus; and an exposure-EXOGENOUS allocation test (weights from
  salt identities / draw-order, not post-birth-truncated totals) to
  close the endogeneity gap in both exp027 Q3 and exp029.  results:
  experiments/exp030.results.json (re-run digest 45467dd1,
  byte-identical consecutive runs 1988279b);
  script: experiments/exp030_birth_structure.py
- exp031a NON-CROSSER CEILING VS POOLED HAZARD AT CENSUS-N
  (INCOMPATIBLE / CONVENTION-ROBUST): sealed exp030 candidate-a executed
  verbatim against the pooled 16-stream corpus. Guards green: pilot
  74/1037/4, census 972/6, non-crosser panel 8 streams / 1360 desert draws /
  0 hits. RULE-1 point-null diagnostic: under shared per-draw hazard
  w = 10/2009 = 0.0049776, X=0 in n0=1360 has exact probability
  p0 = 0.0011289794 < 0.05 → INCOMPATIBLE. RULE-2 confidence-bound read:
  the candidate's one-sided Clopper-Pearson UB95 = 0.0022003201, and the
  exp026-definition two-sided UB95 = 0.0027087361; BOTH sit below the pooled
  point w = 0.0049776. Expected non-crosser hits at pooled w would be 6.77;
  observed 0. Read: the frozen/barren majority is no longer merely
  compatible with a low shared hazard at census-n; the pooled point itself
  is above the non-crosser 95% ceiling. This is the ceiling face of the same
  allocation shock exp029 measured by pooled deviance (p=0.003256); it does
  not re-adjudicate that verdict. Named next (pre-registration required):
  exp031b exposure-EXOGENOUS allocation test — weights from salt identity /
  draw-order, not post-birth-truncated totals — to close the endogeneity gap
  in exp027 Q3 + exp029. Pure exact arithmetic, no rng; re-run digest
  2238e686959aa81846759a46633e11d4; suite 7/7 green outside this file.
  results: experiments/exp031.results.json;
  script: experiments/exp031_noncrosser_ceiling.py
