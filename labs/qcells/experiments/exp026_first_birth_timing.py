"""exp026 — regime-conditioned desert-odds refinement, part 1:
per-stream first-birth timing.  Sealed exp025 left the desert
regime as ONE pooled rate (4 hits / 1037 draws across 74 desert
gens, 1-in-259 per newborn, CI [0.00105, 0.00988]) while naming
the timing fact in its corpus: the three crossers broke at k3 g0,
k5 g3, k6 g8 — an immediate, an early, and a late first birth —
and the five non-crossers never birthed at all.  Is that timing
pattern evidence of PER-STREAM lottery rates (some streams born
hot, some frozen), or is it what one shared low hazard looks like
under heavy censoring?  THIS experiment seals the timing table and
tests both reads against the exact statistics available at n=4.

Doctrine chain under test:
  exp018  FITNESS DESERT AT THE BIRTH CLOUD (hard roots); BAR=0.45.
  exp020  TIE-BAND-DIVERSITY: tie sampling converts 2/3 hard roots.
  exp021  RATE NOT WALL: 3/8 salted streams cross; per-stream rate;
          DESERT-EXTENDS-TO-CLOUD (no >=0.45 cloud cell anywhere
          on non-crossers; 0 hits in 682 desert draws on the
          exp021 salt telemetry).
  exp022  TRAIN-VISIBLE TIE-BREAK-INVARIANT: crossers birth ONE
          train ~0.498 cell at ONE desert-break gen; windows 0.
  exp023/024 break is a per-gen BIRTH event invisible pre-break;
          predict per-draw birth odds, not trajectories.
  exp025  TWO-REGIME per-draw odds: desert 1-in-259 vs plateau
          1-in-3.7; per-draw odds are a property of STREAM STATE
          (has a BAR-lineage entered the cloud), not of the draw;
          tie-width strata FLAT at draw level.

Open questions THIS experiment seals (numbered BEFORE computing):
  Q1  THE TIMING TABLE: per stream — birth gen T (first desert gen
      with >=1 newborn hit) or CENSORED at full exposure; desert
      gens and cumulative newborn draws at T (crossers) and at end
      of run (non-crossers).  Sealed as the canonical timing
      reference; every later timing claim cites this row set.
  Q2  HOMOGENEITY under one shared per-draw desert hazard: exact
      test conditional on the sealed totals (4 hits, 1037 desert
      draws) — each hit independently lands in stream s with
      probability w_s = n_s / 1037 where n_s is the stream's
      desert draw count.  Per-stream exact tail P(X_s >= k_s)
      under Marginal-Binomial(4, w_s); Bonferroni over 8 streams.
      Verdict: HOMOGENEOUS-AT-PILOT-N iff every adjusted p >=
      0.05, else HETEROGENEOUS with the named stream(s).
      (Power honesty: with 4 events this test cannot see anything
      but an extreme concentration — a HOMOGENEOUS verdict means
      'timing evidence does not distinguish per-stream rates',
      never 'rates are proven equal'.)
  Q3  TIMING CALIBRATION under the shared-hazard null: take the
      sealed pooled desert per-draw p (0.003857280617164899 —
      exp025's sealed value, NOT re-estimated here) and each
      stream's actual per-gen newborn counts D_g; per-gen hazard
      q_g = 1-(1-p)^D_g.  (a) Expected birth-STREAM count E =
      sum_s [1 - prod_g (1-q_g(s))]; exact 95% prediction interval
      via Poisson-binomial over the 8 per-stream probabilities;
      CALIBRATED iff observed birth-stream count (3) is inside.
      (b) Per-crosser timing surprise: F_s(T_obs) = P(T <= T_obs)
      under the stream's own q_g sequence (unconditional on
      birthing), i.e. how early each observed break is under the
      shared hazard.  k3's F(0) is the exact probability of an
      AT-BIRTH break under the null.  Reported, not verdicted
      (pilot class).
  Q4  NON-CROSSER HAZARD CEILING: pool the five censored streams'
      desert draws (0 hits in N_nc).  Exact 95% upper bound
      UB = 1 - 0.025**(1/N_nc) for their shared per-draw hazard.
      Verdict: NONCROSSER-UB-EXCLUDES-POOLED iff UB < the sealed
      pooled point estimate 0.003857280617164899; else COMPATIBLE.
      Read if excluded: the pooled 1-in-259 is carried by
      crosser-side exposure; non-crossers are consistent with an
      even lower hazard, and at n=4 the timing evidence cannot
      distinguish 'one shared low hazard, crossers lucky in
      waiting time' from 'crossers genuinely hotter' — the honest
      refinement is a CEILING on the frozen majority, not a rate.

DESIGN: pure analysis of the SEALED census telemetry (8 stream-
runs: exp022 k3-k7 tie_sample lane + exp024 k0-k2 replicate
census).  No re-run, no rng, no new sims.  Every number is
re-derived from the raw telemetry files INDEPENDENTLY of
exp025.results.json, then cross-checked against the sealed values
(desert gens 74, desert draws 1037, desert hits 4) — a mismatch
aborts the run rather than carrying drift.

Draw unit: IDENTICAL operational definition to exp025 (its code,
not its docstring, is the sealed semantics): a cloud cell at gen g
is a newborn iff its genome key was absent from the PREVIOUS gen's
cloud set; carried members (persistent post-break lineages) are
never draws.  hit = train_p >= 0.45.  Desert/plateau regime per
gen: PLATEAU iff any EARLIER gen of the same stream-run held a
>=BAR cloud cell (a gen's own hits do not flip its regime — the
break gen is desert-side), else DESERT.

Honest limits named up front: 4 events over 8 streams is deep-
pilot class; Q2's exact test has near-nil power and a HOMOGENEOUS
verdict is 'not distinguishable', not 'equal'; per-draw framing
understates stream-level clustering (exp025 honesty carries);
cohort C (k0/k1/k2) re-censuses the same salts as the exp021 q1
panel — labeled, never merged.
"""

