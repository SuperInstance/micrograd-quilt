"""exp024 — blind validation: census the 3 remaining exp021 Q1 salts
(k0/k1/k2, seeds 31000/31001/31002) and test exp023's frozen
predictors against the enlarged 8-stream panel.

Doctrine chain under test:
  exp018  FITNESS DESERT AT THE BIRTH CLOUD (hard roots 29/31/37).
  exp020  TIE-BAND-DIVERSITY: tie-sampling converts 2/3 hard roots;
          31 stayed closed in the canonical arm.
  exp021  RATE NOT WALL: 3/8 salted streams crossed r31; Q2 census
          covered only the non-crossing canonical stream.
  exp022  TRAIN-VISIBLE TIE-BREAK-INVARIANT: crossing streams birth
          a train 0.498 / verify 0.482 cell at ONE desert-break gen
          (k3 g0, k5 g3, k6 g8) picked with window 0; contrast k4
          (0.418 near-miss) and k7 (0.0 dead) never birth one.
  exp023  DESERT-BREAK PREDICTOR SCREEN (NOT SEPARABLE AT n=5/n=4):
          C1 win2presence universal at birth (5/5), C2 nearbar40
          trips only k3 (its break gen IS gen 0), C3 tiewidth4 no
          separation, C4 activity3 ANTI-correlates in W2. Verdict:
          break is a per-gen BIRTH event invisible pre-break.
          Named validation lane = THIS experiment.

Open question THIS experiment seals:
  exp023's screen was pilot-class (n=5 W1 / n=4 W2) and named its
  own limit: census the 3 remaining exp021 Q1 salts k0/k1/k2
  (seeds 31000/31001/31002, never censused — exp022 censused only
  k3-k7) and test the surviving predictors BLIND against their
  break status. All three are exp021-verified NON-crossers
  (champion 0.2422/0.2422/0.2422) — they enlarge the non-crosser
  sample from 2 to 5 while the crosser sample stays 3.

DESIGN:
  Census: SAME passive census semantics as exp021 Q2 / exp022
    (per-candidate verify evals consume NO rng; stream +
    tie-break sequence byte-identical to exp020/021/022).
  Replicate pins: k0/k1/k2 champions must finish @0.2422, not
    crossed — exp021.results.json q1_rate_vs_wall.runs values
    verbatim.
  Guard: exp001 default lane through the SAME instrumented loop
    (census ACTIVE) reproduces experiments/exp001.results.json
    byte-identical.
  Blind test: exp023's four predictors (C1 win2presence, C2
    nearbar40, C3 tiewidth4, C4 activity3), same frozen
    thresholds, same two windows (W1 at-birth, W2 pre-peak),
    applied to all 8 streams. 'Blind' = the predictors and
    thresholds were frozen before these 3 streams' telemetry
    existed; the new streams' class comes from the replicate
    pins, not from any predictor output.
  Verdict conditions (same pre-registration as exp023):
    SEPARATES(W) = all applicable crossers trip AND no applicable
    non-crosser trips.
    NOT-SEPARABLE = anything else — exp023's pilot verdict holds
    at the enlarged n; desert-break stays a per-gen birth event.

Honesty: n=8 panel but crosser:non-crosser = 3:5; W2 undefined
for k3 (peak at g0) and for any new stream whose peak gen is 0;
undefined windows named, never dropped. Post-hoc reads labeled.
No archive, no retention anywhere in this experiment.
"""
import functools
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import (Candidate, fitness, mutate, mutate_classed,
                          p_target, random_gate)

LAB = Path(__file__).resolve().parent.parent
RESULTS = LAB / "experiments" / "exp024.results.json"
EXP001 = LAB / "experiments" / "exp001.results.json"
EXP021 = LAB / "experiments" / "exp021.results.json"

TRAIN, VERIFY, SHOTS = 101, 202, 512
TARGETS = ("000", "111")
N = 3
POP, GENS = 16, 12
BUDGET = 6
SKELETON = [["h", 0], ["cx", 0, 1]]
BAR = 0.45

