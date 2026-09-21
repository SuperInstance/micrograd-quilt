"""quilt/lattice_tape.py — the fused substrate: tape/auditor ⊕ lattice grid.

Lane AK slice 1 (2026-09-21): the exact-rational lattice kernel
(quilt/lattice_engine.py, Lane AH³ residue vendored unmodified) gains a WAL
face. Every cell the lattice places is emitted onto a quilt Tape as
BIND (LEAF, exact q16 [num, den] — never a float) / LINK (QADD/QMUL, parent
ids + grid coordinate) rows, so the lattice's broadcast graph inherits the
fleet's hash-chain tamper evidence (design law 2). The FuelReceipt (law: Q3
energy accounting) is fused with the tape tip by FNV-1a over canonical JSON:
either side tampered — a row or a fuel field — breaks the fusion.

Framing matches the M3-01 amendment: this is a determinism/regression guard
and energy attestation, NOT an equivalence theorem.

Constants: FNV-1a 64 reused from quilt.tape (cited there: Fowler/Noll/Vo).
"""

import json

from . import tape
from .lattice_engine import Q16, Lattice

# cell identity on the tape = construction index (cells list order).
# Parents are always placed before their op child, so row order is a valid
# forward-topological encoding — the same property quilt.tape.replay relies on.


def lattice_rows(lat):
    """Project a evaluated/unevaluated Lattice to tape rows (unhashed dicts).

    LEAF → BIND with exact rational q=[num, den] (floats never appear);
    QADD/QMUL → LINK with parent ids and the (k, s) grid coordinate."""
    rows = []
    ids = {id(c): i for i, c in enumerate(lat.cells)}
    for i, c in enumerate(lat.cells):
        base = {"id": i, "k": c.k, "s": c.s, "tag": c.tag}
        if c.op == "LEAF":
            q = c._const if c._const is not None else c.value
            rows.append({"t": "BIND", **base, "q": [q.num, q.den]})
        elif c.op in ("QADD", "QMUL"):
            rows.append({"t": "LINK", **base, "op": c.op,
                         "p": [ids[id(p)] for p in c.parents]})
        # TWIST and other guest ops are not substrate ops; skip by design.
    return rows


def tape_lattice(lat, t=None):
    """Append a lattice's rows onto a Tape (hash-chained). Returns the tape.
    A VIEW row is NOT emitted here — fusion is explicit (fuse_receipt)."""
    if t is None:
        t = tape.Tape()
    for r in lattice_rows(lat):
        t._emit(r)
    return t


def replay_lattice(rows, evaluate=True):
    """Rebuild a Lattice from BIND/LINK rows (quilt.tape replay analogue).
    Returns (lattice, cells_by_id). Values are exact by construction."""
    lat = Lattice()
    cells = {}
    for r in rows:
        if r["t"] == "BIND":
            cells[r["id"]] = lat.scalar(r["q"][0], r["q"][1],
                                        tag=r.get("tag"))
        elif r["t"] == "LINK":
            ps = tuple(cells[i] for i in r["p"])
            if r["op"] == "QADD":
                cells[r["id"]] = lat.qadd(ps[0], ps[1])
            elif r["op"] == "QMUL":
                cells[r["id"]] = lat.qmul(ps[0], ps[1])
            else:
                raise ValueError(f"replay_lattice: unknown op {r['op']!r}")
            cells[r["id"]].tag = r.get("tag", cells[r["id"]].tag)
    if evaluate:
        lat.evaluate()
    return lat, cells


def fuse_receipt(t, fuel, node=None, record=True):
    """Fuse a Tape and a FuelReceipt into one attestation hash (FNV-1a 64).

    Payload = {tip: tape tip hash, fuel: fuel.canonical()}. Tampering with
    ANY tape row changes the tip (hash chain); tampering with ANY fuel field
    changes the canonical string; either breaks the fusion. If record=True,
    a VIEW row carrying fuse + fuel is emitted and chained — the attestation
    itself becomes part of the guarded log (verify() covers it)."""
    payload = {"tip": t._hash, "fuel": fuel.canonical()}
    h = tape.fnv1a_64(json.dumps(payload, sort_keys=True,
                                 separators=(",", ":")))
    if record:
        t._emit({"t": "VIEW", "node": -1 if node is None else node,
                 "fuse": h, "fuel": fuel.canonical()})
    return h


def verify_fusion(rows, fuel):
    """Verify (rows, fuel) and check the recorded fusion VIEW.
    The chain is verified IN PLACE (recomputing each row's hash with the
    hash field excluded — re-emission would double-hash the stored field);
    the attested tip is the chain tip over the pre-fusion VIEW spine.
    Returns (ok, fuse_hash): ok=False on any tape OR fuel tamper."""
    h = tape.fnv1a_64(tape.Tape.GENESIS)
    for r in rows:
        if r["t"] == "VIEW" and "fuse" in r:
            continue                       # fusion rows sit outside the spine
        if r.get("prev") != h or tape.fnv1a_64(tape._canon(
                {k: v for k, v in r.items() if k != "hash"})) != r["hash"]:
            return False, None
        h = r["hash"]
    payload = {"tip": h, "fuel": fuel.canonical()}
    hh = tape.fnv1a_64(json.dumps(payload, sort_keys=True,
                                  separators=(",", ":")))
    views = [r for r in rows if r["t"] == "VIEW" and r.get("fuse") == hh]
    return bool(views), hh
