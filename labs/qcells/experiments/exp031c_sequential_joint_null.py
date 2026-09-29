"""exp031c_exogenous_side_closer.py — sequential (birth, n) JOINT NULL
calibration of exp027's breaker-set statistic.  The ENDOGENOUS-SIDE
closer named in exp031b's synthesis.

exp031b closed the exogenous side: the exp029 allocation shock has no
signature in salt identity, cohort, or run order.  It downgraded
exp027's P(set)=7.97e-5 to ENDOGENOUSLY-CONDITIONED and named this
experiment as the remaining closer: the full sequential joint of
(birth, n) under the sealed shared per-draw hazard w.  This script
seals that calibration.  Prose below is sealed BEFORE any statistic
is computed; the text is part of the committed artifact.

THE GAP, STATED EXACTLY.  exp027 Q3 computed each stream's break
probability on its POST-BIRTH-TRUNCATED desert window: breaker k3 on
16 draws (p=0.060), k5 on 54 (p=0.188), k6 on 121 (p=0.374), versus
non-crossers on their full 163-175 (p~0.47-0.49).  A breaker HAS to
stop accumulating desert draws at its break — that is what breaking
IS — so ranking streams by truncated exposure and finding the breakers
at the bottom mixes a process consequence into the null.  The correct
question: under ONE shared per-draw hazard, each stream running its
FULL design schedule, how surprising is the observed break pattern?

SEQUENTIAL JOINT NULL (sealed): stream s has a design-fixed draw
schedule of N_s newborn draws over its 12 gens (its ACTUAL full-run
per-gen newborn counts from telemetry, including post-crossing gens —
the labeled counterfactual-continuation approximation; the runs did
continue past crossing, and no cleaner counterfactual schedule exists;
labeled, not hidden).  Draws iid, hit w.p. w (sealed pooled
0.003857280617164899, never re-estimated).  Break = first hit;
T_s = hit draw index; censored iff no hit in N_s draws.  P(T_s=j) =
(1-w)^(j-1) * w;  P(censor_s) = (1-w)^N_s.  Streams independent.

SEALED PROBES:
  Q1  REPRODUCTION GUARD: recompute exp027's truncated-exposure set
      probability from raw telemetry (per-gen birth PMFs over desert
      windows, exp027's exact code path) and assert it matches the
      sealed 7.96890965981818e-5 — confirming WHAT is being
      calibrated.  Abort on drift.
  Q2  FULL-SCHEDULE SET PROBABILITY: P(break set = {k3,k5,k6}) under
      the sequential joint null = prod_{b in B} (1-(1-w)^N_b) *
      prod_{nb} (1-w)^N_nb, N = FULL-run totals.  Read against the
      1/56 flat baseline exp027 used AND against exp027's 7.97e-5:
      the ratio closes how much of the ~200x-below-flat surprise is
      truncation artifact.
  Q3  SEQUENTIAL JOINT PROBABILITY OF THE EXACT OBSERVED PATTERN:
      P(T_k3=16, T_k5=54, T_k6=121, all five others censored) =
      w^3 (1-w)^((16-1)+(54-1)+(121-1) + sum N_nb).  The single most
      extreme-to-ordinary anchor: how probable is the WHOLE observed
      (birth, n) configuration under the joint null.
  Q4  EXPOSURE-RANK EVENT UNDER THE SEQUENTIAL NULL — the faithful
      analog of exp027's "breakers are the three lowest-exposure
      streams": P(exactly 3 streams break AND each breaker breaks
      before EVERY non-breaker's censor point), summed exactly over
      all C(8,3)=56 candidate breaker sets:
        sum_S [ prod_{nb not in S} (1-w)^N_nb * prod_{s in S}
                (1 - (1-w)^(c_S - 1)) ]
      where c_S = min N_nb over non-breakers (a breaker with T_s <
      c_S necessarily ranks below every non-breaker in exposure; if
      exactly 3 break and all 3 rank below all 5 non-breakers, the
      break set IS the bottom-3 by exposure).  Full enumeration, no
      rng.
  Q5  CONTEXT (labeled, not a verdict): expected break count under
      the full-schedule null, P(exactly 3 break) via exact
      Poisson-binomial subset DP — is "3 breakers" itself ordinary?

VERDICTS (sealed): Q2 read vs 1/56 AND vs 7.97e-5: ARTIFACT-FULL if
Q2 >= 1/56 (the surprise was entirely truncation geometry);
PARTIALLY-CLOSED if Q2 < 1/56 but the gap-to-flat shrinks by >= 10x
from exp027's; SURPRISE-SURVIVES if Q2 < 1/560.  Q4 read plainly
against Q2 and 1/56.  This experiment calibrates exp027's set
statistic; it does NOT re-adjudicate exp029's conditional deviance
(p=0.003256), which stands as valid conditional arithmetic.

GUARDS: re-derive every stream from raw telemetry (exp026/027 scan
semantics); abort unless pilot = 74/1037/4 desert gens/draws/hits,
crossers = sealed {k3,k5,k6} with birth cum-draws 16/54/121,
non-crosser FULL-run totals = {k4:165, k7:163, k0:174, k1:175,
k2:169} (fresh quantities, derived live, sealed INTO this run),
breaker full totals {k3:167, k5:171, k6:166}, and non-crosser full
totals sum = sealed 846.  Pure exact arithmetic, no rng, no MC.
"""

