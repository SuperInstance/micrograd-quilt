"""tests/test_fused_slice2.py — Lane AK slice 2 on the fused substrate.

Covers the four slice-2 acceptance rows from the queue:
  1. cyclic replay — a placeholder+rewire cycle (h = (h+2)/2) survives the
     tape round-trip: rows chain, replay relaxes to the same fixed point at
     the resolution floor (exact zero is unreachable BY DESIGN of the
     codec — the orbit 1, 3/2, 7/4, ... approaches 2 asymptotically).
  2. twist rows — twist() cells are GUEST ops (twist law lives in
     twist-engine, not the substrate): they are projected out of the tape
     (0 TWIST rows), and the shadow value S = 1-R is exact in q16.
  3. multi-sink fusion — one tape, two sinks, two fuse VIEW rows; each
     receipt verifies independently, either side's tamper breaks only its
     own attestation.
  4. auditor bridge — the fleet auditor (quilt/auditor.py) runs over the
     taped lattice rows (q16 -> float display projection for BIND data,
     QADD/QMUL -> +/*); exact grads agree with the lattice relaxation
     backward to measured drift 0.0 (CI95 degenerate [0,0]).
"""

import os
import sys
import unittest
from copy import deepcopy
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quilt import auditor  # noqa: E402
from quilt import lattice_tape as lt  # noqa: E402
from quilt.lattice_engine import Q16, SCALE, Lattice, twist  # noqa: E402


def build_lat():
    """(a+b)*c with exact rationals; y sink at (k=2, s=0)."""
    lat = Lattice()
    a = lat.parameter(3, 2, tag="a")       # 3/2
    b = lat.scalar(1, 3, tag="b")          # 1/3
    c = lat.parameter(-5, 7, tag="c")      # -5/7
    y = (a + b) * c
    lat.evaluate()
    return lat, a, b, c, y


def build_cycle_lat():
    """h = (h+2) * 1/2 via placeholder + rewire: a mutual cycle."""
    lat = Lattice()
    c2 = lat.scalar(2, 1, tag="c2")
    half = lat.scalar(1, 2, tag="half")
    h = lat.placeholder(tag="h")
    s = lat.qadd(h, c2)
    h2 = lat.qmul(s, half)
    lat.rewire(h, "QMUL", (s, half))
    lat.cells.remove(h2)
    return lat, h


def auditor_rows(lat):
    """Project lattice rows into the fleet auditor's row vocabulary.
    The bridge must stay exact end to end: BIND data carries a Fraction
    (num, den) — the auditor's exact path calls Fraction(data), and a float
    here would smuggle binary rounding into the "exact" audit (measured:
    Fraction(float(-5/7)) drifts from -5/7 immediately). QADD/QMUL -> +/*.
    Ids and parent lists pass through unchanged. Rows carry the
    construction-index id; cells are looked up by id, never assumed."""
    return [
        {"t": "BIND", "id": r["id"], "data": Fraction(r["q"][0], r["q"][1])}
        if r["t"] == "BIND" else
        {"t": "LINK", "id": r["id"],
         "op": "+" if r["op"] == "QADD" else "*", "p": r["p"]}
        for r in lt.lattice_rows(lat)
    ]


