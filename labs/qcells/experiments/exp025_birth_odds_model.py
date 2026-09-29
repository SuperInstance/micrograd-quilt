"""exp025 — birth-cloud per-draw odds model: given exp023/exp024's
verdict (the desert break is a per-gen BIRTH event invisible
pre-break), stop trying to predict WHICH gen breaks and model the
odds directly: what is P(a cloud draw births a >=BAR cell), and is
per-gen birth probability explainable by draw count alone?

Doctrine chain under test:
  exp018  FITNESS DESERT AT THE BIRTH CLOUD (hard roots); BAR=0.45.
  exp020  TIE-BAND-DIVERSITY: tie sampling converts 2/3 hard roots.
  exp021  RATE NOT WALL: 3/8 salted streams cross; per-stream rate.
  exp022  TRAIN-VISIBLE TIE-BREAK-INVARIANT: crossers birth ONE
          train ~0.498 cell at ONE desert-break gen (window 0).
  exp023  NOT SEPARABLE AT AVAILABLE N: no pre-break signal; break
          = per-gen birth event; prediction must target per-draw
          birth odds, not trajectories.
  exp024  exp023 pilot CONFIRMED blind at n=8 (k0/k1/k2: no >=0.45
          cloud cell ever; C1 universal 8/8, zero separation).

Open question THIS experiment seals:
  exp023 named it: 'prediction must target birth-cloud composition
  per-draw odds'. What ARE those odds, measured over every censused
  draw in the sealed corpus — and does tie-band width (n_tied, the
  exp020 lever) move PER-DRAW odds, PER-GEN odds via draw count, or
  neither?

DESIGN: pure analysis of the SEALED census telemetry (no re-run,
no rng, no new sims). Every draw that already exists counts once.

Draw unit (pre-registered, CORRECTED at first run — the initial
definition counted every non-champion cloud row as a fresh draw
and returned 96 hits, contradicting exp022's sealed 3 births; the
telemetry showed why: after a break the winning lineage PERSISTS
in the cloud gen after gen (k3: the 0.498 genome present at all
12 gens), so carried members are not births. Correction sealed
here BEFORE any verdict was read out):
  draw = one cloud cell NEWLY BORN at gen g: its genome absent
  from (cloud ∪ champion) of gen g-1; gen 0 has no predecessor
  so every cloud cell at g0 is a newborn. Champion included in
  the pool symmetrically (at the break gen the bar cell is a
  NON-champion newborn; at later gens the champion is usually a
  carried parent).
  carried = cloud rows whose genome existed last gen — reported
  separately, NEVER counted as draws.
  hit = the draw's train_p >= BAR (0.45, the exp021 lane bar).
  A gen BIRTHS when >=1 of its newborns hits.

Corpus (8 stream-runs, all cloud-censused, zero selection):
  B) exp022 census k3-k7 (tie_sample lane): 3 crossers (k3/k5/k6)
     + k4 near-miss + k7 dead.
  C) exp024 blind-validation census k0/k1/k2 (replicate runs of
     the exp021 q1 salts, replicate pins verbatim per exp024) —
     separate stream-runs, labeled, not merged with B.
  EXCLUDED, named not dropped: the exp021 q1 salt telemetry
  (k0-k7) predates the census lane — it records champion curve +
  tie stats but NO birth-cloud rows, so it contributes zero draws.
  The per-draw odds model is therefore over the censused subset
  (8 stream-runs, 3 of them crossing in the tie_sample lane).

Questions (numbered BEFORE computing):
  Q1  Pooled per-draw hit rate p_hat with exact (Clopper-Pearson)
      95% CI over all 16 stream-runs.
  Q2  Does p_hat stratify by tie-band width (n_tied 1 / 2-3 / >=4)?
      exp020 lever test at DRAW level: if per-draw odds are FLAT
      across strata, tie sampling can only matter via draw COUNT
      (more tied cells = more draws per gen), not draw quality.
  Q3  Per-gen birth model: P(>=1 hit | gen) = 1-(1-p_hat)^D_g with
      D_g = newborns at that gen. Calibration per n_tied stratum:
      expected birth-gens E_s = sum of per-gen probabilities in
      stratum s vs observed birth-gens O_s; CALIBRATED iff O_s
      inside the exact binomial 95% prediction interval around E_s
      (interval computed from per-gen p_g, not around the mean of
      p_g — heterogeneous-probability exact interval).
  Q4  (added at first run, BEFORE reading Q1-Q3 verdicts out — the
      88-hit run showed the corpus is two REGIMES the pooled model
      mixes: desert streams birth ZERO bar cells in ~700 draws,
      while post-break streams mint ~1 new BAR variant per 15
      newborns (neutral re-decompositions of the winner).)
      Regime at gen g: PLATEAU if any EARLIER gen of the same
      stream-run held a >=BAR cloud cell, else DESERT (a gen's own
      hits do not flip its regime — the break gen is desert-side).
      Two-regime per-draw odds with exact CIs each; the desert
      regime carries the exp023 prediction question (P(first bar
      birth per gen)), the plateau regime is post-crossing churn.

Verdict conditions (pre-registered):
  Q2: TIE-WIDTH-DEPENDENT iff stratum CIs are pairwise disjoint;
      else FLAT (doctrine read: tie diversity acts through draw
      count only).
  Q3: CALIBRATED iff all strata inside prediction intervals;
      else MISCALIBRATED (draw count alone insufficient -> birth
      odds conditioned on something else).
  Q4: TWO-REGIME iff the plateau per-draw CI excludes the desert
      point estimate OR the desert CI excludes the plateau point
      estimate (report which disjunct holds; both = strong);
      else ONE-REGIME. A TWO-REGIME verdict reads: per-draw odds
      are a property of the STREAM STATE (has a BAR-lineage
      entered the cloud), not of the draw — the exp023 'invisible
      pre-break' result IS the desert regime, quantified.
  Honest limits named up front: hits cluster within streams (a
  break gen contributes its whole hit set at once) so per-draw CIs
  understate stream-level variance — stream-level hit table
  reported alongside; corpus n=16 stream-runs is PILOT class;
  no zero-inflation modeling, no fit-on-noise: p_hat is pooled,
  never refit per stratum.
"""

