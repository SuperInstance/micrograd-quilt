"""exp003 — mutation-class ablation: what crosses the plateau (Finding 2).

exp001 stalled at 0.502 for gens 1-3 and crossed at gen 4; the suspicion
is that discrete gate moves (replace/insert) are load-bearing and
theta-jitter is not. Same search, same named seeds, four arms:

  control       : full mutate() — must reproduce exp001 byte-for-byte
  replace-only  : gate substitution is the only applicable class
  indel-only    : insert/delete is the only applicable class
  jitter-only   : continuous rotation-angle nudges are the only class

A class that cannot apply (indel on a full/short genome, jitter with no
rotation gate in the genome) is RESAMPLED, never silently replaced by
another class — silent fallback would make the ablation a lie.

Seeds stay named in every result: root 7, train 101, verify 202, shots 512.
Nothing unseeded is ever written down as a result.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import MutationDeadlock, mutate_classed, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp003.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512

ARMS = {
    "control": None,
    "replace_only": ("replace",),
    "indel_only": ("indel",),
    "jitter_only": ("jitter",),
}

runs = {}
for arm, restrict in ARMS.items():
    telem = LAB / "experiments" / f"exp003.telemetry.{arm}.jsonl"
    if telem.exists():
        telem.unlink()
    mutate_fn = None
    if restrict is not None:
        mutate_fn = functools.partial(mutate_classed, restrict=restrict)
    deadlock = None
    try:
        res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                         train_seed=TRAIN, verify_seed=VERIFY,
                         telemetry_path=str(telem), mutate_fn=mutate_fn)
    except MutationDeadlock as exc:
        # the arm literally cannot act on this champion — that IS the
        # ablation result (recorded, never worked around silently)
        deadlock = str(exc)
        res = None
    if res is None:
        runs[arm] = {"restrict": restrict, "deadlock": deadlock}
        print(f"{arm}: DEADLOCK — {deadlock}")
        continue
    champ = res["champion"]
    first_perfect = next((r["gen"] for r in res["curve"]
                          if r["verify_p"] == 1.0), None)
    plateau_end = next((r["gen"] for r in res["curve"]
                        if r["train_p"] > 0.502), None)
    runs[arm] = {
        "restrict": restrict,
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_verify_perfect_gen": first_perfect,
        "first_move_past_0502_gen": plateau_end,
        "curve": res["curve"],
    }
    print(f"{arm}: champion={json.dumps(champ.genome)} "
          f"len={len(champ.genome)} verify_p={champ.verify_p:.3f} "
          f"first_perfect_gen={first_perfect} past_0502_gen={plateau_end}")

# control must reproduce exp001 exactly (byte-level curve + champion)
exp001 = json.loads(EXP001.read_text())
ctrl = runs["control"]
control_ok = (ctrl["curve"] == exp001["curve"]
              and ctrl["champion_genome"] == exp001["champion_genome"])
print("control reproduces exp001:", control_ok)
if not control_ok:
    print("FATAL: ablation harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "control_reproduces_exp001": control_ok,
    "arms": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp003.results.json")
