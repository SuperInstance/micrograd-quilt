"""exp010 — population scaling on the frozen UNSEEDED n=3 balance lane:
is the mutation-locality bottleneck beatable with more parallel draws?

exp005 froze the unaided n=3 GHZ-balance search at pop 16 (12 gens,
champion 0.000, 180 champion-local draws, zero signal hits). Finding 3's
ranked candidates: (a) GHZ-prefix seeding [exp006 CONFIRMED], (b) pop 64
for the n=3 lane [NEVER RUN], (c) curriculum [exp007 covered the n=2
control]. This experiment runs (b): the exact exp005 unaided lane
(no seed, jitter-dropped replace/indel cloud, targets ("000","111"),
mode="balance", same named seeds) at pop 32 and pop 64.

Interpretation pinned BEFORE running (anti-laundering): exp005 measured
signal density 52/2000 random genomes (2.6%). A champion-local cloud of
size P per gen that never leaves the champion's neighborhood draws from
roughly the same local move distribution regardless of P — pop scaling
multiplies DRAWS, not REACH. If pop 64 stays frozen, the locality
verdict gains its pop boundary condition (draws alone don't fix it;
you need reach — seeding, curriculum, or a wider mutator). If it
crosses, the 'frozen forever' verdicts were population-starvation, not
engine law, and exp005's Finding 3 wording needs a pop caveat.

Success = held-out balance >= 0.45 (same threshold as exp005-009).
Telemetry records per-gen champion balance so 'almost moved' is visible.
The exp001 reproduction guard runs the default lane in-harness again.
"""
import functools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import mutate_classed, run_search

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp010.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"

ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512
TARGETS = ("000", "111")
N = 3
POPS = (16, 32, 64)

# --- guard: default lane still reproduces exp001 -------------------------
ctrl_telem = LAB / "experiments" / "exp010.telemetry.control.jsonl"
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
    print("FATAL: exp010 harness changed default behavior; "
          "refusing to write results")
    sys.exit(1)

mutate_fn = functools.partial(mutate_classed, restrict=("replace", "indel"))

runs = {}
for pop in POPS:
    telem = LAB / "experiments" / f"exp010.telemetry.pop{pop}.jsonl"
    if telem.exists():
        telem.unlink()
    res = run_search(ROOT_SEED, generations=12, pop=pop, shots=SHOTS,
                     train_seed=TRAIN, verify_seed=VERIFY,
                     telemetry_path=str(telem), mutate_fn=mutate_fn,
                     targets=TARGETS, n_qubits=N, mode="balance")
    champ = res["champion"]
    first_ok = next((r["gen"] for r in res["curve"]
                     if r["verify_p"] >= 0.45), None)
    champ_balances = [r["train_p"] for r in res["curve"]]
    runs[str(pop)] = {
        "pop": pop,
        "seeded": False,
        "champion_genome": champ.genome,
        "champion_len": len(champ.genome),
        "champion_train_p": champ.train_p,
        "champion_verify_p": champ.verify_p,
        "first_verify_ge_045_gen": first_ok,
        "max_champion_train_p_seen": max(champ_balances),
        "curve": res["curve"],
    }
    print(f"pop={pop}: champion={json.dumps(champ.genome)} "
          f"train={champ.train_p:.3f} verify={champ.verify_p:.3f} "
          f"first_ge_045_gen={first_ok} "
          f"max_train_seen={runs[str(pop)]['max_champion_train_p_seen']:.4f}")

out = {
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY,
              "shots": SHOTS},
    "n_qubits": N,
    "targets": list(TARGETS),
    "lane": "unaided (no seed), restrict=('replace','indel'), "
            "mode='balance' — exact exp005 lane, pop swept",
    "control_reproduces_exp001": control_ok,
    "success_threshold_verify_balance": 0.45,
    "exp005_reference": "pop=16 frozen 12 gens, champion 0.000, "
                        "signal density 2.6% (52/2000)",
    "runs": runs,
}
RESULTS.write_text(json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp010.results.json")
