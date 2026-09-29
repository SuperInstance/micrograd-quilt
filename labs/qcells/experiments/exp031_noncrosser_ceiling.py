"""exp031_noncrosser_ceiling.py — non-crosser upper bound vs pooled hazard at census-n.

Pre-registered candidate (sealed in FINDINGS at exp030 time): exp031a — the
1360 barren non-crosser draws vs the pooled w = 10/2009. This script seals the
procedure in prose BEFORE any statistic is computed; the text is part of the
committed artifact and is not edited after the run.

CORPUS: the same pooled 16-stream census corpus used by exp029/exp030
(pilot B/C + adjudication D). No rng, no new stream runs, no MC.

RULE-1 (candidate-a decision): under the shared per-draw hazard with the
pooled point w = H/N, the 8 non-crosser streams are n0 = 1360 iid Bernoulli(w)
desert draws. OBSERVED X=0. Exact zero probability p0 = (1-w)^n0. VERDICT:
INCOMPATIBLE if p0 < 0.05; COMPATIBLE otherwise. This is deliberately a
point-null diagnostic, not a re-estimated CI test: w is the sealed pooled
point estimate from exp029, and the named candidate compared the non-crosser
UB to that point.

RULE-2 (confidence-bound read): report the exact one-sided Clopper-Pearson
upper 95% bound for 0/n0, 1 - 0.05^(1/n0), matching the 0.0022 value named
in the exp030 candidate; ALSO report the exp026-definition two-sided UB95,
1 - 0.025^(1/n0), for continuity with the earlier ceiling. READ-ONLY: both
are compared to w; no verdict hangs on a convention change.

GUARDS: re-derive every stream from raw telemetry; abort unless pilot =
74/1037/4, census block = 972/6, pooled = 16 streams/2009 draws/10 hits,
non-crossers = 8 streams/1360 draws/0 hits. Recompute w from sealed counts
only after guards pass. exp001 instrument is not re-run here; this analysis
is passive census arithmetic.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = 0.45  # sealed across exp018/exp026/exp027/exp029 — guard aborts on drift
SEALED_PILOT = {"desert_gens": 74, "desert_draws": 1037, "desert_hits": 4}
SEALED_CENSUS = {"desert_gens": 69, "desert_draws": 972, "desert_hits": 6}
SEALED_NONCROSSER = {"streams": 8, "desert_draws": 1360, "desert_hits": 0}


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def derive_stream(rows):
    prev = None
    bar_seen_before = False
    desert_draws = 0
    desert_hits = 0
    desert_gens = 0
    for r in rows:
        cloud = r["census"]["cloud"]
        keys = {genome_key(c) for c in cloud}
        newborns = list(cloud) if prev is None else \
            [c for c in cloud if genome_key(c) not in prev]
        hits = sum(1 for c in newborns if c["train_p"] >= BAR)
        if not bar_seen_before:
            desert_gens += 1
            desert_draws += len(newborns)
            desert_hits += hits
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen_before = True
    return {"desert_gens": desert_gens, "desert_draws": desert_draws,
            "desert_hits": desert_hits, "crossed": bar_seen_before}


def load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main():
    pilot_files = {"k3": "exp022.telemetry.k3.jsonl",
                   "k4": "exp022.telemetry.k4.jsonl",
                   "k5": "exp022.telemetry.k5.jsonl",
                   "k6": "exp022.telemetry.k6.jsonl",
                   "k7": "exp022.telemetry.k7.jsonl",
                   "k0": "exp024.telemetry.k0.jsonl",
                   "k1": "exp024.telemetry.k1.jsonl",
                   "k2": "exp024.telemetry.k2.jsonl"}
    census_ids = ["k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]
    streams = {}
    for sid, fname in pilot_files.items():
        streams[sid] = derive_stream(load(HERE / fname))
    for sid in census_ids:
        streams[sid] = derive_stream(load(HERE / f"exp029.telemetry.{sid}.jsonl"))

    pilot_ids = list(pilot_files)
    noncrossers = [s for s in pilot_ids + census_ids
                   if not streams[s]["crossed"]]
    crossers = [s for s in pilot_ids + census_ids if streams[s]["crossed"]]

    pilot = {k: sum(streams[s][k] for s in pilot_ids)
             for k in ("desert_gens", "desert_draws", "desert_hits")}
    census = {k: sum(streams[s][k] for s in census_ids)
              for k in ("desert_gens", "desert_draws", "desert_hits")}
    non = {k: sum(streams[s][k] for s in noncrossers)
           for k in ("desert_draws", "desert_hits")}
    guards = {
        "pilot_rederivation_vs_sealed": {
            "desert_gens": [pilot["desert_gens"], SEALED_PILOT["desert_gens"],
                            pilot["desert_gens"] == SEALED_PILOT["desert_gens"]],
            "desert_draws": [pilot["desert_draws"], SEALED_PILOT["desert_draws"],
                             pilot["desert_draws"] == SEALED_PILOT["desert_draws"]],
            "desert_hits": [pilot["desert_hits"], SEALED_PILOT["desert_hits"],
                            pilot["desert_hits"] == SEALED_PILOT["desert_hits"]]},
        "census_rederivation_vs_sealed": {
            "desert_gens": [census["desert_gens"], SEALED_CENSUS["desert_gens"],
                            census["desert_gens"] == SEALED_CENSUS["desert_gens"]],
            "desert_draws": [census["desert_draws"], SEALED_CENSUS["desert_draws"],
                             census["desert_draws"] == SEALED_CENSUS["desert_draws"]],
            "desert_hits": [census["desert_hits"], SEALED_CENSUS["desert_hits"],
                            census["desert_hits"] == SEALED_CENSUS["desert_hits"]]},
        "noncrosser_rederivation_vs_sealed": {
            "streams": [len(noncrossers), SEALED_NONCROSSER["streams"],
                        len(noncrossers) == SEALED_NONCROSSER["streams"]],
            "desert_draws": [non["desert_draws"], SEALED_NONCROSSER["desert_draws"],
                             non["desert_draws"] == SEALED_NONCROSSER["desert_draws"]],
            "desert_hits": [non["desert_hits"], SEALED_NONCROSSER["desert_hits"],
                            non["desert_hits"] == SEALED_NONCROSSER["desert_hits"]]},
    }
    ok = all(v[2] for section in guards.values() for v in section.values())
    if not ok:
        raise SystemExit("GUARD ABORT: re-derived totals drifted from sealed")

    N = pilot["desert_draws"] + census["desert_draws"]
    H = pilot["desert_hits"] + census["desert_hits"]
    w = H / N
    n0 = non["desert_draws"]
    p0 = (1 - w) ** n0
    ub95_onesided = 1 - 0.05 ** (1 / n0)
    ub95_twosided_exp026 = 1 - 0.025 ** (1 / n0)
    expected_noncrosser_hits = n0 * w

    out = {
        "experiment": "exp031a non-crosser ceiling vs pooled hazard at census-n",
        "corpus": {"streams": 16, "desert_draws": N, "desert_hits": H,
                   "w_pooled": w, "crossers": crossers, "non_crossers": noncrossers},
        "noncrosser_panel": {"streams": noncrossers, "desert_draws": n0,
                             "desert_hits": 0,
                             "expected_hits_if_pooled_w": expected_noncrosser_hits},
        "rule1_point_null_zero_hits": {
            "null": "non-crosser desert draws are Bernoulli(w=10/2009)",
            "exact_P_X_eq_0_under_null": p0,
            "alpha": 0.05,
            "verdict": "INCOMPATIBLE" if p0 < 0.05 else "COMPATIBLE",
            "read": ("zero hits in 1360 non-crosser draws is below the shared "
                     "hazard's ordinary mood at the pooled point" if p0 < 0.05 else
                     "zero hits remains compatible with the pooled point")},
        "rule2_confidence_bounds_read_only": {
            "ub95_onesided_clopper_pearson": ub95_onesided,
            "ub95_twosided_exp026_definition": ub95_twosided_exp026,
            "pooled_w": w,
            "onesided_ub_below_pooled_w": ub95_onesided < w,
            "twosided_ub_below_pooled_w": ub95_twosided_exp026 < w,
            "read": "both conventions put the non-crosser 95% ceiling below the pooled point"},
        "guards": guards,
        "honesty": ("Named exp030 candidate-a executed with its 0.0022 one-sided "
                    "UB convention, and the exp026 two-sided convention is also "
                    "reported; both are below w. This does NOT re-adjudicate "
                    "exp029 (pooled deviance p=0.003256); it is the ceiling face "
                    "of the same allocation shock. Pure exact arithmetic, no rng."),
    }
    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp031.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("corpus", "noncrosser_panel", "rule1_point_null_zero_hits",
                       "rule2_confidence_bounds_read_only")}, indent=1, sort_keys=True))
    print("digest", digest)


if __name__ == "__main__":
    main()
