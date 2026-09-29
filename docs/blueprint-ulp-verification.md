# Blueprint: proving a reordered/rebuilt computation preserves the result to ulp precision

A reusable procedure built from the instruments in `quilt/`
(`comb.py`, `tape.py`, `auditor.py`, `engine.py`). Companion to
[`understanding-micrograd-quilt.md`](understanding-micrograd-quilt.md), which
explains the instruments. Everything marked "output" was produced by running
the code in this document on this repo; nothing is claimed that wasn't run.

**Scope.** This proves things about computations expressed as quilt `Value`
graphs (scalar `+ * ** relu tanh exp cos`, `quilt/engine.py`). Applying it to
native code (a GPU/CPU kernel, SIMD, FMA) means reproducing that code's
arithmetic as such a graph, or porting the same procedure. That port was not
done or tested here.

## The claim you are actually testing

"Variant V computes the same thing as reference R" is too vague to test. Pick
one of two claims:

- **Byte-exact:** V's outputs are bitwise identical to R's. Test: compare
  `float` values with `==` (and tape `hash`, if the graphs are identical).
  The comb is irrelevant to this claim.
- **Ulp-bounded:** V's output is within *k* ulps of the exact real-number
  result, and no worse than R. Test: the procedure below.

Decide which, and the budget *k*, **before** running. Otherwise you will
choose the threshold that makes the run pass.

## Procedure

1. **Freeze the reference structure and inputs.** Build R under
   `engine.Value.reset_ids()` with a `tape.Tape` attached. Save inputs.
2. **Compute the exact answer** from R's tape:
   `auditor.exact_values(t.rows)[out_id]` (a `Fraction`). If V is a
   *reordering* (same real-number function), the exact value is the same
   for V; check that (`==`) — if not, V is a different function and no
   ulp budget applies.
3. **Grade each variant in ulps vs exact:** `abs(out.data - float(ex)) /
   math.ulp(float(ex))`. Require ≤ *k*, and ≤ R's own error if you claim
   "no worse".
4. **Run the comb on each variant**: `comb.disagreements(out)` → `disag`.
   Require `max(disag.values()) <= comb.TAU` (or your own tighter τ). A
   fallen tooth names the node whose gradient is decided by accumulation
   order.
5. **Audit exactly where the comb is blind.** `auditor.audit(rows,
   grads, mode="exact")` for small graphs; the stochastic default for
   large ones, with several seeds. Require worst drift within budget; read
   the CI, don't just read the mean.
6. **Freeze and prove the receipt.** `t.verify() == (True, None)`;
   `tape.replay(t.rows, root=out.id)` equals live grads bitwise; record
   the final row hash, row count, comb max, teeth count, audit
   `sampled/mean/CI95/worst`.
7. **Store the receipt.** A later rebuild must reproduce it, or the diff is
   the report.

## Worked example (script + real output)

Sum of 64 signed terms spanning 10⁻³…10¹² — a left-to-right chain versus a
pairwise tree. Saved as any file at the repo root and run with
`PYTHONPATH=. python3 file.py`:

```python
import math, random
from quilt import engine, tape, auditor, comb

rng = random.Random(7)
xs = [rng.uniform(-1, 1) * 10 ** rng.randint(-3, 12) for _ in range(64)]

def build(assoc):
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        sq = [engine.Value(x) * 1.0 for x in xs]
        if assoc == "chain":
            acc = sq[0]
            for s in sq[1:]:
                acc = acc + s
        else:                                   # pairwise tree
            lvl = sq
            while len(lvl) > 1:
                lvl = [lvl[i] + lvl[i + 1] for i in range(0, len(lvl), 2)]
            acc = lvl[0]
        acc.backward()
    return t, acc

def ulps(a, b):
    return abs(a - b) / math.ulp(b)

exact = {}
for name in ("chain", "tree"):
    t, out = build(name)
    ok, _ = t.verify()
    g = tape.replay(t.rows, root=out.id)
    live = {v.id: v.grad for v in out.topo()}
    same = all(g.get(i, 0.0) == live[i] for i in live)
    ex = auditor.exact_values(t.rows)[out.id]
    exact[name] = ex
    _, _, dis = comb.disagreements(out)
    print(f"{name:5s} rows={len(t.rows)} chain_ok={ok} replay==live_bitwise={same} "
          f"out={out.data!r} ulps_from_exact={ulps(out.data, float(ex)):.1f} "
          f"comb_max_disag={max(dis.values()):.3e} (tau={comb.TAU:.3e})")
print("exact sums equal across association orders:", exact["chain"] == exact["tree"])
ca, ta = build("chain")[1].data, build("tree")[1].data
print(f"chain vs tree forward result: {ulps(ca, ta):.1f} ulps apart")
t, out = build("chain")
print("verify before tamper:", t.verify())
t.rows[40]["data"] = 0.5   # row 40 is a BIND
print("verify after planting row 40:", t.verify(), "row40 t =", t.rows[40]["t"])
```

Output, as run:

