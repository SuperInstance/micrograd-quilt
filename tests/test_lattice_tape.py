"""tests/test_lattice_tape.py — fused substrate: tape/auditor ⊕ lattice grid.

Lane AK slice 1. Covers: lattice→tape projection with hash-chain integrity,
replay reproducing exact forward values, fuel↔tape fusion determinism +
tamper evidence, and exact lattice backward as the auditor's ground truth.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quilt import tape  # noqa: E402
from quilt.lattice_engine import Lattice, Q16  # noqa: E402
from quilt import lattice_tape as lt  # noqa: E402


def build_lat():
    """(a+b)*c with exact rationals; y sink at (k=2, s=0)."""
    lat = Lattice()
    a = lat.parameter(3, 2, tag="a")       # 3/2
    b = lat.scalar(1, 3, tag="b")          # 1/3
    c = lat.parameter(-5, 7, tag="c")      # -5/7
    y = (a + b) * c
    lat.evaluate()
    return lat, a, b, c, y


class TestLatticeTape(unittest.TestCase):
    def test_tape_chain_verifies(self):
        lat, *_ = build_lat()
        t = lt.tape_lattice(lat)
        self.assertEqual(t.verify(), (True, None))
        kinds = [r["t"] for r in t.rows]
        self.assertEqual(kinds.count("BIND"), 3)
        self.assertEqual(kinds.count("LINK"), 2)

    def test_bind_carries_exact_rational_not_float(self):
        lat, *_ = build_lat()
        rows = lt.lattice_rows(lat)
        bind_q = {r["tag"]: r["q"] for r in rows if r["t"] == "BIND"}
        self.assertEqual(bind_q["a"], [3, 2])
        self.assertEqual(bind_q["b"], [1, 3])
        self.assertNotIn("data", rows[0])  # float field must not appear

    def test_replay_reproduces_values_exactly(self):
        lat, a, b, c, y = build_lat()
        rows = lt.lattice_rows(lat)
        lat2, cells = lt.replay_lattice(rows)
        expect = [c.value for c in lat.cells]
        got = [c.value for c in lat2.cells]
        self.assertEqual(expect, got)
        # hand-check (3/2 + 1/3) * (-5/7) = (11/6)*(-5/7) = -55/42
        self.assertEqual(y.value, Q16(-55, 42))
        self.assertEqual(cells[4].value, Q16(-55, 42))

    def test_replayed_rows_rechain_and_tamper_evident(self):
        lat, *_ = build_lat()
        t = lt.tape_lattice(lat)
        self.assertEqual(t.verify(), (True, None))
        # planted tamper: flip one BIND numerator → chain names row 1
        t.rows[1]["q"] = [999, 1]
        ok, idx = t.verify()
        self.assertFalse(ok)
        self.assertEqual(idx, 1)

    def test_fuse_receipt_deterministic_and_recorded(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        t = lt.tape_lattice(lat)
        h1 = lt.fuse_receipt(t, fuel)
        self.assertEqual(t.verify(), (True, None))   # VIEW row chained
        lat_b, *_ = build_lat()
        fuel_b = lat_b.backward(lat_b.cells[-1])
        t_b = lt.tape_lattice(lat_b)
        h2 = lt.fuse_receipt(t_b, fuel_b)
        self.assertEqual(h1, h2)                     # same build → same fuse

    def test_fusion_tamper_evidence_both_sides(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        t = lt.tape_lattice(lat)
        h = lt.fuse_receipt(t, fuel)
        rows = list(t.rows)
        ok, _ = lt.verify_fusion(rows, fuel)
        self.assertTrue(ok)
        # tamper fuel: sweeps bumped → fusion must fail
        fuel.sweeps += 1
        ok, _ = lt.verify_fusion(rows, fuel)
        self.assertFalse(ok)
        # tamper tape: mutate a LINK parent list → fusion must fail
        fuel.sweeps -= 1
        for r in rows:
            if r["t"] == "LINK":
                r["p"] = list(reversed(r["p"]))
                break
        ok, _ = lt.verify_fusion(rows, fuel)
        self.assertFalse(ok)

    def test_lattice_backward_exact_vs_hand_computed(self):
        """d((a+b)*c)/da = c, /db = c, /dc = a+b — exact q16 ground truth,
        the auditor's role on the fused substrate (no float drift exists)."""
        lat, a, b, c, y = build_lat()
        fuel = lat.backward(y)
        self.assertEqual(a.grad, Q16(-5, 7))
        self.assertEqual(b.grad, Q16(-5, 7))
        self.assertEqual(c.grad, Q16(11, 6))
        self.assertEqual(y.grad, Q16(1, 1))
        self.assertEqual(fuel.residual, Q16(0, 1))  # exact convergence

    def test_fuel_counts_forward_ops(self):
        lat, *_ = build_lat()
        self.assertEqual(lat.fuel.fwd_adds, 1)  # a+b
        self.assertEqual(lat.fuel.fwd_muls, 1)  # *c
        self.assertGreater(lat.fuel.hop_cost, 0)


if __name__ == "__main__":
    unittest.main()
