"""README-runnable demos for the quilt layer.

  python -m quilt.demos a [--exact]    Karpathy's README example, pinned
  python -m quilt.demos b [--seed N]   ill-conditioned graph: comb + auditor
  python -m quilt.demos c [--seed N]   3-generation genotype consumability

Demo A note: Karpathy's own example contains 10.0/f, and f is not a power
of two, so 10/f is not dyadic -- the exact audit legitimately reports a
worst relative drift of ~2e-16 (a couple of ulps) against Karpathy's pinned
4-decimal values. Zero meaningful drift, honestly measured.
"""

import argparse

from . import auditor, breeder, comb as combmod, engine, genotype as gen, tape


def karpathy_graph(exact=False):
    """The README example built on the quilt engine."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t), engine.mode("exact" if exact else "float"):
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
        teeth = combmod.comb(g, t)          # the comb IS the default backward
        return g, a, b, t, teeth


def demo_a(exact=False, seed=0):
    g, a, b, t, teeth = karpathy_graph(exact)
    grads = tape.replay(t.rows, root=g.id)  # replay == the recorded pass, bitwise
    print(f"g = {g.data:.4f}")              # Karpathy pins: 24.7041
    print(f"a.grad = {a.grad:.4f}")          #                 138.8338
    print(f"b.grad = {b.grad:.4f}")          #                 645.5773
    rep = auditor.audit(t.rows, grads, mode="exact" if exact else "stochastic",
                        seed=seed)
    print(rep)
    print(f"replay == live bitwise: "
          f"{grads == {v.id: v.grad for v in g.topo()}}")
    print(f"tape verify: {t.verify()}")
    print(combmod.render(teeth, t.rows))
    return g, a, b


def demo_b(seed=1):
    """Ill-conditioned graph: catastrophic cancellation + deep reconverging
    branches. The comb wobbles; the auditor names the exact drift."""
    engine.Value.reset_ids()
    t = tape.Tape()
    BIG = 1e16
    with tape.attach(t):
        x = engine.Value(1.0)
        a = x * BIG + x + x                    # exact BIG + 2
        b = x * BIG + x + x + x + x            # exact BIG + 4
        y = a - b                              # exact -2, float ~0 (cancel)
        p, q = y * BIG, y
        for _ in range(4):
            p = p + y
            q = q + y * 3
        z = p + q                              # exact BIG*y + 13*y
        r = z + z + z                          # 3z
        s = z * BIG + z - z * BIG              # exact z, float ~0 (cancel)
        out = r + s                            # exact 4z = -8e16 - 136
        teeth = combmod.comb(out, t)
    grads = tape.replay(t.rows, root=out.id)
    ev = auditor.exact_values(t.rows)
    eg = auditor.exact_grads(t.rows, [out.id])
    rep = auditor.audit(t.rows, grads, seed=seed)
    print(f"forward: float = {out.data!r}")
    print(f"forward: exact = {ev[out.id]}")
    print(f"x.grad : float = {grads[x.id]!r}")
    print(f"x.grad : exact = {eg[x.id]}")
    print(rep)
    print(f"tape verify: {t.verify()}")
    print(combmod.render(teeth, t.rows))
    return out, t


def demo_c(seed=0, generations=3):
    """3-generation consumability loop over the genotype encoding.

    The Karpathy graph is the seed individual; the loop hill-climbs one
    input constant per generation toward the pinned g = 24.7041. Each
    generation re-materializes the genotype from scratch: the printed
    genotype hash staying stable across materializations IS the
    consumability proof the negative-space GAN will rely on.
    """
    g, a, b, t, _ = karpathy_graph(exact=False)
    target = g.data
    g0 = gen.genotype(t.rows)
    h0 = gen.genotype_hash(g0)
    sinks, t2 = gen.materialize(g0)
    h1 = gen.genotype_hash(gen.genotype(t2.rows))
    print(f"genotype hash at extraction:   {h0}")
    print(f"genotype hash re-materialized: {h1}")
    print(f"consumability (hashes match, forward identical): "
          f"{h0 == h1 and sinks[0].data == g.data}")
    history, kept = gen.demo_loop(g0, target, seed=seed,
                                  generations=generations)
    print(f"{'gen':>3} {'fitness':>12} {'output':>12} {'kept':>5} "
          f"{'genotype_hash':>20}")
    for row in history:
        print(f"{row['gen']:>3} {row['fitness']:>12.6f} {row['output']:>12.6f} "
              f"{str(row['kept']):>5} {row['genotype_hash']:>20}")
    sinks_k, t_k = gen.materialize(kept)
    floor = breeder.viable(t_k.rows)
    print(f"\nviability floor on kept genotype (binary, exact FD check): "
          f"{'PASS' if floor == 1 else 'FAIL'}")
    return history


def main():
    ap = argparse.ArgumentParser(prog="quilt.demos")
    ap.add_argument("demo", choices=["a", "b", "c"])
    ap.add_argument("--exact", action="store_true", help="full-twin exact mode")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    if args.demo == "a":
        demo_a(exact=args.exact, seed=args.seed)
    elif args.demo == "b":
        demo_b(seed=args.seed or 1)
    else:
        demo_c(seed=args.seed)


if __name__ == "__main__":
    main()
