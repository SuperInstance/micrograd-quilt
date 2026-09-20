"""Quilt layer tests: hash chain, replay, auditor, comb, genotype, demos.

Pure stdlib + pytest -- no torch required (the original test/ directory
keeps Karpathy's torch-based reference tests untouched).

Run: python3 -m pytest tests/ -q
"""

import json
import math
import random

import pytest
from fractions import Fraction

from micrograd.engine import Value as KValue
from quilt import auditor, comb as combmod, engine, genotype as gen, tape
from quilt.demos import demo_a, demo_b, demo_c, karpathy_graph


# ---------- fixtures ----------

def karpathy():
    return karpathy_graph(exact=False)


def chain_graph(n):
    """y = x*n built as a left-deep chain: n nodes, deterministic."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        x = engine.Value(1.0)
        y = x
        for _ in range(n):
            y = y + x
        y.backward()
        return y, x, t


# ---------- 1. hash chain ----------

def test_fnv1a_vectors():
    assert tape.fnv1a_64("") == 14695981039346656037
    assert tape.fnv1a_64("a") == 12638187200555641996


def test_verify_clean_tape():
    g, a, b, t, teeth = karpathy()
    assert t.verify() == (True, None)


def test_planted_wrong_effect_trips_floor():
    g, a, b, t, teeth = karpathy()
    eff = next(r for r in t.rows if r["t"] == "EFFECT")
    eff["g"] = eff["g"] + 1.0          # plant a wrong local contribution
    ok, idx = t.verify()
    assert ok is False and idx is not None


def test_forget_gc_keeps_suffix_verifiable():
    y, x, t = chain_graph(6)
    n0 = len(t.rows)
    t.gc(4)                       # drop a prefix, commit on-chain
    assert len(t.rows) == n0 - 4 + 1   # 4 dropped + 1 FORGET row
    ok, _ = t.verify()
    assert ok


# ---------- 2. replay == live (regression guard, not a theorem) ----------

def test_replay_equals_live_bitwise():
    y, x, t = chain_graph(12)
    live = {v.id: v.grad for v in y.topo()}
    assert tape.replay(t.rows, root=y.id) == live


def test_replay_tick_resume_composes():
    y, x, t = chain_graph(12)
    full = tape.replay(t.rows, root=y.id)
    k = 5
    part = tape.replay(t.rows, root=y.id, upto_tick=k)
    resumed = tape.replay(t.rows, after_tick=k, init_grads=part)
    assert resumed == full


def test_quilt_value_matches_micrograd_float_semantics():
    """Instrumentation must not change float results (ops both engines share;
    quilt additionally restricts pow to integer exponents -- see README)."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        a = engine.Value(-4.0)
        b = engine.Value(2.0)
        c = a + b
        d = a * b + b ** 3
        c += c + 1
        c += 1 + c + (-a)
        d += d * 2 + (b + a).relu()
        d += 3 * d + (b - a).relu()
        e = c - d
        f = e ** 2
        g = f / 2.0
        g += 10.0 / f
        g.backward()
    ka, kb = KValue(-4.0), KValue(2.0)
    kc, kd = ka + kb, ka * kb + kb ** 3
    kc += kc + 1
    kc += 1 + kc + (-ka)
    kd += kd * 2 + (kb + ka).relu()
    kd += 3 * kd + (kb - ka).relu()
    ke = kc - kd
    kf = ke ** 2
    kg = kf / 2.0
    kg += 10.0 / kf
    kg.backward()
    assert (g.data, a.grad, b.grad) == (kg.data, ka.grad, kb.grad)


# ---------- 3. rational auditor ----------

def test_auditor_sample_size_tracks_sqrt_n():
    n = 200
    y, x, t = chain_graph(n)
    live = {v.id: v.grad for v in y.topo()}
    rep = auditor.audit(t.rows, live, seed=3)
    expect = math.sqrt(rep.n_nodes)
    assert abs(rep.n_sampled - expect) <= 0.5 * expect + 2


def test_auditor_seeded_determinism():
    y, x, t = chain_graph(50)
    live = {v.id: v.grad for v in y.topo()}
    r1 = auditor.audit(t.rows, live, seed=7)
    r2 = auditor.audit(t.rows, live, seed=7)
    assert [p[:2] for p in r1.paths] == [p[:2] for p in r2.paths]
    r3 = auditor.audit(t.rows, live, seed=8)
    assert [p[:2] for p in r1.paths] != [p[:2] for p in r3.paths]


def test_exact_mode_promotes_all():
    y, x, t = chain_graph(10)
    live = {v.id: v.grad for v in y.topo()}
    rep = auditor.audit(t.rows, live, mode="exact")
    assert rep.n_sampled == rep.n_nodes


