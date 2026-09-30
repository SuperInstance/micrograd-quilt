"""qcell.emit — micromoth_emit v1: circuit -> witness ledger (JSONL).

Implements the choreography both CELL-MAPPING receipts specify:
  BIND  program cell (fnv1a-64 id over the canonical encoding)
  EFFECT one row per gate application, sha256 state witness per gate
  TICK   monotonic clock, one per gate (ticker lives here, not in the
         payload — x.x returns the state; the clock never returns)
  WORLD  seeded shot-sampling, seed + shots named in params (never
         UNSEALED: a seed is always present or the row is refused)
  PROOF  chain head over prev_hash linkage

Chain rows use the fleet WAL canonical key set
{args, cell, hash, op, prev_hash, seq} — same shape as every other
fleet ledger, so replay tooling crosses over.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field

import micromoth
from micromoth import QuantumCircuit

from qcell import stepper

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK64 = (1 << 64) - 1


def fnv1a64(data: bytes) -> str:
    h = FNV_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return f"{h:016x}"


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sv_digest(sv) -> str:
    """sha256 over the raw statevector pairs — the PROOF witness form."""
    return hashlib.sha256(_canon([[round(re_, 12), round(im, 12)] for re_, im in sv])).hexdigest()


@dataclass
class Row:
    op: str
    args: dict
    cell: str = ""
    seq: int = 0
    prev_hash: str = "0" * 16
    hash: str = ""
    witness: dict = field(default_factory=dict)

    def seal(self) -> dict:
        body = {"args": self.args, "cell": self.cell, "op": self.op,
                "prev_hash": self.prev_hash, "seq": self.seq}
        self.hash = fnv1a64(_canon(body))
        out = dict(body)
        out["hash"] = self.hash
        if self.witness:
            out["witness"] = self.witness
        return out


def circuit_to_program(qc: QuantumCircuit) -> list:
    """Program tuples in simulator-executable arity (sugar already expanded
    at build time by the QuantumCircuit methods)."""
    prog = []
    for t in qc.data:
        prog.append(list(t))
    return prog


def program_to_circuit(prog: list, num_qubits: int, num_clbits: int = 0) -> QuantumCircuit:
    qc = QuantumCircuit(num_qubits, num_clbits)
    qc.data = [tuple(t) for t in prog]
    return qc


def emit_ledger(qc: QuantumCircuit, seed: int, shots: int, path: str,
                kind: str = "qc-program") -> dict:
    """Full witness ledger for one circuit run. Returns the head row."""
    rows = []
    seq = 0
    prog = circuit_to_program(qc)

    bind = Row(op="BIND", args={"kind": kind, "n": qc.num_qubits,
                                "m": qc.num_clbits, "program": prog}, seq=seq)
    bind.cell = fnv1a64(_canon({"kind": kind, "program": prog}))
    bind.witness = {"program_sha256": hashlib.sha256(_canon(prog)).hexdigest()}
    rows.append(bind.seal())
    seq += 1

    prev = rows[-1]["hash"]
    for ticker, (gate, sv) in enumerate(zip(prog, stepper.walk(prog, qc.num_qubits)), start=1):
        row = Row(op="EFFECT", args={"gate": list(gate), "ticker": ticker},
                  cell=bind.cell, seq=seq, prev_hash=prev)
        row.witness = {"state_sha256": sv_digest(sv)}
        rows.append(row.seal())
        seq += 1
        prev = rows[-1]["hash"]
        tick = Row(op="TICK", args={"ticker": ticker}, cell=bind.cell,
                   seq=seq, prev_hash=prev)
        # PROOF statevector witness cell at a TICK: the clock row itself
        # asserts the statevector at that tick (single O(gates) walk via
        # qcell.stepper — per-gate prefix re-simulation would be
        # O(gates^2) and does not scale past n=4).
        tick.witness = {"state_sha256": sv_digest(sv)}
        rows.append(tick.seal())
        seq += 1
        prev = rows[-1]["hash"]

    random.seed(seed)
    counts = micromoth.simulate(qc, shots=shots, get="counts")
    world = Row(op="WORLD", args={"seed": seed, "shots": shots}, cell=bind.cell,
                seq=seq, prev_hash=prev)
    world.witness = {"counts": dict(sorted(counts.items()))}
    rows.append(world.seal())
    seq += 1

    proof = Row(op="PROOF", args={"rows": seq}, cell=bind.cell, seq=seq,
                prev_hash=rows[-1]["hash"])
    head = proof.seal()
    rows.append(head)

    with open(path, "a", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, sort_keys=True) + "\n")
    return head