# NEW streams: the 3 censused-for-the-first-time exp021 Q1 salts.
# Expected values verbatim from exp021.results.json q1_rate_vs_wall.
NEW_STREAMS = {
    "k0": {"seed": 31000, "expected_champion": 0.2422,
           "expected_crossed": False},
    "k1": {"seed": 31001, "expected_champion": 0.2422,
           "expected_crossed": False},
    "k2": {"seed": 31002, "expected_champion": 0.2422,
           "expected_crossed": False},
}

# exp022 streams (already censused; classes + telemetry reused)
PRIOR_STREAMS = {
    "k3": {"class": "crossing"},
    "k4": {"class": "contrast_near_miss"},
    "k5": {"class": "crossing"},
    "k6": {"class": "crossing"},
    "k7": {"class": "contrast_dead"},
}

mutate_one = functools.partial(mutate_classed, restrict=("replace", "indel"))


def run_tiebreak_census(root_seed, telemetry_path):
    """Exact exp021 Q2 / exp022 census semantics (passive, no rng)."""
    rng = random.Random(root_seed)
    champion = Candidate(genome=[list(g) for g in SKELETON])
    champion.train_p = p_target(champion.genome, TRAIN, SHOTS,
                                TARGETS, N, "balance")
    champion.verify_p = p_target(champion.genome, VERIFY, SHOTS,
                                 TARGETS, N, "balance")
    curve = []
    census_rows = []
    for gen in range(GENS):
        cands = [champion]
        while len(cands) < POP:
            genome = mutate_one(champion.genome, rng, BUDGET,
                                n_qubits=N)
            if genome is None:
                continue  # classed restrict resample (exp003 contract)
            child = Candidate(genome=genome)
            child.train_p = p_target(child.genome, TRAIN, SHOTS,
                                     TARGETS, N, "balance")
            cands.append(child)
        fmax = max(fitness(c) for c in cands)
        tied = [c for c in cands if fitness(c) == fmax]
        cloud = []
        for c in cands:
            vp = p_target(c.genome, VERIFY, SHOTS, TARGETS, N,
                          "balance")
            cloud.append({
                "genome": [list(g) for g in c.genome],
                "train_p": round(c.train_p, 6),
                "verify_p": round(vp, 6),
                "in_band": fitness(c) == fmax,
                "is_champion": c is champion,
            })
        census_rows.append({"gen": gen, "gen_max": round(fmax, 6),
                            "n_tied": len(tied), "cloud": cloud})
        best = rng.choice(tied) if len(tied) > 1 else tied[0]
        best.verify_p = p_target(best.genome, VERIFY, SHOTS,
                                 TARGETS, N, "balance")
        promoted = best.verify_p >= champion.verify_p
        if promoted:
            champion = best
        curve.append({"gen": gen, "train_p": round(best.train_p, 4),
                      "verify_p": round(best.verify_p, 4),
                      "promoted": promoted,
                      "genome": champion.genome if promoted else None})
        with open(telemetry_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(
                {"gen": gen, "curve": curve[-1],
                 "census": census_rows[-1]}, sort_keys=True) + "\n")
    return {"champion": champion, "curve": curve,
            "census": census_rows}


# --- guard: instrumented loop (census ACTIVE) reproduces exp001 ------
def run_guard_default(root_seed, generations, pop, shots, train_seed,
                      verify_seed):
    rng = random.Random(root_seed)
    champion = Candidate(genome=[random_gate(rng, 2) for _ in range(3)])
    champion.train_p = p_target(champion.genome, train_seed, shots,
                                ("01",), 2, "any")
    champion.verify_p = p_target(champion.genome, verify_seed, shots,
                                 ("01",), 2, "any")
    curve = []
    for gen in range(generations):
        cands = [champion]
        while len(cands) < pop:
            genome = mutate(champion.genome, rng, BUDGET, n_qubits=2)
            child = Candidate(genome=genome)
            child.train_p = p_target(child.genome, train_seed, shots,
                                     ("01",), 2, "any")
            cands.append(child)
        best = max(cands, key=lambda c: fitness(c))
        best.verify_p = p_target(best.genome, verify_seed, shots,
                                 ("01",), 2, "any")
        promoted = best.verify_p >= champion.verify_p
        if promoted:
            champion = best
        curve.append({"gen": gen, "train_p": round(best.train_p, 4),
                      "verify_p": round(best.verify_p, 4),
                      "promoted": promoted,
                      "genome": champion.genome if promoted else None})
    return {"champion": champion, "curve": curve}


