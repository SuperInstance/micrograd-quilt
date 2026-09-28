"""exp007 — Bell-balance skeleton-seed CONTROL at n=2 (the engine's
home turf).

exp006 (Finding 3 resolution + Finding 4): the seeded-restart doctrine
holds at n=3 — seed a zero-fitness structural prefix (GHZ skeleton),
never a partial solution (partial entangler = fitness trap, 120 draws
never above 0.256). Both arms there were 3-qubit. This control asks
whether the doctrine is engine-general or an n=3 artifact, on the
cheapest entangled target: 2-qubit Bell balance, targets ("01","10"),
mode="balance" — a deterministic product state scores 0.0 (its losing
target never fires), so balance is an entanglement gate here too.

Three lanes, same named seeds (root 7, train 101, verify 202,
shots 512), same jitter-dropped policy (restrict=("replace","indel")):
  control: no seed — random 3-gate birth (is n=2 champion-local search
           already unbottlenecked? the exp005 stall was n=3)
  seedA_wrongbell_skeleton: [["h",0],["cx",0,1]] — the PHI+ skeleton:
           maximally entangled, balance 0.0 against the PSI targets
           (target mismatch, not weakness); ONE x(0) insert from the
           answer (x(0) on phi+ = psi+). Zero fitness at birth, one
           move from correlation — the doctrine's exact prescription.
  seedB_product_trap: [["h",0],["h",1]] — |++>, balance ~0.22 with the
           slope already present; and a TRUE trap: |++> is a fixed
           point of either cx (|+> is an X eigenstate), so any cx
           insert is a no-op and escape needs two coordinated moves.
           The exp006 Finding-4 trap class at n=2.
Success = held-out verify balance >= 0.45 (same bar as exp006).
The exp001 reproduction guard runs the default lane in-harness again.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, p_target, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp007.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("01", "10")

# --- birth-balance documentation (fitness of each seed at the seeds) ----
for name, genome in (("wrongbell_phi_plus", [["h", 0], ["cx", 0, 1]]),
                     ("product_pp", [["h", 0], ["h", 1]])):
    b = p_target(genome, TRAIN, SHOTS, TARGETS, 2, "balance")
    print(f"birth balance {name}: {b:.4f}")

# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp007.telemetry.control.jsonl"
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
    print("FATAL: exp007 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))

lanes = {
    "unseeded_random_birth": None,
    "seedA_wrongbell_skeleton": [["h", 0], ["cx", 0, 1]],
    "seedB_product_trap": [["h", 0], ["h", 1]],
}
runs = {}
for name, seed_genome in lanes.items():
    telem = LAB / "experiments" / f"exp007.telemetry.{name}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=12, pop=16, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), mutate_fn=mutate_fn,
                     targets=TARGETS, n_qubits=2, mode="balance",
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
print("results -> experiments/exp007.results.json")
