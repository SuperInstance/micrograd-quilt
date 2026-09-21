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
from .lattice_engine import Q16, Lattice, Cell

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


def replay_lattice(rows, evaluate=True, resolution=None, max_sweeps=10_000):
    """Rebuild a Lattice from BIND/LINK rows (quilt.tape replay analogue).
    Returns (lattice, cells_by_id). Values are exact by construction.

    Cycles are legal (Lane AK slice 2): a rewired cell's parents may carry
    HIGHER ids than the child, so a strict single pass can deadlock on
    mutual references. Rows whose parents are not yet built are deferred
    and resolved in a fixed-point loop; a remaining mutual cycle is wired
    directly (Cell.parents set post-construction, exactly what rewire()
    does live) with the forward fuel counters bumped by hand — fwd hop_cost
    for cyclic rows is recomputed from final placement. The k/s grid
    coordinates carried in the rows are restored onto the rebuilt cells so
    the replayed lattice occupies the same grid region (Q1 fidelity).

    resolution/max_sweeps pass through to Lattice.evaluate — cyclic graphs
    terminate at the resolution floor, so callers replaying cycles must
    pass the SAME resolution the original evaluated under (default exact
    zero stays correct for acyclic graphs)."""
    lat = Lattice()
    cells = {}
    deferred = []
    for r in rows:
        if r["t"] == "BIND":
            cells[r["id"]] = lat.scalar(r["q"][0], r["q"][1],
                                        tag=r.get("tag"))
        elif r["t"] == "LINK":
            if all(i in cells for i in r["p"]):
                ps = tuple(cells[i] for i in r["p"])
                if r["op"] == "QADD":
                    c = lat.qadd(ps[0], ps[1])
                elif r["op"] == "QMUL":
                    c = lat.qmul(ps[0], ps[1])
                else:
                    raise ValueError(f"replay_lattice: unknown op {r['op']!r}")
                c.tag = r.get("tag", c.tag)
                c.k, c.s = r.get("k", c.k), r.get("s", c.s)
                lat._layer_next_s[c.k] = max(
                    lat._layer_next_s.get(c.k, 0), c.s + 1)
                cells[r["id"]] = c
            else:
                deferred.append(r)
    # fixed-point pass: parents that exist by id but were placed later.
    for _ in range(len(rows) + 1):
        progressed = False
        still = []
        for r in deferred:
            if all(i in cells for i in r["p"]):
                ps = tuple(cells[i] for i in r["p"])
                if r["op"] == "QADD":
                    c = lat.qadd(ps[0], ps[1])
                elif r["op"] == "QMUL":
                    c = lat.qmul(ps[0], ps[1])
                else:
                    raise ValueError(f"replay_lattice: unknown op {r['op']!r}")
                c.tag = r.get("tag", c.tag)
                c.k, c.s = r.get("k", c.k), r.get("s", c.s)
                lat._layer_next_s[c.k] = max(
                    lat._layer_next_s.get(c.k, 0), c.s + 1)
                cells[r["id"]] = c
                progressed = True
            else:
                still.append(r)
        deferred = still
        if not deferred:
            break
    # mutual cycles: direct wiring (the rewire() path), fuel bumped by hand.
    for r in deferred:
        if r["op"] not in ("QADD", "QMUL"):
            raise ValueError(f"replay_lattice: unknown op {r['op']!r}")
        c = Cell(lat, 0, 0, r.get("tag", "cyc"), r["op"], ())
        lat.cells.append(c)
        if r["op"] == "QADD":
            lat.fuel.fwd_adds += 1
        else:
            lat.fuel.fwd_muls += 1
        cells[r["id"]] = c
    for r in deferred:
        c = cells[r["id"]]
        ps = tuple(cells[i] for i in r["p"])
        c.parents = ps
        if ps:
            c.k = min(c.k, max(p.k for p in ps) + 1)
            for p in ps:
                lat.fuel.hop_cost += abs(c.k - p.k)
        c.k, c.s = r.get("k", c.k), r.get("s", c.s)
        lat._layer_next_s[c.k] = max(
            lat._layer_next_s.get(c.k, 0), c.s + 1)
    if evaluate:
        lat.evaluate(max_sweeps=max_sweeps, resolution=resolution)
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
    """Verify (rows, fuel) and check recorded fusion VIEW rows.
    Multi-fusion safe (Lane AK slice 2): each fuse VIEW is checked at ITS
    position — payload = {tip: chain tip just before that VIEW, fuel}. A
    tape may carry several sinks' attestations; each matches (or fails)
    independently. Any spine break (tampered row, broken chain) fails all.
    Returns (ok, fuse_hash): ok=False on any tape OR fuel tamper; the
    returned fuse_hash is the first VIEW this fuel attests."""
    h = tape.fnv1a_64(tape.Tape.GENESIS)
    fuse_hash = None
    ok = True
    for r in rows:
        if r.get("prev") != h or tape.fnv1a_64(tape._canon(
                {k: v for k, v in r.items() if k != "hash"})) != r["hash"]:
            return False, None
        if r["t"] == "VIEW" and "fuse" in r:
            payload = {"tip": h, "fuel": fuel.canonical()}
            hh = tape.fnv1a_64(json.dumps(payload, sort_keys=True,
                                          separators=(",", ":")))
            if hh == r["fuse"] and fuse_hash is None:
                fuse_hash = hh
        h = r["hash"]
    return fuse_hash is not None, fuse_hash
