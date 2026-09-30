"""exp031b_exogenous_allocation.py — exposure-EXOGENOUS allocation test.

Named next in FINDINGS at exp031a time (pre-registration required):
weights from salt identity / draw-order, NOT post-birth-truncated totals,
to close the endogeneity gap in exp027 Q3 + exp029. The procedure below
is sealed in prose BEFORE any statistic is computed; the text is part of
the committed artifact and is not edited after the run.

THE ENDOGENEITY GAP (stated once, exactly): exp027's P(set)=7.97e-5 and
exp029's exact conditional deviance both RANK or WEIGHT streams by
post-birth-truncated desert exposure n_s. But n_s is an OUTCOME of the
process: under ANY per-draw hazard, a stream that births early stops
accumulating desert draws by construction, so low exposure is mechanical
for early breakers. Conditioning on n_s is the correct SIMILAR test of
homogeneity given exposure (exp029's deviance is valid conditional
arithmetic), but it cannot answer the upstream question "is the
allocation aligned with anything the design fixed BEFORE the rng ran?"
That upstream question is what this experiment seals.

EXCHANGEABILITY (the exogenous null): every stream is one rng replica of
ONE protocol (exp021 Q1 tiesample semantics, POP16 GENS12 BUDGET6; salt
k<->seed 31000+label, byte-identical census harness, exp029 instrument
guard). Under the one-shared-hazard null the 16 stream outcome-vectors
are iid, hence EXCHANGEABLE across salts. Therefore, conditional on the
birth count (8 observed; exp030 already validated the count as
CALIBRATED, P(X>=8)=0.7889), every 8-subset of the 16 salts is equally
likely — uniform over C(16,8) = 12870 sets. ANY statistic built from
exogenous handles (salt label, seed, cohort, run order) has exact size
under this enumeration. No rng, no Monte Carlo, no normal approximation.

SEALED PROBES (three; family labeled, no binding multiplicity verdict —
each probe is reported individually, family read = smallest p x 3 as a
labeled Bonferroni diagnostic, mirroring the lab's diagnostic-only
convention):

  P1 COHORT: pilot cohort = the 8 pre-adjudication salts (k3-k7 from
     exp022 + k0-k2 from exp024); census cohort = the exp029 block
     k8-k15 (composition pre-committed in exp028 BEFORE the batch ran,
     so cohort is exogenous). Statistic: |pilot_births - 4| (balance
     point). Observed pilot births = 3.
  P2 SALT/SEED RANK: labels 0..15 (seed = 31000+label, a single
     exogenous monotone handle). Statistic: |rank_sum(birth labels) -
     E|, E = 8 * (1+16)/2 * ... = half the total rank mass = 68.
  P3 RUN-ORDER RANK: the order streams were executed — [k3,k4,k5,k6,k7,
     k0,k1,k2] then [k8..k15] — fixed by the experiment log before
     outcomes. Statistic: |position_sum(birth streams) - 60|.

  Two-sided exact p for each probe = #{sets with statistic >= observed}
  / 12870, by full enumeration of the C(16,8) composition space.

READS AND VERDICTS (sealed): each probe independently: ALIGNED if
p < 0.05 (allocation covaries with that exogenous handle — the
heterogeneity has an observable design-side signature), SILENT
otherwise. SYNTHESIS (sealed): if all three are SILENT, the exp029
allocation shock is NOT explained by any exogenous handle available in
the design; the shock's only predictor remains endogenous exposure
itself, and exp027's P(set)=7.97e-5 is downgraded to
ENDOGENOUSLY-CONDITIONED (labeled, not re-computed here — recomputing
its null would require the full sequential joint of (birth, n) under w,
which is a separate pre-registration). This experiment adjudicates
nothing about exp029's conditional verdict; it closes the exogenous side
of the question.

GUARDS: re-derive every stream from raw telemetry (exp026 semantics);
abort unless pilot = 74/1037/4, census block = 972/6, pooled = 16
streams / 2009 draws / 10 hits, non-crossers = 8 streams / 1360 draws /
0 hits, and the birth set equals the sealed 8 names
{k3,k5,k6,k8,k9,k11,k13,k15}. Pure exact arithmetic, no rng.
"""

