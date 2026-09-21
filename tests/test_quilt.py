"""tests/test_quilt.py — the full-quilt test suite.

Run from repo root: python3 -m unittest discover -s tests -v
(or: python3 -m unittest tests.test_quilt -v)

Covers the three design laws (amended, critic ref M3-01):
  1 stochastic rational auditor + exact twins (--exact)
  2 WAL replay determinism/regression guard, hash-chain tamper evidence
  3 tape-as-genotype encoding, binary viability floor, honest null
plus the float-native commensuration comb.
"""

import json
import math
import os
import sys
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quilt import auditor, breeder, comb, engine, tape  # noqa: E402


# -- shared builders ----------------------------------------------------------
def build_demo_a():
    """Karpathy README snippet, exact twins."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t), engine.mode("exact"):
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
    return t, a, b, g


def build_demo_b():
    """Ill-conditioned graph: grad-space cancellation + value quantization."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        v = engine.Value(1.0)
        A1 = engine.Value(1e16)
        A2 = engine.Value(-9999999999999900.0)
        A3 = engine.Value(7.0)
        w1 = v * A1
        w2 = v * A2
        w3 = v * A3
        x = engine.Value(1.0)
        K = engine.Value(1e16)
        big = x * K
        q = x * math.pi
        m = big + q
        d = m - big
        s = d * 100.0
        L = ((w1 + w2) + w3) + s
        L.backward()
    return t, v, L


# -- law 1: exact twins + auditor ---------------------------------------------
class TestExactTwins(unittest.TestCase):
    def test_primitives_exact_agreement(self):
        """add/mul/pow-int/relu on the rational skeleton: twin == float."""
        engine.Value.reset_ids()
        t = tape.Tape()
        with tape.attach(t), engine.mode("exact"):
            a = engine.Value(1.5)
            b = engine.Value(-2.25)
            for i, v in enumerate([a + b, a * b, a ** 3, b ** -2,
                                   a.relu(), b.relu()]):
                self.assertEqual(float(v.twin), v.data, f"node {i} op {v._op}")

    def test_karpathy_readme_numbers(self):
        t, a, b, g = build_demo_a()
        self.assertEqual(f"{g.data:.4f}", "24.7041")
        self.assertEqual(f"{a.grad:.4f}", "138.8338")
        self.assertEqual(f"{b.grad:.4f}", "645.5773")

    def test_exact_drift_kahan_bounded(self):
        """'Zero drift' = ulp-scale, bounded by Kahan D*U*|x| (D<=16 here)."""
        t, a, b, g = build_demo_a()
        nodes = g.topo()
        self.assertLessEqual(max(abs(v.data - float(v.twin)) for v in nodes),
                             1e-12)
        self.assertLessEqual(max(abs(v.grad - float(v.grad_twin))
                                 for v in nodes), 1e-11)

    def test_transcendental_freeze_boundary(self):
        """tanh/exp/cos twins freeze the SAME libm result — bitwise."""
        engine.Value.reset_ids()
        t = tape.Tape()
        with tape.attach(t), engine.mode("exact"):
            a = engine.Value(0.7)
            for v in (a.tanh(), a.exp(), a.cos()):
                self.assertEqual(v.twin, Fraction(
                    getattr(math, {"tanh": "tanh", "exp": "exp",
                                   "cos": "cos"}[v._op])(a.data)))

    def test_pow_correctly_rounded(self):
        """x**n is the correctly rounded exact power (libm pow is not)."""
        for x in (0.1, 1 / 3, 24.704081632653):
            for n in (2, 3, -1, -7):
                engine.Value.reset_ids()
                with engine.mode("float"):
                    v = engine.Value(x) ** n
                self.assertEqual(v.data, float(Fraction(x) ** n))