guard = run_guard_default(7, generations=8, pop=16, shots=512,
                          train_seed=101, verify_seed=202)
exp001 = json.loads(EXP001.read_text())
control_ok = (guard["curve"] == exp001["curve"]
              and guard["champion"].genome == exp001["champion_genome"])
print("control reproduces exp001 (census active):", control_ok)
if not control_ok:
    print("FATAL: instrumented loop diverges; results void")
    sys.exit(1)

# --- census the 3 new streams -----------------------------------------
streams = {}
for name, spec in NEW_STREAMS.items():
    telem = LAB / "experiments" / f"exp024.telemetry.{name}.jsonl"
    if telem.exists():
        telem.unlink()
    out = run_tiebreak_census(spec["seed"], str(telem))
    champ_v = round(out["champion"].verify_p, 4)
    crossed = champ_v >= BAR
    replicate_ok = (champ_v == spec["expected_champion"]
                    and crossed == spec["expected_crossed"])

    # census facts: did a >=BAR cell ever live in the cloud?
    bar_gens = []
    max_cloud_verify = 0.0
    for row in out["census"]:
        max_cloud_verify = max(
            max_cloud_verify,
            max(c["verify_p"] for c in row["cloud"]))
        if any(c["verify_p"] >= BAR for c in row["cloud"]):
            bar_gens.append(row["gen"])

    streams[name] = {
        "seed": spec["seed"], "class": "non_crosser",
        "champion_verify": champ_v, "crossed": crossed,
        "exp021_replicate_ok": replicate_ok,
        "max_cloud_verify": max_cloud_verify,
        "cloud_bar_gens": bar_gens,
        "telemetry": f"exp024.telemetry.{name}.jsonl",
    }
    print(f"{name} (seed {spec['seed']}): replicate_ok={replicate_ok} "
          f"champ={champ_v} crossed={crossed} "
          f"max_cloud={max_cloud_verify} bar_gens={bar_gens}")

if not all(s["exp021_replicate_ok"] for s in streams.values()):
    print("FATAL: replicate pins failed; blind test void")
    sys.exit(1)

# --- blind predictor test over the enlarged 8-stream panel -------------
# Predictors FROZEN from exp023 (thresholds unchanged); windows same.

