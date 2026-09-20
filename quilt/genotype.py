"""quilt/genotype.py — the tape IS the genotype (design law 3, amended M3-01).

We ship ONLY the encoding plus a minimal seeded 3-generation consumability
loop. No in-repo MAP-Elites: the negative-space GAN (SuperInstance/the-tap
PR #7) breeds tapes later through its composition seam; brains live there,
not here.

genotype(rows):  project a tape's BIND/LINK spine to a JSON-able dict.
materialize(g):  rebuild a live graph from the encoding. With reset ids and
                 identical construction order, the rebuilt tape reproduces
                 the original BIND/LINK rows -- same bodies, same FNV-1a
                 chain -- which is the consumability proof.
demo_loop(g0):   seeded 3-generation smoke harness over the encoding.
"""

import json
import random

from . import engine, tape


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _canon_ids(g):
    """Renumber ids by first appearance (inputs then links, topo order).
    Genotype identity = graph structure + constants, independent of the
    accidental id namespace -- so any faithful materialization hashes the
    same. This is the consumability contract the breeder relies on."""
    remap = {}

    def rid(i):
        if i not in remap:
            remap[i] = len(remap)
        return remap[i]

    return {"version": 1,
            "inputs": [{"id": rid(i["id"]), "data": i["data"]}
                       for i in g["inputs"]],
            "links": [{"id": rid(l["id"]), "op": l["op"],
                       "p": [rid(x) for x in l["p"]]} for l in g["links"]],
            "sinks": [rid(s) for s in g["sinks"]]}


def genotype_hash(g):
    return tape.fnv1a_64(_canon(_canon_ids(g)))


def genotype(rows):
    """Project tape rows to the breedable genotype: inputs (leaf BINDs),
    links (op spine), sinks. EFFECT/TICK/VIEW rows are phenotype (runtime),
    not genotype — evolution breeds structure, not one backward pass."""
    links = [r for r in rows if r["t"] == "LINK"]
    used = {i for r in links for i in r["p"]}
    link_ids = {r["id"] for r in links}
    used = {i for r in links for i in r["p"]}
    inputs = [{"id": r["id"], "data": r["data"]} for r in rows
              if r["t"] == "BIND" and r["id"] not in link_ids]
    return {"version": 1,
            "inputs": inputs,
            "links": [{"id": r["id"], "op": r["op"], "p": list(r["p"])}
                      for r in links],
            "sinks": sorted(_sinks(rows))}


def _sinks(rows):
    links = [r for r in rows if r["t"] == "LINK"]
    used = {i for r in links for i in r["p"]}
    return sorted(r["id"] for r in links if r["id"] not in used)


def materialize(g):
    """Rebuild (sinks, tape) from a genotype. The fresh tape re-emits the
    same BIND/LINK rows as the original spine (deterministic ids, same
    data, same op order) — verify() passes and forward values are bitwise
    identical to the source graph."""
    engine.Value.reset_ids()
    t = tape.Tape()
    with tape.attach(t):
        nodes = {}
        for spec in g["inputs"]:
            nodes[spec["id"]] = engine.Value(spec["data"])
        for spec in g["links"]:
            ps = [nodes[i] for i in spec["p"]]
            op = spec["op"]
            if op == "+":
                out = ps[0] + ps[1]
            elif op == "*":
                out = ps[0] * ps[1]
            elif op.startswith("**"):
                out = ps[0] ** int(op[2:])
            elif op == "relu":
                out = ps[0].relu()
            elif op == "tanh":
                out = ps[0].tanh()
            elif op == "exp":
                out = ps[0].exp()
            elif op == "cos":
                out = ps[0].cos()
            else:
                raise ValueError(f"materialize: unknown op {op!r}")
            nodes[spec["id"]] = out
        sinks = [nodes[i] for i in g["sinks"]]
    return sinks, t


def demo_loop(g0, target, seed=0, generations=3, sigma=0.05):
    """Seeded 3-generation consumability harness (NOT a search engine):
    each generation materializes the genotype fresh, scores |target - out|,
    then hill-climbs one input constant. Seeded rng + reset ids make the
    whole run reproducible. Returns (history, kept_genotype)."""
    rng = random.Random(seed)
    history = []
    g = json.loads(json.dumps(g0))          # deep copy
    best = g
    best_fit = None
    for gen in range(generations):
        sinks, t = materialize(g)
        out = sinks[0].data
        fit = abs(target - out)
        accepted = best_fit is None or fit <= best_fit
        if accepted:
            best_fit = fit
            best = json.loads(json.dumps(g))
        else:
            g = best                     # greedy keep: reject the worse draw
        history.append({"gen": gen, "fitness": fit, "output": out,
                        "genotype_hash": genotype_hash(g), "kept": accepted})
        if gen + 1 == generations:
            break
        idx = rng.randrange(len(g["inputs"]))
        g["inputs"][idx]["data"] += rng.gauss(0.0, sigma)
    return history, best
