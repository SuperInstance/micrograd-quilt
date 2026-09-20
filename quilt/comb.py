"""quilt/comb.py — the float-native comb (design law 4, amended M3-01).

Default view: TWO backward passes under different topo/reduction orders
(engine.reduction_orders() = 'fwd' | 'rev'). Edges are shaded by grad
disagreement -- pure float, cheap. The rational auditor (auditor.py)
then spot-checks sampled paths against exact rational ground truth and
names the drift the comb can only gesture at.

The comb IS the default backward: pass A is the recorded canonical pass
(replay == its grads bitwise), pass B is a quiet shadow. VIEW rows carry
the drift map onto the tape without disturbing replay.
"""

from . import engine


def comb(root, t=None):
    """Run both reduction orders; return teeth sorted by diff desc.

    Each tooth: {"id", "a" (fwd grad), "b" (rev grad), "diff", "shade"}.
    With a tape attached, each tooth also emits a VIEW row (drift map)."""
    if t is None:
        t = engine._TAPE
    root.backward(order="fwd")                    # pass A: canonical, recorded
    nodes = {v.id: v for v in root.topo()}
    ga = {i: v.grad for i, v in nodes.items()}
    with engine.quiet():
        root.backward(order="rev", zero=True)     # pass B: silent shadow
    gb = {i: v.grad for i, v in nodes.items()}
    teeth = []
    for i in sorted(ga):
        d = abs(ga[i] - gb[i])
        if d > 0.0:
            teeth.append({"id": i, "a": ga[i], "b": gb[i], "diff": d})
    peak = max((x["diff"] for x in teeth), default=0.0)
    for x in teeth:
        x["shade"] = x["diff"] / peak if peak else 0.0
        if t is not None:
            t.view(nodes[x["id"]], kind="comb-tooth", diff=x["diff"],
                   shade=x["shade"])
    # restore pass A as the canonical grad state: replay(rows) == these
    # grads bitwise, and downstream readers see the recorded pass.
    for i, v in nodes.items():
        v.grad = ga[i]
    teeth.sort(key=lambda x: x["diff"], reverse=True)
    return teeth


def render(teeth, rows=None, limit=12):
    """ASCII money-shot: one bar per tooth, length ~ shade."""
    lines = ["COMB  (dual-order backward disagreement; # = tooth shade)"]
    if not teeth:
        lines.append("  no teeth -- both reduction orders agree bit-for-bit")
        return "\n".join(lines)
    ops = {}
    if rows is not None:
        ops = {r["id"]: r.get("op") for r in rows if r["t"] == "LINK"}
    for x in teeth[:limit]:
        bar = "#" * max(1, round(30 * x["shade"]))
        name = f"q{x['id']:>3} {ops.get(x['id'], 'leaf'):>4}"
        lines.append(f"  [{name}] A={x['a']:.10e} B={x['b']:.10e} "
                     f"diff={x['diff']:.6e} |{bar}|")
    if len(teeth) > limit:
        lines.append(f"  ... and {len(teeth) - limit} more teeth")
    return "\n".join(lines)
