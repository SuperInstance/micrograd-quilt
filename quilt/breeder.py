"""quilt/breeder.py — tape-as-genotype + a minimal consumability demo.

Design law 3, amended per critic ref M3-01: this repo ships ONLY the genotype
encoding and a tiny seeded proof that the encoding is consumable (decode →
rebuild → evaluate → viability floor). No in-repo MAP-Elites. The real
negative-space GAN — binary viability floor, tripwire doctrine, empty-cell
novelty objective — lives in SuperInstance/the-tap PR #7
(NEGATIVE-SPACE-GAN.md @2c60f314, floor doctrine per PR #6) and breeds tapes
later via the composition seam.

Viability floor (binary, multiplicative): an organism scores 1 iff EVERY leaf
passes an exact gradient-check — analytic exact grads (auditor.exact_grads)
vs central finite differences in exact Fraction arithmetic, h = 1/1000,
rel tol 1e-3 (derived: FD truncation is O(h^2) ~ 1e-6 under exact arithmetic,
so a 1e-3 tolerance sits three orders above truncation error → the floor is
binary-safe). Multiplicative = product of per-leaf pass indicators.

Constants:
  H_FD = Fraction(1, 1000): FD step (derived above).
  TOL_FD = 1e-3: relative tolerance (derived above).
  N_OPS ~ 14: "a few dozen nodes max" per the brief; we stay well under.
"""

import json
import random
from fractions import Fraction

from . import auditor, engine, tape

H_FD = Fraction(1, 1000)   # FD step; truncation O(h^2)~1e-6 << TOL_FD
TOL_FD = 1e-3              # 3 orders above FD truncation → binary-safe floor
_OPS = ["+", "*", "tanh", "relu", "**2"]


# -- genotype encoding --------------------------------------------------------
def _canon_ids(rows):
    """Renumber ids by first appearance over the BIND/LINK spine (row order
    == construction order, so parents always precede children). Genotype
    identity = graph structure + constants, INDEPENDENT of the accidental
    id namespace — any faithful materialization hashes the same. This is
    the consumability contract the composition seam relies on."""
    remap = {}
    out = []
    for r in rows:
        r = dict(r)
        if r["id"] not in remap:
            remap[r["id"]] = len(remap)
        r["id"] = remap[r["id"]]
        if r["t"] == "LINK":
            r["p"] = [remap[i] for i in r["p"]]
        out.append(r)
    return out


def _spine(rows):
    """BIND/LINK rows projected to genome form — structure + constants only.
    The WAL's hash/prev chain fields are per-instance evidence, NOT genome:
    they differ across materializations by construction."""
    out = []
    for r in rows:
        if r["t"] == "BIND":
            out.append({"t": "BIND", "id": r["id"], "data": r["data"]})
        elif r["t"] == "LINK":
            out.append({"t": "LINK", "id": r["id"], "op": r["op"],
                        "p": list(r["p"])})
    return out


def genotype(tape):
    """The genome: canonical JSON of the tape's BIND/LINK spine (the forward
    graph — everything backward needs is derivable by replay), ids renumbered
    by first appearance (see _canon_ids)."""
    return json.dumps(_canon_ids(_spine(tape.rows)),
                      sort_keys=True, separators=(",", ":"))


def decode(geno):
    """Genome → row list (BIND/LINK only, canon ids). Consumability proof:
    materialize(decode(genotype(t))) rebuilds the graph; replay reproduces
    its values and gradients bitwise."""
    return json.loads(geno)


