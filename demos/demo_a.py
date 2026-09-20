"""Demo A — Karpathy's own README example, run under --exact (full twins).

micrograd's README example, op for op (README.md lines 24-38 of the fork's
base). Under engine mode 'exact' every node carries a fractions.Fraction
twin; the float path is a sequence of correctly-rounded ops, so float vs
twin drift is bounded by the Kahan accumulation bound D*U*|x| (Kahan 1965,
cited in quilt/comb.py) — for this graph D<=16, |g|<=48, |grad|<=650, i.e.
"zero drift" = ulp-scale, far below the comb wobble threshold TAU=1e4*U.
The comb shows every tooth intact; the exact-mode auditor's CI upper bound
sits below TAU.

Run from repo root: python3 -m demos.demo_a
"""

from quilt import auditor, comb, engine, tape

SNIPPET_NOTE = "verbatim Karpathy README example (README.md L24-38)"


def build():
    """The README snippet, quilt engine, exact twins, one tape attached."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t), engine.mode("exact"):
        a = engine.Value(-4.0)
        b = engine.Value(2.0)
        c = a + b
        d = a * b + b ** 3
        c += c + 1
        c += 1 + c + (-a)
        d += d * 2 + (b + a).relu()
        d += 3 * d + (b - a).relu()
        e = c - d
        f = e ** 2
        g = f / 2.0
        g += 10.0 / f
        g.backward()
    return t, a, b, g


def main():
    t, a, b, g = build()
    print(f"Demo A — {SNIPPET_NOTE}")
    print(f"  g.data  = {g.data:.4f}   (README: 24.7041)")
    print(f"  a.grad  = {a.grad:.4f}   (README: 138.8338)")
    print(f"  b.grad  = {b.grad:.4f}   (README: 645.5773)")
    assert f"{g.data:.4f}" == "24.7041", "g.data mismatch vs README"
    assert f"{a.grad:.4f}" == "138.8338", "a.grad mismatch vs README"
    assert f"{b.grad:.4f}" == "645.5773", "b.grad mismatch vs README"

    # exact-twin audit: drift bounded by Kahan D*U*|x| (D<=16 ops here),
    # i.e. ulp-scale "zero drift"; bounds derived from magnitudes above.
    nodes = g.topo()
    max_data_drift = max(abs(v.data - float(v.twin)) for v in nodes)
    max_grad_drift = max(abs(v.grad - float(v.grad_twin)) for v in nodes)
    print(f"  exact-twin drift: data max={max_data_drift:.3e} (bound 1e-12) "
          f"grad max={max_grad_drift:.3e} (bound 1e-11)")
    assert max_data_drift <= 1e-12, "data drift above Kahan bound"
    assert max_grad_drift <= 1e-11, "grad drift above Kahan bound"

    ok, bad = t.verify()
    assert ok, f"tape chain broken at row {bad}"
    print(f"  tape: {len(t.rows)} rows, hash chain verified")

    # float-native comb: every tooth intact
    grads_a, grads_b, disag = comb.disagreements(g)
    max_disag = max(disag.values())
    print(f"  comb: max dual-order disagreement={max_disag:.3e} "
          f"(tau={comb.TAU:.3e})")
    assert max_disag <= comb.TAU, "comb shows a wobble on a healthy graph"

    # exact-mode auditor: CI upper bound below tau
    rep = auditor.audit(t.rows, grads_a, mode="exact")
    print(f"  exact-mode auditor: {rep}")
    assert rep.ci95[1] < comb.TAU, "exact audit CI above tau"

    print()
    print(comb.render_comb(g, t, seed=0))
    print()
    print("Demo A PASS — ulp-scale drift (Kahan-bounded), comb intact, "
          "exact-mode CI below tau.")


if __name__ == "__main__":
    main()
