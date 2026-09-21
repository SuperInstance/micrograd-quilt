"""tests/test_fuel_receipt_guard.py — Lane AK slice 3: the FuelReceipt
in-place-mutation guard (deepcopy discipline, enforced).

Closes the slice-2 documented hazard: backward() mutated lat.fuel IN PLACE
and returned it, so a second backward pass silently rewrote a receipt a
caller had already fused into a tape VIEW row. Slice 2 worked around it
with caller-side deepcopy + a comment; slice 3 makes the discipline law:

  1. issuance  — backward() freezes the receipt before returning; any
                 post-freeze write raises ReceiptFrozenError (ValueError).
  2. re-run    — a second backward() issues a FRESH receipt; the held one
                 stays frozen, unchanged, still attesting its own pass.
  3. build lock — fuel counters are bumped at op placement, so building
                 new cells after a backward would rewrite an attested
                 ledger: frozen fuel refuses; reset_fuel() opens a fresh
                 ledger explicitly.
  4. fusion    — fuse_receipt attests a snapshot's canonical string taken
                 ONCE; amending the live receipt afterward cannot desync
                 payload from recorded VIEW row. verify_fusion against the
                 amended receipt honestly FAILS (fuel tamper), against the
                 snapshot passes — every sink attests its own fuel.
"""

import os
import sys
import unittest
from copy import deepcopy

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quilt import lattice_tape as lt  # noqa: E402
from quilt.lattice_engine import (  # noqa: E402
    Lattice, Q16, ReceiptFrozenError,
)


def build_lat():
    """(a+b)*c with exact rationals; y sink at (k=2, s=0)."""
    lat = Lattice()
    a = lat.parameter(3, 2, tag="a")       # 3/2
    b = lat.scalar(1, 3, tag="b")          # 1/3
    c = lat.parameter(-5, 7, tag="c")      # -5/7
    y = (a + b) * c
    lat.evaluate()
    return lat, a, b, c, y


class TestIssuanceFreeze(unittest.TestCase):
    def test_backward_returns_frozen_receipt(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        self.assertTrue(fuel.frozen)

    def test_post_freeze_write_raises(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        for field_name in ("sweeps", "hop_cost", "residual"):
            with self.assertRaises(ReceiptFrozenError):
                setattr(fuel, field_name,
                        fuel.sweeps + 1 if field_name == "sweeps" else None)
        # ReceiptFrozenError is a ValueError — existing catch paths hold.
        with self.assertRaises(ValueError):
            fuel.grad_adds = 0

    def test_freeze_is_idempotent(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        self.assertIs(fuel.freeze(), fuel)
        self.assertTrue(fuel.frozen)

    def test_deepcopy_of_frozen_stays_frozen(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        clone = deepcopy(fuel)
        self.assertTrue(clone.frozen)
        with self.assertRaises(ReceiptFrozenError):
            clone.sweeps += 1
        # ...and the original is untouched by the copy's existence.
        self.assertTrue(fuel.frozen)


class TestReRunIssuesFreshReceipt(unittest.TestCase):
    def test_second_backward_leaves_first_receipt_valid(self):
        lat, a, b, c, y = build_lat()
        fuel_y = lat.backward(y)
        canon_y = fuel_y.canonical()
        hash_y = fuel_y.hash()
        # second pass on a different sink already in the graph: NEW receipt,
        # old one unchanged
        ab = next(cell for cell in lat.cells if cell.op == "QADD")
        fuel_ab = lat.backward(ab)
        self.assertIsNot(fuel_y, fuel_ab)
        self.assertTrue(fuel_ab.frozen)
        self.assertEqual(fuel_y.canonical(), canon_y)
        self.assertEqual(fuel_y.hash(), hash_y)

    def test_new_pass_is_not_accumulated_onto_old(self):
        lat, a, b, c, y = build_lat()
        fuel_y = lat.backward(y)
        lat.backward(y)  # identical re-run: fresh receipt, same numbers
        self.assertEqual(lat.fuel.sweeps, fuel_y.sweeps)
        self.assertEqual(lat.fuel.grad_adds, fuel_y.grad_adds)


class TestBuildLockAndReset(unittest.TestCase):
    def test_cell_construction_after_backward_refuses(self):
        lat, a, b, c, y = build_lat()
        lat.backward(y)
        # fuel counters bump at op placement — an attested ledger must not
        # be rewritten by new op construction. (LEAF placement touches no
        # fuel counter; QADD/QMUL do.)
        with self.assertRaises(ReceiptFrozenError):
            lat.cells[0] + lat.cells[1]

    def test_reset_fuel_opens_fresh_ledger(self):
        lat, a, b, c, y = build_lat()
        fuel_y = lat.backward(y)
        fresh = lat.reset_fuel()
        self.assertFalse(fresh.frozen)
        self.assertIs(lat.fuel, fresh)
        late = lat.scalar(1, 1, tag="late")  # now legal
        late.value = Q16(1, 1)
        # the attested receipt is still intact and still frozen
        self.assertTrue(fuel_y.frozen)
        self.assertGreater(fuel_y.sweeps, 0)


class TestFusionSnapshotDiscipline(unittest.TestCase):
    def test_fusion_uses_frozen_snapshot_canonical(self):
        lat, *_ = build_lat()
        fuel = lat.backward(lat.cells[-1])
        t = lt.tape_lattice(lat)
        f = lt.fuse_receipt(t, fuel)
        view = [r for r in t.rows if r["t"] == "VIEW" and "fuse" in r][-1]
        self.assertEqual(view["fuel"], fuel.canonical())
        # amend the live receipt honestly (thaw): the recorded VIEW row
        # keeps the attested string...
        fuel.thaw()
        fuel.sweeps += 1
        self.assertNotEqual(view["fuel"], fuel.canonical())
        # ...re-derivation against the amended receipt FAILS (fuel tamper)
        rows = list(t.rows)
        ok, _ = lt.verify_fusion(rows, fuel)
        self.assertFalse(ok)
        # ...against the pristine snapshot PASSES — the attestation names
        # its own pass, not whatever the ledger says now.
        lat2, *_ = build_lat()
        fuel2 = lat2.backward(lat2.cells[-1])
        ok2, f2 = lt.verify_fusion(rows, fuel2)
        self.assertTrue(ok2)
        self.assertEqual(f2, f)


if __name__ == "__main__":
    unittest.main()
