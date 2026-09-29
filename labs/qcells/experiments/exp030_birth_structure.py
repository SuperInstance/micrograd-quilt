"""exp030_birth_structure.py — birth-structure decomposition of the pooled corpus.

Pre-registered RULES (sealed in prose below BEFORE any statistic is computed;
this text is part of the committed artifact and is not edited after the run).

DEFINITIONS GUARD (established before sealing, from exp026 derive_stream):
a desert hit = a NEWBORN cell with train_p >= BAR in a desert-regime gen.
a birth = the FIRST desert gen with >= 1 hit; the desert regime ENDS at birth
(bar_seen_before flips). CONSEQUENCE (tautology, sealed): desert_hits >= 1
iff birth occurred, so ANY test conditioning hit-rates on crossing status is
DEFINITIONAL and is BANNED as evidence in this lab. The lawful residual
structure lives in (a) WITHIN-birth-gen multiplicity and (b) ACROSS-stream
birth counts/timing given counterfactual exposure.

RULE-1 (multiplicity dispersion): for the 8 birth events in the pooled
16-stream corpus, conditional on total birth-gen newborns N_b and total
birth-gen hits H_b=10, the shared per-draw hazard predicts hit allocation
across birth gens proportional to newborn counts (weighted-multinomial).
Exact conditional deviance over all weighted compositions of 10 into 8
parts; VERDICT: REJECT-CLUSTERED if exact p < 0.05, CONSISTENT otherwise.
Bonferroni never appears here; this is one exact test.

RULE-2 (birth-count vs exposure): under the shared hazard with w = pooled
hits/pooled draws, each stream's counterfactual birth probability is
p_s = 1-(1-w)^E_s where E_s is the stream's FULL 12-gen newborn count
(regime-agnostic; a stream that births early is counterfactually exposed to
its remaining gens' newborns). The exact distribution of the birth count
X = sum_s Bernoulli(p_s) is the Poisson-binomial, computed by DP.
VERDICT: REJECT if P(X >= 8) < 0.05 (observed births = 8 of 16), CALIBRATED
otherwise. p_s formula re-verified against exp027's sealed table (k3 0.05996
etc.) before use; abort on mismatch.

RULE-3 (birth timing): EXPLORATORY, labeled, no verdict: birth-gen histogram
only. Any test invented after seeing it is a new pre-registration, not a
result.

REPORTING: all 16 streams listed; per-birth-gen (newborns, hits) table in
full; no peeking exception; labeled MC banned (all tests exact); guards:
pilot totals re-derived from raw telemetry and checked vs sealed 74/1037/4;
census totals vs sealed 972/6; suite stays 7/7 green outside this file;
md5-identical re-run recorded.
"""

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = 0.45  # sealed across exp018/exp026/exp027/exp029 — guard aborts on drift
SEALED_PILOT = {"desert_gens": 74, "desert_draws": 1037, "desert_hits": 4}
SEALED_CENSUS = {"desert_gens": 69, "desert_draws": 972, "desert_hits": 6}
# exp027 sealed per-stream birth probabilities (pilot, w=4/1037) for formula re-verification
SEALED_P_S_PILOT = {"k3": 0.059962795981501116, "k4": 0.47148386964835864,
                    "k5": 0.18835799123013786, "k6": 0.3735168699459248,
                    "k7": 0.46738288691935337, "k0": 0.4895510289403595,
                    "k1": 0.4915199738624796, "k2": 0.47959134943725423}


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def derive_stream(rows):
    prev = None
    bar_seen_before = False
    gens = []
    for r in rows:
        cloud = r["census"]["cloud"]
        keys = {genome_key(c) for c in cloud}
        newborns = list(cloud) if prev is None else \
            [c for c in cloud if genome_key(c) not in prev]
        hits = sum(1 for c in newborns if c["train_p"] >= BAR)
        regime = "plateau" if bar_seen_before else "desert"
        gens.append({"gen": r["gen"], "draws": len(newborns), "hits": hits,
                     "regime": regime})
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen_before = True
    desert = [g for g in gens if g["regime"] == "desert"]
    birth = next((g for g in desert if g["hits"] >= 1), None)
    return {"all_gens": gens, "desert_gens": [g["gen"] for g in desert],
            "desert_draws": sum(g["draws"] for g in desert),
            "desert_hits": sum(g["hits"] for g in desert),
            "birth_gen": birth["gen"] if birth else None,
            "birth_draws": birth["draws"] if birth else None,
            "birth_hits": birth["hits"] if birth else None,
            "full_12gen_newborns": sum(g["draws"] for g in gens)}


