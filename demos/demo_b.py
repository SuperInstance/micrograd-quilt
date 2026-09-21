"""Demo B — the ill-conditioned graph: float-native comb + rational auditor.

Two ill-conditioned structures in one small graph:

1. GRAD-SPACE CATASTROPHIC CANCELLATION (the falling tooth). Leaf v feeds
   three consumers w_i = v * A_i with A = [1e16, -(1e16-100), 7]. The true
   gradient dv = 1e16 - (1e16 - 100) + 7 = 107 — computed through +/-1e16
   terms whose low bits decide the answer. The two reduction orders
   accumulate those contributions in different sequences:
   IEEE-754 addition is not associative, so one order lands on 107 and the
   other on 108. The comb's tooth at v FALLS (disag >> LOST).

2. VALUE-SPACE QUANTIZATION RESIDUE (the named node). big = x*1e16 is not
   exactly representable; m = big + q absorbs q's low bits at ulp(1e16)=2;
   d = m - big returns a QUANTIZED residue instead of q. The stochastic
   rational auditor names d's exact drift and prints the 95% CI.

Float autograd shows neither; the comb shows (1) in pure float, the auditor
confirms both with exact rational ground truth on sampled paths.

Run from repo root: python3 -m demos.demo_b
"""

import math

from quilt import auditor, comb, engine, tape


def build():
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        v = engine.Value(1.0)                    # grad-cancellation leaf
        A1 = engine.Value(1e16)
        A2 = engine.Value(-9999999999999900.0)   # -(1e16 - 100)
        A3 = engine.Value(7.0)
        w1 = v * A1
        w2 = v * A2
        w3 = v * A3
        x = engine.Value(1.0)                    # value-residue leaf
        K = engine.Value(1e16)
        big = x * K
        q = x * math.pi                          # the signal being quantized
        m = big + q                              # absorption at ulp(1e16)=2
        d = m - big                              # quantized residue (true: q)
        s = d * 100.0                            # amplified residue
        L = ((w1 + w2) + w3) + s                 # sink
        L.backward()
    return t, dict(v=v, d=d, q=q, L=L)


def main():
    t, nodes = build()
    L = nodes["L"]
    v, d, q = nodes["v"], nodes["d"], nodes["q"]
    print("Demo B — ill-conditioned graph (grad-space cancellation + "
          "value-space quantization)")
    print(f"  true dv = 1e16 - (1e16-100) + 7 = 107 "
          f"(computed through +/-1e16 terms)")
    print(f"  value residue: d_float = {d.data:.10e}  true q = {q.data:.10e}"
          f"  (quantized at ulp(1e16)=2)")

    print()
    print(comb.render_comb(L, t, seed=1))

    print()
    print("Demo B done — the fallen tooth names v (grad-space cancellation); "
          "the auditor's CI is calibrated ground truth on sampled paths.")


if __name__ == "__main__":
    main()
