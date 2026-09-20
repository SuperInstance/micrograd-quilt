
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

The quilt is four small modules, one tape, three demos. It was redesigned per a hostile-review amendment (critic ref M3-01, MiniMax-M3, 2026-09-21) — the engineering changed, the doctrine didn't:

1. **Stochastic rational auditor, exact twins opt-in** (`quilt/auditor.py`, `quilt/engine.py`). Every `Value` carries a hidden exact-arithmetic twin (`fractions.Fraction`); `--exact` mode (Demo A) pins the Karpathy README numbers with ulp-scale drift. Default mode samples ~1/√N nodes per pass and audits their dependency paths exactly, emitting mean drift + a 95% CI (Z = 1.96, NIST e-Handbook). This is calibrated measurement, not claimed equivalence.
2. **The WAL shrank to its justification** (`quilt/tape.py`). Five opcodes (BIND / LINK / EFFECT / VIEW / TICK) hash-chained with FNV-1a 64 — justified as the breeding genotype format and a determinism/regression guard (`replay(rows)` reproduces live gradients bitwise), not as an "equivalence theorem". FORGET re-anchors the chain after prefix GC.
3. **Breeder ships brains-out** (`quilt/breeder.py`). Only the genotype encoding (the tape's BIND/LINK rows as canonical JSON) plus a tiny seeded 3-generation consumability demo: decode → `materialize` → live backward. The real negative-space GAN lives in [the-tap](https://github.com/SuperInstance/the-tap) (PR #7; floor doctrine per PR #6) and breeds tapes through the composition seam. The viability floor is binary and multiplicative: one wrong leaf gradient → score 0, which is also the tripwire seam.
4. **The comb is float-native** (`quilt/comb.py`). Default view: two backward passes under different topo/reduction orders (`fwd`/`rev`); per-node disagreement is the tooth. τ = 1e4·U (Kahan 1965 accumulation bound), LOST = 100·τ. The auditor supplies exact spot-checks on sampled paths (`*exact` column).

```bash
python3 -m demos.demo_a   # Karpathy README example under --exact
python3 -m demos.demo_b   # ill-conditioned graph: a tooth falls
python3 -m demos.demo_c   # tape-as-genotype, 3 seeded generations
python3 -m unittest discover -s tests -v   # 20 tests, stdlib only
```

Demo A, verbatim (the `*exact` column is the auditor's spot-check; dual-order disagreement is the stricter signal — every tooth intact):

```
Demo A — verbatim Karpathy README example (README.md L24-38)
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

Demo B plants two classic instabilities in one small graph — grad-space catastrophic cancellation (`dv = 1e16 − (1e16−100) + 7 = 107` computed through ±1e16 terms; the two reduction orders land on 107 and 108) and value-space quantization (`(x·1e16 + π·x) − x·1e16` at ulp = 2). The comb's tooth at the cancellation node falls (disag = 9.3e-3 ≫ LOST); the auditor names the residue node (rel drift 0.273) with a printed CI.

Documented boundaries: transcendentals (tanh/exp/cos) freeze the libm result as the exact rational — twins agree with float bitwise there and claim nothing more; `x**n` is the correctly rounded exact power (libm `pow` is not guaranteed so). Design notes and the amendment log: [DESIGN.md](DESIGN.md).

### License

MIT
