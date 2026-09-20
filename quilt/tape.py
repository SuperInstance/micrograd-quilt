"""quilt/tape.py — the 5-opcode WAL: BIND / LINK / EFFECT / VIEW / TICK
(+ FORGET for GC).

Design law 2, amended per critic ref M3-01 (MiniMax-M3 hostile review,
2026-09-21 ~01:10Z): the tape is (a) a determinism/regression guard — replay
reproduces live-graph gradients bitwise given the same seed and reduction
order, guarding regressions rather than asserting an abstraction — and (b)
the breeding genotype format (DESIGN.md 3), which is what justifies it.

Hash chain: FNV-1a 64, cited: Fowler/Noll/Vo, "FNV-1a hash function",
http://www.isthe.com/chongo/tech/comp/fnv/ — same as the fleet's other WALs.
"""

import json
import math
from contextlib import contextmanager

from . import engine

FNV_OFF = 14695981039346656037   # FNV-1a 64-bit offset basis (cited)
FNV_PRIME = 1099511628211        # FNV-1a 64-bit prime (cited)
_MASK64 = (1 << 64) - 1


def fnv1a_64(s):
    h = FNV_OFF
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * FNV_PRIME) & _MASK64
    return h


def _canon(row):
    """Canonical serialization: sorted keys, tight separators, ASCII.
    CPython's float repr is shortest-round-trip, hence deterministic."""
    return json.dumps(row, sort_keys=True, separators=(",", ":"))


@contextmanager
def attach(t):
    """Attach a Tape so engine ops append rows (engine._TAPE)."""
    global _T
    old, engine._TAPE = engine._TAPE, t
    try:
        yield t
    finally:
        engine._TAPE = old


class Tape:
    """Append-only hash-chained row log. Structural opcodes: BIND (new value),
    LINK (op + parents), EFFECT (local gradient contribution during backward),
    VIEW (drift-map state, written by comb/auditor), TICK (backward step
    boundary). FORGET (GC event) is the sixth, GC-extension row."""

    GENESIS = "QUILT-TAPE-v1"

    def __init__(self):
        self.rows = []
        self._hash = fnv1a_64(self.GENESIS)

    def _emit(self, row):
        row["prev"] = self._hash
        self._hash = row["hash"] = fnv1a_64(_canon(row))
        self.rows.append(row)
        return row

    # -- row emitters (called by engine / comb / auditor) -------------------
    def bind(self, v):
        return self._emit({"t": "BIND", "id": v.id, "data": v.data})

    def link(self, v):
        return self._emit({"t": "LINK", "id": v.id, "op": v._op,
                           "p": [p.id for p in v._parents]})

    def effect(self, node, parent, g, gt=None):
        row = {"t": "EFFECT", "node": node.id, "parent": parent.id, "g": g}
        if gt is not None:
            row["gt"] = [gt.numerator, gt.denominator]
        return self._emit(row)

    def tick(self, step, v):
        return self._emit({"t": "TICK", "step": step, "node": v.id})

    def view(self, node, **kw):
        return self._emit({"t": "VIEW", "node": node.id, **kw})

    def forget(self, before):
        return self._emit({"t": "FORGET", "before": before})

    def begin_backward(self):
        pass  # TICK rows carry step indices; no marker row needed

    # -- integrity -----------------------------------------------------------
    def verify(self):
        """Recompute the chain. Returns (ok, bad_row_index). The first
        surviving row's anchoring `prev` is waived when a FORGET row is
        present: the drop is committed on-chain by the FORGET row itself
        (it hashes the drop count). Everything from that anchor onward --
        every body, every link -- is recomputed and must match."""
        h = fnv1a_64(self.GENESIS)
        anchored = not any(r["t"] == "FORGET" for r in self.rows)
        for i, r in enumerate(self.rows):
            if (anchored or i > 0) and r.get("prev") != h:
                return False, i
            if i == 0 and not anchored:
                anchored = True
            if fnv1a_64(_canon({k: v for k, v in r.items() if k != "hash"})) \
                    != r["hash"]:
                return False, i
            h = r["hash"]
        return True, None

    def gc(self, before):
        """Drop rows[:before] — a PREFIX (e.g. stale forward rows after the
        graph is rebuilt). FORGET commits to the drop count on-chain."""
        assert 0 <= before <= len(self.rows), "gc: prefix drop only"
        del self.rows[:before]
        self.forget(before)


# -- replay -------------------------------------------------------------------
def _apply(row, vals):
    op, ps = row["op"], [vals[i] for i in row["p"]]
    if op == "+":
        return ps[0] + ps[1]
    if op == "*":
        return ps[0] * ps[1]
    if op.startswith("**"):
        return pow(ps[0], int(op[2:]))
    if op == "relu":
        return ps[0] if ps[0] > 0 else 0.0
    if op == "tanh":
        return math.tanh(ps[0])
    if op == "exp":
        return math.exp(ps[0])
    if op == "cos":
        return math.cos(ps[0])
    raise ValueError(f"replay: unknown op {op!r}")


def replay(rows, root=None, after_tick=None, upto_tick=None, init_grads=None):
    """Re-apply a tape's EFFECT rows to recover gradients, in row order —
    the same order the live backward accumulated them, hence bitwise-equal.

    root: sink id; seeds grads[root] = 1.0 (mirrors backward()).
    after_tick=k: apply only EFFECT rows after the k-th TICK (resume).
    upto_tick=k: apply EFFECT rows of the first k backward steps only
        (through the k-th TICK inclusive). The two legs complement:
        replay(upto=k) then replay(after=k, init=part) == replay(full).
    init_grads: starting gradient state for the resumed leg."""
    vals = {}
    grads = dict(init_grads or {})
    if root is not None:
        grads[root] = 1.0
    tick = 0
    live = after_tick is None
    for r in rows:
        t = r["t"]
        if t == "BIND":
            vals[r["id"]] = r["data"]
        elif t == "LINK":
            vals[r["id"]] = _apply(r, vals)
        elif t == "EFFECT":
            if live:
                grads[r["parent"]] = grads.get(r["parent"], 0.0) + r["g"]
        elif t == "TICK":
            tick += 1
            if upto_tick is not None and tick == upto_tick:
                break
            if after_tick is not None and tick == after_tick:
                live = True
    return grads
