# Understanding micrograd-quilt

For two readers: a **visitor** with no context, and a **practitioner** who
wants to reuse the machinery. Every claim below was either read in the code
(cited by path) or produced by a command I ran; outputs are pasted verbatim.
Where something is *not* verified here, it says so.

Note on the base branch: the brief said "from main"; this repo's default
branch is `master`, so `claude/docs-ulp` was cut from `master` @ `83c3171`.

---

## 1. One breath

micrograd-quilt is Karpathy's micrograd (untouched in `micrograd/`) plus a
`quilt/` layer that answers "did this float computation drift, and can I
prove what it did?" — by running backward twice in different orders (the
**comb**), recording every step on a hash-chained **tape** you can replay
bit-for-bit, and spot-checking a random sample of nodes against exact
rational arithmetic (the **auditor**).

## 2. Why it exists

Floating-point addition is not associative. Reorder a sum, rebuild a graph,
or change the order gradients accumulate, and the last bits can move. Most
of the time that is harmless; occasionally (cancellation of large terms) it
is not. Plain autograd gives you one answer and no way to tell which case
you are in.

The repo's README frames three questions (`README.md`, "The three
questions"): where float backprop breaks (auditor), how to prove a gradient
(tape), how a graph evolves (genotype, `quilt/breeder.py`, out of scope
here). The design law and its amendment log are in `DESIGN.md`. The design
was revised after a hostile review ("critic ref M3-01"): the claims are
deliberately modest — *measurement and regression guard, not an equivalence
theorem*.

Concrete use: before you trust that a re-ordered or rewritten computation
still computes the same thing, you want a cheap, mechanical check that
either passes or points at the node that moved.

## 3. The mental model — detecting that a rebuilt/reordered computation still computes the same thing, to ulp precision

This is the part to read slowly. There are **three independent instruments**,
each answering a different question. Confusing them is the main way to
misuse the repo.

### 3a. The unit: ulps and τ

`quilt/engine.py` defines `U = 2**-52 = 2.22e-16`, float64 unit roundoff.
"To ulp precision" means differences measured in multiples of that scale.
`quilt/comb.py` sets the tolerance `TAU = 1e4 * U = 2.22e-12` (rationale in
the file header: accumulated rounding over ≤1e4 steps is bounded ~D·U, per
Kahan 1965) and `LOST = 100 * TAU`. Below τ a node is "intact" (✓), between
τ and LOST "wobbling" (◐), above "lost" (✗). Note the tolerance is 10⁴ ulps,
generous on purpose so healthy graphs never false-alarm. If you need a
tighter claim, pass `tau=` to `render_comb`, or read the raw `disag` dict.

### 3b. Instrument 1 — the comb: *does the answer depend on the order?*

`quilt/comb.py:disagreements(root)` runs `backward()` twice on the **same
graph**: pass A with `order="fwd"`, pass B with `order="rev"`
(`engine.reduction_orders()`). `"rev"` reverses both the topological
traversal (`Value.topo`) and the order parents are visited within each node
(`Value.backward` in `quilt/engine.py`), so gradient contributions are
summed into each node in a different sequence. Per node:

```
disag[i] = |gA - gB| / max(|gA|, |gB|)      (0 if both are exactly 0)
```

If the two orders agree to within τ everywhere, the gradient does not hinge
on accumulation order. If a node's disagreement is large, floating-point
non-associativity is deciding the answer at that node — a *wobbling tooth*.
The comb then restores pass-A gradients as the canonical state, so callers
downstream see the recorded pass.

What the comb **does not** measure: it never touches forward values, and it
never compares two different graphs. It perturbs only the *backward*
reduction order of one graph. (See scar 1 below; I demonstrated this.)

### 3c. Instrument 2 — the tape and `replay()`: *did the recorded run really do what it says?*