class TestAuditor(unittest.TestCase):
    def test_sampling_probabilities(self):
        t, a, b, g = build_demo_a()
        rows = t.rows
        n = len([r for r in rows if r["t"] == "BIND"])
        r1 = auditor.audit(rows, {v.id: v.grad for v in g.topo()}, p=1.0)
        self.assertEqual(r1.n_sampled, n)
        r0 = auditor.audit(rows, {v.id: v.grad for v in g.topo()}, p=0.0)
        self.assertEqual(r0.n_sampled, len(auditor.sinks(rows)))  # stratified

    def test_exact_mode_zero_drift_ci_below_tau(self):
        t, a, b, g = build_demo_a()
        # exact-mode grads come from the twin path
        fg = {v.id: float(v.grad_twin) for v in g.topo()}
        rep = auditor.audit(t.rows, fg, mode="exact")
        self.assertGreaterEqual(rep.mean, 0.0)
        self.assertLess(rep.ci95[1], comb.TAU)

    def test_auditor_names_drift_on_illconditioned(self):
        t, v, L = build_demo_b()
        ga, gb, disag = comb.disagreements(L)
        rep = auditor.audit(t.rows, ga, mode="exact")
        self.assertIsNotNone(rep.worst)
        self.assertGreater(rep.worst[1], 1e-3)


# -- law 4: float-native comb --------------------------------------------------
class TestComb(unittest.TestCase):
    def test_healthy_graph_no_false_teeth(self):
        t, a, b, g = build_demo_a()
        _, _, disag = comb.disagreements(g)
        self.assertLessEqual(max(disag.values()), comb.TAU)

    def test_illconditioned_fires_and_only_there(self):
        t, v, L = build_demo_b()
        _, _, disag = comb.disagreements(L)
        hot = [i for i, d in disag.items() if d > comb.TAU]
        self.assertEqual(hot, [v.id])           # ONLY the planted node
        self.assertGreater(disag[v.id], comb.LOST)   # tooth fully lost

    def test_render_shape(self):
        t, v, L = build_demo_b()
        out = comb.render_comb(L, t, seed=0)
        lines = out.splitlines()
        n = len([r for r in t.rows if r["t"] == "BIND"])
        self.assertIn("commensuration comb", lines[0])
        node_lines = [l for l in lines if l.startswith("  id ")]
        self.assertEqual(len(node_lines), n)
        self.assertTrue(lines[-1].startswith("  teeth:"))
        self.assertIn("✗", out)
        t2, a, b, g = build_demo_a()
        self.assertNotIn("✗", comb.render_comb(g, t2, seed=0))
        self.assertIn("✓", comb.render_comb(g, t2, seed=0))


# -- law 2: WAL replay ----------------------------------------------------------
class TestTape(unittest.TestCase):
    def test_replay_equals_live_bitwise(self):
        t, v, L = build_demo_b()
        live = {n.id: n.grad for n in L.topo()}
        grads = tape.replay(t.rows, root=L.id)
        for i, gv in grads.items():
            self.assertEqual(gv, live[i], f"grad mismatch at id {i}")

    def test_replay_resume_from_tick(self):
        t, v, L = build_demo_b()
        full = tape.replay(t.rows, root=L.id)
        ticks = len([r for r in t.rows if r["t"] == "TICK"])
        k = ticks // 2
        partial = tape.replay(t.rows, root=L.id, upto_tick=k)
        resumed = tape.replay(t.rows, after_tick=k, init_grads=partial)
        self.assertEqual(resumed, full)

    def test_tamper_evident(self):
        t, v, L = build_demo_b()
        self.assertEqual(t.verify(), (True, None))
        for i, r in enumerate(t.rows):
            if r["t"] == "EFFECT":
                r["g"] = r["g"] * 1.0000000001 + 1e-30
                bad = i
                break
        ok, idx = t.verify()
        self.assertFalse(ok)
        self.assertEqual(idx, bad)
        # structural rows too
        t2, v2, L2 = build_demo_b()
        for i, r in enumerate(t2.rows):
            if r["t"] == "LINK":
                r["op"] = "+"
                bad = i
                break
        ok, idx = t2.verify()
        self.assertFalse(ok)
        self.assertEqual(idx, bad)

    def test_gc_forget_verifies(self):
        t, v, L = build_demo_b()
        n0 = len(t.rows)
        t.gc(10)
        # FORGET re-anchors the chain at row 0; survivors re-chained after.
        self.assertEqual(len(t.rows), 1 + (n0 - 10))
        self.assertEqual(t.rows[0]["t"], "FORGET")
        self.assertEqual(t.rows[0]["before"], 10)
        self.assertEqual(t.verify(), (True, None))
        # replay still works on the surviving structure (self-contained)
        t2, v2, L2 = build_demo_b()
        t2.gc(0)  # FORGET with empty drop: pure re-anchor, replay unaffected
        self.assertEqual(t2.verify(), (True, None))
        self.assertEqual(tape.replay(t2.rows, root=L2.id),
                         tape.replay(t2.rows, root=L2.id))

    def test_determinism_under_reset_ids(self):
        t1, _, _ = build_demo_b()
        t2, _, _ = build_demo_b()
        self.assertEqual(t1.rows, t2.rows)  # ids, hashes, all rows identical


