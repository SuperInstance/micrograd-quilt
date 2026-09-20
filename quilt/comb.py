"""quilt/comb.py — the float-native commensuration comb (amendment 4, M3-01).

Default view: TWO backward passes under different reduction orders
(engine.reduction_orders(): 'fwd' and 'rev'). Per-node disagreement
|gA - gB| / max(|gA|, |gB|) is the tooth signal — pure float, cheap,
legible. The rational auditor (quilt.auditor) then supplies exact ground
truth on its ~1/sqrt(N) sampled paths: spot-check column in the render.

The comb's value is legibility of unstable gradient paths, not exactness —
its teeth tell you WHERE to point the auditor.

Constants:
  TAU = 1e4 * U = 2.220446049250313e-12: wobble threshold. Derived: Kahan,
    "Further remarks on reducing truncation errors", ACM Commun. 8(1), 1965 —
    accumulated rounding over D<=1e4 steps is bounded ~D*U; TAU sits 4 orders
    above unit roundoff so healthy graphs never false-positive.
  LOST = 100*TAU: tooth fully lost (three orders into genuine instability).
  Bar length = digits of precision destroyed = max(0, 16 + log10(disag));
    16 = decimal digits carried by float64's 53-bit mantissa (cited:
    log10(2**53) = 15.95, IEEE 754-2019).
"""

import math

from . import auditor
from .engine import U, reduction_orders

TAU = 1e4 * U     # 2.220446049250313e-12, derived above
LOST = 100 * TAU  # tooth lost
_DIGITS = 16      # log10(2**53) = 15.95 -> 16 (IEEE 754-2019, cited)
_BAR_MAX = 40     # render cap


def disagreements(root):
    """Two backward passes, different reduction orders. Returns
    (grads_a, grads_b, disag) keyed by node id; run under an attached tape so
    the auditor can spot-check. After measuring, the graph's live grads are
    RESTORED to pass A — pass A is the canonical, recorded pass (replay ==
    its grads bitwise), and downstream readers should see it."""
    root.backward(order=reduction_orders()[0])
    grads_a = {v.id: v.grad for v in root.topo()}
    root.backward(order=reduction_orders()[1], zero=True)
    grads_b = {v.id: v.grad for v in root.topo()}
    for v in root.topo():          # restore pass A as canonical state
        v.grad = grads_a[v.id]
    disag = {}
    for i in grads_a:
        ga, gb = grads_a[i], grads_b[i]
        disag[i] = abs(ga - gb) / max(abs(ga), abs(gb)) if \
            (ga != 0.0 or gb != 0.0) else 0.0
    return grads_a, grads_b, disag


def render_comb(root, tape, seed=0, tau=TAU):
    """Float-native commensuration comb render (ASCII string).

    Teeth: one line per node; tooth glyph from order-disagreement vs TAU/LOST;
    bar = digits of precision destroyed; '*' marks auditor spot-checked
    paths with their exact rel drift."""
    grads_a, grads_b, disag = disagreements(root)
    report = auditor.audit(tape.rows, grads_a, seed=seed)
    exact_paths = {a: r for _, a, r in report.paths}
    ops = {r["id"]: r["op"] for r in tape.rows if r["t"] == "LINK"}
    lines = [
        f"commensuration comb  orders={reduction_orders()}  "
        f"tau={tau:.3e} (1e4*U, Kahan 1965)",
        f"  {report}",
    ]
    for i in sorted(disag):
        d = disag[i]
        lost = max(0, _DIGITS + math.log10(d)) if d > 0 else 0.0
        w = min(_BAR_MAX, int(round(lost)))
        bar = "█" * w if w else "·"
        glyph = "✓" if d <= tau else ("◐" if d <= LOST else "✗")
        spot = f"  *exact {exact_paths[i]:.3e}" if i in exact_paths else ""
        op = ops.get(i, "·")
        lines.append(f"  id{i:>3} {op:<5} |{bar:<40}| {glyph} "
                     f"disag={d:.3e}{spot}")
    n_bad = sum(1 for d in disag.values() if d > tau)
    lines.append(f"  teeth: {len(disag) - n_bad}/{len(disag)} intact, "
                 f"{n_bad} wobbling/lost")
    return "\n".join(lines)
