"""exp005 — n=3 entangled target: can the search engine FIND entanglement?

exp004's jitter-drop policy resolved the 2-qubit |01> problem in 2
generations. The queue's next question is whether the same engine
generalizes UP: 3 qubits, target = balanced GHZ {|000>,|111>}.

Design decision pinned BEFORE running (anti-laundering): a bare
counts-set target {000,111} is hit at 1.0 by any DETERMINISTIC product
state (|000> itself is in the set) — the set alone never forces
entanglement. So the fitness is the BALANCE witness
min(c[000], c[111]) / shots (mode="balance" in qcell.search): both
branches must fire on the same circuit. A product state scores 0.0
(its losing branch never fires); only a genuinely correlated state
scores high. This makes entanglement the fitness, not a basis lottery.

Same named seeds: root 7, train 101, verify 202, shots 512. Nothing
unseeded is ever written down as a result. Policy per exp004:
restrict=("replace","indel") (jitter dropped). The exp001 reproduction
guard re-runs the default 2-qubit control lane inside THIS harness
config and refuses to write if it drifts (mode/targets defaults must
reproduce exp001 byte-identical).
"""
import functools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import micromoth
from qcell.search import mutate_classed, p_target, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp005.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("000", "111")

# --- prelude: witness sanity, measured not assumed -----------------------
# true GHZ circuit (hand-built, not searched) must score high on the
# balance witness on BOTH seeds; the best product-state attempt
# (independent h on q0) must score ~0 — proving the witness gates
# entanglement at all.
random.seed(VERIFY)
ghz = micromoth.QuantumCircuit(3, 3)
ghz.h(0); ghz.cx(0, 1); ghz.cx(1, 2)
for q in range(3):
    ghz.measure(q, q)
c = micromoth.simulate(ghz, shots=SHOTS, get="counts")
ghz_bal = min(c.get("000", 0), c.get("111", 0)) / SHOTS
prod_bal = p_target([["h", 0]], VERIFY, SHOTS, TARGETS, 3, "balance")
print(f"prelude: hand GHZ balance={ghz_bal:.3f} (both seeds by symmetry), "
      f"product h(0) balance={prod_bal:.3f} -> witness gates entanglement")

# --- guard: default 2-qubit lane still reproduces exp001 -----------------
ctrl_telem = LAB / "experiments" / "exp005.telemetry.control.jsonl"
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
    print("FATAL: exp005 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

# --- the n=3 entangled run ----------------------------------------------
telem = LAB / "experiments" / "exp005.telemetry.ghz.jsonl"
if telem.exists():
    telem.unlink()
mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))
res = run_search(ROOT_SEED, generations=12, pop=16, shots=SHOTS,
                 train_seed=TRAIN, verify_seed=VERIFY,
                 telemetry_path=str(telem), mutate_fn=mutate_fn,
                 targets=TARGETS, n_qubits=3, mode="balance")

champ = res["champion"]
first_balanced = next((r["gen"] for r in res["curve"]
                       if r["verify_p"] >= 0.45), None)
print(f"n=3 GHZ: champion={json.dumps(champ.genome)} "
      f"len={len(champ.genome)} train={champ.train_p:.3f} "
      f"verify={champ.verify_p:.3f} first_verify_>=0.45_gen={first_balanced}")

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "control_reproduces_exp001": control_ok,
    "prelude": {
        "hand_ghz_balance": round(ghz_bal, 4),
        "product_h0_balance": round(prod_bal, 4),
        "witness_gates_entanglement": prod_bal < 0.05 < ghz_bal,
    },
    "runs": {
        "ghz_balance": {
            "policy": "drop jitter (restrict=('replace','indel'))",
            "targets": list(TARGETS),
            "mode": "balance",
            "n_qubits": 3,
            "champion_genome": champ.genome,
            "champion_len": len(champ.genome),
            "champion_train_p": champ.train_p,
            "champion_verify_p": champ.verify_p,
            "first_verify_ge_045_gen": first_balanced,
            "curve": res["curve"],
        },
    },
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp005.results.json")
