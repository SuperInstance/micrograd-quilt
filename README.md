
# micrograd-quilt

A fork of [karpathy/micrograd](https://github.com/karpathy/micrograd) that keeps
the `micrograd/` package byte-for-byte and adds a `quilt/` layer answering
three questions the 100 lines can't ask. The original README is untouched
below; nothing in `micrograd/` changes behavior, so every notebook and
test upstream still runs.

**micrograd is the best 100 lines in ML education; micrograd-quilt keeps
that transparency and asks where floats lie, how to prove a gradient, and
what evolution does to a backprop graph.**

## The three questions

**1. Where does float backprop break? → the stochastic rational auditor**
(`quilt/auditor.py`). Every forward pass also runs a full-twin graph in
exact `fractions.Fraction` arithmetic. By default the auditor is
*stochastic*: it samples ~N/√N of the N live nodes under a fixed seed and
reports exact drift + a 95% confidence interval on the sampled paths —
calibrated measurement, not a claimed equivalence with float (critic ref
M3-01). `--exact` promotes every node (full twin) for small graphs:

```bash
python3 -m quilt.demos a --exact
```

**2. How do you prove a gradient? → the quilt tape**
(`quilt/tape.py`). Every op appends a hash-chained row (FNV-1a, 64-bit):
`BIND` / `LINK` / `EFFECT` / `VIEW` / `TICK`, plus `FORGET` for tape GC.
`backward()` writes `EFFECT` rows in application order; `replay(rows)`
re-applies them row-for-row, so replay is bit-for-bit identical to the live
backward pass — a regression guard, not a theorem. A planted wrong `EFFECT`
breaks the chain: `verify()` returns `(False, row_index)`. The tape is also
the breeding genotype (question 3).

**3. How does the engine evolve? → genotype encoding, brains elsewhere**
(`quilt/genotype.py`, `quilt/breeder.py`). The genotype is the tape's
BIND/LINK spine; `materialize(g)` rebuilds a live graph with identical
forward values, and `genotype_hash` is namespace-independent, so any
faithful rebuild hashes the same. The in-repo demo loop is a *smoke
harness only* — no MAP-Elites here. The real negative-space GAN lives in
[SuperInstance/the-tap](https://github.com/SuperInstance/the-tap) (PR #7,
`NEGATIVE-SPACE-GAN.md` @ 2c60f314) and breeds these tapes later through
its composition seam.

**The comb** (`quilt/comb.py`) is the default view: two backward passes
under different topo/reduction orders, edges shaded by float disagreement.
Pure float, cheap — no exact arithmetic needed to see a wobbling tooth.

## Demos

```bash
python3 -m quilt.demos a            # Karpathy's example, pinned: g=24.7041,
                                    # a.grad=138.8338, b.grad=645.5773;
                                    # comb intact, exact audit ≤1e-12 drift
python3 -m quilt.demos b            # ill-conditioned graph: comb tooth at
                                    # diff=1e32, auditor CI95 names the drift
python3 -m quilt.demos c            # 3-generation genotype loop:
                                    # hash-stable consumability + viability
python3 -m quilt.breeder            # random-organism viability floor harness
```

One honest caveat (A): Karpathy's example contains `10.0/f` with `f` not a
power of two, so `10/f` is not exactly representable — the exact audit
legitimately measures a worst relative drift of ~2e-16 (a couple of ulps)
on that path. That *is* zero meaningful drift, and the comb shows the same
term as its one ulp-scale tooth.

## Tests

The quilt suite is pure stdlib + pytest — no torch required (the original
`test/` keeps its torch-based reference tests untouched):

```bash
python3 -m pytest tests/ -q     # 22 tests
```

Covered: FNV vectors; hash-chain verify; planted-`EFFECT` tripwire
(binary); `FORGET` GC keeps the suffix verifiable; replay ≡ live bitwise;
tick-resume composes; quilt vs micrograd agree to a few ulps on the shared
op set (both engines' DFS topo iterates parent sets in allocation-dependent
order — that last-ulp wobble is the comb's raison d'être, not a bug); auditor √N sampling stats, seeded determinism, exact promotion;
exact-vs-float agreement on dyadic graphs; comb fires on the
ill-conditioned graph and is silent on exactly-representable ones; genotype
round-trip (bitwise forward, namespace-independent hash); demo-loop seeded
determinism; the Karpathy pins.

Stdlib only: `fractions`, `hashlib`, `math`, `json`, `random`.

---

# micrograd (original README)

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

### License

MIT