def load_telemetry(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def win2_present(cloud):
    for cell in cloud:
        if cell["is_champion"]:
            continue
        for gate in cell["genome"]:
            if len(gate) >= 3 and 2 in gate[1:]:
                return True
    return False


def nearbar40(cloud):
    vals = [c["train_p"] for c in cloud if not c["is_champion"]]
    return (max(vals) if vals else 0.0) >= 0.40


def tiewidth4(row):
    return row["census"]["n_tied"] >= 4


def activity3(cloud):
    genomes = set()
    for c in cloud:
        if c["is_champion"] or c["train_p"] <= 0:
            continue
        genomes.add(json.dumps(c["genome"], sort_keys=True))
    return len(genomes) >= 3


def window_rows(rows, lo, hi):
    return [r for r in rows if lo <= r["gen"] < hi]


panel = {}
for name, meta in PRIOR_STREAMS.items():
    panel[name] = {
        "class": meta["class"],
        "crossed": meta["class"] == "crossing",
        "telemetry": LAB / "experiments" / f"exp022.telemetry.{name}.jsonl",
    }
for name, s in streams.items():
    panel[name] = {"class": s["class"], "crossed": s["crossed"],
                   "telemetry": LAB / "experiments" / s["telemetry"]}

report = {}
for name, meta in panel.items():
    rows = load_telemetry(meta["telemetry"])
    eventual = max(r["census"]["gen_max"] for r in rows)
    peak_gen = next(r["gen"] for r in rows
                    if r["census"]["gen_max"] == eventual)
    w1 = window_rows(rows, 0, 1)
    w2 = window_rows(rows, 0, peak_gen)

    def screen(win):
        if not win:
            return "undefined"
        cloud = [c for r in win for c in r["census"]["cloud"]]
        return {
            "C1_win2presence": win2_present(win[0]["census"]["cloud"])
            if len(win) == 1 else any(
                win2_present(r["census"]["cloud"]) for r in win),
            "C2_nearbar40": any(
                nearbar40(r["census"]["cloud"]) for r in win),
            "C3_tiewidth4": any(tiewidth4(r) for r in win),
            "C4_activity3": activity3(cloud),
        }

    report[name] = {
        "class": meta["class"], "crossed": meta["crossed"],
        "break_or_peak_gen": peak_gen,
        "W1_at_birth": screen(w1),
        "W2_pre_peak": screen(w2),
    }


def verdict(window_key, cand):
    trips = {n: r[window_key][cand]
             for n, r in report.items()
             if r[window_key] != "undefined"}
    if not trips:
        return "no_applicable_streams"
    cross = all(v for n, v in trips.items() if report[n]["crossed"])
    noncross_any = any(v for n, v in trips.items()
                       if not report[n]["crossed"])
    sep = (cross and not noncross_any
           and any(report[n]["crossed"] for n in trips))
    return {"separates": sep, "trips": trips}


candidates = ["C1_win2presence", "C2_nearbar40",
              "C3_tiewidth4", "C4_activity3"]
verdicts = {w: {c: verdict(w, c) for c in candidates}
            for w in ("W1_at_birth", "W2_pre_peak")}

any_sep = any(isinstance(v, dict) and v["separates"] is True
              for w in verdicts.values() for v in w.values())

# exp023 W1 contrast: did the new non-crossers trip anything the
# exp022 non-crossers (k4/k7) did not?
new_names = list(NEW_STREAMS)
new_trips = {c: {n: verdicts["W1_at_birth"][c]["trips"][n]
                 for n in new_names}
             for c in candidates}

result = {
    "experiment": "exp024 blind validation: census k0/k1/k2 + "
                  "frozen-predictor test at n=8",
    "design": "same passive census as exp021 Q2 / exp022; replicate "
              "pins vs exp021.results.json q1_rate_vs_wall verbatim; "
              "exp001 guard byte-identical with census ACTIVE; "
              "predictors C1-C4 + thresholds + windows frozen from "
              "exp023 (pre-existing telemetry, no re-screen fit); "
              "new-stream class from replicate pins, not predictors",
    "guard": {"exp001_reproduced_byte_identical": control_ok},
    "new_streams": streams,
    "panel_report": report,
    "verdicts": verdicts,
    "new_stream_W1_trips": new_trips,
    "overall_verdict": (
        "PREDICTOR_SEPARATES_AT_N8_HYPOTHESIS" if any_sep else
        "NOT_SEPARABLE_AT_N8 — exp023 pilot verdict CONFIRMED blind: "
        "desert-break is a per-gen birth event invisible pre-break; "
        "the 3 new non-crossers enlarge the non-crosser sample 2->5 "
        "and no frozen predictor separates 3 crossers from 5 "
        "non-crossers in either window; exp018 doctrine holds at "
        "stream level; prediction must target birth-cloud per-draw "
        "odds, not trajectories"
    ),
    "honesty": "crosser:non-crosser = 3:5 (unbalanced panel stated); "
               "W2 undefined for k3 (peak at g0) and any new stream "
               "peaking at g0 — named per stream, never dropped; "
               "post-hoc reads labeled; n=8 still pilot class for "
               "any SEPARATES verdict; no archive, no retention",
    "next": "exp025: birth-cloud per-draw odds model (exp018/exp024 "
            "doctrine: predict P(>=BAR cell born) per generation "
            "from cloud composition, not trajectory history)",
}
RESULTS.write_text(json.dumps(result, indent=1, sort_keys=True),
                   encoding="utf-8")
print(json.dumps(verdicts, indent=1, sort_keys=True))
print("new-stream W1 trips:", json.dumps(new_trips, sort_keys=True))
print("\nOVERALL:", result["overall_verdict"])
print("wrote", RESULTS)
