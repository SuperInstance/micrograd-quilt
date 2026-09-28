"""qcell.search — champion-seeded circuit search (the learning system).

Population loop in the loadCoev pattern the fleet already uses for
classical lanes: a champion genome, a cloud of mutants, promotion gated
on a HELD-OUT seed — train fitness picks candidates, verify fitness
(a different named seed) must not regress before promotion. That split
is not decoration: seeded sampling still carries seed-variance, and a
search that promotes on one seed alone is overfitting noise.

Ledger discipline: every champion transition emits a full witness
ledger (qcell.emit); candidate telemetry stays unchained experiment
data. Nothing unseeded is ever written down as a result.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass, field

import micromoth
from qcell.emit import program_to_circuit

SINGLE = ["x", "h", "rx", "rz"]
TWO = ["cx", "swap", "crx"]
THETAS = [0.25, 0.5, 0.75, 1.0]  # fractions of pi


@dataclass
class Candidate:
    genome: list
    train_p: float = 0.0
    verify_p: float = 0.0

    def digest(self) -> str:
        return json.dumps(self.genome, sort_keys=True)


def random_gate(rng: random.Random, n_qubits: int = 2) -> list:
    if rng.random() < 0.6:
        op = rng.choice(SINGLE)
        q = rng.randrange(n_qubits)
        return [op, rng.choice(THETAS), q] if op.startswith("r") else [op, q]
    op = rng.choice(TWO)
    s, t = rng.sample(range(n_qubits), 2)
    return [op, rng.choice(THETAS), s, t] if op == "crx" else [op, s, t]


def genome_circuit(genome, n_qubits=2):
    qc = micromoth.QuantumCircuit(n_qubits, n_qubits)
    for g in genome:
        op = g[0]
        if op == "x":
            qc.x(g[1])
        elif op == "h":
            qc.h(g[1])
        elif op == "rx":
            qc.rx(g[1] * 3.141592653589793, g[2])
        elif op == "rz":
            qc.rz(g[1] * 3.141592653589793, g[2])
        elif op == "cx":
            qc.cx(g[1], g[2])
        elif op == "swap":
            qc.swap(g[1], g[2])
        elif op == "crx":
            qc.crx(g[1] * 3.141592653589793, g[2], g[3])
    for q in range(n_qubits):
        qc.measure(q, q)
    return qc


def p_target(genome, seed: int, shots: int, target: str = "01") -> float:
    random.seed(seed)
    qc = genome_circuit(genome)
    counts = micromoth.simulate(qc, shots=shots, get="counts")
    return counts.get(target, 0) / shots


def mutate(genome, rng: random.Random, budget: int = 6):
    g = [list(gate) for gate in genome]
    if not g:
        return [random_gate(rng)]
    move = rng.random()
    i = rng.randrange(len(g))
    if move < 0.30 or len(g) >= budget:
        g[i] = random_gate(rng)
    elif move < 0.55 and len(g) < budget:
        g.insert(i, random_gate(rng))
    elif move < 0.75 and len(g) > 1:
        g.pop(i)
    else:
        for gate in g:
            if gate[0].startswith("r") and rng.random() < 0.5:
                gate[1] = max(0.05, min(1.0, gate[1] + rng.choice([-0.25, 0.25])))
    return g


# exp003 (Finding 2): which mutation class crosses the plateau? The
# sampler below draws the SAME move value from the same rng stream as
# mutate() — only the APPLICATION is restricted. A restricted class that
# cannot apply (indel on a full/short genome, jitter with no rotation
# gate) returns None and the caller resamples; nothing silently falls
# back to a different class, or the ablation would be a lie.
MUT_CLASSES = ("replace", "indel", "jitter")


def mutate_classed(genome, rng: random.Random, budget: int = 6,
                   restrict: tuple = MUT_CLASSES):
    g = [list(gate) for gate in genome]
    if not g:
        return [random_gate(rng)]
    move = rng.random()
    i = rng.randrange(len(g))
    if move < 0.30 or len(g) >= budget:
        if "replace" not in restrict:
            return None
        g[i] = random_gate(rng)
    elif move < 0.55 and len(g) < budget:
        if "indel" not in restrict:
            return None
        g.insert(i, random_gate(rng))
    elif move < 0.75 and len(g) > 1:
        if "indel" not in restrict:
            return None
        g.pop(i)
    else:
        if "jitter" not in restrict:
            return None
        hit = False
        for gate in g:
            if gate[0].startswith("r") and rng.random() < 0.5:
                gate[1] = max(0.05, min(1.0, gate[1] + rng.choice([-0.25, 0.25])))
                hit = True
        if not hit:
            return None
    return g


def fitness(c: Candidate, parsimony: float = 0.0) -> float:
    """Selection score: train fitness minus a per-gate parsimony penalty.

    parsimony=0.0 reproduces exp001 exactly (fitness == raw P(target)).
    The penalty is charged on genome LENGTH only, never on verify fitness,
    so promotion gating (held-out seed) is untouched by the pressure.
    """
    return c.train_p - parsimony * len(c.genome)


class MutationDeadlock(RuntimeError):
    """Raised when a class-restricted mutator (exp003) has no applicable
    move for the current champion — the ablation arm literally cannot
    act. Recorded as a result, never worked around silently."""


class _NoApplicableMove:
    pass


def run_search(root_seed: int, generations: int, pop: int, shots: int,
               train_seed: int, verify_seed: int, budget: int = 6,
               telemetry_path=None, parsimony: float = 0.0,
               mutate_fn=None, max_resample: int = 10000) -> dict:
    """mutate_fn defaults to mutate(); exp003 passes a class-restricted
    wrapper. Default path must stay byte-identical to exp001/exp002.

    max_resample bounds how long we wait for a restricted mutator to
    find an applicable move; exceeding it raises MutationDeadlock — a
    no-move-exists verdict on the current champion, not a hang."""
    if mutate_fn is None:
        mutate_fn = mutate
    rng = random.Random(root_seed)
    champion = Candidate(genome=[random_gate(rng) for _ in range(3)])
    champion.train_p = p_target(champion.genome, train_seed, shots)
    champion.verify_p = p_target(champion.genome, verify_seed, shots)
    curve = []
    for gen in range(generations):
        cands = [champion]
        while len(cands) < pop:
            genome = _NoApplicableMove
            for _ in range(max_resample):
                genome = mutate_fn(champion.genome, rng, budget)
                if genome is not None:
                    break
            if genome is None:
                raise MutationDeadlock(
                    f"no applicable mutation for champion "
                    f"{champion.genome} at gen {gen}")
            child = Candidate(genome=genome)
            child.train_p = p_target(child.genome, train_seed, shots)
            cands.append(child)
        best = max(cands, key=lambda c: fitness(c, parsimony))
        best.verify_p = p_target(best.genome, verify_seed, shots)
        promoted = best.verify_p >= champion.verify_p
        if promoted:
            champion = best
        curve.append({"gen": gen, "train_p": round(best.train_p, 4),
                      "verify_p": round(best.verify_p, 4),
                      "promoted": promoted,
                      "genome": champion.genome if promoted else None})
        if telemetry_path:
            with open(telemetry_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(curve[-1], sort_keys=True) + "\n")
    return {"champion": champion, "curve": curve}
