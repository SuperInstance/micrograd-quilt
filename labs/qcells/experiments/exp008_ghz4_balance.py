"""exp008 — n=4 GHZ balance: the witness-cell blocker is gone, does the
doctrine hold at the next scale?

The PROOF statevector witness cell (qcell/stepper.py) replaced
O(gates^2) prefix simulations with one O(gates) pass, explicitly naming
"n=4+" as the unblocked target. exp005-007 established the doctrine on
entanglement-gated targets: unaided champion-local search NEVER crosses
(frozen 12 gens at n=3, plateau 0.234 at n=2), while a zero-fitness
STRUCTURAL prefix seed crosses fast (GHZ skeleton at n=3: gen 2;
wrong-bell phi+ skeleton at n=2: gen 5). Seed CHOICE beats seed
FITNESS (partial entangler = trap, |++> = trap).

This experiment is the doctrine's scale test: n=4, targets
("0000","1111"), mode="balance" — still an entanglement gate (product
state scores 0.0, its losing target never fires).

Three lanes, same named seeds (root 7, train 101, verify 202,
shots 512), same jitter-dropped policy (restrict=("replace","indel")):
  control: no seed — random 3-gate birth at n=4. Prediction per
           doctrine: never crosses 12 gens.
  seedA_ghz3_skeleton: [["h",0],["cx",0,1],["cx",1,2]] — GHZ on qubits
           0-2 tensor |0>: balance vs (0000,1111) is 0.0 at birth,
           exactly ONE cx insert from GHZ4. The doctrine's prescription.
  seedB_product4_trap: [["h",0],["h",1],["h",2],["h",3]] — |++++>:
           c0000 ~ c1111 ~ shots/16, balance ~0.0625 with NO slope
           toward correlation (any single-qubit move keeps it
           product). The Finding-4 trap class at n=4.
Success = held-out verify balance >= 0.45 (same bar as exp006/exp007).
The exp001 reproduction guard runs the default lane in-harness again.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, p_target, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp008.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("0000", "1111")
N = 4

# --- birth-balance documentation (fitness of each seed at the seeds) ----
for name, genome in (("ghz3_skeleton", [["h", 0], ["cx", 0, 1], ["cx", 1, 2]]),
                     ("product_++++", [["h", 0], ["h", 1], ["h", 2], ["h", 3]])):
    b = p_target(genome, TRAIN, SHOTS, TARGETS, N, "balance")
    print(f"birth balance {name}: {b:.4f}")

# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp008.telemetry.control.jsonl"
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
    print("FATAL: exp008 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))

lanes = {
    "unseeded_random_birth": None,
    "seedA_ghz3_skeleton": [["h", 0], ["cx", 0, 1], ["cx", 1, 2]],
    "seedB_product4_trap": [["h", 0], ["h", 1], ["h", 2], ["h", 3]],
}
runs = {}
for name, seed_genome in lanes.items():
    telem = LAB / "experiments" / f"exp008.telemetry.{name}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=12, pop=16, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), mutate_fn=mutate_fn,
                     targets=TARGETS, n_qubits=N, mode="balance",
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
    "n_qubits": N,
    "targets": list(TARGETS),
    "control_reproduces_exp001": control_ok,
    "policy": "drop jitter (restrict=('replace','indel'))",
    "success_threshold_verify_balance": 0.45,
    "runs": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp008.results.json")
