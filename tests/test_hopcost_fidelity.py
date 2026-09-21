"""tests/test_hopcost_fidelity.py — Lane AK slice 4 on the fused substrate.

hop_cost historical fidelity for cyclic rows. Slice 2 charged cyclic
rows from a transient min-adjusted k the replayed cell never occupied
(measured on the canonical cycle fixture: live ledger hop_cost=5,
replay charged 0) — so a WAL replay could not re-derive the receipt a
live run had fused into a VIEW row. Slice 4 law: the replayed receipt
is a pure function of the ROWS.

  hop_cost = Σ over LINK rows of Σ_p |row.k − parent_row.k|
  fwd_adds/fwd_muls = one per LINK row (by op)

Acceptance rows:
  1. acyclic graphs — replayed fuel equals the live engine's receipt
     EXACTLY (the row-derived hop coincides with construction-time
     accounting when no rewire moved any k).
  2. cyclic graphs — replayed hop is row-faithful (fixture: s@k=1 over
     h@k=0,c2@k=0 → 2; h@k=0 over s@k=1,half@k=0 → 1; total 3),
     deterministic across replays, and a fusion recorded against the
     REPLAYED receipt verifies from rows alone.
  3. honesty — the live ledger charges the dropped successor h2 (3 hop)
     but never the rewired h (rewire bumps no fuel); the row-faithful
     ledger charges h (1 hop) but h2 left no row. Net: op counts agree,
     hop differs by 2 — off-tape construction history, stated not hidden.
     The tape's receipt is the durable one.
  4. tamper — editing a row's recorded k changes the replayed receipt,
     so a k-tampered tape can never re-derive the original fusion.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quilt import lattice_tape as lt  # noqa: E402
from quilt.lattice_engine import Q16, SCALE  # noqa: E402


def build_cycle_lat():
    """The canonical cycle pattern (placeholder + rewire, successor
    dropped before taping) — same construction as demos/demo_fused.py."""
    from quilt.lattice_engine import Lattice
    lat = Lattice()
    c2 = lat.scalar(2, 1, tag="c2")
    half = lat.scalar(1, 2, tag="half")
    h = lat.placeholder(tag="h")
    s = lat.qadd(h, c2)
    h2 = lat.qmul(s, half)
    lat.rewire(h, "QMUL", (s, half))
    lat.cells.remove(h2)
    return lat, h


def build_abc_lat():
    """Plain acyclic (a+b)*c."""
    from quilt.lattice_engine import Lattice
    lat = Lattice()
    a = lat.parameter(3, 2, tag="a")
    b = lat.scalar(1, 3, tag="b")
    c = lat.parameter(-5, 7, tag="c")
    lat.evaluate()
    return lat, a, b, c


class TestAcyclicFuelEquality(unittest.TestCase):
    def test_replay_receipt_equals_live_receipt_acyclic(self):
        lat, *_ = build_abc_lat()
        t = lt.tape_lattice(lat)
        lat2, _ = lt.replay_lattice(list(t.rows))
        self.assertEqual(lat2.fuel.canonical(), lat.fuel.canonical())


class TestCyclicRowFaithfulHop(unittest.TestCase):
    def test_replay_hop_is_row_faithful(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        rows = list(t.rows)
        # fixture accounting, from the recorded k coordinates:
        #   s  = QADD @k=1 over h@k=0, c2@k=0  -> |1-0| + |1-0| = 2
        #   h  = QMUL @k=0 over s@k=1, half@k=0 -> |0-1| + |0-0| = 1
        row_k = {r["id"]: r["k"] for r in rows}
        links = [r for r in rows if r["t"] == "LINK"]
        expect = sum(abs(r["k"] - row_k[i]) for r in links for i in r["p"])
        self.assertEqual(expect, 3)
        lat2, _ = lt.replay_lattice(rows, resolution=Q16(1, SCALE))
        self.assertEqual(lat2.fuel.hop_cost, expect)
        self.assertEqual(lat2.fuel.fwd_adds, 1)
        self.assertEqual(lat2.fuel.fwd_muls, 1)

    def test_replay_receipt_is_deterministic(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        rows = list(t.rows)
        r1, _ = lt.replay_lattice(rows, resolution=Q16(1, SCALE))
        r2, _ = lt.replay_lattice(rows, resolution=Q16(1, SCALE))
        self.assertEqual(r1.fuel.canonical(), r2.fuel.canonical())

    def test_fusion_against_replayed_receipt_verifies_from_rows(self):
        """The WAL promise: rows alone re-derive the receipt that was
        fused — for cyclic graphs too (the slice-2 gap)."""
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        lat2, _ = lt.replay_lattice(list(t.rows), resolution=Q16(1, SCALE))
        lt.fuse_receipt(t, lat2.fuel)
        ok, fuse_hash = lt.verify_fusion(list(t.rows), lat2.fuel)
        self.assertTrue(ok)
        self.assertIsNotNone(fuse_hash)


class TestLiveExcessIsOffTapeHistory(unittest.TestCase):
    def test_live_ledger_counts_dropped_successor(self):
        """Honesty row: the live receipt differs from the row-derived
        receipt by exactly the off-tape construction history, STATED NOT
        PAPERED: the live ledger charges the dropped successor h2
        (QMUL @k=2 over s@k=1, half@k=0 -> 3 hop) but never charges the
        rewired h (rewire() bumps no fuel — engine law, vendored
        unmodified); the row-faithful ledger charges h (1 hop: |0-1|+|0-0|)
        but h2 left no row. Net: op counts agree (1 add / 1 mul both
        sides); hop differs by 3 - 1 = 2. The tape's receipt is the
        durable, re-derivable one."""
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        live = lat.fuel
        t = lt.tape_lattice(lat)
        lat2, _ = lt.replay_lattice(list(t.rows), resolution=Q16(1, SCALE))
        row_faithful = lat2.fuel
        self.assertEqual(live.hop_cost - row_faithful.hop_cost, 2)
        self.assertEqual(live.fwd_muls, row_faithful.fwd_muls)
        self.assertEqual(live.fwd_adds, row_faithful.fwd_adds)


class TestKTamperBreaksReDerivation(unittest.TestCase):
    def test_k_tamper_changes_replayed_receipt(self):
        lat, h = build_cycle_lat()
        lat.evaluate(resolution=Q16(1, SCALE))
        t = lt.tape_lattice(lat)
        rows = list(t.rows)
        good, _ = lt.replay_lattice(rows, resolution=Q16(1, SCALE))
        tampered = [dict(r) for r in rows]
        link = next(r for r in tampered if r["t"] == "LINK")
        link["k"] = link["k"] + 5  # move one op's recorded layer
        bad, _ = lt.replay_lattice(tampered, resolution=Q16(1, SCALE))
        self.assertNotEqual(good.fuel.canonical(), bad.fuel.canonical())


if __name__ == "__main__":
    unittest.main()