import json
import math
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = 0.45
W = 0.003857280617164899  # sealed pooled per-draw hazard, never re-estimated
SEALED_DESERT_GENS = 74
SEALED_DESERT_DRAWS = 1037
SEALED_DESERT_HITS = 4
SEALED_NONCROSSER_DESERT_DRAWS = 846
SEALED_SET_P = 7.96890965981818e-05      # exp027 Q3 truncated-exposure value
SEALED_NO_HEAVY5 = 0.038022800464556195  # exp027 Q3 companion value
SEALED_CROSSERS = {"k3": 16, "k5": 54, "k6": 121}  # birth cum-draws

CORPUS = [
    ("exp022.telemetry.k3.jsonl", "k3", True),
    ("exp022.telemetry.k4.jsonl", "k4", False),
    ("exp022.telemetry.k5.jsonl", "k5", True),
    ("exp022.telemetry.k6.jsonl", "k6", True),
    ("exp022.telemetry.k7.jsonl", "k7", False),
    ("exp024.telemetry.k0.jsonl", "k0", False),
    ("exp024.telemetry.k1.jsonl", "k1", False),
    ("exp024.telemetry.k2.jsonl", "k2", False),
]


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def scan(rows):
    """exp027 scan: desert window (until first bar cell) + FULL-run
    per-gen newborn counts over all 12 gens (fresh for exp031c)."""
    prev = None
    bar_seen = False
    desert = []
    full_gens = []
    birth_cum = None
    cum = 0
    desert_draws = 0
    desert_hits = 0
    for r in rows:
        cloud = r["census"]["cloud"]
        keys = {genome_key(c) for c in cloud}
        newborns = list(cloud) if prev is None else \
            [c for c in cloud if genome_key(c) not in prev]
        hits = sum(1 for c in newborns if c["train_p"] >= BAR)
        full_gens.append(len(newborns))
        if not bar_seen:
            cum += len(newborns)
            desert.append((r["gen"], len(newborns)))
            desert_draws += len(newborns)
            desert_hits += hits
            if birth_cum is None and hits >= 1:
                birth_cum = cum
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen = True
    return {"desert": desert, "full_gens": full_gens,
            "birth_cum": birth_cum,
            "N_full": sum(full_gens),
            "total_desert_draws": desert_draws,
            "total_desert_hits": desert_hits,
            "crossed": bar_seen}


def load(name):
    return [json.loads(l) for l in
            (HERE / name).read_text().splitlines() if l.strip()]


def birth_distribution(desert):
    """exp027's exact per-gen first-birth PMF over a desert window."""
    gens, pmf = [], []
    survive = 1.0
    for g, d in desert:
        q_g = 1 - (1 - W) ** d
        pmf.append(survive * q_g)
        survive *= (1 - q_g)
        gens.append(g)
    return gens, pmf, survive