class TestCyclicReplay(unittest.TestCase):
    def test_cycle_relaxes_to_fixed_point_live(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        # h = (h+2)/2 has fixed point 2; the q16 orbit approaches it
        # monotonically from below: 1, 3/2, 7/4, 15/8, ... The sweep stops
        # when the per-sweep delta <= resolution, so the residual distance
        # to the fixed point is at most 2*resolution (next delta = err/2).
        self.assertLessEqual(2.0 - h.value.to_float(), 2.0 / SCALE)
        self.assertGreater(h.value.to_float(), 1.0)
        # deterministic trajectory: relaxation halts at 2 - 2^-19
        self.assertEqual(h.value, Q16(1048575, 524288))

    def test_cyclic_replay_reproduces_fixed_point(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        self.assertEqual(t.verify(), (True, None))
        rows = list(t.rows)
        lat2, cells = lt.replay_lattice(rows, resolution=Q16(1, SCALE))
        # id 0 is c2 (construction index) — the rewired cell is found by id
        # from its row, not assumed. Same fixed point, exact same rational
        # (deterministic relaxation: rebuilt cells occupy the same list
        # order and grid coordinates as the live graph).
        hid = next(r["id"] for r in rows if r.get("tag") == "cyc[h]")
        self.assertEqual(cells[hid].value, h.value)
        self.assertEqual(cells[hid].value, Q16(1048575, 524288))
        self.assertEqual((cells[hid].k, cells[hid].s), (h.k, h.s))

    def test_cyclic_tamper_still_evident(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        t.rows[1]["q"] = [7, 1]  # plant: c2 was 2/1
        ok, idx = t.verify()
        self.assertFalse(ok)
        self.assertEqual(idx, 1)


class TestTwistRows(unittest.TestCase):
    def test_twist_is_guest_op_projected_out(self):
        lat, *_ = build_lat()
        sh = twist(lat.cells[0], 5)
        rows = lt.lattice_rows(lat)
        self.assertTrue(all(r["t"] in ("BIND", "LINK") for r in rows))
        # the twisted cell itself is not substrate: no row carries it
        self.assertNotIn("TWIST", {r.get("op") for r in rows})
        # ... and the shadow pairing is exact: S = 1 - R, in the codec
        self.assertEqual(sh.value, Q16(1, 1) - lat.cells[0].value)
        # replay of the substrate rows is unaffected by the guest cell
        lat2, cells2 = lt.replay_lattice(rows)
        self.assertEqual(cells2[len(cells2) - 1].value, Q16(-55, 42))

    def test_twist_is_exact_involution_pairing(self):
        lat, *_ = build_lat()
        a = lat.cells[0]  # 3/2
        sh = twist(a, 5)
        self.assertEqual(sh.value, Q16(-1, 2))  # 1 - 3/2
        # the pairing is total on the codec: R + S = 1 exactly
        self.assertEqual(a.value + sh.value, Q16(1, 1))


class TestMultiSinkFusion(unittest.TestCase):
    def test_two_sinks_two_fusions_one_tape(self):
        lat, a, b, c, y = build_lat()
        # second sink in the SAME graph: a*b (independent of c)
        ab = lat.cells[0] * lat.cells[1]
        lat.evaluate()
        t = lt.tape_lattice(lat)
        fuel_y = deepcopy(lat.backward(y))
        f_y = lt.fuse_receipt(t, fuel_y, node=y.k)
        # SLICE 3: backward() freezes its receipt at issuance and re-runs
        # issue FRESH receipts — the old "in-place rewrite" hazard is now
        # law-enforced (ReceiptFrozenError), not a caller-side comment.
        # deepcopy at capture stays as belt-and-suspenders.
        fuel_ab = deepcopy(lat.backward(ab))
        f_ab = lt.fuse_receipt(t, fuel_ab, node=ab.k)
        self.assertNotEqual(f_y, f_ab)
        self.assertEqual(t.verify(), (True, None))
        # each receipt verifies independently against its own view row
        # (dict copies: tampering below must not touch t.rows' shared dicts)
        rows = [dict(r) for r in t.rows]
        ok_y, hh_y = lt.verify_fusion(rows, fuel_y)
        ok_ab, hh_ab = lt.verify_fusion(rows, fuel_ab)
        self.assertTrue(ok_y)
        self.assertTrue(ok_ab)
        self.assertEqual(hh_y, f_y)
        self.assertEqual(hh_ab, f_ab)
        # tampering the tape breaks BOTH (the chain tip feeds every fuse)...
        for r in rows:
            if r["t"] == "LINK":
                r["p"] = list(reversed(r["p"]))
                break
        self.assertFalse(lt.verify_fusion(rows, fuel_y)[0])
        self.assertFalse(lt.verify_fusion(rows, fuel_ab)[0])
        # ...but a pure fuel tamper on one receipt only breaks its own
        # (slice 3: the frozen receipt refuses direct writes — honest
        # tamper simulation amends a thawed copy, same as the tape test)
        rows = [dict(r) for r in t.rows]
        fuel_ab_bad = deepcopy(fuel_ab)
        fuel_ab_bad.thaw()
        fuel_ab_bad.sweeps += 1
        self.assertTrue(lt.verify_fusion(rows, fuel_y)[0])
        self.assertFalse(lt.verify_fusion(rows, fuel_ab_bad)[0])


class TestAuditorBridge(unittest.TestCase):
    def test_exact_audit_zero_drift_vs_lattice_backward(self):
        lat, a, b, c, y = build_lat()
        fuel = lat.backward(y)
        rows = auditor_rows(lat)
        sink_ids = auditor.sinks(rows)
        float_grads = {i: lat.cells[i].grad.to_float()
                       for i in range(len(lat.cells))}
        rep = auditor.audit(rows, float_grads, sink_ids, mode="exact")
        # the fleet auditor's exact grads ARE the lattice's relaxation
        # grads — measured drift is exactly 0.0, CI degenerate
        self.assertEqual(rep.mode, "exact")
        self.assertEqual(rep.n_sampled, rep.n_nodes)
        self.assertEqual(rep.mean, 0.0)
        self.assertEqual(rep.ci95, (0.0, 0.0))
        eg = auditor.exact_grads(rows, sink_ids)
        for i, cell in enumerate(lat.cells):
            self.assertEqual(eg[i], Fraction(cell.grad.num, cell.grad.den))
        # hand-check: d((a+b)c)/da = c = -5/7 (exact ground truth)
        self.assertEqual(eg[0], Fraction(-5, 7))

    def test_bridge_bind_data_exact_not_float(self):
        """The bridge BIND rows must carry exact Fractions: the auditor's
        exact path computes Fraction(data), and a float input smuggles
        binary rounding into the 'exact' audit (measured: Fraction of the
        float nearest -5/7 is -6433713753386423/9007199254740992, not
        -5/7). The substrate rows underneath still carry exact q=[num,den]
        ints; no float identity anywhere in the pipeline."""
        lat, *_ = build_lat()
        bridge = auditor_rows(lat)
        self.assertTrue(all(isinstance(r["data"], Fraction)
                            for r in bridge if r["t"] == "BIND"))
        self.assertEqual(bridge[0]["data"], Fraction(3, 2))
        sub = lt.lattice_rows(lat)
        self.assertTrue(all("q" in r for r in sub if r["t"] == "BIND"))
        self.assertTrue(all("data" not in r for r in sub))


if __name__ == "__main__":
    unittest.main()