```
chain rows=891 chain_ok=True replay==live_bitwise=True out=-100470158761.03165 ulps_from_exact=4.0 comb_max_disag=0.000e+00 (tau=2.220e-12)
tree  rows=891 chain_ok=True replay==live_bitwise=True out=-100470158761.03162 ulps_from_exact=2.0 comb_max_disag=0.000e+00 (tau=2.220e-12)
exact sums equal across association orders: True
chain vs tree forward result: 2.0 ulps apart
verify before tamper: (True, None)
verify after planting row 40: (False, 40) row40 t = BIND
```

How to read it against the procedure:

- Step 2 passes: the exact sums are equal, so the tree is a legitimate
  reordering of the chain.
- Step 3: chain 4 ulps from exact, tree 2 ulps. If your budget were *k* = 4
  both pass; at *k* = 2 the chain fails and the tree passes ("no worse than
  R" holds).
- Step 4: comb max disagreement 0.0 for both. This is *correct but
  uninformative* — the gradient of a sum is 1 per term in any order. The
  drift lived in the forward value, which only step 2/3 sees.
- Step 6: both tapes verify; replay matches bitwise; tamper at row 40 is
  localized as `(False, 40)`.

## Second worked example: when the comb *is* the detector

`python3 -m demos.demo_b` (real output excerpt):

```
  id  0 ·     |██████████████                          | ✗ disag=9.259e-03  *exact 9.346e-03
  id 16 ·     |·                                       | ✓ disag=0.000e+00  *exact 2.732e-01
  teeth: 20/21 intact, 1 wobbling/lost
```

id 0 is a leaf whose gradient is `1e16 − (1e16−100) + 7` summed through
±1e16 terms: the two accumulation orders land on 107 vs 108, so the comb
fires, and the exact column agrees. id 16 is the opposite: a forward
absorption error both orders share, so the comb is silent and only the exact
column shows 27% drift. Between them, that is why steps 4 and 5 are both
required.

## Scars (reusable rules)

1. **Grade against exact, not against the old implementation.** Two floats
   that agree with each other can both be wrong; two that disagree can both
   be within budget (above: chain vs tree 2 ulps apart, both near exact).
2. **The comb tests backward reduction order only.** It never varies the
   forward pass and never compares two graphs. Do not cite a clean comb as
   evidence a forward reorder is safe.
3. **Shared error is invisible to any order-swapping test.** Use the
   exact spot-check.
4. **A sampled audit is evidence, not proof.** Default probability 1/√N and
   the sink always included; 3 of 39 nodes sampled in Demo A's comb run.
   Report `sampled`, use `mode="exact"` when affordable, vary `seed`.
5. **State τ honestly.** `TAU = 1e4·U ≈ 2.2e-12` is 10⁴ ulps of slack. A
   pass at τ is not a pass at "1 ulp". For tight claims use step 3's
   ulp count, not the comb glyph.
6. **Transcendentals are frozen at libm's answer** (`engine.py`). If V
   changes the libm, the auditor agrees with whichever result is fed to it;
   compare bitwise instead.
7. **Ids are namespace.** `reset_ids()` before each build if tapes are to be
   compared; the breeder's genotype canon renumbers by first appearance
   (`quilt/breeder.py`) for structure-only identity.
8. **FNV-1a is tamper-evident, not tamper-proof**, and `gc()` discards the
   dropped prefix's evidence by design (`tape.py`). Don't GC a tape you
   intend to use as a receipt.
9. **A test that can't fail isn't a check.** The suite carries a
   comb-fires-on-ill-conditioned test and a comb-silent-on-integers test
   (`tests/test_quilt.py`); keep an equivalent positive control (a
   deliberately broken variant) in any verifier you build from this.

## Use as a gate for on-metal optimization

The shape is Weakest-Claim localization applied to performance: an
optimization is a claim ("same result, faster"); you do not re-prove the
whole kernel, you find where the claim is weakest — the nodes whose value
depends on order — and test those against exact arithmetic. The optimizer
proposes; the verifier says "no drift" (with a receipt) or names the node.

Per the brief for this doc set, Syzygy's production plan names
micrograd-quilt as the ulp/byte-exact verifier behind its P4 optimization
agent. That plan is not in this repository and I did not read it; this
document describes what the repo's mechanism can support, not what that
system does today. To make the gate real, a minimum contract for the agent:

1. The candidate kernel is accompanied by a graph (or trace) of its
   arithmetic in the same op set, or an op-for-op port.
2. It passes steps 2–6, with the receipt attached to the change.
3. For byte-exact claims, outputs are compared bitwise on a fixed input set,
   and the receipt records the hash of those outputs (not the comb).
4. A failing candidate is returned with the named node/row, not a bare
   "rejected".

## Next links

- `quilt/comb.py`, `quilt/tape.py`, `quilt/auditor.py` — the instruments.
- `tests/test_quilt.py` — executable spec, incl. replay-equals-live and
  comb positive/negative controls.
- `docs/understanding-micrograd-quilt.md` — the front door.