# -- organism construction ----------------------------------------------------
def random_organism(rng, n_leaves=3, n_ops=14):
    """A tiny random DAG on a fresh tape. Seeded: identical rng → identical
    tape (hence identical genotype). ids reset per organism so genotypes are
    portable local graphs (ids always start at 0)."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        leaves = [engine.Value(rng.uniform(-1.0, 1.0))
                  for _ in range(n_leaves)]
        pool = list(leaves)
        for _ in range(n_ops):
            op = rng.choice(_OPS)
            if op in ("tanh", "relu"):
                v = getattr(pool[rng.randrange(len(pool))], op)()
            elif op == "**2":
                v = pool[rng.randrange(len(pool))] ** 2
            else:
                a = pool[rng.randrange(len(pool))]
                b = pool[rng.randrange(len(pool))]
                v = a + b if op == "+" else a * b
            pool.append(v)
    return t


def materialize(rows):
    """Decode → LIVE graph: rebuild Values by replaying BIND/LINK rows
    through the engine (float mode, fresh ids matching the tape's).
    Returns (sink_value, {id: Value}) — the consumability proof: the genome
    is not just replayable, it re-instantiates."""
    engine.Value.reset_ids()
    vals = {}
    sink = None
    for r in rows:
        if r["t"] == "BIND":
            vals[r["id"]] = engine.Value(r["data"])
        elif r["t"] == "LINK":
            ps = [vals[i] for i in r["p"]]
            op = r["op"]
            if op == "+":
                v = ps[0] + ps[1]
            elif op == "*":
                v = ps[0] * ps[1]
            elif op.startswith("**"):
                v = ps[0] ** int(op[2:])
            else:
                v = getattr(ps[0], op)()
            vals[r["id"]] = v
            sink = v
    return sink, vals


def phenotype(rows):
    """Behavioral descriptors for negative-space maps: (depth, op-diversity).
    Depth = longest chain from any leaf to the sink."""
    pmap = auditor.parents_map(rows)
    sink = auditor.sinks(rows)[-1]
    depth = 0
    stack = [(sink, 0)]
    seen = set()
    while stack:
        n, d = stack.pop()
        if (n, d) in seen:
            continue
        seen.add((n, d))
        depth = max(depth, d)
        for p in pmap.get(n, []):
            stack.append((p, d + 1))
    ops = {r["op"] for r in rows if r["t"] == "LINK"}
    return depth, len(ops)


def sink_value(rows):
    """The output value — what selection actually optimizes for here."""
    return auditor.exact_values(rows)[auditor.sinks(rows)[-1]]


# -- viability floor ----------------------------------------------------------
def viable(rows, analytic_grads=None):
    """BINARY floor, multiplicative over TRUE leaves: 1 iff every leaf's
    analytic (exact) gradient w.r.t. THE sink (sinks()[-1] — the last op)
    matches an exact-arithmetic finite difference within TOL_FD.
    analytic_grads override = the tripwire seam (the-tap PR #7 doctrine: a
    planted wrong-gradient organism must score 0)."""
    leaves = auditor.leaves(rows)
    sink = auditor.sinks(rows)[-1]          # single-sink organisms
    g = analytic_grads if analytic_grads is not None \
        else auditor.exact_grads(rows, [sink])
    vals = auditor.exact_values(rows)
    out = sink
    score = 1
    for leaf in leaves:
        fp = auditor.exact_values(rows, {leaf: vals[leaf] + H_FD})[out]
        fm = auditor.exact_values(rows, {leaf: vals[leaf] - H_FD})[out]
        fd = (fp - fm) / (2 * H_FD)
        rel = abs(fd - g[leaf]) / max(abs(g[leaf]), Fraction(1, 10 ** 30))
        score *= 1 if rel <= TOL_FD else 0
    return score


# -- minimal 3-generation demo (consumability proof, not MAP-Elites) ----------
def demo(seed=0, generations=3, pop=6, archive=None):
    """Seeded 3-generation loop over random tape genotypes. Archive cells =
    (depth, op-diversity) buckets; novelty objective = open an EMPTY cell.
    Honest-null valid: a generation that opens no new viable cell says so.
    archive: pass a dict to resume/extend an existing archive (repeat runs
    deterministically re-walk the same cells → honest nulls)."""
    rng = random.Random(seed)
    if archive is None:
        archive = {}   # cell -> (score, geno)
    log = [f"breeder demo: seed={seed} generations={generations} pop={pop}"]
    for gen in range(generations):
        opened = 0
        for _ in range(pop):
            t = random_organism(rng)
            rows = t.rows
            v = viable(rows)
            cell = phenotype(rows)
            if v == 1 and cell not in archive:
                archive[cell] = (float(sink_value(rows)), genotype(t))
                opened += 1
        if opened:
            log.append(f"  gen{gen}: +{opened} viable new cell(s); "
                       f"archive={len(archive)}")
        else:
            log.append(f"  gen{gen}: HONEST NULL — no viable organism opened "
                       f"new space this generation; archive={len(archive)}")
    cells = sorted(archive)
    log.append("  negative-space map (depth x op-diversity):")
    for cell in cells:
        log.append(f"    cell {cell}: sink={archive[cell][0]:.6f} "
                   f"geno_sha={_short(archive[cell][1])}")
    log.append(f"  archive size: {len(archive)} cells")
    return "\n".join(log)


def _short(geno, n=12):
    import hashlib
    return hashlib.sha256(geno.encode()).hexdigest()[:n]
