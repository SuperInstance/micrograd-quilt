"""exp004 — jitter-drop policy: does dropping angle-jitter speed convergence?

exp003 (Finding 2) showed gate substitution is the entire engine and
jitter-only deadlocks at birth; exp003's fleet tile recommends dropping
pure angle-jitter when the genome class matters more than fine angles.
exp004 is the policy version of that recommendation: run the SAME
search with the jitter branch removed entirely
(mutate_classed restrict=("replace","indel") — one policy change, zero
harness change) and measure convergence vs the exp001 control.

Same named seeds: root 7, train 101, verify 202, shots 512. Nothing
unseeded is ever written down as a result. The exp001 curve+champion
reproduction guard applies to the control lane of this runner too.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp004.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512

telem = LAB / "experiments" / "exp004.telemetry.no_jitter.jsonl"
if telem.exists():
    telem.unlink()

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))
res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                 train_seed=TRAIN, verify_seed=VERIFY,
                 telemetry_path=str(telem), mutate_fn=mutate_fn)

champ = res["champion"]
first_perfect = next((r["gen"] for r in res["curve"]
                      if r["verify_p"] == 1.0), None)
plateau_end = next((r["gen"] for r in res["curve"]
                    if r["train_p"] > 0.502), None)

# guard: an unrestricted control re-run inside THIS harness config must
# still reproduce exp001 byte-for-byte (policy, not harness, changed)
ctrl_telem = LAB / "experiments" / "exp004.telemetry.control.jsonl"
if ctrl_telem.exists():
    ctrl_telem.unlink()
ctrl_res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                      train_seed=TRAIN, verify_seed=VERIFY,
                      telemetry_path=str(ctrl_telem), mutate_fn=None)
exp001 = json.loads(EXP001.read_text())
control_ok = (ctrl_res["curve"] == exp001["curve"]
              and ctrl_res["champion"].genome == exp001["champion_genome"])
print("control reproduces exp001:", control_ok)
if not control_ok:
    print("FATAL: exp004 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

ctrl_first_perfect = next((r["gen"] for r in ctrl_res["curve"]
                           if r["verify_p"] == 1.0), None)

run = {
    "policy": "drop jitter (restrict=('replace','indel'))",
    "champion_genome": champ.genome,
    "champion_len": len(champ.genome),
    "champion_train_p": champ.train_p,
    "champion_verify_p": champ.verify_p,
    "first_verify_perfect_gen": first_perfect,
    "first_move_past_0502_gen": plateau_end,
    "curve": res["curve"],
}
print(f"no_jitter: champion={json.dumps(champ.genome)} "
      f"len={len(champ.genome)} verify_p={champ.verify_p:.3f} "
      f"first_perfect_gen={first_perfect} past_0502_gen={plateau_end}")
print(f"control:   first_perfect_gen={ctrl_first_perfect}")

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "control_reproduces_exp001": control_ok,
    "runs": {
        "no_jitter": run,
        "control": {
            "policy": "full mutate() (exp001 semantics)",
            "first_verify_perfect_gen": ctrl_first_perfect,
        },
    },
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp004.results.json")
