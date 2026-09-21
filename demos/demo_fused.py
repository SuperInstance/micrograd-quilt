"""Demo F — the fused substrate end to end (Lane AK slice 2).

The exact-rational lattice (values/grads on an integer (k,s) grid, q16
identity — Lane AH3) wearing its WAL face (Lane AK slice 1): every cell the
lattice places is a BIND/LINK row on a hash-chained quilt Tape, the backward
FuelReceipt is fused into the chain by FNV-1a over {tip, fuel.canonical()},
and the whole graph replays from rows alone — cycles included.

Story, in order:
  1. build (a+b)*c with exact rationals, tape it, fuse the fuel receipt
  2. replay from rows alone: values + grads exact, fusion verifies
  3. tamper one tape row -> the chain names the row, fusion fails
  4. a legal cycle (placeholder + rewire): h = (h+2)/2 relaxes to 2,
     replays to the same fixed point at the resolution floor
  4. the fleet auditor bridges on: exact grads over the taped rows agree
     with the lattice's relaxation backward — measured drift 0.0, CI [0,0]
     (bridge BIND data carries Fraction(num,den): a float there smuggles
     binary rounding into the auditor's "exact" path)
  5. twist rows are guest ops (not substrate): projected out of the tape,
     twist's shadow S = 1-R exact by construction

Honest limits (per M3-01): this is a determinism/regression guard and
energy attestation, NOT an equivalence theorem. Cyclic replay reproduces
the fixed point AT THE RESOLUTION the original evaluated under; hop_cost
for cyclic rows is recomputed from final placement, not historically exact.

Run from repo root: python3 -m demos.demo_fused
"""

from fractions import Fraction

from quilt import auditor, lattice_tape as lt, tape
from quilt.lattice_engine import Q16, SCALE, twist


def build_abc():
    """(a+b)*c with exact rationals; y sink at (k=2, s=0)."""
    from quilt.lattice_engine import Lattice
    lat = Lattice()
    a = lat.parameter(3, 2, tag="a")       # 3/2
    b = lat.scalar(1, 3, tag="b")          # 1/3
    c = lat.parameter(-5, 7, tag="c")      # -5/7
    y = (a + b) * c
    lat.evaluate()
    return lat, a, b, c, y


def build_cycle():
    """h = (h + 2) * 1/2 — a legal cycle closed by placeholder + rewire.
    Relaxation converges to the fixed point h = 2 at the resolution floor
    (exact zero is unreachable: the orbit is 1, 3/2, 7/4, ... -> 2)."""
    from quilt.lattice_engine import Lattice
    lat = Lattice()
    c2 = lat.scalar(2, 1, tag="c2")
    half = lat.scalar(1, 2, tag="half")
    h = lat.placeholder(tag="h")
    s = lat.qadd(h, c2)
    h2 = lat.qmul(s, half)
    # h was a placeholder; h2 is the relaxed successor. Close the loop:
    # rewire h to compute (h+2)*1/2 itself, drop h2 from the graph.
    lat.rewire(h, "QMUL", (s, half))
    lat.cells.remove(h2)
    lat.evaluate(resolution=Q16(1, SCALE))
    return lat, h