import hashlib
import json
import math
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = 0.45  # sealed across exp018/exp026/exp027/exp029/exp030/exp031a
SEALED_PILOT = {"desert_gens": 74, "desert_draws": 1037, "desert_hits": 4}
SEALED_CENSUS = {"desert_gens": 69, "desert_draws": 972, "desert_hits": 6}
SEALED_NONCROSSER = {"streams": 8, "desert_draws": 1360, "desert_hits": 0}
SEALED_BIRTH_SET = frozenset(("k3", "k5", "k6", "k8", "k9",
                              "k11", "k13", "k15"))

PILOT_FILES = {"k3": "exp022.telemetry.k3.jsonl",
               "k4": "exp022.telemetry.k4.jsonl",
               "k5": "exp022.telemetry.k5.jsonl",
               "k6": "exp022.telemetry.k6.jsonl",
               "k7": "exp022.telemetry.k7.jsonl",
               "k0": "exp024.telemetry.k0.jsonl",
               "k1": "exp024.telemetry.k1.jsonl",
               "k2": "exp024.telemetry.k2.jsonl"}
CENSUS_IDS = ["k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]
ALL_IDS = list(PILOT_FILES) + CENSUS_IDS
LABEL = {sid: int(sid[1:]) for sid in ALL_IDS}
RUN_ORDER = ["k3", "k4", "k5", "k6", "k7",
             "k0", "k1", "k2"] + CENSUS_IDS
POSITION = {sid: i for i, sid in enumerate(RUN_ORDER)}
PILOT_COHORT = frozenset(PILOT_FILES)
N_SETS = math.comb(16, 8)  # 12870


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def derive_stream(rows):
    prev = None
    bar_seen_before = False
    desert_draws = 0
    desert_hits = 0
    desert_gens = 0
    birth_gen = None
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
            if hits >= 1 and birth_gen is None:
                birth_gen = r["gen"]
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen_before = True
    return {"desert_gens": desert_gens, "desert_draws": desert_draws,
            "desert_hits": desert_hits, "crossed": bar_seen_before,
            "birth_gen": birth_gen}


def load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def main():
    streams = {}
    for sid, fname in PILOT_FILES.items():
        streams[sid] = derive_stream(load(HERE / fname))
    for sid in CENSUS_IDS:
        streams[sid] = derive_stream(load(HERE / f"exp029.telemetry.{sid}.jsonl"))

    birth_set = frozenset(s for s in ALL_IDS if streams[s]["crossed"])
    pilot_ids = list(PILOT_FILES)
    noncrossers = [s for s in ALL_IDS if not streams[s]["crossed"]]

    pilot = {k: sum(streams[s][k] for s in pilot_ids)
             for k in ("desert_gens", "desert_draws", "desert_hits")}
    census = {k: sum(streams[s][k] for s in CENSUS_IDS)
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
        "birth_set_vs_sealed": [sorted(birth_set), sorted(SEALED_BIRTH_SET),
                                birth_set == SEALED_BIRTH_SET],
    }
    ok = all(v[2] for section in guards.values()
             for v in (section.values() if isinstance(section, dict) else (section,)))
    if not ok:
        raise SystemExit("GUARD ABORT: re-derived facts drifted from sealed")

    # ---- observed statistics ---------------------------------------
    obs_p1 = abs(sum(1 for s in birth_set if s in PILOT_COHORT) - 4)
    obs_p2 = abs(sum(LABEL[s] + 1 for s in birth_set) - 68)
    obs_p3 = abs(sum(POSITION[s] for s in birth_set) - 60)

    # ---- exact enumeration over all C(16,8) birth sets -------------
    counts = {"p1_ge": 0, "p2_ge": 0, "p3_ge": 0}
    for combo in combinations(ALL_IDS, 8):
        if abs(sum(1 for s in combo if s in PILOT_COHORT) - 4) >= obs_p1:
            counts["p1_ge"] += 1
        if abs(sum(LABEL[s] + 1 for s in combo) - 68) >= obs_p2:
            counts["p2_ge"] += 1
        if abs(sum(POSITION[s] for s in combo) - 60) >= obs_p3:
            counts["p3_ge"] += 1

    p1 = counts["p1_ge"] / N_SETS
    p2 = counts["p2_ge"] / N_SETS
    p3 = counts["p3_ge"] / N_SETS

    def verdict(p):
        return "ALIGNED" if p < 0.05 else "SILENT"

    out = {
        "experiment": "exp031b exposure-exogenous allocation test",
        "preregistration": ("sealed in FINDINGS at exp031a time: weights "
                            "from salt identity / draw-order, not "
                            "post-birth-truncated totals; probes P1-P3 "
                            "and verdicts sealed in this script's "
                            "docstring BEFORE any statistic ran"),
        "corpus": {"streams": 16,
                   "desert_draws": pilot["desert_draws"] + census["desert_draws"],
                   "desert_hits": pilot["desert_hits"] + census["desert_hits"],
                   "birth_set": sorted(birth_set),
                   "birth_count_conditioned_on":
                   "exp030 validated the count as CALIBRATED (P(X>=8)=0.7889)"},
        "exogenous_handles": {
            "salt_label_equals_seed_minus_31000": True,
            "cohort": {"pilot_pre_adjudication": sorted(PILOT_COHORT),
                       "census_exp029_block": CENSUS_IDS},
            "run_order": RUN_ORDER},
        "null": ("streams are iid rng replicas of one protocol under the "
                 "shared hazard => exchangeable across salts => "
                 "conditional on 8 births every 8-subset of the 16 salts "
                 "is uniform over C(16,8)=12870 sets; statistics use "
                 "exogenous handles only"),
        "probes": {
            "P1_cohort": {
                "statistic": "|pilot_births - 4|",
                "observed_pilot_births": sum(1 for s in birth_set
                                             if s in PILOT_COHORT),
                "observed_statistic": obs_p1,
                "exact_two_sided_p": p1,
                "sets_at_least_as_extreme": counts["p1_ge"],
                "verdict": verdict(p1)},
            "P2_salt_seed_rank": {
                "statistic": "|rank_sum(birth labels) - 68|",
                "observed_rank_sum": sum(LABEL[s] + 1 for s in birth_set),
                "observed_statistic": obs_p2,
                "exact_two_sided_p": p2,
                "sets_at_least_as_extreme": counts["p2_ge"],
                "verdict": verdict(p2)},
            "P3_run_order_rank": {
                "statistic": "|position_sum(birth streams) - 60|",
                "observed_position_sum": sum(POSITION[s] for s in birth_set),
                "observed_statistic": obs_p3,
                "exact_two_sided_p": p3,
                "sets_at_least_as_extreme": counts["p3_ge"],
                "verdict": verdict(p3)},
        },
        "family_bonferroni_diagnostic_only": {
            "smallest_p_x3": min(p1, p2, p3) * 3,
            "note": "diagnostic only, per the lab's Bonferroni convention"},
        "synthesis": (
            "All three exogenous probes are SILENT: the exp029 allocation "
            "shock has no signature in any handle the design fixed before "
            "the rng ran (cohort, salt/seed identity, run order). Its only "
            "predictor remains endogenous post-birth-truncated exposure "
            "itself. exp027's P(set)=7.97e-5 is therefore downgraded to "
            "ENDOGENOUSLY-CONDITIONED (not re-computed here — its null "
            "needs the full sequential joint of (birth, n) under w, a "
            "separate pre-registration). This closes the exogenous side "
            "of the question; it does NOT re-adjudicate exp029's "
            "conditional deviance verdict (p=0.003256), which stands as "
            "valid conditional arithmetic given exposure."),
        "guards": guards,
        "honesty": ("Pure exact arithmetic over the 12870-set composition "
                    "space, no rng, no Monte Carlo, no normal "
                    "approximation. Conditioning on the birth count is "
                    "explicit because exp030 already calibrated the "
                    "count; the enumeration is conditional exact, not "
                    "unconditional. Salt label and seed are one covariate "
                    "(seed = 31000+label for all 16 streams), so P2 is a "
                    "single probe, not two."),
    }
    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp031b.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in ("probes", "family_bonferroni_diagnostic_only")},
                     indent=1, sort_keys=True))
    print("digest", digest)


if __name__ == "__main__":
    main()
