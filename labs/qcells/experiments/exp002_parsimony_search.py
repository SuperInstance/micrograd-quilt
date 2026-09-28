"""exp002 — parsimony pressure vs the degenerate champion (Finding 1).

exp001's champion [h(1),h(1),x(0)] reaches P(01)=1.0 while carrying a
dead gate pair (h;h = identity). Nothing penalized genome length. Here
the same search, same named seeds, gains a per-gate penalty on the
TRAIN selection score only (verify promotion gate untouched):

  control  (parsimony=0.00): must reproduce the exp001 curve byte-for-byte
  pressure (parsimony=0.02): champion should shrink toward x(0) alone
  pressure (parsimony=0.05): stronger shrink, watch for fitness collapse

Seeds stay named in every result: root 7, train 101, verify 202, shots 512.
Nothing unseeded is ever written down as a result.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp002.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
PENALTIES = [0.0, 0.02, 0.05]

runs = {}
for pen in PENALTIES:
    telem = LAB / "experiments" / f"exp002.telemetry.p{pen:.2f}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), parsimony=pen)
    champ = res["champion"]
    first_perfect = next((r["gen"] for r in res["curve"]
                          if r["verify_p"] == 1.0), None)
    runs[str(pen)] = {
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_verify_perfect_gen": first_perfect,
        "curve": res["curve"],
    }
    print(f"parsimony={pen:.2f}: champion={json.dumps(champ.genome)} "
          f"len={len(champ.genome)} verify_p={champ.verify_p:.3f} "
          f"first_perfect_gen={first_perfect}")

# control must reproduce exp001 exactly (byte-level curve + champion)
exp001 = json.loads(EXP001.read_text())
ctrl = runs["0.0"]
control_ok = (ctrl["curve"] == exp001["curve"]
              and ctrl["champion_genome"] == exp001["champion_genome"])
print("control reproduces exp001:", control_ok)
if not control_ok:
    print("FATAL: parsimony=0 changed behavior; refusing to write results")
    sys.exit(1)

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "control_reproduces_exp001": control_ok,
    "parsimony_sweep": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp002.results.json")
