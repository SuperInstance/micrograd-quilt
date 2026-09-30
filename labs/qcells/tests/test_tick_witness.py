"""FAIL-first pins: stepper bit-identity, TICK witness, O(gates) sims.

Run: python -m unittest discover -s tests -v   (or python tests/test_tick_witness.py)

Pins trip RED on:
  - stepper drift vs micromoth.simulate per-gate prefixes
  - TICK rows missing their statevector witness (PROOF at a tick)
  - replay not catching a tampered TICK witness
  - legacy ledgers (pre-TICK-witness) breaking under new replay
  - emit re-running prefix simulations (O(gates^2) regression)
"""
from __future__ import annotations

import json
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import micromoth
import qcell.emit as emit
import qcell.replay as replay
from qcell import stepper
from micromoth import QuantumCircuit


def _random_prog(rng, n, g):
    prog = []
    singles = ['x', 'h', 'rx', 'rz']
    twos = ['cx', 'swap', 'crx']
    for _ in range(g):
        if n > 1 and rng.random() < 0.4:
            op = rng.choice(twos)
            s, t = rng.sample(range(n), 2)
            if op == 'swap':
                prog.append((op, s, t))
            elif op == 'cx':
                prog.append((op, s, t))
            else:
                prog.append((op, rng.choice([0.25, 0.5, 0.75, 1.0]), s, t))
        else:
            op = rng.choice(singles)
            q = rng.randrange(n)
            if op in ('rx', 'rz'):
                prog.append((op, rng.choice([0.25, 0.5, 0.75, 1.0]), q))
            else:
                prog.append((op, q))
    return prog


class StepperIdentity(unittest.TestCase):
    def test_walk_bit_identical_to_prefix_simulate(self):
        rng = random.Random(20260928)
        for trial in range(25):
            n = rng.choice([1, 2, 3])
            prog = [list(t) for t in _random_prog(rng, n, rng.randint(1, 12))]
            walked = [ [list(e) for e in sv] for sv in stepper.walk(prog, n) ]
            self.assertEqual(len(walked), len(prog))
            for t in range(1, len(prog) + 1):
                qc = QuantumCircuit(n)
                qc.data = [tuple(x) for x in prog[:t]]
                ref = micromoth.simulate(qc, get="statevector")
                self.assertEqual(walked[t - 1], ref, f"trial {trial} ticker {t}")

    def test_stepper_init_and_measure(self):
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.measure(0, 0)
        prog = emit.circuit_to_program(qc)
        walked = list(stepper.walk(prog, 1))
        self.assertEqual(len(walked), 2)  # measure is a walked no-op
        ref = micromoth.simulate(qc, get="statevector")
        self.assertEqual(walked[-1], ref)

    def test_stepper_unsupported_gate_refused(self):
        with self.assertRaises(ValueError):
            stepper.apply_gate(stepper.zero_state(1), ('foo', 0), 1)


class TickWitness(unittest.TestCase):
    def _emit(self, n=2, gates=6):
        rng = random.Random(7)
        qc = QuantumCircuit(n)
        qc.data = [tuple(t) for t in _random_prog(rng, n, gates)]
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "ledger.jsonl")
        head = emit.emit_ledger(qc, seed=11, shots=64, path=path)
        rows = [json.loads(l) for l in open(path) if l.strip()]
        return rows, path, head

    def test_tick_rows_carry_state_witness(self):
        rows, _, _ = self._emit()
        ticks = [r for r in rows if r["op"] == "TICK"]
        effects = [r for r in rows if r["op"] == "EFFECT"]
        self.assertTrue(ticks, "no TICK rows emitted")
        for t in ticks:
            self.assertIn("witness", t, "TICK row carries no statevector witness")
            self.assertIn("state_sha256", t["witness"])
        # TICK witness is the PROOF of the same state its EFFECT asserted
        for t, e in zip(ticks, effects):
            self.assertEqual(t["witness"]["state_sha256"],
                             e["witness"]["state_sha256"])

    def test_replay_verifies_tick_witness(self):
        rows, path, _ = self._emit()
        with open(path, "w") as fh:
            for r in rows:
                if r["op"] == "TICK":
                    r["witness"]["state_sha256"] = "0" * 64
                fh.write(json.dumps(r, sort_keys=True) + "\n")
        res = replay.replay_ledger(path)
        self.assertFalse(res["ok"])
        self.assertTrue(any("TICK" in e or "witness" in e for e in res["errors"]),
                        f"replay errors must name the TICK witness: {res['errors']}")

    def test_legacy_ledger_without_tick_witness_still_replays(self):
        ledger = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "ledgers", "exp001-champion.jsonl")
        if not os.path.exists(ledger):
            self.skipTest("legacy champion ledger absent")
        res = replay.replay_ledger(ledger)
        self.assertTrue(res["ok"], f"legacy ledger broke: {res['errors']}")

    def test_emit_is_single_simulation(self):
        orig = micromoth.simulate
        calls = {"n": 0}
        def counting(qc, **kw):
            calls["n"] += 1
            return orig(qc, **kw)
        emit.micromoth.simulate = counting
        try:
            self._emit(n=2, gates=10)
        finally:
            emit.micromoth.simulate = orig
        # exactly ONE simulation total: the WORLD sampling. No per-gate
        # prefixes — the O(gates^2) shape must never return.
        self.assertEqual(calls["n"], 1)


if __name__ == "__main__":
    unittest.main()