import json
import math
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
TL = LAB / "experiments"
BAR = 0.45

# corpus: (telemetry file, stream id, cohort, crossed per sealed results)
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

TIERS = [("n_tied=1", lambda n: n == 1),
         ("n_tied=2-3", lambda n: 2 <= n <= 3),
         ("n_tied>=4", lambda n: n >= 4)]


def load(name):
    rows = []
    with open(TL / name, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def clopper_pearson(k, n, alpha=0.05):
    """Exact two-sided CI for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    if k == 0:
        lo = 0.0
    else:
        lo = _beta_ppf(alpha / 2, k, n - k + 1)
    if k == n:
        hi = 1.0
    else:
        hi = _beta_ppf(1 - alpha / 2, k + 1, n - k)
    return (lo, hi)


def _beta_ppf(p, a, b):
    """Incomplete-beta inverse by bisection (regularized)."""
    if a <= 0 or b <= 0:
        return 0.0 if p < 0.5 else 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if _betainc(mid, a, b) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def _betainc(x, a, b):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    # continued fraction (Numerical Recipes betacf)
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a)
                  - math.lgamma(b) + a * math.log(x)
                  + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(x, a, b) / a
    return 1 - bt * _betacf(1 - x, b, a) / b


def _betacf(x, a, b):
    MAXIT, EPS, FPMIN = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1 / d
        h *= d * c
        aa = -(a + m) * (qap + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1 / d
        de = d * c
        h *= de
        if abs(de - 1) < EPS:
            break
    return h


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


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def main():
    gens = []  # one entry per gen across corpus
    stream_table = {}
    carried_table = {"rows": 0, "bar_rows": 0}
    for fname, sid, cohort, crossed in CORPUS:
        rows = load(fname)
        key = f"{cohort}:{sid}"
        st = {"cohort": cohort, "crossed_sealed": crossed,
              "gens": 0, "newborn_draws": 0, "hits": 0,
              "birth_gens": []}
        prev = None  # set of genome keys present last gen
        bar_seen_before = False
        for r in rows:
            cloud = r["census"]["cloud"]
            keys = {genome_key(c) for c in cloud}
            if prev is None:
                newborns = list(cloud)
                carried = 0
            else:
                newborns = [c for c in cloud
                            if genome_key(c) not in prev]
                carried = len(cloud) - len(newborns)
                for c in cloud:
                    if genome_key(c) in prev:
                        carried_table["rows"] += 1
                        if c["train_p"] >= BAR:
                            carried_table["bar_rows"] += 1
            hits = [c for c in newborns if c["train_p"] >= BAR]
            g = r["gen"]
            gens.append({"stream": key, "cohort": cohort, "gen": g,
                         "n_tied": r["census"]["n_tied"],
                         "draws": len(newborns), "hits": len(hits),
                         "carried": carried,
                         "regime": ("plateau" if bar_seen_before
                                    else "desert")})
            st["gens"] += 1
            st["newborn_draws"] += len(newborns)
            st["hits"] += len(hits)
            if hits:
                st["birth_gens"].append(g)
            prev = keys
            if any(c["train_p"] >= BAR for c in cloud):
                bar_seen_before = True
        stream_table[key] = st

    total_draws = sum(g["draws"] for g in gens)
    total_hits = sum(g["hits"] for g in gens)
    p_hat = total_hits / total_draws
    p_ci = clopper_pearson(total_hits, total_draws)

    # Q2: per-draw rate by n_tied tier
    strata = {}
    for label, pred in TIERS:
        sub_gens = [g for g in gens if pred(g["n_tied"])]
        d = sum(g["draws"] for g in sub_gens)
        h = sum(g["hits"] for g in sub_gens)
        ci = clopper_pearson(h, d) if d else (0.0, 0.0)
        strata[label] = {"draws": d, "hits": h,
                         "rate": (h / d) if d else None,
                         "ci95": ci}
    labs = list(strata)
    disjoint = all(
        strata[labs[i]]["ci95"][1] < strata[labs[j]]["ci95"][0]
        or strata[labs[j]]["ci95"][1] < strata[labs[i]]["ci95"][0]
        for i in range(len(labs)) for j in range(i + 1, len(labs)))

    # Q3: per-gen birth model with pooled p_hat
    calib = {}
    for label, pred in TIERS:
        sub_gens = [g for g in gens if pred(g["n_tied"])]
        p_gs = [1 - (1 - p_hat) ** g["draws"] for g in sub_gens]
        pmf = poisson_binomial_pmf(p_gs)
        obs = sum(1 for g in sub_gens if g["hits"] >= 1)
        exp = sum(p_gs)
        # exact two-sided tail interval at alpha=.05: smallest set of
        # outcomes containing >=95% probability mass
        order = sorted(range(len(pmf)), key=lambda k: -pmf[k])
        acc, kept = 0.0, set()
        for k in order:
            acc += pmf[k]
            kept.add(k)
            if acc >= 0.95:
                break
        lo_i, hi_i = min(kept), max(kept)
        calib[label] = {
            "gens": len(sub_gens), "observed_birth_gens": obs,
            "expected_birth_gens": round(exp, 4),
            "prediction_interval_95": [lo_i, hi_i],
            "in_interval": lo_i <= obs <= hi_i,
        }
    calibrated = all(c["in_interval"] for c in calib.values())

    # Q4: two-regime per-draw odds (desert vs plateau)
    regime_stats = {}
    for reg in ("desert", "plateau"):
        sub = [g for g in gens if g["regime"] == reg]
        d = sum(g["draws"] for g in sub)
        h = sum(g["hits"] for g in sub)
        regime_stats[reg] = {
            "gens": len(sub), "draws": d, "hits": h,
            "rate": (h / d) if d else None,
            "ci95": clopper_pearson(h, d) if d else (0.0, 0.0),
        }
    des, pla = regime_stats["desert"], regime_stats["plateau"]
    disj_pla_excludes_des = pla["ci95"][0] > des["rate"]
    disj_des_excludes_pla = des["ci95"][1] < pla["rate"]
    two_regime = disj_pla_excludes_des or disj_des_excludes_pla
    q4_verdict = ("TWO-REGIME"
                  if two_regime else "ONE-REGIME")
    q4_detail = []
    if disj_pla_excludes_des:
        q4_detail.append("plateau CI excludes desert point estimate")
    if disj_des_excludes_pla:
        q4_detail.append("desert CI excludes plateau point estimate")

    result = {
        "experiment": "exp025 birth-cloud per-draw odds model",
        "design": "pure analysis of the sealed cloud-census corpus "
                  "(8 stream-runs: exp022 k3-k7 tie_sample lane, "
                  "exp024 k0-k2 replicate census; the exp021 q1 salt "
                  "telemetry has no cloud rows and is named-excluded); "
                  "draw = a cloud cell NEWLY BORN at gen g (genome "
                  "absent from last gen's cloud+champion; corrected "
                  "at first run — carried lineage members are not "
                  "births); hit = train_p >= 0.45 (exp021 lane BAR); "
                  "birth = >=1 newborn hit at a gen; p_hat pooled "
                  "never refit per stratum",
        "honesty": "hits cluster within streams (a break gen lands "
                   "its whole hit set at once) so per-draw CIs "
                   "understate stream-level variance — stream table "
                   "is the honest unit for rates; n=16 stream-runs "
                   "is PILOT class; replicate cohort C is the same "
                   "salts as A re-censused, labeled never merged; "
                   "per-draw odds answer HOW OFTEN, not WHEN",
        "q1_pooled_per_draw": {
            "draws": total_draws, "hits": total_hits,
            "p_hat": p_hat, "ci95_clopper_pearson": p_ci,
            "read": f"about 1 in {round(1 / p_hat)} cloud draws births "
                    f"a >=BAR cell",
        },
        "q2_tie_width_strata": {
            "strata": strata,
            "verdict": "TIE-WIDTH-DEPENDENT" if disjoint else "FLAT",
        },
        "q3_per_gen_birth_model": {
            "model": "P(>=1 hit | gen) = 1-(1-p_hat)^D_g",
            "calibration_by_tier": calib,
            "verdict": "CALIBRATED" if calibrated else "MISCALIBRATED",
            "explanation_if_miscalibrated": "pooled p_hat mixes two "
                "stream regimes (see q4); per-gen draw count alone "
                "cannot predict births without the regime state",
        },
        "q4_two_regime_odds": {
            "regimes": regime_stats,
            "verdict": q4_verdict,
            "evidence": q4_detail,
            "read": ("desert: a first bar birth is ~1-in-"
                     + (f"{round(1 / des['rate'])}" if des["rate"] else "inf")
                     + " newborns per gen across ~"
                     + str(des["gens"])
                     + " desert gens (the exp023 invisible event, "
                       "quantified); plateau: ~1-in-"
                     + f"{round(1 / pla['rate'])}"
                     + " newborns is a fresh BAR variant "
                       "(neutral re-decomposition churn)") if two_regime
                    else "regimes not separable at this n",
        },
        "stream_table": stream_table,
        "carried_contrast": carried_table,
        "cross_check": {
            "corpus_births": sum(len(s["birth_gens"])
                                 for s in stream_table.values()),
            "crossing_streams_with_birth": sum(
                1 for s in stream_table.values()
                if s["crossed_sealed"] and s["birth_gens"]),
            "noncrossing_streams_with_birth": sum(
                1 for s in stream_table.values()
                if not s["crossed_sealed"] and s["birth_gens"]),
        },
    }
    out = TL / "exp025.results.json"
    out.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({k: result[k] for k in
                      ("q1_pooled_per_draw", "q2_tie_width_strata",
                       "q3_per_gen_birth_model", "q4_two_regime_odds",
                       "carried_contrast", "cross_check")},
                     indent=1))


if __name__ == "__main__":
    main()
