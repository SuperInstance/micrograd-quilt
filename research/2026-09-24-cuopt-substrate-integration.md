# LP Router ↔ quilt-optimization substrate — integration design
**Casey directive 14:22 (cuOpt where it counts) + 16:10 (I want it all) · kimi1 2026-09-24**

## Substrate surface (verified via gh)

`SuperInstance/quilt-optimization` — NVIDIA cuOpt as Quilt substrate, Apache-2.0, 21/21 tests, ~340 LOC.

```
src/quilt_optimization/
  substrate.py            # CellReceipt {witness_id, prev_witness_id, polarity ∈ {ACCEPT,DRIFT,REFUSE}, payload}
  routing.py              # RoutingSubstrate(prev_witness_id=…), RoutingProblem(name, n_locations, n_vehicles, n_orders, cost_matrix, order_locations, vehicle_starts/ends, capacities, demands)
  linear_programming.py   # LPSubstrate, LPProblem(variables=[LPVariable], constraints=[LPConstraint(terms=[LinearTerm], rhs, sense)], objective=LPObjective(sense=MAXIMIZE|MINIMIZE))
  # backends: Mock*Backend (deterministic offline) / CuOpt*Backend (import cuopt, GPU)
```

Family confirmation: substrate receipts chain via `prev_witness_id` — the same chain
doctrine as our fnv1a-64 ledger and laya4quilt's fnv1a-32 QuiltLedger. Three cells,
one receipt lineage.

## Seam

`router/fleet_router.py::cuopt_lp()` already emits the exact LP formulation as a
solver-agnostic dict (same dict feeds CPU and cuOpt). The substrate's LPProblem is
the same object with names. Adapter is a **translation, not a rewrite**:

| fleet_router (ours) | quilt-optimization (theirs) |
|---|---|
| `x[t,p]` binary vars, one per (task, provider) | `LPVariable(name=f"x_{t}_{p}", lb=0)` — binary via MILP flag on substrate |
| objective terms `utility − λ·cost − μ·latency − ν·context_risk` | `LPObjective(terms=[LinearTerm(f"x_{t}_{p}", coeff)], sense="MAXIMIZE")` |
| `one_provider_per_task` (Σ_p x = 1) | `LPConstraint(terms=[…], rhs=1, sense="==")` per task |
| `provider_cap` (Σ_t x ≤ cap_p) | `LPConstraint(rhs=cap_p, sense="<=")` per provider |
| `dag_precedence` (x=0 until deps assigned) | pre-solve topological filter, then LP — same as solve_cpu does today |
| `dispatch()` books TICK + REFUSED rows | **dual-book**: substrate CellReceipt ALSO booked as EFFECT row (see below) |

## Fallback chain (receipts doctrine: visible gaps, never silent)

1. **solve_cpu** — seeded greedy + 2-opt, stdlib, always available. Books formulation_sha.
2. **quilt-optimization Mock*Backend** — deterministic offline; the substrate's own test-grade path. Validates the translation on every box, no GPU.
3. **CuOpt direct** (`import cuopt`) — GPU present. Today: absent on this box → REFUSED row says so.
4. **quilt-optimization CuOpt*Backend** — same GPU path behind the witness chain; preferred over (3) once wired because the receipt chains into the org's legalese layer.

Chain selection is itself receipted: every dispatch books which solver ran, which
were unavailable and why, and the formulation hash — already true in `dispatch()`.

## Dual-book: two receipts, one truth

Our ledger stays the fleet's source of truth (single-ledger doctrine, same call
that killed laya4quilt's second ledger). The substrate receipt is **booked as
payload**, not adopted as structure:

```json
{"op": "EFFECT", "payload": {"solver": "quilt-optimization",
  "witness_id": "…", "prev_witness_id": "…", "polarity": "ACCEPT",
  "objective_value": 12.4, "solve_ms": 33.1, "formulation_sha": "…",
  "chain_family": "prev_witness_id ≡ parent_hash"}}
```

Cross-verification (jeviter doctrine): the witness chain and our fnv1a chain are
independent encodings of the same before/after — a checker can assert both verify
and disagree on nothing. That checker is a 20-line test pin worth writing.

## Build order (test-pinned)

1. `router/substrate_adapter.py` — `to_lp_problem(tasks, caps, lam, mu, nu) -> LPProblem` (pure translation, ≤80 LOC) + pins: formulation equivalence (adapter output ≡ cuopt_lp dict coefficients), topological DAG filter.
2. `Mock*Backend` round-trip pins: 3-provider dispatch solved on substrate mock equals solve_cpu assignment on the same seeded instance (they may differ — greedy ≠ LP-optimal; pin LP ≥ greedy objective value, not identity).
3. Dual-book EFFECT-row pins: witness fields present, chain verify OK, formulation_sha matches.
4. GPU-gated pins (`skipUnless`): CuOpt direct vs substrate CuOpt same objective.
5. Latency/cost fields per receipts doctrine: solve_ms booked per chain step; the CHOICE of chain step is itself in the row.

## Risks

- **MILP vs LP**: substrate supports MILP via cuOpt; our formulation is 0-1 → keep
  variables binary explicitly in translation. Mock backend must honor integrality
  or pins compare apples to oranges.
- **Objective mismatch**: solve_cpu nets utility − 0.5·risk − 0.001·latency/1000
  while cuopt_lp uses λ=1.0, μ=0.001, ν=0.5 — the adapter must consume the SAME
  (lam, mu, nu) or the formulation_sha drifts from what was solved. Pin it.
- **Chain hygiene**: never let the substrate witness chain REPLACE our parent_hash;
  two chains, one direction (ours authoritative, theirs corroborating) — jeviter
  lattice doctrine.
