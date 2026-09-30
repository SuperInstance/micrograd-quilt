"""exp006 — Finding 3 candidate (a): GHZ-prefix seeded restart.

exp005 (Finding 3, VERIFIED): the engine cannot reach an entangled
target from a random 3-qubit birth — champion-local mutation is the
bottleneck class, not fitness shape. Ranked fix, first candidate:
seed the initial champion with a GHZ PREFIX (loadCoev doctrine —
seeds around champs, pong-quilt #73 — applied at birth instead of
waiting for promotion to earn it).

Two seeded lanes, same named seeds (root 7, train 101, verify 202,
shots 512), same jitter-dropped policy (restrict=("replace","indel")):
  lane A: seed [["h",0],["cx",0,1]]      (GHZ skeleton, balance 0.0 —
          indel can add h(2) or cx(1,2) in ONE move)
  lane B: seed [["h",0],["cx",0,1],["h",2]] (partial entangler,
          balance ~0.25 — replace/jitter-free slope already present)
Success = held-out verify balance >= 0.45 (near-balanced GHZ).
The exp001 reproduction guard runs the default lane in-harness again.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp006.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("000", "111")

# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp006.telemetry.control.jsonl"
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
    print("FATAL: exp006 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))

lanes = {
    "seedA_ghz_prefix": [["h", 0], ["cx", 0, 1]],
    "seedB_partial_entangler": [["h", 0], ["cx", 0, 1], ["h", 2]],
}
runs = {}
for name, seed_genome in lanes.items():
    telem = LAB / "experiments" / f"exp006.telemetry.{name}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), mutate_fn=mutate_fn,
                     targets=TARGETS, n_qubits=3, mode="balance",
                     seed_genome=seed_genome)
    champ = res["champion"]
    first_ok = next((r["gen"] for r in res["curve"]
                     if r["verify_p"] >= 0.45), None)
    runs[name] = {
        "seed_genome": seed_genome,
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_verify_ge_045_gen": first_ok,
        "curve": res["curve"],
    }
    print(f"{name}: champion={json.dumps(champ.genome)} "
          f"train={champ.train_p:.3f} verify={champ.verify_p:.3f} "
          f"first_ge_045_gen={first_ok}")

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "control_reproduces_exp001": control_ok,
    "policy": "drop jitter (restrict=('replace','indel'))",
    "success_threshold_verify_balance": 0.45,
    "runs": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp006.results.json")