def main():
    print("Demo F — fused substrate: tape/auditor ⊕ lattice grid")

    # 1. tape + fuse -------------------------------------------------------
    lat, a, b, c, y = build_abc()
    fuel = lat.backward(lat.cells[-1])
    t = lt.tape_lattice(lat)
    fuse = lt.fuse_receipt(t, fuel)
    print(f"  1. taped (a+b)*c: "
          f"{len(t.rows)} rows, chain tip {t._hash & 0xffffffff:08x}, fuse {fuse & 0xffffffff:08x}")
    assert t.verify() == (True, None)

    # 2. replay from rows alone --------------------------------------------
    rows = list(t.rows)
    lat2, cells = lt.replay_lattice(rows, evaluate=False)
    fuel2 = lat2.backward(lat2.cells[-1])
    ok, _ = lt.verify_fusion(rows, fuel)
    print(f"  2. replay: y = {lat2.cells[-1].value} (live {y.value}), "
          f"grad a = {cells[0].grad if 0 in cells else lat2.cells[0].grad}, fusion verified = {ok}")
    assert y.value == lat2.cells[-1].value == Q16(-55, 42)
    assert ok

    # 3. tamper evidence ----------------------------------------------------
    rows_bad = [dict(r) for r in rows]
    for r in rows_bad:
        if r["t"] == "LINK":
            r["p"] = list(reversed(r["p"]))
            break
    ok_bad, _ = lt.verify_fusion(rows_bad, fuel)
    print(f"  3. tamper one LINK parent list -> fusion verified = {ok_bad} (must be False)")
    assert not ok_bad

    # 4. a legal cycle ---------------------------------------------------------
    latc, h = build_cycle()
    print(f"  4. cycle h=(h+2)/2: relaxed h = {h.value} "
          f"(display {h.value.to_float():.6f}, fixed point 2; sweep stops when "
          f"delta <= resolution, so residual <= 2*resolution)")
    assert 0 < 2.0 - h.value.to_float() <= 2.0 / SCALE
    rows_c = lt.lattice_rows(latc)
    latc2, cells_c = lt.replay_lattice(rows_c, resolution=Q16(1, SCALE))
    hid = next(r["id"] for r in rows_c if r.get("tag") == "cyc[h]")
    d = 2.0 - cells_c[hid].value.to_float()
    print(f"     cyclic replay reproduces fixed point at same rational: "
          f"{cells_c[hid].value == h.value} (residual {d:.2e} <= 2*resolution)")
    assert cells_c[hid].value == h.value
    assert 0 < d <= 2.0 / SCALE

    # 5. auditor bridge -------------------------------------------------------
    # BIND data carries Fraction(num, den): exact through the auditor's
    # Fraction(data) path — a float here smuggles binary rounding into the
    # "exact" audit (Fraction(float(-5/7)) != -5/7, measured).
    audit_rows = [
        {"t": "BIND", "id": r["id"], "data": Fraction(r["q"][0], r["q"][1])}
        if r["t"] == "BIND" else
        {"t": "LINK", "id": r["id"], "op": "+" if r["op"] == "QADD" else "*",
         "p": r["p"]}
        for r in lt.lattice_rows(build_abc()[0])
    ]
    lat3, a3, b3, c3, y3 = build_abc()
    lat3.backward(y3)
    float_grads = {i: lat3.cells[i].grad.to_float() for i in range(len(lat3.cells))}
    sink_ids = auditor.sinks(audit_rows)
    rep = auditor.audit(audit_rows, float_grads, sink_ids, mode="exact")
    eg = auditor.exact_grads(audit_rows, sink_ids)
    agree = all(
        eg[i] == Fraction(lat3.cells[i].grad.num, lat3.cells[i].grad.den)
        for i in range(len(lat3.cells)))
    print(f"  5. auditor bridge: mode=exact nodes={rep.n_nodes} "
          f"drift mean={rep.mean:.1e} CI95=[{rep.ci95[0]:.1e},{rep.ci95[1]:.1e}] "
          f"exact-grad agreement = {agree}")
    assert agree and rep.mean == 0.0

    # 6. twist is a guest op ---------------------------------------------------
    latt = build_abc()[0]
    cell_a = latt.cells[0]
    sh = twist(cell_a, 5)
    rows_t = lt.lattice_rows(latt)
    print(f"  6. twist: a={cell_a.value} shadow S=1-R={sh.value} "
          f"(exact {sh.value == Q16(cell_a.value.den - cell_a.value.num, cell_a.value.den)}); "
          f"TWIST rows on tape = {sum(1 for r in rows_t if r['t'] == 'TWIST')} (guest op, 0 by design)")
    assert sh.value == Q16(1, 1) - cell_a.value
    assert all(r["t"] in ("BIND", "LINK") for r in rows_t)

    print("Demo F OK — fused substrate: exact values, hash-chained evidence,")
    print("legal cycles, zero-drift auditor bridge, twist as guest.")


if __name__ == "__main__":
    main()