import json
import math
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
TL = LAB / "experiments"
BAR = 0.45

# sealed exp025 values — cross-check targets, never inputs
SEALED_DESERT_GENS = 74
SEALED_DESERT_DRAWS = 1037
SEALED_DESERT_HITS = 4
SEALED_DESERT_P = 0.003857280617164899
SEALED_DESERT_CI = (0.0010515115660763353, 0.009876264981316496)
ALPHA = 0.05
N_STREAMS = 8

CORPUS = [
    ("exp022.telemetry.k3.jsonl", "k3", "B_exp022_tiesample", True),
    ("exp022.telemetry.k4.jsonl", "k4", "B_exp022_tiesample", False),
    ("exp022.telemetry.k5.jsonl", "k5", "B_exp022_tiesample", True),
    ("exp022.telemetry.k6.jsonl", "k6", "B_exp022_tiesample", True),
    ("exp022.telemetry.k7.jsonl", "k7", "B_exp022_tiesample", False),
    ("exp024.telemetry.k0.jsonl", "k0", "C_exp024_replicate", False),
    ("exp024.telemetry.k1.jsonl", "k1", "C_exp024_replicate", False),
    ("exp024.telemetry.k2.jsonl", "k2", "C_exp024_replicate", False),
]


def load(name):
    rows = []
    with open(TL / name, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def poisson_binomial_pmf(probs):
    """Exact PMF of sum of independent Bernoullis (DP, O(n^2))."""
    dp = [1.0]
    for p in probs:
        nxt = [0.0] * (len(dp) + 1)
        for i, v in enumerate(dp):
            nxt[i] += v * (1 - p)
            nxt[i + 1] += v * p
        dp = nxt
    return dp


def prediction_interval_95(probs):
    """Smallest-outcome-set exact two-sided 95% interval."""
    pmf = poisson_binomial_pmf(probs)
    order = sorted(range(len(pmf)), key=lambda k: -pmf[k])
    acc, kept = 0.0, set()
    for k in order:
        acc += pmf[k]
        kept.add(k)
        if acc >= 0.95:
            break
    return min(kept), max(kept), pmf


def binomial_tail_at_least(k, n, p):
    """P(X >= k), X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j)
               for j in range(k, n + 1))


def main():
    # ---- re-derive the sealed desert facts independently ----------
    # per stream: ordered desert-gene sequence of newborn draws and
    # hits, plus the first-birth gen (None = censored)
    streams = {}
    total_desert_gens = 0
    total_desert_draws = 0
    total_desert_hits = 0
    for fname, sid, cohort, crossed in CORPUS:
        rows = load(fname)
        prev = None
        bar_seen_before = False
        gens = []
        for r in rows:
            cloud = r["census"]["cloud"]
            keys = {genome_key(c) for c in cloud}
            if prev is None:
                newborns = list(cloud)
            else:
                newborns = [c for c in cloud
                            if genome_key(c) not in prev]
            hits = sum(1 for c in newborns if c["train_p"] >= BAR)
            regime = ("plateau" if bar_seen_before else "desert")
            gens.append({"gen": r["gen"], "draws": len(newborns),
                         "hits": hits, "regime": regime})
            if regime == "desert":
                total_desert_gens += 1
                total_desert_draws += len(newborns)
                total_desert_hits += hits
            prev = keys
            if any(c["train_p"] >= BAR for c in cloud):
                bar_seen_before = True
        desert_gens = [g for g in gens if g["regime"] == "desert"]
        birth = next((g for g in desert_gens if g["hits"] >= 1), None)
        streams[sid] = {
            "cohort": cohort, "crossed_sealed": crossed,
            "desert_gens": [g["gen"] for g in desert_gens],
            "desert_draws_per_gen": [g["draws"] for g in desert_gens],
            "desert_hits": sum(g["hits"] for g in desert_gens),
            "birth_gen": (birth["gen"] if birth else None),
        }

    guard = {
        "desert_gens": (total_desert_gens, SEALED_DESERT_GENS,
                        total_desert_gens == SEALED_DESERT_GENS),
        "desert_draws": (total_desert_draws, SEALED_DESERT_DRAWS,
                         total_desert_draws == SEALED_DESERT_DRAWS),
        "desert_hits": (total_desert_hits, SEALED_DESERT_HITS,
                        total_desert_hits == SEALED_DESERT_HITS),
    }
    if not all(g[2] for g in guard.values()):
        raise SystemExit(f"SEALED-VALUE DRIFT, aborting: {guard}")

    # ---- Q1: the canonical timing table ----------------------------
    timing_table = {}
    for sid, s in streams.items():
        cum = 0
        cum_at_birth = None
        for g, d in zip(s["desert_gens"], s["desert_draws_per_gen"]):
            cum += d
            if s["birth_gen"] is not None and g == s["birth_gen"]:
                cum_at_birth = cum
        timing_table[sid] = {
            "cohort": s["cohort"],
            "crossed_sealed": s["crossed_sealed"],
            "birth_gen": s["birth_gen"],
            "status": ("birth_at_g" + str(s["birth_gen"])
                       if s["birth_gen"] is not None else "censored"),
            "desert_gens_exposed": len(s["desert_gens"]),
            "desert_draws_exposed": cum,
            "cumulative_draws_at_birth": cum_at_birth,
            "desert_hits": s["desert_hits"],
        }

    # ---- Q2: homogeneity under one shared per-draw hazard ----------
    # conditional on 4 hits among 1037 draws, hit-stream ~ w_s
    homog = {}
    for sid, s in streams.items():
        n_s = timing_table[sid]["desert_draws_exposed"]
        w_s = n_s / total_desert_draws
        k_s = s["desert_hits"]
        p_tail = binomial_tail_at_least(k_s, SEALED_DESERT_HITS, w_s)
        homog[sid] = {
            "desert_draws": n_s, "share_w": round(w_s, 6),
            "hits": k_s,
            "exact_tail_P_X_ge_k": p_tail,
            "bonferroni_p": min(1.0, p_tail * N_STREAMS),
        }
    all_clear = all(h["bonferroni_p"] >= ALPHA for h in homog.values())
    q2_verdict = ("HOMOGENEOUS-AT-PILOT-N" if all_clear
                  else "HETEROGENEOUS")

    # ---- Q3: timing calibration under the sealed pooled p ----------
    p = SEALED_DESERT_P
    per_stream_birth_p = {}
    for sid, s in streams.items():
        q_gs = [1 - (1 - p) ** d for d in s["desert_draws_per_gen"]]
        birth_p = 1.0
        for q in q_gs:
            birth_p *= (1 - q)
        per_stream_birth_p[sid] = 1 - birth_p
    expected_birth_streams = sum(per_stream_birth_p.values())
    lo_i, hi_i, pmf = prediction_interval_95(
        list(per_stream_birth_p.values()))
    observed_birth_streams = sum(
        1 for s in streams.values() if s["birth_gen"] is not None)
    if lo_i <= observed_birth_streams <= hi_i:
        q3a_verdict = "CALIBRATED"
    elif observed_birth_streams > hi_i:
        q3a_verdict = "EARLY-EXCESS"
    else:
        q3a_verdict = "LATE-DEFICIT"

    # per-crosser F(T_obs): P(first birth gen <= T_obs) under the
    # stream's own q_g sequence (unconditional on birthing)
    timing_surprise = {}
    for sid, s in streams.items():
        if s["birth_gen"] is None:
            continue
        survive = 1.0
        f_at_birth = None
        for g, d in zip(s["desert_gens"], s["desert_draws_per_gen"]):
            q_g = 1 - (1 - p) ** d
            survive *= (1 - q_g)
            if g == s["birth_gen"]:
                # F(T <= g) = 1 - survival through g
                f_at_birth = 1 - survive
                break
        timing_surprise[sid] = {
            "birth_gen": s["birth_gen"],
            "F_T_obs_under_shared_hazard": f_at_birth,
            "read": (f"under the shared {round(1 / p)}-in-1 hazard, "
                     f"a stream of this shape births at or before "
                     f"g{s['birth_gen']} with probability "
                     f"{f_at_birth:.4f}"),
        }

    # ---- Q4: non-crosser hazard ceiling ----------------------------
    nc_draws = sum(t["desert_draws_exposed"]
                   for t in timing_table.values()
                   if t["birth_gen"] is None)
    nc_hits = sum(t["desert_hits"] for t in timing_table.values()
                  if t["birth_gen"] is None)
    assert nc_hits == 0
    ub95 = 1 - 0.025 ** (1 / nc_draws)
    q4_verdict = ("NONCROSSER-UB-EXCLUDES-POOLED"
                  if ub95 < SEALED_DESERT_P else "COMPATIBLE")

    result = {
        "experiment": "exp026 desert first-birth timing + "
                      "regime-conditioned hazard ceiling",
        "design": "pure analysis of the sealed 8-stream census "
                  "corpus (exp022 k3-k7 + exp024 k0-k2); independent "
                  "re-derivation from raw telemetry cross-checked "
                  "against sealed exp025 values (74/1037/4) with "
                  "abort-on-drift; newborn/draw/hit/regime units "
                  "identical to exp025's operational code; shared "
                  "hazard tests condition on the sealed totals",
        "honesty": "4 events over 8 streams is deep-pilot class; "
                   "Q2 HOMOGENEOUS means 'not distinguishable at "
                   "this n', never 'rates equal'; Q3b timing "
                   "surprises are reported not verdicted; Q4's "
                   "ceiling is the honest refinement available for "
                   "the frozen majority — a bound, not a rate",
        "guard_rederivation_vs_sealed": guard,
        "q1_timing_table": timing_table,
        "q2_homogeneity_shared_hazard": {
            "null": "conditional on 4 hits / 1037 desert draws, "
                    "each hit lands in stream s w.p. n_s/1037",
            "per_stream": homog,
            "alpha_per_stream_bonferroni": ALPHA / N_STREAMS,
            "verdict": q2_verdict,
        },
        "q3_timing_calibration_under_pooled_p": {
            "p_used": p,
            "p_source": "sealed exp025 desert point estimate "
                        "(never re-estimated here)",
            "per_stream_P_at_least_one_desert_birth":
                per_stream_birth_p,
            "expected_birth_streams": expected_birth_streams,
            "observed_birth_streams": observed_birth_streams,
            "prediction_interval_95": [lo_i, hi_i],
            "verdict_count": q3a_verdict,
            "per_crosser_timing_surprise": timing_surprise,
            "read": ("how early each observed break is under ONE "
                     "shared hazard; k3's F(0) is the exact "
                     "at-birth-break probability under the null"),
        },
        "q4_noncrosser_hazard_ceiling": {
            "noncrosser_desert_draws": nc_draws,
            "noncrosser_hits": nc_hits,
            "exact_ub95_per_draw": ub95,
            "sealed_pooled_point_estimate": SEALED_DESERT_P,
            "sealed_pooled_ci95": list(SEALED_DESERT_CI),
            "verdict": q4_verdict,
            "read": (f"the five censored streams' shared hazard is "
                     f"below {ub95:.6f} (95% exact); "
                     + ("this EXCLUDES the pooled 1-in-259 point "
                        "estimate — the pooled rate is carried by "
                        "crosser-side exposure, and at n=4 timing "
                        "cannot separate 'shared low hazard, lucky "
                        "waits' from 'hot crossers'"
                        if q4_verdict.startswith("NONCROSSER")
                        else "the pooled point estimate stays "
                             "inside the non-crosser ceiling")),
        },
    }
    out = TL / "exp026.results.json"
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({
        "guard": {k: g[:2] + (g[2],) for k, g in guard.items()},
        "q2_verdict": q2_verdict,
        "q3_verdict_count": q3a_verdict,
        "q3_expected_vs_observed": [round(expected_birth_streams, 4),
                                    observed_birth_streams,
                                    [lo_i, hi_i]],
        "q4_verdict": q4_verdict,
        "q4_ub95": ub95,
    }, indent=1))


if __name__ == "__main__":
    main()