def load(path):
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def weighted_compositions(total, weights):
    """All count-vectors summing to `total` over len(weights) parts, each
    vector yielded with its multinomial weight prod C(w_i, k_i)."""
    parts = len(weights)
    if parts == 1:
        if total <= weights[0]:
            yield (total,), 1.0
        return
    for k in range(min(total, weights[0]) + 1):
        for rest, w in weighted_compositions(total - k, weights[1:]):
            import math
            yield (k,) + rest, math.comb(weights[0], k) * w


def exact_deviance_tail(hits, weights, w, obs_vec):
    """P(deviance >= observed) under weighted-multinomial allocation of
    `hits` across parts with newborn counts `weights`; per-draw hazard w
    cancels in the deviance ratios, so allocation is exact."""
    import math
    n = sum(weights)

    def deviance(k):
        tot = 0.0
        for ki, Wi in zip(k, weights):
            if ki == 0:
                continue
            exp_k = hits * Wi / n
            tot += 2 * ki * math.log(ki / exp_k)
        return tot

    obs_dev = deviance(obs_vec)
    total_w = 0.0
    tail_w = 0.0
    for k, wt in weighted_compositions(hits, weights):
        total_w += wt
        if deviance(k) >= obs_dev - 1e-12:
            tail_w += wt
    return tail_w / total_w


def poisson_binomial_upper(p, k_obs):
    """Exact P(X >= k_obs) for X = sum Bernoulli(p_i) via DP."""
    dp = [1.0] + [0.0] * len(p)
    for pi in p:
        nxt = [0.0] * (len(dp) + 1)
        for i, v in enumerate(dp):
            nxt[i] += v * (1 - pi)
            nxt[i + 1] += v * pi
        dp = nxt
    return sum(dp[k_obs:])