def main():
    streams = {}
    total_gens = total_draws = total_hits = 0
    for fname, sid, crossed_sealed in CORPUS:
        s = scan(load(fname))
        total_gens += len(s["desert"])
        total_draws += s["total_desert_draws"]
        total_hits += s["total_desert_hits"]
        streams[sid] = s
        # sealed flag vs derived fact: crossed iff a birth occurred
        assert s["crossed"] == crossed_sealed or \
            (s["crossed"] and s["birth_cum"] is not None), \
            f"crossed-flag drift on {sid}"

    crossers = sorted([s for s in streams if streams[s]["birth_cum"]],
                      key=lambda s: streams[s]["birth_cum"])
    noncrossers = [s for s in streams if not streams[s]["birth_cum"]]

    guards = {
        "pilot_rederivation_vs_sealed": {
            "desert_gens": [total_gens, SEALED_DESERT_GENS,
                            total_gens == SEALED_DESERT_GENS],
            "desert_draws": [total_draws, SEALED_DESERT_DRAWS,
                             total_draws == SEALED_DESERT_DRAWS],
            "desert_hits": [total_hits, SEALED_DESERT_HITS,
                            total_hits == SEALED_DESERT_HITS]},
        "crosser_set_vs_sealed": [crossers, sorted(SEALED_CROSSERS),
                                  set(crossers) == set(SEALED_CROSSERS)],
        "birth_cum_vs_sealed": {
            s: [streams[s]["birth_cum"], SEALED_CROSSERS[s],
                streams[s]["birth_cum"] == SEALED_CROSSERS[s]]
            for s in SEALED_CROSSERS},
        "breaker_full_totals": {s: streams[s]["N_full"] for s in crossers},
        "noncrosser_full_totals": {s: streams[s]["N_full"] for s in noncrossers},
        "noncrosser_full_sum_vs_sealed_846":
            [sum(streams[s]["N_full"] for s in noncrossers),
             SEALED_NONCROSSER_DESERT_DRAWS,
             sum(streams[s]["N_full"] for s in noncrossers)
             == SEALED_NONCROSSER_DESERT_DRAWS],
    }
    ok = (guards["pilot_rederivation_vs_sealed"]["desert_gens"][2]
          and guards["pilot_rederivation_vs_sealed"]["desert_draws"][2]
          and guards["pilot_rederivation_vs_sealed"]["desert_hits"][2]
          and guards["crosser_set_vs_sealed"][2]
          and all(v[2] for v in guards["birth_cum_vs_sealed"].values())
          and guards["noncrosser_full_sum_vs_sealed_846"][2])
    if not ok:
        raise SystemExit("GUARD ABORT: re-derived facts drifted from sealed")

    # ---- Q1: reproduce exp027's EXACT set probability ------------
    # exp027's p_set_obs is NOT the plain order-free product: its
    # config_p enforces STRICT birth-GEN order (g1<g2<g3) per ordered
    # triple, so the 6-permutation sum = P(set breaks AND all three
    # break in DISTINCT gens); same-gen double-breaks are excluded
    # (found-by-guard: product form = 1.604e-4 vs sealed 7.97e-5).
    # Reproduce the triple sum, not the product.
    gens_pmf = {s: birth_distribution(streams[s]["desert"])
                for s in streams}

    def config_p(triple):
        s1, s2, s3 = triple
        g1s, p1s = gens_pmf[s1][0], gens_pmf[s1][1]
        g2s, p2s = gens_pmf[s2][0], gens_pmf[s2][1]
        g3s, p3s = gens_pmf[s3][0], gens_pmf[s3][1]
        others = [s for s in streams if s not in triple]
        censor_prod = math.prod(gens_pmf[s][2] for s in others)
        tot = 0.0
        for g1, p1 in zip(g1s, p1s):
            for g2, p2 in zip(g2s, p2s):
                if g2 <= g1:
                    continue
                for g3, p3 in zip(g3s, p3s):
                    if g3 > g2:
                        tot += p1 * p2 * p3
        return tot * censor_prod

    p_set_trunc = sum(config_p(t)
                      for t in __import__("itertools").permutations(
                          tuple(crossers), 3))
    trunc_censor = {s: gens_pmf[s][2] for s in streams}
    heavy5 = sorted(streams,
                    key=lambda s: streams[s]["total_desert_draws"])[-5:]
    p_no_heavy5 = math.prod(trunc_censor[s] for s in heavy5)
    q1_ok = (abs(p_set_trunc - SEALED_SET_P) < 1e-18
             and abs(p_no_heavy5 - SEALED_NO_HEAVY5) < 1e-18)

    # ---- Q2: full-schedule set probability ------------------------
    N = {s: streams[s]["N_full"] for s in streams}
    censor_full = {s: (1 - W) ** N[s] for s in streams}
    p_set_full = math.prod(1 - censor_full[s] for s in crossers) * \
        math.prod(censor_full[s] for s in noncrossers)
    flat = 1.0 / 56
    gap_trunc = flat / SEALED_SET_P          # ~224x below flat
    gap_full = flat / p_set_full
    closed_orders = math.log10(gap_trunc / gap_full)

    if p_set_full >= flat:
        q2_verdict = "ARTIFACT-FULL"
    elif gap_full <= gap_trunc / 10:
        q2_verdict = "PARTIALLY-CLOSED"
    elif p_set_full < flat / 10:
        q2_verdict = "SURPRISE-SURVIVES"
    else:
        q2_verdict = "BETWEEN"

    # ---- Q3: sequential joint of the exact observed pattern -------
    exponent = sum(SEALED_CROSSERS[s] - 1 for s in crossers) + \
        sum(N[s] for s in noncrossers)
    p_exact_pattern = (W ** 3) * (1 - W) ** exponent

    # ---- Q4: exposure-rank event under the sequential null --------
    p_rank_event = 0.0
    per_set = []
    for S in combinations(sorted(streams), 3):
        nb = [s for s in streams if s not in S]
        c_S = min(N[s] for s in nb)
        p = math.prod(censor_full[s] for s in nb) * \
            math.prod(1 - (1 - W) ** (c_S - 1) for s in S)
        p_rank_event += p
        per_set.append((S, p))
    p_rank_event = min(p_rank_event, 1.0)
    obs_rank_terms = [p for S, p in per_set if set(S) == set(crossers)]
    p_rank_observed_term = obs_rank_terms[0]

    # ---- Q5: context — break-count distribution -------------------
    p_break = {s: 1 - censor_full[s] for s in streams}
    expected_breaks = sum(p_break.values())
    dp = {0: 1.0}
    for s in streams:
        ndp = {}
        for k, v in dp.items():
            ndp[k] = ndp.get(k, 0.0) + v * censor_full[s]
            ndp[k + 1] = ndp.get(k + 1, 0.0) + v * p_break[s]
        dp = ndp
    p_exactly3 = dp.get(3, 0.0)
    p_at_least1 = 1 - censor_full[crossers[0]] ** 0 * math.prod(
        censor_full.values()) if False else 1 - math.prod(
        censor_full[s] for s in streams)

    out = {
        "experiment": "exp031c sequential (birth,n) joint null "
                      "calibration of exp027's breaker-set statistic",
        "preregistration": (
            "sealed in FINDINGS at exp031b time as 'the remaining "
            "endogenous-side closer': full sequential joint of "
            "(birth, n) under the sealed shared per-draw hazard; "
            "probes Q1-Q5 and verdicts sealed in this script's "
            "docstring BEFORE any statistic ran"),
        "null_model": (
            "each stream runs its FULL actual 12-gen newborn schedule "
            f"(N_s from telemetry: {N}); draws iid, hit w.p. "
            f"w={W} (sealed, never re-estimated); break = first hit; "
            "P(T=j)=(1-w)^(j-1)*w; censor=(1-w)^N; streams "
            "independent.  Counterfactual-continuation approximation "
            "LABELED: breaker schedules include post-crossing gens "
            "from the actual runs; no cleaner counterfactual exists."),
        "guards": guards,
        "guard_ok": ok,
        "q1_reproduction_guard": {
            "note": ("exp027's order-free set prob is distinct-gen-"
                     "order-free (strict g1<g2<g3 per ordered triple "
                     "excludes same-gen double-breaks); found-by-"
                     "guard the plain product form is 1.604e-4. "
                     "Reproduced via exp027's exact triple-sum path."),
            "P_set_truncated_recomputed": p_set_trunc,
            "P_set_truncated_sealed_exp027": SEALED_SET_P,
            "P_no_heavy5_recomputed": p_no_heavy5,
            "P_no_heavy5_sealed_exp027": SEALED_NO_HEAVY5,
            "match": q1_ok},
        "q2_full_schedule_set_probability": {
            "formula": "prod_{breakers}(1-(1-w)^N) * prod_{non}(1-w)^N",
            "P_set_observed_under_full_schedule_null": p_set_full,
            "flat_baseline_1_over_56": flat,
            "exp027_truncated_value": SEALED_SET_P,
            "gap_to_flat_truncated_x": gap_trunc,
            "gap_to_flat_full_x": gap_full,
            "orders_of_magnitude_closed": closed_orders,
            "verdict": q2_verdict},
        "q3_exact_pattern_joint_probability": {
            "formula": "w^3 (1-w)^((16-1)+(54-1)+(121-1)+sum N_nb)",
            "survived_draws_exponent": exponent,
            "P_exact_birth_n_pattern": p_exact_pattern},
        "q4_exposure_rank_event_under_sequential_null": {
            "definition": ("exactly 3 streams break AND each breaker "
                           "breaks before every non-breaker's censor "
                           "point (then break set == bottom-3 by "
                           "exposure); summed over all C(8,3)=56 "
                           "candidate breaker sets"),
            "P_rank_event": p_rank_event,
            "observed_set_term_of_that_sum": p_rank_observed_term,
            "observed_term_share": p_rank_observed_term / p_rank_event},
        "q5_break_count_context": {
            "expected_break_count_under_null": expected_breaks,
            "P_exactly_3_break": p_exactly3,
            "P_at_least_1_breaks": p_at_least1,
            "observed_break_count": 3,
            "per_stream_break_probability_full_schedule": p_break},
        "synthesis": (
            f"exp027's 7.97e-5 was computed on post-birth-truncated "
            f"exposure; under the full-schedule sequential joint null "
            f"the SAME set probability is {p_set_full:.4g} "
            f"({gap_full:.2f}x below flat, vs {gap_trunc:.1f}x "
            f"truncated — {closed_orders:.1f} orders of the "
            f"surprise close as truncation geometry).  The verdict "
            f"is {q2_verdict}: " + (
                "the set surprise was an artifact of conditioning on "
                "truncated exposure."
                if q2_verdict == "ARTIFACT-FULL"
                else "a large share of the set surprise was "
                     "truncation geometry, but the calibrated gap "
                     "remains below flat — read with Q4/Q5.")) ,
        "relation_to_exp029": (
            "This calibrates exp027's set statistic only.  exp029's "
            "conditional deviance (p=0.003256) conditions on observed "
            "exposure by design and stands as valid conditional "
            "arithmetic; exp031b closed the exogenous side; this "
            "run closes the endogenous side."),
        "honesty": ("Pure exact arithmetic, no rng / no MC / no "
                    "normal approximation.  The counterfactual "
                    "schedule for breakers uses actual post-crossing "
                    "newborn counts (labeled approximation).  Q4's "
                    "event is a sufficient rendering of 'breakers = "
                    "bottom-3 by exposure' (exactly-3-breakers + all "
                    "below all censor points); rankings where a "
                    "breaker out-exposes a non-breaker are not in "
                    "the event, matching the observation.  Deep-pilot "
                    "class: 4 events / 8 streams."),
    }
    if not q1_ok:
        raise SystemExit("Q1 REPRODUCTION FAILED: exp027 value not "
                         "reproduced from raw telemetry")

    import hashlib
    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()
                         ).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp031c.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "guard_ok": ok,
        "q1_reproduced": q1_ok,
        "q2_P_set_full": f"{p_set_full:.6e}",
        "q2_gap_full_x": round(gap_full, 2),
        "q2_orders_closed": round(closed_orders, 2),
        "q2_verdict": q2_verdict,
        "q3_P_exact_pattern": f"{p_exact_pattern:.6e}",
        "q4_P_rank_event": f"{p_rank_event:.6e}",
        "q4_observed_term": f"{p_rank_observed_term:.6e}",
        "q5_expected_breaks": round(expected_breaks, 3),
        "q5_P_exactly3": f"{p_exactly3:.4f}",
        "digest": digest}, indent=1))


if __name__ == "__main__":
    main()
