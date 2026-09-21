# micrograd-quilt

A fork of [karpathy/micrograd](https://github.com/karpathy/micrograd) that keeps
the `micrograd/` package byte-for-byte and adds a `quilt/` layer answering
three questions the 100 lines can't ask. The original README is untouched
below; nothing in `micrograd/` changes behavior, so every notebook and
test upstream still runs.

**micrograd is the best 100 lines in ML education; micrograd-quilt keeps
that transparency and asks where floats lie, how to prove a gradient, and
what evolution does to a backprop graph.** The layer was redesigned per a
hostile-review amendment — **critic ref M3-01** (MiniMax-M3 hostile-review
persona, 2026-09-21 ~01:10Z); the engineering changed, the doctrine didn't.
Design notes + amendment log: [DESIGN.md](DESIGN.md).

## The three questions

**1. Where does float backprop break? → the stochastic rational auditor**
(`quilt/auditor.py`, twins in `quilt/engine.py`). Every `Value` can carry a
hidden exact-arithmetic twin (`fractions.Fraction`); `--exact` mode (Demo A)
promotes every node for small graphs. The default is *stochastic*: per pass
it samples ~1/√N of the live nodes — sink always promoted, an audit that
never looks at the output is empty on small graphs — promotes only those to
exact arithmetic, and audits their dependency paths exactly, reporting mean
drift + a 95% CI (Z = 1.96, NIST e-Handbook). Calibrated measurement, not
a claimed equivalence with float (critic ref M3-01).

**2. How do you prove a gradient? → the quilt tape**
(`quilt/tape.py`). Every op appends a hash-chained row (FNV-1a 64, cited):
`BIND` / `LINK` / `EFFECT` / `VIEW` / `TICK`, plus `FORGET` for prefix GC —
the FORGET row commits the drop count and old tip, then survivors are
re-anchored so every remaining row still verifies. `backward()` writes
`EFFECT` rows in application order; `replay(rows)` re-applies them
row-for-row, bit-for-bit identical to the live backward pass — a
determinism/regression guard, not an equivalence theorem. A planted wrong
row breaks the chain: `verify()` returns `(False, row_index)`. The tape is
also the breeding genotype (question 3).

**3. How does the engine evolve? → genotype encoding, brains elsewhere**
(`quilt/breeder.py`). The genotype is the tape's BIND/LINK spine as canonical
JSON, ids renumbered by first appearance — genotype identity is graph
structure + constants, independent of the accidental id namespace. `decode`
→ `materialize(rows)` rebuilds a live graph (identical forward values,
bitwise gradients via replay). The viability floor is binary and
multiplicative: one wrong leaf gradient → score 0 — which is also the
tripwire seam. The in-repo loop is a tiny seeded 3-generation *smoke
harness only* — no MAP-Elites here. The real negative-space GAN lives in
[SuperInstance/the-tap](https://github.com/SuperInstance/the-tap)
(PR #7, `NEGATIVE-SPACE-GAN.md` @ 2c60f314; floor doctrine per PR #6) and
breeds these tapes later through the composition seam.

**The comb** (`quilt/comb.py`) is the default view: two backward passes
under different topo/reduction orders (`fwd`/`rev`), per-node disagreement
graded against τ = 1e4·U (Kahan 1965), LOST = 100·τ. Pure float, cheap —
no exact arithmetic needed to see a wobbling tooth. The auditor supplies
`*exact` spot-checks on sampled paths.

## Demos

```bash
python3 -m demos.demo_a         # Karpathy's README example under --exact,
                                # pinned: g=24.7041, a.grad=138.8338,
                                # b.grad=645.5773; all 39 teeth intact
python3 -m demos.demo_b         # ill-conditioned graph: a comb tooth FALLS
                                # (grad-space cancellation, disag=9.3e-3),
                                # auditor names the quantized residue node
                                # with CI95 printed
python3 -m demos.demo_c         # 3-generation genotype loop, seeded:
                                # hash-stable consumability + viability
                                # floor + honest nulls
```

One honest caveat (Demo A): Karpathy's example contains `10.0/f` with `f`
not a power of two, so `10/f` is not exactly representable — the exact
audit legitimately measures worst relative drift ~2.8e-14 (grad) / ~2.8e-17
(data, a couple of ulps) on that path. That *is* zero meaningful drift,
honestly measured; the comb shows the same term as a ulp-scale `*exact`
tooth while the two float reduction orders agree bit-for-bit.

## Demo A, verbatim (pins)

```
Demo A — verbatim Karpathy README example (README.md, original "Example usage")
  g.data  = 24.7041   (README: 24.7041)
  a.grad  = 138.8338   (README: 138.8338)
  b.grad  = 645.5773   (README: 645.5773)
  exact-twin drift: data max=2.776e-17 (bound 1e-12) grad max=2.842e-14 (bound 1e-11)
  tape: 157 rows, hash chain verified
  comb: max dual-order disagreement=2.047e-16 (tau=2.220e-12)
  exact-mode auditor: nodes=39 sampled=39 paths=398
  drift mean=8.931e-17 std=6.759e-17 CI95=[8.267e-17, 9.595e-17]
  teeth: 39/39 intact, 0 wobbling/lost
```

Documented boundaries: transcendentals (`tanh`/`exp`/`cos`) freeze the libm
result as the exact rational — twins agree with float bitwise there and
claim nothing more; `x**n` for integer n is the correctly rounded exact
power `float(Fraction(x)**n)`, because libm `pow` is not guaranteed
correctly rounded (we observed a 1-ulp deviation, `0.2040816326530612` vs
`...123`, on this repo's own Demo A snippet `10.0/f`, `f**-1`, when routed
through C `pow`).

## Tests

The quilt suite is pure stdlib `unittest` — no torch, no pytest required
(the original `test/` keeps its torch-based reference tests untouched):

```bash
python3 -m unittest discover -s tests -v
```

Covered: FNV-1a vectors; hash-chain verify; planted-row tripwires (binary);
FORGET-GC re-anchor; replay ≡ live bitwise (both reduction orders);
tick resume; quilt vs upstream micrograd agree to a few ulps on the shared
op set (both engines' DFS topo iterates parent sets in allocation-dependent
order — that last-ulp wobble is the comb's raison d'être, not a bug);
auditor √N sampling statistics, seeded determinism, stratified sink
promotion, exact-mode promotion, CI containment; comb fires on the
ill-conditioned graph, is silent on exactly-representable integers, and
restores pass-A canonical grads; genotype round-trip (bitwise forward,
namespace-independent hash); breeder seeded determinism, viability-floor
binary tripwire, honest-null archive path; the Karpathy pins.

Stdlib only: `fractions`, `hashlib`, `math`, `json`, `random`, `unittest`.

---

# micrograd (original README)
# micrograd

![awww](puppy.jpg)

A tiny Autograd engine (with a bite! :)). Implements backpropagation (reverse-mode autodiff) over a dynamically built DAG and a small neural networks library on top of it with a PyTorch-like API. Both are tiny, with about 100 and 50 lines of code respectively. The DAG only operates over scalar values, so e.g. we chop up each neuron into all of its individual tiny adds and multiplies. However, this is enough to build up entire deep neural nets doing binary classification, as the demo notebook shows. Potentially useful for educational purposes.

### Installation

```bash
pip install micrograd
```

### Example usage

Below is a slightly contrived example showing a number of possible supported operations:

```python
from micrograd.engine import Value

a = Value(-4.0)
b = Value(2.0)
c = a + b
d = a * b + b**3
c += c + 1
c += 1 + c + (-a)
d += d * 2 + (b + a).relu()
d += 3 * d + (b - a).relu()
e = c - d
f = e**2
g = f / 2.0
g += 10.0 / f
print(f'{g.data:.4f}') # prints 24.7041, the outcome of this forward pass
g.backward()
print(f'{a.grad:.4f}') # prints 138.8338, i.e. the numerical value of dg/da
print(f'{b.grad:.4f}') # prints 645.5773, i.e. the numerical value of dg/db
```

### Training a neural net

The notebook `demo.ipynb` provides a full demo of training an 2-layer neural network (MLP) binary classifier. This is achieved by initializing a neural net from `micrograd.nn` module, implementing a simple svm "max-margin" binary classification loss and using SGD for optimization. As shown in the notebook, using a 2-layer neural net with two 16-node hidden layers we achieve the following decision boundary on the moon dataset:

![2d neuron](moon_mlp.png)

### Training a GPT

For a more advanced example, see [microgpt](https://gist.github.com/karpathy/8627fe009c40f57531cb18360106ce95), which trains and samples from a full GPT-2-like transformer in pure, dependency-free Python. It builds on a more efficient and better version of the autograd engine here (storing local gradients at forward time instead of per-op backward closures), and is the complete algorithm in a single file — everything else is just efficiency. See also the accompanying [explainer post](https://karpathy.github.io/2026/02/12/microgpt/) for a detailed walkthrough.

### Tracing / visualization

For added convenience, the notebook `trace_graph.ipynb` produces graphviz visualizations. E.g. this one below is of a simple 2D neuron, arrived at by calling `draw_dot` on the code below, and it shows both the data (left number in each node) and the gradient (right number in each node).

```python
from micrograd import nn
n = nn.Neuron(2)
x = [Value(1.0), Value(-2.0)]
y = n(x)
dot = draw_dot(y)
```

![2d neuron](gout.svg)

### Running tests

To run the unit tests you will have to install [PyTorch](https://pytorch.org/), which the tests use as a reference for verifying the correctness of the calculated gradients. Then simply:

```bash
python -m pytest
```

### The quilt

*exactness × auditability × breeding × commensuration — a layer over the engine that answers "how much do you trust that gradient?" with measurements, not vibes. Stdlib only (`math`, `json`, `fractions`, `random`, `hashlib`, `unittest`).*
