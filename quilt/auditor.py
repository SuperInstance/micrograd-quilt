"""quilt/auditor.py — the stochastic rational auditor (design law 1, amended).

Default mode: per audit, each node is promoted to exact rational evaluation
with probability p = 1/sqrt(N) (derived: E[#sampled] = N * 1/sqrt(N) = sqrt(N)
— enough sampled paths to tighten a confidence interval, few enough to keep
Fraction cost ~O(sqrt(N)) rather than O(N) — critic ref M3-01's 50-200x cost
critique). Exact gradients are computed along the sampled nodes' dependency
paths with fractions.Fraction arithmetic; per-path drift is
|float_grad - exact_grad| relative to exact magnitude.

Output is CALIBRATED MEASUREMENT (sample mean + 95% CI over sampled paths),
not claimed equivalence — that honesty is the point of the amendment.

mode='exact' promotes ALL nodes (opt-in for small graphs; Demo A pins under
it). Transcendental boundary: see engine.py header — libm freezes.

Constants:
  z = 1.96: standard-normal 95% critical value (cited: NIST/SEMATECH
    e-Handbook, standard normal table).
"""

import math
import random
from fractions import Fraction

Z95 = 1.96  # standard normal 95% critical value (cited: NIST e-Handbook)


def _xapply(op, xs):
    if op == "+":
        return xs[0] + xs[1]
    if op == "*":
        return xs[0] * xs[1]
    if op.startswith("**"):
        return xs[0] ** int(op[2:])
    if op == "relu":
        return xs[0] if xs[0] > 0 else Fraction(0)
    if op == "tanh":
        return Fraction(math.tanh(float(xs[0])))
    if op == "exp":
        return Fraction(math.exp(float(xs[0])))
    if op == "cos":
        return Fraction(math.cos(float(xs[0])))
    raise ValueError(f"auditor: unknown op {op!r}")


def _xpartial(op, xs, out):
    """Exact local partials d(out)/d(parent_i), evaluated at exact values."""
    if op == "+":
        return (Fraction(1), Fraction(1))
    if op == "*":
        return (xs[1], xs[0])
    if op.startswith("**"):
        n = int(op[2:])
        return (n * xs[0] ** (n - 1),)
    if op == "relu":
        return (Fraction(1) if xs[0] > 0 else Fraction(0),)
    if op == "tanh":
        return (1 - out * out,)
    if op == "exp":
        return (out,)
    if op == "cos":
        return (Fraction(-math.sin(float(xs[0]))),)
    raise ValueError(f"auditor: unknown op {op!r}")


def _links(rows):
    return [r for r in rows if r["t"] == "LINK"]


def sinks(rows):
    """Nodes that are never a parent: the graph outputs."""
    used = {i for r in _links(rows) for i in r["p"]}
    return [r["id"] for r in _links(rows) if r["id"] not in used]


def leaves(rows):
    """Source nodes: BIND rows never produced by a LINK (inputs + constants
    coerced from scalars)."""
    link_ids = {r["id"] for r in _links(rows)}
    return [r["id"] for r in rows
            if r["t"] == "BIND" and r["id"] not in link_ids]


def parents_map(rows):
    return {r["id"]: list(r["p"]) for r in _links(rows)}


def ancestors(pmap, node):
    seen, stack = set(), [node]
    while stack:
        n = stack.pop()
        for p in pmap.get(n, []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return sorted(seen)


def exact_values(rows, overrides=None):
    """Exact forward pass in row order (BIND/LINK are forward-topological).
    overrides: {id: Fraction} replaces BIND inputs (finite differences)."""
    overrides = overrides or {}
    vals = {}
    for r in rows:
        if r["t"] == "BIND":
            vals[r["id"]] = overrides.get(r["id"], Fraction(r["data"]))
        elif r["t"] == "LINK":
            vals[r["id"]] = _xapply(r["op"], [vals[i] for i in r["p"]])
    return vals


def exact_grads(rows, sink_ids):
    """Exact reverse mode. Rows are forward-topological, so reversed LINK
    order is a valid reverse topo; single pass suffices."""
    vals = exact_values(rows)
    g = {i: Fraction(0) for i in vals}
    for s in sink_ids:
        g[s] = Fraction(1)
    for r in reversed(_links(rows)):
        if g[r["id"]] == 0:
            continue
        xs = [vals[i] for i in r["p"]]
        for pid, part in zip(r["p"], _xpartial(r["op"], xs, vals[r["id"]])):
            g[pid] += g[r["id"]] * part
    return g


class AuditReport:
    def __init__(self, mode, n_nodes, n_sampled, paths, mean, std, ci_half,
                 worst):
        self.mode, self.n_nodes, self.n_sampled = mode, n_nodes, n_sampled
        self.paths = paths          # list[(sampled_node, ancestor, rel_drift)]
        self.mean, self.std, self.ci_half = mean, std, ci_half
        self.worst = worst          # (ancestor, rel_drift) or None

    @property
    def ci95(self):
        return (self.mean - self.ci_half, self.mean + self.ci_half)

    def __str__(self):
        lo, hi = self.ci95
        lines = [
            f"auditor[{self.mode}] nodes={self.n_nodes} "
            f"sampled={self.n_sampled} paths={len(self.paths)}",
            f"  drift mean={self.mean:.3e} std={self.std:.3e} "
            f"CI95=[{lo:.3e}, {hi:.3e}]",
        ]
        if self.worst:
            lines.append(f"  worst node id={self.worst[0]} "
                         f"rel_drift={self.worst[1]:.3e}")
        return "\n".join(lines)


def audit(rows, float_grads, sink_ids=None, mode="stochastic", seed=0,
          p=None):
    """Stochastic rational audit. float_grads: {id: float grad} from a live
    backward (or tape.replay). Returns AuditReport."""
    ids = [r["id"] for r in rows if r["t"] == "BIND"]
    n = len(ids)
    if sink_ids is None:
        sink_ids = sinks(rows)
    if mode == "exact":
        sampled = list(ids)
    else:
        if p is None:
            p = 1.0 / math.sqrt(n)  # derived: E[#sampled] = sqrt(N)
        rng = random.Random(seed)
        sampled = [i for i in ids if rng.random() < p]
    eg = exact_grads(rows, sink_ids)
    pmap = parents_map(rows)
    paths = []
    for s in sampled:
        for a in [s] + ancestors(pmap, s):
            ge = eg[a]
            gf = float_grads.get(a, 0.0)
            rel = abs(gf - float(ge)) / max(abs(float(ge)), 1e-300)
            paths.append((s, a, rel))
    if len(paths) >= 2:
        mean = sum(r for _, _, r in paths) / len(paths)
        var = sum((r - mean) ** 2 for _, _, r in paths) / (len(paths) - 1)
        std = math.sqrt(var)
        ci_half = Z95 * std / math.sqrt(len(paths))
    elif len(paths) == 1:
        mean, std, ci_half = paths[0][2], 0.0, 0.0
    else:
        mean = std = ci_half = 0.0
    worst = max(paths, key=lambda t: t[2]) if paths else None
    worst = (worst[1], worst[2]) if worst else None
    return AuditReport(mode, n, len(sampled), paths, mean, std, ci_half, worst)
