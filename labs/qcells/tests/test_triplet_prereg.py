"""FAIL-first pins: exp036 triplet-gate pre-registration seal.

Pins trip RED on:
  - family arithmetic drift (C(24,3) / gate / family size)
  - guard failure against sealed 24-stream tables
  - rerun digest instability (non-determinism or unsealed edit)
  - a real-data triplet statistic sneaking into the seal
    (any per-triplet observed count would break the pre-registration)
  - closure statement missing (triplets = last analytic rung)

Run: python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import json
import math
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "experiments"))

import exp036_triplet_joint_gates_prereg as exp036  # noqa: E402

RESULTS = os.path.join(HERE, "experiments", "exp036.results.json")


class TestTripletPrereg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(RESULTS) as f:
            cls.results = json.load(f)

    def test_01_family_arithmetic(self):
        self.assertEqual(exp036.M_TRIPLETS, 2024)          # C(24,3)
        self.assertEqual(exp036.M_TESTS, 8096)             # 2024 x 4
        self.assertEqual(exp036.TESTS_PER_TRIPLET, 4)
        self.assertAlmostEqual(exp036.G, 0.05 / 8096,
                               places=15)
        self.assertAlmostEqual(
            self.results["q1_family_size"]["gate"], 0.05 / 8096,
            places=15)
        self.assertEqual(self.results["q1_family_size"]["m_tests"],
                         8096)

    def test_02_guards_green(self):
        self.assertTrue(self.results["guard_ok"])
        for sid, g in self.results["guards"].items():
            for metric, entry in g.items():
                self.assertTrue(entry[2],
                                f"{sid}.{metric} drifted: {entry}")

    def test_03_rerun_digest_stable(self):
        with tempfile.TemporaryDirectory() as td:
            dest = os.path.join(td, "exp036.results.json")
            exp036.main(dest=dest)
            with open(dest) as f:
                rerun = json.load(f)
        self.assertEqual(rerun["rerun_digest"],
                         self.results["rerun_digest"])

    def test_04_no_real_triplet_statistic(self):
        # the seal must contain NO observed triplet counts — only
        # expectations under the sealed null and labeled design
        # power.  Any key suggesting observed triplet data trips.
        blob = json.dumps(self.results).lower()
        for banned in ("\"h_tri\"", "\"observed_triplet\"",
                       "\"triplet_counts\"", "\"would_trip\""):
            self.assertNotIn(banned, blob)
        q1 = self.results["q1_family_size"]
        self.assertGreater(q1["expected_null_trips_probe_A"], 0.0)
        self.assertGreaterEqual(q1["expected_null_trips_probe_B"],
                                0.0)
        # probe-B silence at census-n margins: exact expectation
        # must be far below the design-hot trip probability, and
        # tiny in absolute terms (Fisher structurally silent here)
        self.assertLess(q1["expected_null_trips_probe_B"], 1e-4)

    def test_05_closure_sealed(self):
        prereg = self.results["preregistration"]
        self.assertIn("exhaustive C(24,3)=2024", prereg)
        self.assertIn("no real-data triplet statistic is computed",
                      prereg)
        closure = self.results["sealed_design"]["closure"]
        self.assertIn("no quadruples", closure)
        self.assertIn("new telemetry", closure)


if __name__ == "__main__":
    unittest.main()