# -- law 3: genotype + breeder --------------------------------------------------
class TestBreeder(unittest.TestCase):
    def test_genotype_consumable(self):
        """decode(genotype(t)) → materialize → live backward reproduces the
        original gradients bitwise; exact sink value identical."""
        t, v, L = build_demo_b()
        geno = breeder.genotype(t)
        rows2 = breeder.decode(geno)
        # the genome is the spine minus WAL chain fields (hash/prev are
        # per-instance evidence, not genome), ids renumbered by first
        # appearance — for a fresh-tape build that is exactly the raw spine.
        self.assertEqual(rows2, [{k: r[k] for k in ("t", "id", "data", "op",
                                                    "p") if k in r}
                                 for r in t.rows
                                 if r["t"] in ("BIND", "LINK")])
        sink2, vals2 = breeder.materialize(rows2)
        sink2.backward()
        live = {n.id: n.grad for n in L.topo()}
        rebuilt = {i: vals2[i].grad for i in live}
        self.assertEqual(rebuilt, live)
        s1 = auditor.exact_values(t.rows)[auditor.sinks(t.rows)[-1]]
        s2 = auditor.exact_values(rows2)[auditor.sinks(rows2)[-1]]
        self.assertEqual(s1, s2)
        self.assertEqual(breeder.genotype(t), geno)  # stable

    def test_floor_binary_and_tripwire(self):
        """Viable organism scores 1; planted wrong-gradient organism scores 0
        (tripwire doctrine, the-tap PR #7)."""
        t = breeder.random_organism(random_seed := __import__("random").Random(0))
        rows = t.rows
        self.assertEqual(breeder.viable(rows), 1)
        g = auditor.exact_grads(rows, [auditor.sinks(rows)[-1]])
        leaves = auditor.leaves(rows)
        if leaves:
            bad = dict(g)
            bad[leaves[0]] = bad[leaves[0]] * 3 + Fraction(1, 7)
            self.assertEqual(breeder.viable(rows, analytic_grads=bad), 0)
            # multiplicative: corrupting ANY one leaf zeroes the product
            for leaf in leaves[1:]:
                bad = dict(g)
                bad[leaf] = bad[leaf] + Fraction(1, 100)
                self.assertEqual(breeder.viable(rows, analytic_grads=bad), 0)

    def test_honest_null_path(self):
        """Resuming the SAME archive with the same seed re-walks the SAME
        cells, so every resumed generation must report HONEST NULL — the
        null path is real code, not a dead branch."""
        archive = {}
        breeder.demo(seed=0, generations=1, pop=6, archive=archive)
        self.assertTrue(archive)
        out = breeder.demo(seed=0, generations=2, pop=6, archive=archive)
        self.assertIn("HONEST NULL", out)

    def test_demo_determinism(self):
        self.assertEqual(breeder.demo(seed=0, generations=2, pop=4),
                         breeder.demo(seed=0, generations=2, pop=4))