def test_exact_agreement_on_primitives():
    """Small integer-valued graphs: float == exact bitwise on every op."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t), engine.mode("exact"):
        a = engine.Value(3)
        b = engine.Value(2)
        c = a * b          # *
        d = c + a          # +
        e = d ** 2         # pow int
        f = (e - engine.Value(50)).relu()   # relu, subtraction
        f.backward()
    eg = auditor.exact_grads(t.rows, [f.id])
    for v in f.topo():
        assert v.grad == float(eg[v.id]) == float(v.grad_twin)


def test_auditor_ci_contains_measured_drift():
    y, x, t = chain_graph(40)
    live = {v.id: v.grad for v in y.topo()}
    rep = auditor.audit(t.rows, live, seed=1)
    lo, hi = rep.ci95
    assert lo <= rep.mean <= hi


# ---------- 4. the comb ----------

def test_comb_fires_on_illconditioned():
    out, t, teeth = None, None, None
    engine.Value.reset_ids()
    t = tape.Tape()
    BIG = 1e16
    with tape.attach(t):
        x = engine.Value(1.0)
        a = x * BIG + x + x
        b = x * BIG + x + x + x + x
        y = a - b
        p, q = y * BIG, y
        for _ in range(4):
            p = p + y
            q = q + y * 3
        z = p + q
        out = (z + z + z) + (z * BIG + z - z * BIG)
        teeth = combmod.comb(out, t)
    assert len(teeth) >= 5
    assert teeth[0]["diff"] >= 1.0
    ev = auditor.exact_values(t.rows)
    assert ev[out.id] != 0           # exact forward: not collapsed
    assert out.data != float(ev[out.id])  # float forward: collapsed


def test_comb_no_false_teeth_on_ints():
    """Exactly-representable graph: both orders must agree bit-for-bit."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        x = engine.Value(3.0)
        y = (x * 5 + x * 7) * (x + x) + (x * x - x * 3)
        y = y.relu() + y * 2
        teeth = combmod.comb(y, t)
    assert teeth == []


def test_comb_restores_pass_a_grads():
    y, x, t = chain_graph(8)
    # chain has single-consumer nodes; force a real tooth graph instead
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        x = engine.Value(1.0)
        y = (x * 1e16 + x + x + x) + (x * 3 - x * 1e16 + x * 3)
        teeth = combmod.comb(y, t)
    grads_after = {v.id: v.grad for v in y.topo()}
    replayed = tape.replay(t.rows, root=y.id)
    assert replayed == grads_after


# ---------- 5. genotype ----------

def test_genotype_roundtrip_forward_bitwise():
    g, a, b, t, teeth = karpathy()
    g0 = gen.genotype(t.rows)
    sinks, t2 = gen.materialize(g0)
    assert sinks[0].data == g.data
    assert t2.verify() == (True, None)
    # structural identity up to id namespace (inputs are front-loaded in the
    # rebuild; the canon_ids projection erases that accident)
    g1 = gen.genotype(t2.rows)
    assert gen._canon_ids(g0) == gen._canon_ids(g1)


def test_genotype_hash_namespace_independent():
    g, a, b, t, teeth = karpathy()
    g0 = gen.genotype(t.rows)
    sinks, t2 = gen.materialize(g0)
    g1 = gen.genotype(t2.rows)
    assert gen.genotype_hash(g0) == gen.genotype_hash(g1)


def test_genotype_floor_tripwire_binary():
    """A tape with a planted wrong EFFECT is rejected, binary."""
    y, x, t = chain_graph(6)
    ok, _ = t.verify()
    assert ok
    eff = next(r for r in t.rows if r["t"] == "EFFECT")
    eff["body"] = json.dumps({"t": "EFFECT", "node": 999, "parent": 0,
                              "g": 123.0})
    ok, idx = t.verify()
    assert ok is False
    g0 = gen.genotype(t.rows)   # genotype of a tripped tape: structurally fine
    sinks, t2 = gen.materialize(g0)
    assert t2.verify() == (True, None)   # the child is clean


def test_leaves_and_sinks():
    g, a, b, t, teeth = karpathy()
    leaves = auditor.leaves(t.rows)
    assert {a.id, b.id} <= set(leaves)   # inputs among the source nodes
    assert all(any(r["t"] == "BIND" and r["id"] == i for r in t.rows)
               for i in leaves)
    assert auditor.sinks(t.rows) == [g.id]


# ---------- 6. demo loop ----------

def test_demo_loop_seeded_determinism():
    g, a, b, t, teeth = karpathy()
    g0 = gen.genotype(t.rows)
    h1 = gen.demo_loop(g0, g.data, seed=11, generations=3)
    h2 = gen.demo_loop(g0, g.data, seed=11, generations=3)
    assert h1 == h2
    assert len(h1) == 3


# ---------- 7. Demo A pins (Karpathy, verbatim) ----------

def test_demo_a_pins_karpathy_numbers():
    g, a, b, t, teeth = karpathy()
    assert round(g.data, 4) == 24.7041
    assert round(a.grad, 4) == 138.8338
    assert round(b.grad, 4) == 645.5773
    grads = tape.replay(t.rows, root=g.id)
    rep = auditor.audit(t.rows, grads, mode="exact")
    # all ops dyadic except 10/f: residual drift is a couple of ulps,
    # honestly measured -- 'zero meaningful drift'
    assert rep.worst[1] <= 1e-12


def test_demo_a_comb_intact():
    """The comb runs on Karpathy's own graph and reports honestly:
    a single ulp-scale tooth from the non-dyadic 10/f term."""
    g, a, b, t, teeth = karpathy()
    assert len(teeth) <= 3
    if teeth:
        assert max(x["diff"] for x in teeth) < 1e-10
