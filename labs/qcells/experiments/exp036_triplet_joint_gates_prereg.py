"""exp036 — TRIPLET-STREAM JOINT GATES: pre-registration of the
escalation lane named by the tension doc (docs/TENSION-exp029-vs-
exp033-035.md): 'commission block-F census / triplet-gate seal
(both need fresh pre-registration)'.

WHY TRIPLETS: exp033 closed the per-stream lane (gate 0.05/24,
no stream named), exp035 closed the pair lane (gate 0.05/552,
zero trips on both probes).  The pooled exp029 deviance
refutation (p=0.003256) still decomposes into no nameable unit.
The one remaining analytic rung WITHOUT new telemetry is
resolution 3: TRIPLETS.  Cherry-picking triplets after seeing
counts would be Goodhart, so this seal fixes the triplet rule =
EXHAUSTIVE enumeration of ALL C(24,3)=2024 unordered triplets
BEFORE any triplet statistic is computed.

SEALED DESIGN (this script, BEFORE any triplet statistic):
  Universe: the 24 existing census streams (16 corpus k0-k15 +
  block E k16-k23).  NO new runs — triplets are pure re-analysis
  of sealed telemetry.
  Null hazard: w_tri = 15/3078 (full 24-stream pooled MLE),
  FIXED, never re-estimated within this lane.  The 15 hits set
  it; every triplet read in the evaluation is conditioning-on-
  total context (shrink toward the middle); labeled, not hidden.
  Family: m = 2024 triplets x 4 tests = 8096 tests
    (probe A: 1 joint-count per triplet;
     probe B: the 3 pairwise Fisher contrasts inside the
     triplet — trip iff ANY of the three p <= g).
  Gate: g = 0.05 / 8096 (Bonferroni over the sealed family).
  PROBE A (joint-count): triplet n = n_i+n_j+n_k, h likewise;
    TRIP iff min(P(Bin(n,w_tri) >= h), P(Bin(n,w_tri) <= h))
    <= g.  Asks: does this TRIPLET deviate from the pooled
    hazard?
  PROBE B (within-triplet contrast): the three two-sided Fisher
    exact tests on the triplet's member pairs; TRIP iff any
    p <= g.  Asks: is there ANY internal heterogeneity?  Each
    Fisher test is exact-valid (P(p <= g) <= g under the shared
    null), so the union bound closes the whole 8096-test family
    at exactly 0.05 with NO independence assumption — dependence
    between the three in-triplet Fisher tests is real (shared
    streams) and irrelevant to the bound.
  SEALED DECISION RULES (evaluated once, in a separate
  experiment, only if Casey commissions it):
    FAMILY-TRIPLET-REFUTED iff any (probe, triplet) trips.
    TRIPLET-DEVIANT (A): named triplet, direction from tail.
    TRIPLET-HETEROGENEOUS (B): named triplet + named pair.
  CLOSURE (sealed): triplets are the LAST analytic rung of the
    rate lane over these 24 streams.  No quadruples, no re-
    tripletion, no probe drops.  Beyond triplets = new telemetry
    (a fresh census block under its own pre-registration), not
    more arithmetic on the same 15 hits.

SEALED PROBES (this script, pure exact arithmetic, no rng):
  Q0  GUARDS: re-derive all 24 streams from raw telemetry and
      abort on drift (same sealed tables as exp034).
  Q1  FAMILY SIZE / FEASIBILITY: the exact expected number of
      null trips for probe A (sum over triplets of
      P(Bin(n_tri, w_tri) in the null gate-hit set)) and for
      probe B (sum over the 6072 pair-instances of the exact
      per-pair Fisher gate-hit probabilities; linearity of
      expectation needs NO independence).  Verdict sealed in
      prose BEFORE numbers: at gate 6.17e-6 the family is
      calibrated by construction, and the informative question
      is whether ANY design-hot triplet has non-trivial power.
  Q2  DESIGN POWER (labeled): exp028 two-class composition on a
      design triplet (3 hot @10x, 5 frozen @0.1x, design
      n=169/stream, triplet n=507): probe A per-class pi for
      HHH/HHF/HFF/FFF; probe B HF-pair contrast at the sealed g;
      union-bound power ceiling for >=1 trip over the design
      block's C(8,3)=56 triplets.
  Q3  FROZEN VISIBILITY: n_zero for a zero-hit triplet under
      probe A ((1-w_tri)^n <= g) vs design triplet n=507.
      Verdict sealed in prose BEFORE the number.
  Q4  NONE.  No real-data triplet statistic is computed anywhere
      in this script — not even 'which triplets WOULD trip'.
      The evaluation is a separate experiment, run only if Casey
      commissions it after reading the tension face.

GUARDS: sealed 24-stream table re-derived from raw telemetry;
abort on drift.  Pure exact arithmetic (Binomial direct
summation; log-space hypergeometric Fisher), no rng, no MC, no
normal approximation.  Probe-B per-pair gate-hit probabilities
are memoized on (n_i, n_j) — there are only 24 streams, so at
most C(24,2) distinct pairs; linearity of expectation closes
Q1 without any independence assumption.
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
from exp034_pair_joint_gates_prereg import (
    SEALED_BLOCK_E,
    BLOCK_E_FILES,
    SEALED_BLOCK_E_TOTALS,
    W_PAIR as W_TRI,
    fisher_two_sided,
    binom_pmf_list,
    _sparse_pmf,
)

HERE = Path(__file__).resolve().parent

TOTAL_DRAWS_24 = 3078
TOTAL_HITS_24 = 15
M_TRIPLETS = 2024          # C(24,3), exhaustive enumeration
TESTS_PER_TRIPLET = 4      # probe A + 3 pairwise Fisher
M_TESTS = M_TRIPLETS * TESTS_PER_TRIPLET
G = 0.05 / M_TESTS         # sealed Bonferroni gate
DESIGN_N = 169             # design draws per stream (exp032 label)
DESIGN_TRIPLET_N = 3 * DESIGN_N


def probA_trip_set(n):
    """Probe A null gate-hit set at (n, w_tri): H = {h : min tail
    <= g}.  Gate defined once at the sealed null."""
    p_plus, p_minus = binom_tails(n, W_TRI)
    return sorted(h for h in range(n + 1)
                  if min(p_plus[h], p_minus[h]) <= G)


def pi_at(n, p, trip):
    """P(Bin(n,p) lands in the null-defined gate-hit set)."""
    pmf = binom_pmf_list(n, p)
    return sum(pmf[h] for h in trip)


def _pair_null_trip_prob(n_i, n_j, memo):
    """Exact P(Fisher p <= g) under the sealed null w_tri for a
    pair with margins (n_i, n_j): sum over (h_i,h_j) cells of the
    product pmf x indicator.  Memoized on the margins — at most
    C(24,2) distinct pairs exist.  Fisher validity gives <= g;
    this computes the exact expectation contribution.  Linearity
    of expectation closes the triplet family sum WITHOUT any
    independence assumption across the 3 in-triplet tests."""
    key = (n_i, n_j)
    if key not in memo:
        cells_i = _sparse_pmf(n_i, W_TRI)
        cells_j = _sparse_pmf(n_j, W_TRI)
        tot = 0.0
        for hi, pi_ in cells_i:
            for hj, pj in cells_j:
                if fisher_two_sided(n_i, n_j, hi, hj) <= G:
                    tot += pi_ * pj
        memo[key] = tot
    return memo[key]


def _pair_alt_trip_prob(n_i, p_i, n_j, p_j):
    """Power of one Fisher contrast under alternative hazards."""
    cells_i = _sparse_pmf(n_i, p_i)
    cells_j = _sparse_pmf(n_j, p_j)
    tot = 0.0
    for hi, pi_ in cells_i:
        for hj, pj in cells_j:
            if fisher_two_sided(n_i, n_j, hi, hj) <= G:
                tot += pi_ * pj
    return tot


def main(dest=None):
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

    # ---- Q1 family size / feasibility ---------------------------
    # Construction guarantee: 8096 exact-valid tests, Bonferroni
    # gate -> family size <= 0.05 by union bound, no independence.
    # Exact expected null trips: probe A per triplet (integrate
    # over h at the null with the triplet's real n — ancillary,
    # sealed at evaluation time), probe B as the linearity sum
    # over the 6072 pair-instances (memoized exact per-pair
    # probabilities).  NO real h enters anything below.
    q1_prose_sealed = (
        "at gate 6.17e-6 the family is calibrated by construction "
        "(union bound); the informative question is whether ANY "
        "design-hot triplet retains non-trivial power at this "
        "gate — answered in Q2, before any real statistic")
    expA = 0.0
    expB = 0.0
    memo = {}
    trip_cache = {}
    for a in range(len(sids)):
        for b in range(a + 1, len(sids)):
            for c in range(b + 1, len(sids)):
                si, sj, sk = sids[a], sids[b], sids[c]
                n_tri = (streams[si]["draws"] + streams[sj]["draws"]
                         + streams[sk]["draws"])
                if n_tri not in trip_cache:
                    trip_cache[n_tri] = probA_trip_set(n_tri)
                expA += pi_at(n_tri, W_TRI, trip_cache[n_tri])
                for x, y in ((si, sj), (si, sk), (sj, sk)):
                    expB += _pair_null_trip_prob(
                        streams[x]["draws"], streams[y]["draws"], memo)

    # ---- Q2 design power (labeled) -------------------------------
    trip_design = probA_trip_set(DESIGN_TRIPLET_N)
    altA = {}
    for mult in (10.0, 3.0, 1.0, 0.1):
        altA[f"{mult:g}x"] = pi_at(DESIGN_TRIPLET_N, mult * W_TRI,
                                   trip_design)
    # probe A triplet classes at design n: HHH, HHF, HFF, FFF
    p_hhh = altA["10x"]
    p_hhf = pi_at(DESIGN_TRIPLET_N, (10.0 + 10.0 + 0.1) / 3 * W_TRI,
                  trip_design)
    p_hff = pi_at(DESIGN_TRIPLET_N, (10.0 + 0.1 + 0.1) / 3 * W_TRI,
                  trip_design)
    p_fff = altA["0.1x"]
    # design composition: 3 hot, 5 frozen (exp028) over C(8,3)=56
    # triplets: class counts = C(3,3)=1 HHH, C(3,2)*C(5,1)=15 HHF,
    # C(3,1)*C(5,2)=30 HFF, C(5,3)=10 FFF
    eA_design = 1 * p_hhh + 15 * p_hhf + 30 * p_hff + 10 * p_fff
    # probe B: hot-frozen pair contrast at the sealed gate
    pB_hf = _pair_alt_trip_prob(DESIGN_N, 10 * W_TRI,
                                DESIGN_N, 0.1 * W_TRI)
    pB_hh = _pair_alt_trip_prob(DESIGN_N, 10 * W_TRI,
                                DESIGN_N, 10 * W_TRI)
    pB_ff = _pair_alt_trip_prob(DESIGN_N, 0.1 * W_TRI,
                                DESIGN_N, 0.1 * W_TRI)
    # probe B expected trips over the 56 design triplets: each
    # triplet carries 3 pair tests; class pair-composition:
    #   HHH: 3 HH ; HHF: 1 HH + 2 HF ; HFF: 2 HF + 1 FF
    #   FFF: 3 FF
    eB_design = (1 * 3 * pB_hh + 15 * (pB_hh + 2 * pB_hf)
                 + 30 * (2 * pB_hf + pB_ff) + 10 * 3 * pB_ff)
    ub_power = eA_design + eB_design

    # ---- Q3 frozen visibility -------------------------------------
    n_zero = math.ceil(math.log(G) / math.log(1 - W_TRI))
    q3_prose_sealed = ("if n_zero >> 507 the frozen arm stays "
                       "triplet-invisible under probe A and probe "
                       "B's contrast is the only frozen-side "
                       "instrument — at gate 6.17e-6 probe B is "
                       "Fisher-silent at census-n margins (exp035 "
                       "measured min Fisher p 0.0585 vs a LOOSER "
                       "9.06e-5 gate, 646x above), so a frozen "
                       "read at triplet resolution has NO "
                       "instrument at all")
    q3_verdict = ("FROZEN-TRIPLET-BLIND under probe A at design n"
                  if n_zero > 2 * DESIGN_TRIPLET_N else
                  "FROZEN-TRIPLET-VISIBLE under probe A at design n")

    out = {
        "experiment": (
            "exp036 triplet-stream joint gates PRE-REGISTRATION "
            "(escalation lane named by the tension doc: triplet-"
            "gate seal needs fresh pre-registration).  Sealed "
            "BEFORE any triplet statistic exists; evaluation is "
            "a separate experiment, run only if Casey commissions "
            "it after reading the tension face."),
        "preregistration": (
            "sealed in this script; exhaustive C(24,3)=2024 "
            "triplet enumeration (no cherry-picking); 4 tests per "
            "triplet (probe A joint-count + 3 pairwise Fisher "
            "contrasts); gate g=0.05/8096; null hazard "
            "w_tri=15/3078 fixed; closure: triplets are the LAST "
            "analytic rung of the rate lane over these 24 "
            "streams — beyond triplets = new telemetry under a "
            "fresh pre-registration, not more arithmetic on the "
            "same 15 hits; no real-data triplet statistic is "
            "computed here — Q4 deliberately absent"),
        "sealed_design": {
            "universe": ("24 census streams (16 corpus k0-k15 + "
                         "block E k16-k23), no new runs"),
            "null_hazard": ("w_tri = 15/3078 full pooled MLE at "
                            "seal time, fixed, never re-estimated; "
                            "the 15 hits set it (conditioning-on-"
                            "total caveat, labeled context); "
                            "exp032/033's w_hat=10/2009 and "
                            "exp034/035's w_pair=15/3078 seals "
                            "stand for their own lanes"),
            "family": ("m = 2024 triplets x 4 tests = 8096; "
                       "Bonferroni gate g = 0.05/8096"),
            "probe_A": ("joint-count: n=n_i+n_j+n_k, h=h_i+h_j+h_k; "
                        "trip iff min(P(Bin(n,w_tri)>=h), "
                        "P(Bin(n,w_tri)<=h)) <= g; asks does the "
                        "TRIPLET deviate from the pooled hazard"),
            "probe_B": ("the three two-sided Fisher exact tests on "
                        "the triplet's member pairs; trip iff any "
                        "p <= g; asks is there ANY internal "
                        "heterogeneity; each Fisher test is exact-"
                        "valid so the union bound closes the "
                        "8096-test family at exactly 0.05 with NO "
                        "independence assumption (in-triplet test "
                        "dependence is real and irrelevant to the "
                        "bound)"),
            "decision_rules": ("FAMILY-TRIPLET-REFUTED iff any "
                               "(probe,triplet) trips; TRIPLET-"
                               "DEVIANT (A) named with tail "
                               "direction; TRIPLET-HETEROGENEOUS "
                               "(B) named triplet + named pair"),
            "closure": ("triplets are the LAST analytic rung of "
                        "the rate lane over these 24 streams; no "
                        "quadruples, no re-tripletion, no probe "
                        "drops; beyond triplets = new telemetry "
                        "(fresh census block under its own pre-"
                        "registration)")},
        "guards": guards,
        "guard_ok": ok,
        "q1_family_size": {
            "sealed_prose_first": q1_prose_sealed,
            "gate": G,
            "m_tests": M_TESTS,
            "construction_guarantee": ("family size <= 0.05 exact "
                                       "by union bound over 8096 "
                                       "exact-valid tests"),
            "linearity_note": ("probe-B expectation is a linearity "
                               "sum over the 6072 pair-instances; "
                               "no independence assumption needed "
                               "across the dependent in-triplet "
                               "Fisher tests"),
            "expected_null_trips_probe_A": expA,
            "expected_null_trips_probe_B": expB,
            "expected_null_trips_total": expA + expB},
        "q2_design_power_labeled": {
            "note": ("exp028 composition on a design block: 3 hot "
                     "@10x, 5 frozen @0.1x, design n=169/stream, "
                     "triplet n=507; exact arithmetic; existing "
                     "streams excluded (observed facts, not "
                     "random future data)"),
            "probe_A_triplet_n": DESIGN_TRIPLET_N,
            "probe_A_per_unit_pi": altA,
            "probe_A_triplet_classes_HHH_HHF_HFF_FFF":
                [p_hhh, p_hhf, p_hff, p_fff],
            "probe_A_expected_trips_design_block": eA_design,
            "probe_B_contrast_HH_HF_FF": [pB_hh, pB_hf, pB_ff],
            "probe_B_expected_trips_design_block": eB_design,
            "union_bound_power_ceiling_design_block": ub_power},
        "q3_frozen_visibility": {
            "sealed_prose": q3_prose_sealed,
            "gate": G,
            "n_zero_for_zero_hit_triplet": n_zero,
            "design_triplet_n": DESIGN_TRIPLET_N,
            "verdict": q3_verdict},
        "synthesis": (
            f"Triplet escalation sealed before any triplet "
            f"statistic exists.  Family of 8096 exact-valid tests "
            f"is CALIBRATED-BY-CONSTRUCTION (union bound <= 0.05); "
            f"exact expected null trips: probe A {expA:.4f}, "
            f"probe B {expB:.6f} (total {expA + expB:.4f} of "
            f"8096 tests).  Design power at triplet n=507 under "
            f"the exp028 3-hot/5-frozen composition: probe A "
            f"trips for HHH w.p. {p_hhh:.4f}, HHF {p_hhf:.4f}, "
            f"HFF {p_hff:.4f}, FFF {p_fff:.4f}; probe B HF "
            f"contrast {pB_hf:.6f} — the hot side RETAINS "
            f"power at resolution 3 (HHH {p_hhh:.3f}) but the "
            f"frozen side is fully blind: n_zero={n_zero} vs "
            f"design triplet n={DESIGN_TRIPLET_N} -> "
            f"{q3_verdict}, and probe B is structurally silent "
            f"at census-n margins (exp035 measured min Fisher "
            f"p 0.0585 against a LOOSER 9.06e-5 gate).  So the "
            f"seal's arithmetic reads: a triplet evaluation is "
            f"worth running ONLY as a hot-side check under "
            f"fresh design assumptions — as a read on the "
            f"OBSERVED 15 hits it cannot decompose anything "
            f"the pair lane did not, and it closes the frozen "
            f"side completely.  Rate lane CLOSES analytically "
            f"at triplets: hot-side escalation needs new "
            f"telemetry (fresh census block under its own pre-"
            f"registration), frozen-side escalation has no "
            f"instrument at any resolution."),
        "honesty": ("Pure exact arithmetic (Binomial direct "
                    "summation; log-space hypergeometric Fisher), "
                    "no rng / no MC / no normal approximation.  "
                    "Guards re-derive all 24 streams from raw "
                    "telemetry and abort on drift.  No real-data "
                    "triplet statistic is computed anywhere in "
                    "this script — not even a peek at which "
                    "triplets would trip.  The 15 hits set "
                    "w_tri; every triplet read in any evaluation "
                    "is conditioning-on-total context.  Probe-B "
                    "expectation by linearity, no independence."),
    }

    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()
                         ).hexdigest()
    out["rerun_digest"] = digest
    dest_path = Path(dest) if dest is not None else HERE / "exp036.results.json"
    dest_path.write_text(
        json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "guard_ok": ok,
        "q1_expected_null_trips_A": round(expA, 4),
        "q1_expected_null_trips_B": round(expB, 4),
        "q2_piA_HHH": round(p_hhh, 4),
        "q2_piA_HHF": round(p_hhf, 4),
        "q2_piA_HFF": round(p_hff, 4),
        "q2_piB_HF_contrast": round(pB_hf, 6),
        "q2_ub_power_56_triplets": round(ub_power, 4),
        "q3_n_zero_triplet": n_zero,
        "q3_verdict": q3_verdict,
        "digest": digest}, indent=1))


if __name__ == "__main__":
    main()