`quilt/tape.py`. Every op appends a row: `BIND` (a value), `LINK` (op +
parent ids), `EFFECT` (one gradient contribution, with its float `g`),
`TICK` (step boundary), `VIEW`, and `FORGET` (GC). Each row carries `prev`
and `hash`, where `hash = FNV-1a-64(canonical JSON of the row incl. prev)`;
the chain starts from the hash of `"QUILT-TAPE-v1"`.

- `Tape.verify()` recomputes the chain and returns `(True, None)` or
  `(False, first_bad_row_index)`.
- `replay(rows, root=...)` re-applies the EFFECT rows in row order to rebuild
  gradients, and is bit-for-bit equal to the live backward pass because it
  performs the identical additions in the identical order.

FNV-1a is a non-cryptographic hash: it detects accidental edits and casual
tampering, not an adversary who can recompute the chain. The README says
"determinism/regression guard, not an equivalence theorem"; I agree with
that reading of the code.

Why this matters for *rebuilt* computations: to say "the rebuilt graph is
the same", you need a fixed reference. The tape freezes one — structure
(BIND/LINK), inputs, and the exact float contributions — so a later run can
be compared bitwise, and any edited row is located by index.

### 3d. Instrument 3 — the stochastic rational auditor: *how far is float from the true real-number answer?*

`quilt/auditor.py`. Given the tape's BIND/LINK rows it recomputes the whole
forward and reverse pass in `fractions.Fraction` (exact rational arithmetic;
a float's binary expansion is an exact rational, so this is real arithmetic
on the same inputs). Then per sampled node it compares the float gradient to
the exact one (relative drift). Sampling: each non-sink node is promoted with
probability `1/sqrt(N)`; **the sink is always included**; a mean and 95% CI
(z = 1.96) over sampled (node, ancestor) paths are reported. `mode="exact"`
audits all nodes.

Two documented boundaries (`quilt/engine.py` header): `tanh/exp/cos` are
evaluated by libm and frozen as the "exact" value, so the auditor claims
nothing beyond bitwise agreement there; and integer `**n` uses the correctly
rounded exact power rather than libm `pow`.

The exact forward values are also available directly:
`auditor.exact_values(rows)[node_id]` is the true-real result of the recorded
graph, which is what lets you say "this float result is k ulps from truth".

### 3e. Putting them together: the decision procedure

To check that a rebuilt/reordered computation still computes the same thing:

1. **Reference is exact, not the old code.** Compute the exact rational value
   of the *original* structure. Two different float orderings can only be
   compared fairly against something neither of them is.
2. **Each variant is graded against that exact value in ulps.** (Instrument 3.)
3. **Each variant is checked for backward-order sensitivity.** (Instrument 1.)
4. **Each variant is frozen and replayed.** (Instrument 2.)
5. **A variant passes if** its error vs exact is within the budget you set
   *and* its comb has no fallen teeth *and* its tape verifies and replays
   bitwise. Otherwise you get the index/node that moved.

The full reusable version, with the code, is
[`docs/blueprint-ulp-verification.md`](blueprint-ulp-verification.md).

## 4. Walkthrough (copy-paste, real output)

Prerequisite: Python 3, no dependencies (stdlib only). From the repo root.

**a) Run the suite.**

```bash
python3 -m unittest discover -s tests
```

Actual output when I ran it:

```
.........................
----------------------------------------------------------------------
Ran 25 tests in 0.101s

OK
```

**b) Demo A — a well-behaved graph** (`demos/demo_a.py`):

```bash
python3 -m demos.demo_a | head -12
```

```
Demo A — verbatim Karpathy README example (original README, "Example usage")
  g.data  = 24.7041   (README: 24.7041)
  a.grad  = 138.8338   (README: 138.8338)
  b.grad  = 645.5773   (README: 645.5773)
  exact-twin drift: data max=2.776e-17 (bound 1e-12) grad max=2.842e-14 (bound 1e-11)
  tape: 157 rows, hash chain verified
  comb: max dual-order disagreement=2.047e-16 (tau=2.220e-12)
  exact-mode auditor: auditor[exact] nodes=39 sampled=39 paths=398
  drift mean=8.931e-17 std=6.759e-17 CI95=[8.267e-17, 9.595e-17]
  worst node id=0 rel_drift=2.047e-16
```