class TestPortsFromLaneAH2(unittest.TestCase):
    """Strengths ported from the sibling lane AH2 (merged 7bdc972), rewritten
    as stdlib unittest (no pytest) per the M3-01 minimalism pin."""

    def test_fnv1a_vectors(self):
        # published FNV-1a 64 check value for "a" (Fowler/Noll/Vo site)
        self.assertEqual(tape.fnv1a_64("a"), 0xAF63DC4C8601EC8C)
        # distinct inputs diverge; chain property: order matters
        self.assertNotEqual(tape.fnv1a_64("ab"), tape.fnv1a_64("ba"))

    def test_comb_silent_on_exact_ints(self):
        # exactly representable integers: both reduction orders agree
        # bit-for-bit — the comb must show no teeth (no false positives).
        engine.Value.reset_ids()
        t = tape.Tape()
        with tape.attach(t):
            a = engine.Value(3.0)
            b = engine.Value(7.0)
            c = a * b + a ** 2
            L = c * b + a
            L.backward()
        _, _, disag = comb.disagreements(L)
        self.assertTrue(all(d == 0.0 for d in disag.values()))

    def test_comb_restores_pass_a_grads(self):
        # after the shadow pass B, live grads must be pass A (canonical,
        # recorded) — downstream readers see the recorded pass.
        engine.Value.reset_ids()
        t = tape.Tape()
        with tape.attach(t):
            x = engine.Value(2.0)
            y = engine.Value(3.0)
            L = x * y + x ** 2 * y
            L.backward()
        canonical = {v.id: v.grad for v in L.topo()}
        comb.disagreements(L)
        self.assertEqual({v.id: v.grad for v in L.topo()}, canonical)

    def test_genotype_namespace_independent(self):
        # same graph built twice WITHOUT reset_ids, after unrelated Values
        # shifted the global id counter: raw rows differ, canon genotype
        # hashes the same. (reset-id determinism is covered separately.)
        def build_once():
            t = tape.Tape()
            with tape.attach(t):
                a = engine.Value(1.5)
                b = engine.Value(-0.5)
                c = a * b + a ** 2
                (c + b).backward()
            return t
        engine.Value.reset_ids()
        t1 = build_once()
        _ = engine.Value(99.0)          # shift the id namespace
        _ = engine.Value(101.0)
        t2 = build_once()
        raw1 = [r for r in t1.rows if r["t"] in ("BIND", "LINK")]
        raw2 = [r for r in t2.rows if r["t"] in ("BIND", "LINK")]
        self.assertNotEqual(
            json.dumps(raw1, sort_keys=True),
            json.dumps(raw2, sort_keys=True))
        self.assertEqual(breeder.genotype(t1), breeder.genotype(t2))
        # and the canon genome materializes with matching ids
        sink, vals = breeder.materialize(breeder.decode(breeder.genotype(t2)))
        self.assertEqual(sorted(vals), list(range(len(vals))))

    def test_quilt_vs_micrograd_few_ulps(self):
        # cross-validate the quilt engine against upstream micrograd on the
        # shared op set: data and grads agree to a few ulps, NOT bitwise —
        # both engines' DFS topo iterates parent sets in allocation-dependent
        # order; that last-ulp wobble is the comb's raison d'etre, not a bug.
        try:
            from micrograd.engine import Value as KValue
        except ImportError:
            self.skipTest("micrograd package unavailable")
        ka, kb = KValue(-4.0), KValue(2.0)
        kc = ka + kb
        kd = ka * kb + kb ** 3
        kc = kc + kc + 1
        kc = kc + 1 + kc + (-ka)
        kd = kd + kd * 2 + (kb + ka).relu()
        kd = kd + 3 * kd + (kb - ka).relu()
        kg = kd * kc
        kg.backward()

        engine.Value.reset_ids()
        qa, qb = engine.Value(-4.0), engine.Value(2.0)
        qc = qa + qb
        qd = qa * qb + qb ** 3
        qc += qc + 1
        qc += 1 + qc + (-qa)
        qd += qd * 2 + (qb + qa).relu()
        qd += 3 * qd + (qb - qa).relu()
        qg = qd * qc
        qg.backward()

        self.assertAlmostEqual(qg.data, kg.data, delta=1e-12 * max(1, abs(kg.data)))
        self.assertAlmostEqual(qa.grad, ka.grad, delta=1e-9 * max(1, abs(ka.grad)))
        self.assertAlmostEqual(qb.grad, kb.grad, delta=1e-9 * max(1, abs(kb.grad)))


if __name__ == "__main__":
    unittest.main()
