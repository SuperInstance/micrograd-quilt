"""Tension-face doc pins: the exp029-vs-exp033/exp035 synthesis doc must
quote its receipts exactly. FAIL-first: doc absent or quote drifted -> red.

No new statistics are computed here; this guards the laundering risk that
someone cites one verdict without the other (the doc's own warning).
"""
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "TENSION-exp029-vs-exp033-035.md"


def _load(name):
    with open(ROOT / "experiments" / name) as f:
        return json.load(f)


class TensionDocPins(unittest.TestCase):
    def test_doc_exists_and_names_both_faces(self):
        self.assertTrue(DOC.exists(), "tension-face doc missing")
        text = DOC.read_text()
        self.assertIn("SHARED-HAZARD-REFUTED", text)
        self.assertIn("ALL-SHARE-W_HAT RETAINED", text)
        self.assertIn("FAMILY-PAIR-HAZARD RETAINED", text)

    def test_exp029_pooled_p_matches_receipt(self):
        text = DOC.read_text()
        p = _load("exp029.results.json")["sealed_decision"]["exact_conditional_deviance_p"]
        self.assertIn(f"{p:.6g}", text)

    def test_exp033_gate_and_hazard_match_receipt(self):
        text = DOC.read_text()
        fam = _load("exp033.results.json")["family_of_24"]
        self.assertIn(f"{fam['null_hazard']:.6g}", text)
        self.assertAlmostEqual(fam["gate"], 0.05 / 24)
        self.assertIn("0.05/24", text)

    def test_exp035_numbers_match_receipt(self):
        text = DOC.read_text()
        d = _load("exp035.results.json")
        self.assertEqual(d["trips_probe_a"], [])
        self.assertEqual(d["trips_probe_b"], [])
        self.assertIn(f"{d['closest_probe_a']['p']:.6g}", text)
        self.assertIn(f"{d['closest_probe_b']['p']:.6g}", text)
        self.assertIn("15/3078", text)

    def test_no_unsealed_new_statistics(self):
        # The doc must not contain a p-value that appears in no receipt.
        text = DOC.read_text()
        allowed = set()
        for name in ("exp029.results.json", "exp033.results.json",
                     "exp035.results.json"):
            allowed.update(
                f"{float(v):.6g}" for v in re.findall(
                    r"0\.\d+",
                    json.dumps(_load(name)))
            )
        for m in re.findall(r"0\.\d+", text):
            self.assertIn(f"{float(m):.6g}", allowed,
                          f"doc quotes unsealed statistic {m}")

    def test_open_decisions_named(self):
        text = DOC.read_text()
        self.assertIn("Casey", text)
        self.assertIn("block F", text)


if __name__ == "__main__":
    unittest.main()