The run ends `teeth: 39/39 intact, 0 wobbling/lost` and `Demo A PASS`.
In plain terms: the largest order-sensitivity anywhere is about one unit
roundoff (2.05e-16 vs U = 2.22e-16), roughly ten thousand times below the
alarm level τ.

**c) Demo B — a graph that should trip the comb** (`demos/demo_b.py`):

```bash
python3 -m demos.demo_b
```

Excerpt of the actual output:

```
  value residue: d_float = 4.0000000000e+00  true q = 3.1415926536e+00  (quantized at ulp(1e16)=2)
  auditor[stochastic] nodes=21 sampled=6 paths=36
  drift mean=8.369e-03 std=4.548e-02 CI95=[-6.489e-03, 2.323e-02]
  worst node id=16 rel_drift=2.732e-01
  id  0 ·     |██████████████                          | ✗ disag=9.259e-03  *exact 9.346e-03
  ...
  id 16 ·     |·                                       | ✓ disag=0.000e+00  *exact 2.732e-01
  teeth: 20/21 intact, 1 wobbling/lost
```

Two different failures, and the instruments see different halves:
- **id 0** (grad-space cancellation): the two orders disagree by 0.9% —
  a fallen tooth (✗); the auditor confirms it (`*exact 9.346e-03`).
- **id 16** (value-space quantization: `(1e16 + π) - 1e16` yields 4.0, not 3.14…):
  the comb shows ✓ with `disag=0`, because both orders make the *same*
  forward rounding mistake. Only the exact spot-check (`*exact 2.732e-01`)
  sees it. This is the reason the comb is not sufficient alone.

**d) The reorder walkthrough** — sum 64 signed terms spanning ~15 decades,
built as a left-to-right chain and as a pairwise tree. Full script is in the
blueprint (§ Worked example). Output as run:

```
chain rows=891 chain_ok=True replay==live_bitwise=True out=-100470158761.03165 ulps_from_exact=4.0 comb_max_disag=0.000e+00 (tau=2.220e-12)
tree  rows=891 chain_ok=True replay==live_bitwise=True out=-100470158761.03162 ulps_from_exact=2.0 comb_max_disag=0.000e+00 (tau=2.220e-12)
exact sums equal across association orders: True
chain vs tree forward result: 2.0 ulps apart
verify before tamper: (True, None)
verify after planting row 40: (False, 40) row40 t = BIND
```

Reading it: the rebuilt (tree) version is 2 ulps from the chain version and
2 ulps from exact; the chain is 4 ulps from exact. The comb reports 0
disagreement for both — the gradient of a sum is 1 for every term whatever
the order — so **the comb alone would have called this "no change"; the
exact comparison is what measured it.** And a planted edit to row 40 is
reported as `(False, 40)`.

## 5. The contract

What you get, and what you don't:

| Guarantee | Where | Strength |
|---|---|---|
| Two backward orders disagree by ≤ τ (10⁴·U) at every node ⇒ ✓ | `comb.py` | Measurement of *backward accumulation-order* sensitivity for one graph. |
| `verify()` → `(True, None)` or `(False, i)` | `tape.py` | Detects any edit to a row that the chain covers; not adversary-proof (FNV-1a). |
| `replay()` ≡ live gradients, bitwise | `tape.py`; test `test_replay_equals_live_bitwise` | Determinism/regression guard for the same seed and order. |
| Auditor drift mean + 95% CI vs exact rationals | `auditor.py` | Calibrated *sample* estimate; the CI covers sampled paths only. |
| Exact-mode drift bounded (Demo A: 2.8e-14 grad) | `demos/demo_a.py` | Holds for the rational skeleton; transcendentals frozen. |

