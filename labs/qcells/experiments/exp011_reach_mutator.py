"""exp011 — reach-class mutator candidates on the frozen UNSEEDED n=3
balance lane: does REACH (not draws) fix what pop scaling (exp010)
could not?

exp005 froze the unaided n=3 GHZ-balance search: champion-local
replace/indel cloud, 12 gens x pop 16, champion 0.000 throughout.
exp009 (budget) and exp010 (pop 16/32/64) both VERIFIED the freeze is
not a leash artifact — pop multiplies DRAWS, not REACH. Finding 3's
remaining candidate class is reach: seeding [exp006 CONFIRMED],
curriculum [exp007], or a WIDER MUTATOR [never run — this experiment].

Design pin BEFORE running (anti-laundering): signal density is 2.6%
(52/2000 random genomes, exp005). The winning genome is ~2 indels away
from the frozen champion neighborhood (h(2) + cx insert). Two
reach-class arms, both on the exact exp005 unaided lane (no seed,
jitter-dropped replace/indel classes, targets ("000","111"),
mode="balance", same named seeds):

  A: TWO-MOVE children — mutate_classed(replace/indel) applied twice
     per child. Each child spans a 2-move ball around the parent,
     doubling the neighborhood diameter per draw.
  B: NON-CHAMPION-PARENT cloud — parent_pool=True: each child mutated
     from a parent sampled uniformly from the candidate list (champion
     + already-generated children), one move each. Diversity via
     genealogy, not via move count.
  C: BOTH — two-move children off non-champion parents.

Interpretation pinned BEFORE running: if any arm crosses to
verify >= 0.45, the locality verdict gains its mutator boundary
condition (reach fixes it; seeding is not the only path). If all three
freeze, champion-locality is robust across every reach-class fix short
of seeding/curriculum — 'birth proximity is the whole game' (exp006)
hardens from INFERRED to boundary-tested engine law.

Success = held-out balance >= 0.45 (same threshold as exp005-010).
Telemetry records per-gen champion balance so 'almost moved' is
visible. The exp001 reproduction guard runs the default lane
in-harness again (the parent_pool default stays False, so this must
reproduce byte-identical).
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp011.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("000", "111")
N = 3
POP, GENS = 16, 12


def mutate_two_move(genome, rng, budget=6, n_qubits=2):
    """exp011 arm A/C: two classed moves per child (replace/indel only,
    jitter dropped per exp004 doctrine). A None at either step defers
    to the caller's resample loop — same no-silent-fallback contract
    as mutate_classed."""
    g = mutate_classed(genome, rng, budget,
                       restrict=("replace", "indel"), n_qubits=n_qubits)
    if g is None:
        return None
    return mutate_classed(g, rng, budget,
                          restrict=("replace", "indel"), n_qubits=n_qubits)


# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp011.telemetry.control.jsonl"
if ctrl_telem.exists():
    ctrl_telem.unlink()
ctrl_res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                      train_seed=TRAIN, verify_seed=VERIFY,
                      telemetry_path=str(ctrl_telem))
exp001 = json.loads(EXP001.read_text())
control_ok = (ctrl_res["curve"] == exp001["curve"]
              and ctrl_res["champion"].genome == exp001["champion_genome"])
print("control reproduces exp001:", control_ok)
if not control_ok:
    print("FATAL: exp011 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_one = functools.partial(mutate_classed, restrict=("replace", "indel"))

ARMS = {
    # A: two-move children, champion parents (classic exp005 cloud shape)
    "two_move": dict(mutate_fn=mutate_two_move, parent_pool=False),
    # B: one-move children, non-champion-parent cloud
    "parent_pool": dict(mutate_fn=mutate_one, parent_pool=True),
    # C: two-move children off non-champion parents
    "both": dict(mutate_fn=mutate_two_move, parent_pool=True),
}

runs = {}
for name, kw in ARMS.items():
    telem = LAB / "experiments" / f"exp011.telemetry.{name}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=GENS, pop=POP, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), targets=TARGETS,
                     n_qubits=N, mode="balance", **kw)
    champ = res["champion"]
    first_ok = next((r["gen"] for r in res["curve"]
                     if r["verify_p"] >= 0.45), None)
    champ_balances = [r["train_p"] for r in res["curve"]]
    draws_with_signal = sum(1 for b in champ_balances if b > 0)
    runs[name] = {
        "arm": name,
        "seeded": False,
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_gen_over_0.45": first_ok,
        "gens_champion_nonzero": draws_with_signal,
        "curve": res["curve"],
    }
    print(f"arm {name}: champion {champ.genome} "
          f"train={champ.train_p:.4f} verify={champ.verify_p:.4f} "
          f"first>=0.45 gen={first_ok} "
          f"gens_champion_nonzero={draws_with_signal}/{GENS}")

RESULTS.write_text(json.dumps({
    "exp": "exp011",
    "question": "does a reach-class mutator (two-move children / "
                "non-champion-parent cloud) unfreeze the unaided n=3 "
                "balance lane that pop scaling (exp010) could not?",
    "lane": {"root_seed": ROOT_SEED, "train_seed": TRAIN,
             "verify_seed": VERIFY, "shots": SHOTS, "pop": POP,
             "generations": GENS, "targets": TARGETS, "n_qubits": N,
             "mode": "balance", "seeded": False,
             "mut_classes": ["replace", "indel"]},
    "control_reproduces_exp001": control_ok,
    "runs": runs,
}, indent=2) + "\n")
print("wrote", RESULTS)
