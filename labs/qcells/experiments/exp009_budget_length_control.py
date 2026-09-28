"""exp009 — budget>6 length control at n=4: is the 6-gate ceiling a
search constraint, or is mutation locality the whole story?

exp008's n=4 GHZ-balance scale test crossed with a 4-gate champion
under budget=6 — the minimal entangling route (h + 3 cx) never
presses the ceiling. But 'the winning route is short' is not the same
as 'the ceiling never mattered': a cloud that can never grow past 6
gates cannot express redundant/temporizing circuits at all, and the
exp005-008 frozen-unaided verdicts were all recorded UNDER budget=6.

This experiment isolates the ceiling as a variable on the one lane
that reliably crosses (the doctrine lane, seedA GHZ3 skeleton,
restrict=('replace','indel'), same named seeds root7/train101/
verify202/shots512): budget swept 6 -> 8 -> 12 at n=4. If crossing
speed and held-out verify are budget-invariant, the ceiling is not a
binding constraint on this target class and the frozen-unaided
verdicts stand as engine laws, not artifacts of a short leash. If a
larger budget crosses FASTER (or the unseeded control unfreezes), the
'mutation locality is the bottleneck' doctrine gets its first
boundary condition.

Telemetry also records champion length per generation, so 'did anyone
even try to use the extra room' is answered from data, not assumed.
The exp001 reproduction guard runs the default lane in-harness again.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, p_target, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp009.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("0000", "1111")
N = 4
SEED_GENOME = [["h", 0], ["cx", 0, 1], ["cx", 1, 2]]  # GHZ3 skeleton
BUDGETS = (6, 8, 12)

print(f"seed birth balance: "
      f"{p_target(SEED_GENOME, TRAIN, SHOTS, TARGETS, N, 'balance'):.4f}")

# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp009.telemetry.control.jsonl"
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
    print("FATAL: exp009 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))

runs = {}
for budget in BUDGETS:
    telem = LAB / "experiments" / f"exp009.telemetry.budget{budget}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=12, pop=16, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY, budget=budget,
                     telemetry_path=str(telem), mutate_fn=mutate_fn,
                     targets=TARGETS, n_qubits=N, mode="balance",
                     seed_genome=SEED_GENOME)
    champ = res["champion"]
    first_ok = next((r["gen"] for r in res["curve"]
                     if r["verify_p"] >= 0.45), None)
    champ_lens = [len(r["genome"]) for r in res["curve"] if r["genome"]]
    runs[str(budget)] = {
        "budget": budget,
        "seed_genome": SEED_GENOME,
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_verify_ge_045_gen": first_ok,
        "max_champion_len_seen": max(champ_lens) if champ_lens else None,
        "curve": res["curve"],
    }
    print(f"budget={budget}: champion={json.dumps(champ.genome)} "
          f"len={len(champ.genome)} train={champ.train_p:.3f} "
          f"verify={champ.verify_p:.3f} first_ge_045_gen={first_ok} "
          f"max_len_seen={runs[str(budget)]['max_champion_len_seen']}")

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "n_qubits": N,
    "targets": list(TARGETS),
    "lane": "seedA GHZ3 skeleton, restrict=('replace','indel')",
    "control_reproduces_exp001": control_ok,
    "success_threshold_verify_balance": 0.45,
    "runs": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp009.results.json")
