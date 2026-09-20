"""Demo B — the ill-conditioned graph: float-native comb + rational auditor.

Catastrophic cancellation in the rational skeleton, (1-cos x)/x-style:
a small signal q is added to a LARGE path p = x*1e8 and then p is subtracted
again. In float64 the difference s = (p + q) - p keeps an absolute residue
~ U * |p| ~ 1e-8 — comparable to q itself — and the amplifier u = s * 1e6
blows the residue into the output. Float autograd cannot show you this; the
comb's dual-order disagreement names the unstable nodes, and the stochastic
rational auditor confirms the exact drift on its sampled paths, with the
confidence interval printed.

Run: python3 demos/demo_b.py
"""

import math

from quilt import auditor, comb, engine, tape


def build():
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        x = engine.Value(1.234567889)
        k = engine.Value(1e8)                # big magnitude path
        q = x * math.pi                      # the small signal (~3.88)
        p = x * k                            # the big path (~1.23e8)
        r = p + q                            # absorption: q's low bits lost
        s = r - p                            # cancellation: s ~= q + residue
        u = s * 1e6                          # amplifier: residue -> O(1e-2)
        L = u * x                            # sink
        L.backward()
    return t, dict(x=x, k=k, q=q, p=p, r=r, s=s, u=u, L=L)


def main():
    t, nodes = build()
    L = nodes["L"]
    print("Demo B — ill-conditioned graph (catastrophic cancellation)")
    print(f"  float:      s = {nodes['s'].data:.10e} "
          f"(true q = {nodes['q'].data:.10e})")
    exact = auditor.exact_values(t.rows)
    print(f"  exact:      s = {float(exact[nodes['s'].id]):.10e} "
          f"— residue named: {abs(nodes['s'].data - float(exact[nodes['s'].id])):.3e}")

    print()
    print(comb.render_comb(L, t, seed=0))

    print()
    print("Demo B done — teeth above name the unstable gradient paths; the "
          "auditor's CI is the calibrated ground truth on sampled paths.")


if __name__ == "__main__":
    main()