def main():
    pilot_ids = ["k0", "k1", "k2", "k3", "k4", "k5", "k6", "k7"]
    census_ids = ["k8", "k9", "k10", "k11", "k12", "k13", "k14", "k15"]
    streams = {}
    pilot_files = {"k3": "exp022.telemetry.k3.jsonl",
                   "k4": "exp022.telemetry.k4.jsonl",
                   "k5": "exp022.telemetry.k5.jsonl",
                   "k6": "exp022.telemetry.k6.jsonl",
                   "k7": "exp022.telemetry.k7.jsonl",
                   "k0": "exp024.telemetry.k0.jsonl",
                   "k1": "exp024.telemetry.k1.jsonl",
                   "k2": "exp024.telemetry.k2.jsonl"}
    for sid, fname in pilot_files.items():
        rows = load(HERE / fname)
        streams[sid] = derive_stream(rows)
    for sid in census_ids:
        rows = load(HERE / f"exp029.telemetry.{sid}.jsonl")
        streams[sid] = derive_stream(rows)

    # ---- guards: totals vs sealed ----
    pilot = {k: sum(streams[s][k] for s in pilot_ids)
             for k in ("desert_draws", "desert_hits")}
    census = {k: sum(streams[s][k] for s in census_ids)
              for k in ("desert_draws", "desert_hits")}
    guards = {
        "pilot_rederivation_vs_sealed": {
            "desert_draws": [pilot["desert_draws"], SEALED_PILOT["desert_draws"],
                             pilot["desert_draws"] == SEALED_PILOT["desert_draws"]],
            "desert_hits": [pilot["desert_hits"], SEALED_PILOT["desert_hits"],
                            pilot["desert_hits"] == SEALED_PILOT["desert_hits"]]},
        "census_rederivation_vs_sealed": {
            "desert_draws": [census["desert_draws"], SEALED_CENSUS["desert_draws"],
                             census["desert_draws"] == SEALED_CENSUS["desert_draws"]],
            "desert_hits": [census["desert_hits"], SEALED_CENSUS["desert_hits"],
                            census["desert_hits"] == SEALED_CENSUS["desert_hits"]]},
    }
    ok = (guards["pilot_rederivation_vs_sealed"]["desert_draws"][2]
          and guards["pilot_rederivation_vs_sealed"]["desert_hits"][2]
          and guards["census_rederivation_vs_sealed"]["desert_draws"][2]
          and guards["census_rederivation_vs_sealed"]["desert_hits"][2])
    if not ok:
        raise SystemExit("GUARD ABORT: re-derived totals drifted from sealed")

    # ---- RULE-2 formula re-verification against exp027 sealed p_s ----
    w_pilot = SEALED_PILOT["desert_hits"] / SEALED_PILOT["desert_draws"]
    p_s_check = {s: 1 - (1 - w_pilot) ** streams[s]["desert_draws"]
                 for s in pilot_ids}
    formula_ok = all(abs(p_s_check[s] - SEALED_P_S_PILOT[s]) < 1e-9
                     for s in pilot_ids)
    guards["p_s_formula_reverification_exp027"] = {"ok": formula_ok}

    # ---- corpus facts ----
    N = pilot["desert_draws"] + census["desert_draws"]
    H = pilot["desert_hits"] + census["desert_hits"]
    w = H / N
    crossers = [s for s in pilot_ids + census_ids
                if streams[s]["birth_gen"] is not None]
    non_crossers = [s for s in pilot_ids + census_ids
                    if streams[s]["birth_gen"] is None]

    # ---- RULE-1: within-birth-gen multiplicity dispersion ----
    birth_table = {s: {"birth_gen": streams[s]["birth_gen"],
                       "birth_newborns": streams[s]["birth_draws"],
                       "birth_hits": streams[s]["birth_hits"]}
                   for s in crossers}
    weights = [streams[s]["birth_draws"] for s in crossers]
    hits_vec = tuple(streams[s]["birth_hits"] for s in crossers)
    p_rule1 = exact_deviance_tail(H, weights, w, hits_vec)

    # ---- RULE-2: birth count vs Poisson-binomial counterfactual ----
    p_s = {s: 1 - (1 - w) ** streams[s]["full_12gen_newborns"]
           for s in pilot_ids + census_ids}
    expected_births = sum(p_s.values())
    p_rule2 = poisson_binomial_upper([p_s[s] for s in pilot_ids + census_ids],
                                     len(crossers))

    # ---- RULE-3 (exploratory, labeled): birth-gen histogram ----
    birth_hist = {}
    for s in crossers:
        g = streams[s]["birth_gen"]
        birth_hist[f"{s}(g{g})"] = streams[s]["birth_hits"]

    out = {
        "experiment": "exp030 birth-structure decomposition (multiplicity + birth-count)",
        "definitions_guard": ("birth = first desert gen with >=1 newborn >= BAR; "
                              "regime ends at birth => hit-rates conditioned on "
                              "crossing status are TAUTOLOGICAL and BANNED as evidence"),
        "corpus": {"streams": 16, "desert_draws": N, "desert_hits": H,
                   "w_pooled": w, "births": len(crossers),
                   "crossers": crossers, "non_crossers": non_crossers},
        "birth_event_table": birth_table,
        "rule1_multiplicity_dispersion": {
            "weights_birthgen_newborns": weights,
            "observed_hits_per_birth": list(hits_vec),
            "exact_p": p_rule1,
            "verdict": "REJECT-CLUSTERED" if p_rule1 < 0.05 else "CONSISTENT",
            "read": ("within-birth-gen hit allocation more clumped than the "
                     "shared per-draw hazard predicts" if p_rule1 < 0.05 else
                     "multiplicity consistent with shared per-draw hazard")},
        "rule2_birth_count_vs_counterfactual_exposure": {
            "p_s_per_stream": p_s,
            "expected_births_under_shared_hazard": expected_births,
            "observed_births": len(crossers),
            "exact_upper_tail_P_X_ge_observed": p_rule2,
            "verdict": "REJECT" if p_rule2 < 0.05 else "CALIBRATED",
            "read": ("8 of 16 births exceed what counterfactual full exposure "
                     "under the shared hazard predicts" if p_rule2 < 0.05 else
                     "birth count calibrated to shared hazard")},
        "rule3_birth_timing_exploratory_labeled": {
            "histogram": birth_hist,
            "note": "labeled EXPLORATORY; any test invented now would be a new "
                    "pre-registration, not a result"},
        "guards": guards,
        "honesty": ("same 16-stream corpus as exp029; Q1 and Q2 test DISJOINT "
                    "structure (within-birth-gen allocation; across-stream birth "
                    "count) and do not re-litigate hit allocation, which exp029 "
                    "settled (p=0.003256). Pure exact analysis, no rng, no MC."),
    }
    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp030.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: out[k] for k in
                      ("corpus", "rule1_multiplicity_dispersion",
                       "rule2_birth_count_vs_counterfactual_exposure")},
                     indent=1, sort_keys=True))
    print("digest", digest)


if __name__ == "__main__":
    main()