**The receipt** is what a check should leave behind: the tape's final `hash`
(`t.rows[-1]["hash"]`), the row count, the `(ok, bad_index)` from `verify()`,
the comb's max disagreement and teeth count, and the auditor's
`nodes / sampled / mean / CI95 / worst`. Store those; a later run that
reproduces them is the same computation as far as these instruments can see.

Not guaranteed: equivalence of two *different* graphs (the docs and code
say so); correctness of libm transcendentals; the forward pass's
order-sensitivity via the comb (see scars); detection by a sampled audit of a
bad node that wasn't sampled.

## 6. Scars

1. **The comb is blind to forward reorder.** In the walkthrough above, chain
   and tree forward results differ by 2 ulps and the comb shows 0.000e+00.
   Fix: always compare forward values against `auditor.exact_values`.
2. **Symmetric errors cancel out of the comb.** Demo B's id 16 (✓ at 0
   disagreement, yet 27% exact drift). Both orders share the forward
   rounding. Fix: the exact spot-check column.
3. **The stochastic audit can miss.** Default p = 1/√N; in Demo A's comb run
   only 3 of 39 nodes were sampled (`sampled=3`). Use `mode="exact"` for
   small graphs, or several seeds.
4. **Namespace / id fragility.** Tapes carry node ids; call
   `Value.reset_ids()` before a build if you want two tapes to be comparable
   (`engine.py`).
5. **GC forgets evidence.** `Tape.gc` drops a prefix and re-anchors; survivors
   still verify but the dropped rows are gone by design (`tape.py`).
6. **libm `pow` is not correctly rounded.** The repo observed a 1-ulp
   deviation on `10.0/f`; hence the exact-power path (`engine.py` header).
7. **Order-dependent DFS in upstream micrograd** produces last-ulp wobble
   against quilt — expected; the test allows a few ulps
   (`test_quilt_vs_micrograd_few_ulps`).
8. **Not a hardware-level tool.** Everything is Python floats in scalar ops.
   It says nothing about fused multiply-add, vector reductions, or
   different libm builds on other hardware until *you* express those
   operations as the same graph. Not tested here.

## 7. How it composes

**Weakest-Claim localization applied to performance.** An optimization
(reordered reduction, rebuilt kernel, fused ops) is a claim: "this computes
the same thing." The cheap way to trust it is not to prove all of it, but to
find the *weakest* place it could be false and test exactly there. In this
repo that is the comb's job: rank every node by how much the answer depends
on order, mark the ones above τ, and point the exact auditor there. Passing
teeth mean "nothing wobbles"; a fallen tooth names the node.

Per the brief for this doc set, Syzygy's production plan names
micrograd-quilt as the ulp/byte-exact verifier behind its P4 optimization
agent: a rebuilt kernel is trusted only if the comb says it did not drift.
That plan is not in this repository and I did not read it, so treat that as
the stated integration intent rather than something checked here. What this
repo does supply is the mechanism: reference (exact) → variant (float) →
comb + tape receipt. The gap to close before it can gate a real kernel is
scar 8: the kernel must be expressed as a quilt graph (or the same
procedure ported to the kernel's own value/derivative trace), and
byte-exact claims need replay/hash comparison of outputs, not the comb.

Procedure and code: [`blueprint-ulp-verification.md`](blueprint-ulp-verification.md).

## 8. Next links

- `docs/blueprint-ulp-verification.md` — the reusable procedure.
- `README.md` — three questions, Demo A pins; `DESIGN.md` — the design law.
- `quilt/breeder.py` and `demos/demo_c.py` — genotype (tape as breeding spine);
  not covered here.
- `tests/test_quilt.py` — 25 tests; the comb, tape, and auditor cases are the
  best executable spec.
- `.quilt/links.yml` — sibling forks and upstream pointers.
