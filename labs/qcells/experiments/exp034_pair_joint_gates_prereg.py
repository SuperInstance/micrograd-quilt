"""exp034 — PAIRED-STREAM JOINT GATES: pre-registration of the
escalation lane named by exp033's report: 'per-stream rate lane
CLOSED at n=24 per seal - any escalation needs a fresh
pre-registration (candidate: paired-stream joint gates)'.

WHY PAIRS: exp029's pooled exact deviance REFUTED one-shared-
hazard at 10 events / 16 streams (p=0.003256, sealed), but the
per-stream Bonferroni gates (exp032 design, exp033 evaluation at
n=24) named NO stream hot or frozen — per-stream resolution is
frozen-side-blind (n_zero=1238 vs design n=169, exp032 Q3) and
hot-side-thin.  Between pooled-everything (resolution 24) and
single streams (resolution 1, underpowered) sits resolution 2:
PAIRS.  Pairing doubles the draw mass (~2x n) while keeping a
nameable unit.  Cherry-picking pairs after seeing counts would be
Goodhart, so this seal fixes the pairing rule = EXHAUSTIVE
enumeration of ALL C(24,2)=276 unordered pairs BEFORE any pair
statistic is computed.

SEALED DESIGN (this script, BEFORE any pair statistic):
  Universe: the 24 existing census streams (16 corpus k0-k15 +
  block E k16-k23).  NO new runs — pairs are pure re-analysis of
  sealed telemetry; the seal's job is to fix the gates and the
  decision rules before the pair statistics exist.
  Null hazard: w_pair = 15/3078 (full 24-stream pooled MLE at
  seal time), FIXED, never re-estimated within this lane.
  Honesty: the 15 hits set w_pair, so every pair read in exp035
  is conditioning-on-total context (shrink toward the middle);
  labeled, not hidden.
  Family: m = 276 pairs x 2 probes = 552 tests.
  Gate: g = 0.05 / 552 (Bonferroni over the sealed family).
  PROBE A (joint-count): pair n = n_i+n_j, h = h_i+h_j;
    p_plus = P(Bin(n, w_pair) >= h), p_minus = P(Bin(n, w_pair)
    <= h); TRIP iff min(p_plus, p_minus) <= g.  Asks: does this
    PAIR deviate from the pooled hazard?
  PROBE B (pair-contrast): two-sided Fisher exact on
    [[h_i, n_i-h_i], [h_j, n_j-h_j]]; TRIP iff p <= g.  Asks: do
    these two streams DIFFER (any direction)?  Validity is by
    construction: Fisher's exact p is valid under the pair-shared
    null, so P(p <= g) <= g, and the union bound closes the
    family at exactly 0.05 with NO independence assumption.
  SEALED DECISION RULES (evaluated once, in exp035):
    FAMILY-PAIR-REFUTED iff any (probe, pair) trips.
    PAIR-DEVIANT (A): named pair, direction from the tail.
    PAIR-HETEROGENEOUS (B): named pair.
    A-trip without B-trip = pair deviates from w_pair together.
    B-trip without A-trip = hazard difference without net
    deviation from w_pair.
  CLOSURE (sealed): pairs are the FINEST resolution this lane
  ever reaches.  No triples, no re-pairing, no dropping probes.
  Any finer resolution = a fresh pre-registration.

SEALED PROBES (this script, pure exact arithmetic, no rng):
  Q0  GUARDS: re-derive all 24 streams from raw telemetry (16
      corpus vs exp032 sealed table; block E vs exp033 sealed
      facts) and abort on drift.
  Q1  FAMILY SIZE: construction guarantee (union bound over 552
      exact-valid tests = family size <= 0.05, no independence
      needed) PLUS the exact expected number of null trips for
      both probes (sum of per-pair null trip probabilities).
      Verdict sealed in prose BEFORE numbers: calibrated by
      construction; the informative number is the expectation.
  Q2  DESIGN POWER (labeled): exp028 two-class composition on a
      design block (3 hot at 10x, 5 frozen at 0.1x, design
      n=169/stream, pair n=338): probe A per-class pi;
      probe B hot-frozen contrast power; bounds on P(>=1 trip).
  Q3  FROZEN VISIBILITY: n_zero for a zero-hit PAIR under probe A
      ((1-w_pair)^n <= g) vs design pair n=338.  Verdict sealed
      in prose BEFORE the number: if n_zero >> 338 the frozen arm
      stays pair-invisible and probe B's contrast is the only
      frozen-side instrument.
  Q4  NONE.  No real-data pair statistic is computed anywhere in
      this script — not even 'which pairs WOULD trip'.  The
      evaluation is exp035, a separate experiment.

GUARDS: sealed 24-stream table re-derived from raw telemetry;
abort on drift.  Pure exact arithmetic (direct summation /
log-space hypergeometric), no rng, no MC, no normal approx.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp032_censusn_prereg import (
    SEALED as SEALED_CORPUS,
    SEALED_TOTAL_DRAWS,
    SEALED_TOTAL_HITS,
    CORPUS,
    scan,
    load,
    binom_tails,
)

HERE = Path(__file__).resolve().parent

W_PAIR = 15 / 3078          # sealed null hazard: 24-stream pooled MLE
TOTAL_DRAWS_24 = 3078
TOTAL_HITS_24 = 15
M_PAIRS = 276               # C(24,2), exhaustive enumeration
M_TESTS = 552               # 276 pairs x 2 probes
G = 0.05 / M_TESTS          # sealed Bonferroni gate
DESIGN_N = 169              # design draws per stream (exp032 label)
DESIGN_PAIR_N = 2 * DESIGN_N

# sealed block-E facts (exp033 sealed evaluation, actual counts)
SEALED_BLOCK_E = {
    "k16": (166, 0, None), "k17": (164, 0, None),
    "k18": (129, 1, 129), "k19": (161, 0, None),
    "k20": (55, 2, 55), "k21": (121, 1, 121),
    "k22": (157, 0, None), "k23": (116, 1, 116),
}
BLOCK_E_FILES = {f"k{16 + i}": f"exp033.telemetry.k{16 + i}.jsonl"
                 for i in range(8)}
SEALED_BLOCK_E_TOTALS = (1069, 5)


def hypergeom_log_pmf(N, K, draws, x):
    """log P(X=x), X ~ Hypergeometric(N, K, draws)."""
    return (math.lgamma(K + 1) - math.lgamma(x + 1)
            - math.lgamma(K - x + 1)
            + math.lgamma(N - K + 1) - math.lgamma(draws - x + 1)
            - math.lgamma(N - K - draws + x + 1)
            - (math.lgamma(N + 1) - math.lgamma(draws + 1)
               - math.lgamma(N - draws + 1)))


def fisher_two_sided(n_i, n_j, h_i, h_j):
    """Two-sided Fisher exact p on [[h_i, n_i-h_i],[h_j, n_j-h_j]]
    via the probability-ordering definition (sum hypergeom masses
    <= observed mass).  Exact; log-space with linear pass."""
    N = n_i + n_j
    H = h_i + h_j
    lo = max(0, H - n_j)
    hi = min(H, n_i)
    logs = {x: hypergeom_log_pmf(N, H, n_i, x) for x in range(lo, hi + 1)}
    l_obs = logs[h_i]
    m = max(logs.values())
    num = sum(math.exp(v - m) for v in logs.values() if v <= l_obs + 1e-12)
    den = sum(math.exp(v - m) for v in logs.values())
    return num / den


def binom_pmf_list(n, p):
    """Full Binomial pmf, h = 0..n, by recurrence.  Pure exact
    float arithmetic; p in (0,1)."""
    p_plus, _ = binom_tails(n, p)
    pmf = [p_plus[h] - (p_plus[h + 1] if h < n else 0.0)
           for h in range(n + 1)]
    return pmf


def probA_trip_set(n):
    """Probe A null gate-hit set at (n, w_pair): H = {h : min tail
    <= g}.  The gate is defined once at the sealed null."""
    p_plus, p_minus = binom_tails(n, W_PAIR)
    return sorted(h for h in range(n + 1)
                  if min(p_plus[h], p_minus[h]) <= G)


def pi_at(n, p, trip):
    """P(Bin(n,p) lands in the null-defined gate-hit set)."""
    pmf = binom_pmf_list(n, p)
    return sum(pmf[h] for h in trip)


def _sparse_pmf(n, p, floor=1e-15):
    """[(h, pmf)] for h with pmf > floor.  Cells below the floor
    carry < 1e-15 mass each (<< gate 9.06e-5); dropping them is an
    exactness-preserving truncation, total dropped mass < 1e-12."""
    pmf = binom_pmf_list(n, p)
    return [(h, v) for h, v in enumerate(pmf) if v > floor]


def probeB_null_trip_prob(n_i, n_j):
    """Exact P(Fisher p <= g) under the sealed null w_pair for
    both streams: sum over all (h_i,h_j) cells of the product
    pmf x indicator.  Fisher validity gives <= g; this computes
    the exact expectation contribution."""
    cells_i = _sparse_pmf(n_i, W_PAIR)
    cells_j = _sparse_pmf(n_j, W_PAIR)
    tot = 0.0
    for hi, pi_ in cells_i:
        for hj, pj in cells_j:
            if fisher_two_sided(n_i, n_j, hi, hj) <= G:
                tot += pi_ * pj
    return tot


def probeB_alt_trip_prob(n_i, p_i, n_j, p_j):
    """Power of the probe-B contrast under alternative hazards
    (p_i, p_j) for the two streams.  Same exact cell sum."""
    cells_i = _sparse_pmf(n_i, p_i)
    cells_j = _sparse_pmf(n_j, p_j)
    tot = 0.0
    for hi, pi_ in cells_i:
        for hj, pj in cells_j:
            if fisher_two_sided(n_i, n_j, hi, hj) <= G:
                tot += pi_ * pj
    return tot


def main():
    # ---- Q0 guards ----------------------------------------------
    streams = {}
    for fname, sid in CORPUS:
        streams[sid] = scan(load(fname))
    for sid, fname in BLOCK_E_FILES.items():
        streams[sid] = scan(load(fname))
    guards = {}
    total_draws = total_hits = 0
    for sid, (d, h, b) in {**SEALED_CORPUS, **SEALED_BLOCK_E}.items():
        s = streams[sid]
        total_draws += s["draws"]
        total_hits += s["hits"]
        guards[sid] = {
            "draws": [s["draws"], d, s["draws"] == d],
            "hits": [s["hits"], h, s["hits"] == h],
            "birth_cum": [s["birth_cum"], b, s["birth_cum"] == b]}
    guards["corpus_totals"] = {
        "draws": [sum(streams[s]["draws"] for s in SEALED_CORPUS),
                  SEALED_TOTAL_DRAWS,
                  sum(streams[s]["draws"] for s in SEALED_CORPUS)
                  == SEALED_TOTAL_DRAWS],
        "hits": [sum(streams[s]["hits"] for s in SEALED_CORPUS),
                 SEALED_TOTAL_HITS,
                 sum(streams[s]["hits"] for s in SEALED_CORPUS)
                 == SEALED_TOTAL_HITS]}
    be_draws = sum(streams[s]["draws"] for s in SEALED_BLOCK_E)
    be_hits = sum(streams[s]["hits"] for s in SEALED_BLOCK_E)
    guards["blockE_totals"] = {
        "draws": [be_draws, SEALED_BLOCK_E_TOTALS[0],
                  be_draws == SEALED_BLOCK_E_TOTALS[0]],
        "hits": [be_hits, SEALED_BLOCK_E_TOTALS[1],
                 be_hits == SEALED_BLOCK_E_TOTALS[1]]}
    guards["totals_24"] = {
        "draws": [total_draws, TOTAL_DRAWS_24,
                  total_draws == TOTAL_DRAWS_24],
        "hits": [total_hits, TOTAL_HITS_24,
                 total_hits == TOTAL_HITS_24]}
    ok = all(guards[sid]["draws"][2] and guards[sid]["hits"][2]
             and guards[sid]["birth_cum"][2]
             for sid in {**SEALED_CORPUS, **SEALED_BLOCK_E}) \
        and all(guards[t][k][2] for t in
                ("corpus_totals", "blockE_totals", "totals_24")
                for k in ("draws", "hits"))
    if not ok:
        raise SystemExit("GUARD ABORT: corpus drifted from sealed tables")

    sids = sorted(streams.keys(), key=lambda s: int(s[1:]))

    # ---- Q1 family size ------------------------------------------
    # Construction guarantee: 552 exact-valid tests, Bonferroni
    # gate -> family size <= 0.05 by union bound, no independence.
    # Exact expected null trips: probe A per pair (integrate over
    # h at the null with the pair's real n = n_i+n_j — n is
    # ancillary, sealed at evaluation time), probe B per pair
    # (exact cell sum).  NO real h enters anything below.
    expA = 0.0
    expB = 0.0
    per_pair = {}
    for a in range(len(sids)):
        for b in range(a + 1, len(sids)):
            si, sj = sids[a], sids[b]
            n_i = streams[si]["draws"]
            n_j = streams[sj]["draws"]
            n_pair = n_i + n_j
            trip = probA_trip_set(n_pair)
            piA = pi_at(n_pair, W_PAIR, trip)
            piB = probeB_null_trip_prob(n_i, n_j)
            expA += piA
            expB += piB
            per_pair[f"{si},{sj}"] = {"n_pair": n_pair,
                                      "pi_null_A": piA,
                                      "pi_null_B": piB}
    q1_verdict = ("CALIBRATED-BY-CONSTRUCTION: union bound closes "
                  "the 552-test family at exactly 0.05 with no "
                  "independence assumption; exact expected null "
                  "trips reported as the informative number")

    # ---- Q2 design power (labeled) -------------------------------
    trip_design = probA_trip_set(DESIGN_PAIR_N)
    altA = {}
    for mult in (10.0, 3.0, 1.0, 0.1):
        altA[f"{mult:g}x"] = pi_at(DESIGN_PAIR_N, mult * W_PAIR,
                                   trip_design)
    # design composition: 3 hot @10x, 5 frozen @0.1x (exp028).
    # probe A pair classes at design n: HH, HF, FF
    p_hh = altA["10x"]
    p_hf = pi_at(DESIGN_PAIR_N, (10.0 + 0.1) / 2 * W_PAIR, trip_design)
    p_ff = altA["0.1x"]
    # expected trips probe A over the design block's C(8,2)=28 pairs
    eA_design = 3 * p_hh + 15 * p_hf + 10 * p_ff
    # probe B: hot-frozen contrast (the informative design pair)
    pB_hf = probeB_alt_trip_prob(DESIGN_N, 10 * W_PAIR,
                                 DESIGN_N, 0.1 * W_PAIR)
    pB_hh = probeB_alt_trip_prob(DESIGN_N, 10 * W_PAIR,
                                 DESIGN_N, 10 * W_PAIR)
    pB_ff = probeB_alt_trip_prob(DESIGN_N, 0.1 * W_PAIR,
                                 DESIGN_N, 0.1 * W_PAIR)
    # union-bound power ceiling for >=1 trip (design block pairs
    # only, 28 pairs x 2 probes): sum of alt trip probs
    ub_power = (eA_design
                + 3 * pB_hh + 15 * pB_hf + 10 * pB_ff)

    # ---- Q3 frozen visibility -------------------------------------
    n_zero = math.ceil(math.log(G) / math.log(1 - W_PAIR))
    q3_prose_sealed = ("if n_zero >> 338 the frozen arm stays "
                       "pair-invisible under probe A and probe B's "
                       "contrast is the only frozen-side instrument")
    q3_verdict = ("FROZEN-PAIR-BLIND under probe A at design n"
                  if n_zero > 2 * DESIGN_PAIR_N else
                  "FROZEN-PAIR-VISIBLE under probe A at design n")

    out = {
        "experiment": (
            "exp034 paired-stream joint gates PRE-REGISTRATION "
            "(escalation lane named by exp033: per-stream rate lane "
            "CLOSED at n=24; fresh pre-registration required; "
            "candidate = paired-stream joint gates).  Sealed BEFORE "
            "any pair statistic exists; evaluation = exp035."),
        "preregistration": (
            "sealed in this script; exhaustive C(24,2)=276 pair "
            "enumeration (no cherry-picking); two probes per pair; "
            "gate g=0.05/552; null hazard w_pair=15/3078 fixed; "
            "closure: pairs are the finest resolution, no re-pairing "
            "/no triples/no probe drops; no real-data pair statistic "
            "is computed here — Q4 deliberately absent"),
        "sealed_design": {
            "universe": ("24 census streams (16 corpus k0-k15 + "
                         "block E k16-k23), no new runs"),
            "null_hazard": ("w_pair = 15/3078 full pooled MLE at "
                            "seal time, fixed, never re-estimated; "
                            "the 15 hits set it (conditioning-on-"
                            "total caveat, all pair reads in exp035 "
                            "are labeled context); exp032/033's "
                            "w_hat=10/2009 seals stand for their "
                            "own lanes"),
            "family": ("m = 276 pairs x 2 probes = 552 tests; "
                       "Bonferroni gate g = 0.05/552"),
            "probe_A": ("joint-count: n=n_i+n_j, h=h_i+h_j; trip "
                        "iff min(P(Bin(n,w_pair)>=h), "
                        "P(Bin(n,w_pair)<=h)) <= g; asks does the "
                        "PAIR deviate from the pooled hazard"),
            "probe_B": ("two-sided Fisher exact on the 2x2; trip "
                        "iff p <= g; asks do the streams DIFFER; "
                        "validity by construction (Fisher exact => "
                        "P(p<=g) <= g under the shared-null)"),
            "decision_rules": ("FAMILY-PAIR-REFUTED iff any "
                               "(probe,pair) trips; PAIR-DEVIANT "
                               "(A) named with tail direction; "
                               "PAIR-HETEROGENEOUS (B) named; "
                               "A-only = pair deviates together; "
                               "B-only = hazard difference without "
                               "net deviation"),
            "closure": ("pairs are the FINEST resolution of the "
                        "rate lane; finer = fresh pre-registration")},
        "guards": guards,
        "guard_ok": ok,
        "q1_family_size": {
            "sealed_prose": ("family calibrated by construction "
                             "(union bound, no independence); the "
                             "informative number is the exact "
                             "expected null trips"),
            "gate": G,
            "m_tests": M_TESTS,
            "construction_guarantee": ("family size <= 0.05 exact "
                                       "by union bound over 552 "
                                       "exact-valid tests"),
            "expected_null_trips_probe_A": expA,
            "expected_null_trips_probe_B": expB,
            "expected_null_trips_total": expA + expB,
            "verdict": q1_verdict,
            "per_pair_null_trip_probs": per_pair},
        "q2_design_power_labeled": {
            "note": ("exp028 composition on a design block: 3 hot "
                     "@10x, 5 frozen @0.1x, design n=169/stream, "
                     "pair n=338; exact arithmetic; existing "
                     "streams excluded (observed facts, not random "
                     "future data)"),
            "probe_A_pair_n": DESIGN_PAIR_N,
            "probe_A_per_class_pi": altA,
            "probe_A_pair_classes_HH_HF_FF": [p_hh, p_hf, p_ff],
            "probe_A_expected_trips_design_block": eA_design,
            "probe_B_contrast_HH_HF_FF": [pB_hh, pB_hf, pB_ff],
            "probe_B_power_note": ("hot-frozen contrast is the "
                                   "frozen-side instrument"),
            "union_bound_power_ceiling_design_block": ub_power},
        "q3_frozen_visibility": {
            "sealed_prose": q3_prose_sealed,
            "gate": G,
            "n_zero_for_zero_hit_pair": n_zero,
            "design_pair_n": DESIGN_PAIR_N,
            "verdict": q3_verdict},
        "synthesis": (
            f"Pair escalation sealed before any pair statistic "
            f"exists.  Family of 552 exact-valid tests is "
            f"CALIBRATED-BY-CONSTRUCTION (union bound <= 0.05); "
            f"exact expected null trips: probe A {expA:.4f}, "
            f"probe B {expB:.4f} (total {expA + expB:.4f} of 552 "
            f"tests).  Design power at pair n=338: probe A trips "
            f"for a 10x-hot pair w.p. {altA['10x']:.3f}, hot-"
            f"frozen pair {p_hf:.3f}, frozen pair {altA['0.1x']:.3f}"
            f"; probe B hot-frozen contrast {pB_hf:.3f}.  Frozen "
            f"side: n_zero={n_zero} vs design pair n="
            f"{DESIGN_PAIR_N} -> {q3_verdict}.  Next: exp035 "
            "evaluates the sealed gates once over the 24 streams; "
            "whatever the verdict, the rate lane CLOSES at pair "
            "resolution."),
        "honesty": ("Pure exact arithmetic (Binomial direct "
                    "summation; log-space hypergeometric Fisher), "
                    "no rng / no MC / no normal approximation.  "
                    "Guards re-derive all 24 streams from raw "
                    "telemetry and abort on drift.  No real-data "
                    "pair statistic is computed anywhere in this "
                    "script — not even a peek at which pairs would "
                    "trip.  The 15 hits set w_pair; every pair "
                    "read in exp035 is conditioning-on-total "
                    "context."),
    }

    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()
                         ).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp034.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "guard_ok": ok,
        "q1_expected_null_trips_A": round(expA, 4),
        "q1_expected_null_trips_B": round(expB, 4),
        "q2_piA_10x_pair": round(altA["10x"], 4),
        "q2_piA_HF_pair": round(p_hf, 4),
        "q2_piB_HF_contrast": round(pB_hf, 4),
        "q3_n_zero_pair": n_zero,
        "q3_verdict": q3_verdict,
        "digest": digest}, indent=1))


if __name__ == "__main__":
    main()
