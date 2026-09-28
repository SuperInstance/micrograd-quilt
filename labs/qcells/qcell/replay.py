"""qcell.replay — re-execute a witness ledger, prove it or refuse it.

Replay > trust: rebuild every row from its args, recompute each
per-gate state witness, re-sample every WORLD with its named seed, and
verify the prev_hash chain. Anything that disagrees is reported by
seq — never silently skipped.
"""
from __future__ import annotations

import json
import random

import micromoth
from qcell.emit import (Row, _canon, circuit_to_program, fnv1a64,
                        program_to_circuit, sv_digest)


def _rebind(row: dict) -> str:
    body = {"args": row["args"], "cell": row["cell"], "op": row["op"],
            "prev_hash": row["prev_hash"], "seq": row["seq"]}
    return fnv1a64(_canon(body))


def replay_ledger(path: str) -> dict:
    rows = [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    errors = []
    prev = "0" * 16
    ticker = 0
    prog = None
    n = m = 0
    for row in rows:
        if row["prev_hash"] != prev:
            errors.append(f"seq {row['seq']}: prev_hash {row['prev_hash']} != {prev}")
        if row["hash"] != _rebind(row):
            errors.append(f"seq {row['seq']}: hash mismatch on canonical body")
        prev = row["hash"]

        if row["op"] == "BIND":
            prog = row["args"]["program"]
            n, m = row["args"]["n"], row["args"]["m"]
            if row["cell"] != fnv1a64(_canon({"kind": row["args"]["kind"],
                                              "program": prog})):
                errors.append(f"seq {row['seq']}: BIND cell id mismatch")
        elif row["op"] == "EFFECT":
            ticker += 1
            if row["args"]["ticker"] != ticker:
                errors.append(f"seq {row['seq']}: ticker jump {ticker} -> {row['args']['ticker']}")
            prefix = program_to_circuit(prog[:ticker], n)
            sv = micromoth.simulate(prefix, get="statevector")
            live = sv_digest(sv)
            if live != row["witness"]["state_sha256"]:
                errors.append(f"seq {row['seq']}: state witness drift")
        elif row["op"] == "TICK":
            if row["args"]["ticker"] != ticker:
                errors.append(f"seq {row['seq']}: TICK ticker != effect ticker")
        elif row["op"] == "WORLD":
            if row["args"]["seed"] is None:
                errors.append(f"seq {row['seq']}: UNSEALED WORLD row refused")
            random.seed(row["args"]["seed"])
            qc = program_to_circuit(prog, n, m)
            counts = micromoth.simulate(qc, shots=row["args"]["shots"], get="counts")
            live = dict(sorted(counts.items()))
            if live != row["witness"]["counts"]:
                errors.append(f"seq {row['seq']}: WORLD histogram not reproduced")
    return {"ok": not errors, "rows": len(rows), "errors": errors,
            "head": prev}
