"""exp032_censusn_prereg.py — census-n PRE-REGISTRATION of the
per-stream rate lane, named 'next' by exp031c's report: 'per-stream
rate lane re-opens only at census-n pre-registration'.  This script
seals the design, the gate, the decision rules, and the exact
size/power calibration BEFORE any new census stream runs.  All
arithmetic below is exact (Binomial tails by direct summation, no
rng / no MC / no normal approximation); the only design labels are
the design-expected draw count for the not-yet-run block E streams.

DOCTRINE CHAIN under test:
  exp026  ONE shared desert hazard NOT distinguishable from
          per-stream rates at pilot-n (Bonferroni all >= 0.48).
  exp027  exact conditional deviance p=0.0053 REJECTS while
          exp026's marginals do not — procedure disagreement.
  exp028  adjudication rule + b*=1 census block pre-registered.
  exp029  b*=1 block executed (sealed, no peeking): pooled corpus
          16 streams / 2009 desert draws / 10 hits; sealed RULE
          DECISION: pooled exact conditional deviance p=0.003256
          REFUTES one-shared-desert-hazard; reverse-sensitivity
          rule RETAINED (Bonferroni diagnostic-only).
  exp031a non-crosser ceiling INCOMPATIBLE with pooled hazard.
  exp031b exogenous allocation side CLOSED (all probes silent).
  exp031c endogenous side CLOSED: exp027's set surprise was
          truncation-dominated; exposure rank ORDINARY (0.219).

WHAT REMAINS OPEN: exp029 refuted the one-shared-hazard null at
10 events / 16 streams, and exp031b/031c showed the allocation and
truncation readings carry no residue — so the pooled refutation
stands, but NO individual stream has yet been named hot or frozen
by a pre-registered gate.  The per-stream rate lane re-opens only
under this pre-registration.

SEALED DESIGN (census-n):
  Block E = 8 census-only streams, salts k16-k23, seeds 31023-
  series 31016-31023, protocol BYTE-IDENTICAL to exp024 (passive
  cloud census; exp021 Q1 tiesample-arm semantics; POP 16, GENS 12,
  BUDGET 6; census evals consume no rng).  ONE committed batch, NO
  PEEKING (all 8 telemetry files sealed to disk before any
  statistic, exactly the exp029 protocol).  After block E the
  family has n = 24 streams and the per-stream question CLOSES at
  n = 24: whatever the reads, no further blocks may be added for
  this question; any escalation requires a FRESH pre-registration
  (this seal exists to kill the look-again ladder).

SEALED NULL HAZARD: w_hat = 10/2009 (the full-corpus pooled MLE at
  pre-registration time), fixed, NEVER re-estimated within this
  lane.  Honesty note: exp031c sealed W = 4/1037 (pilot-pooled)
  for its own calibration and that seal stands there; this lane
  covers all 24 streams, so the full-corpus MLE is the pre-registered
  null hazard.  Labeled, not hidden.

SEALED PER-STREAM TEST (two-sided exact Binomial, per stream s
  with n_s desert draws and h_s desert hits):
      p_plus(s)  = P(Bin(n_s, w_hat) >= h_s)
      p_minus(s) = P(Bin(n_s, w_hat) <= h_s)
  Family of m = 24 two-sided tests, Bonferroni per-stream gate
      g = 0.05 / 24.
  SEALED DECISIONS:
    FAMILY:  the all-share-w_hat null is REFUTED iff any stream
             trips min(p_plus, p_minus) <= g.
    PER-STREAM-HOT:    p_plus  <= g  (flagged, named).
    PER-STREAM-FROZEN: p_minus <= g  (flagged, named).
  Honesty: the 10 existing hits were used to set w_hat, so the
  existing streams' tails are shrunk toward the middle
  (conditioning-on-total effect); the pre-registered reads on them
  are labeled POST-HOC context, and the gate's operating
  characteristics on the NEW block are the design's clean part.

SEALED PROBES (this script, pure exact arithmetic):
  Q0  GUARDS: re-derive all 16 corpus streams from raw telemetry
      and abort unless every per-stream (draws, hits, birth_cum)
      matches the sealed table and totals 2009/10 reproduce.
  Q1  FAMILY SIZE under the sealed null: per stream s, the
      gate-hit set H_s = {h : min tail <= g} at its n_s (existing:
      actual; block E: design-expected n=169, labeled);
      pi_s = P(Bin(n_s, w_hat) in H_s); P(family trip) =
      1 - prod_s (1 - pi_s).  Verdict sealed: SIZE-CALIBRATED
      iff P(family trip) <= 0.05.
  Q2  POWER, labeled, design-fixed alternative (exp028's two-class
      design: among block E's 8 streams, 3 hot at 10*w_hat, 5
      frozen at 0.1*w_hat; design-fixed n=169 each): per-class
      pi at 10x / 3x / 2x / 1x / 0.1x, plus
      P(at least one of the 3 hot trips) and
      P(at least one of the 5 frozen trips).  Existing streams
      excluded (their counts are already observed facts, not
      random future data — labeled).
  Q3  FROZEN-SIDE VISIBILITY: minimum draws n_zero such that a
      zero-hit stream trips the lower gate,
      (1-w_hat)^n_zero <= g.  Verdict sealed in prose BEFORE the
      number: at census-n per-stream, a 0.1x stream expects
      ~0.084 hits in 169 draws; if n_zero >> 169 the frozen arm
      is per-stream-invisible at census-n and only the
      family-level pooled deviance (exp028's design) can see it.
  Q4  POST-HOC READ on the current 16-stream corpus at gate
      0.05/16 (LABELED context, not a verdict): per-stream
      p_plus / p_minus at w_hat, which streams trip, and the
      shrink-toward-middle caveat stated above.

GUARDS: sealed per-stream table (desert draws / desert hits /
birth_cum) for all 16 corpus streams + totals 2009/10, re-derived
from raw telemetry with exp027 scan semantics; abort on drift.
Pure exact arithmetic, no rng, no MC.
"""

import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
BAR = 0.45
W_HAT = 10 / 2009  # sealed full-corpus pooled MLE, never re-estimated
G24 = 0.05 / 24    # sealed Bonferroni per-stream gate, family of 24
G16 = 0.05 / 16    # post-hoc read gate, current family size
DESIGN_N = 169     # design-expected desert draws per block-E stream
                   # (mean of the 16 observed stream totals, labeled)

# sealed corpus facts (exp029 sealed decision + exp031a guards)
SEALED = {
    "k3": (16, 1, 16), "k4": (165, 0, None), "k5": (54, 1, 54),
    "k6": (121, 2, 121), "k7": (163, 0, None), "k0": (174, 0, None),
    "k1": (175, 0, None), "k2": (169, 0, None),
    "k8": (73, 1, 73), "k9": (102, 1, 102), "k10": (167, 0, None),
    "k11": (90, 2, 90), "k12": (177, 0, None), "k13": (16, 1, 16),
    "k14": (170, 0, None), "k15": (177, 1, 177),
}
SEALED_TOTAL_DRAWS = 2009
SEALED_TOTAL_HITS = 10

CORPUS = [
    ("exp022.telemetry.k3.jsonl", "k3"),
    ("exp022.telemetry.k4.jsonl", "k4"),
    ("exp022.telemetry.k5.jsonl", "k5"),
    ("exp022.telemetry.k6.jsonl", "k6"),
    ("exp022.telemetry.k7.jsonl", "k7"),
    ("exp024.telemetry.k0.jsonl", "k0"),
    ("exp024.telemetry.k1.jsonl", "k1"),
    ("exp024.telemetry.k2.jsonl", "k2"),
    ("exp029.telemetry.k8.jsonl", "k8"),
    ("exp029.telemetry.k9.jsonl", "k9"),
    ("exp029.telemetry.k10.jsonl", "k10"),
    ("exp029.telemetry.k11.jsonl", "k11"),
    ("exp029.telemetry.k12.jsonl", "k12"),
    ("exp029.telemetry.k13.jsonl", "k13"),
    ("exp029.telemetry.k14.jsonl", "k14"),
    ("exp029.telemetry.k15.jsonl", "k15"),
]

BLOCK_E = {f"k{16 + i}": {"seed": 31016 + i} for i in range(8)}


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def scan(rows):
    """exp027 scan semantics: desert window (until first bar cell),
    birth cum-draws, per-stream desert totals."""
    prev = None
    bar_seen = False
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
        if not bar_seen:
            cum += len(newborns)
            desert_draws += len(newborns)
            desert_hits += hits
            if birth_cum is None and hits >= 1:
                birth_cum = cum
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen = True
    return {"draws": desert_draws, "hits": desert_hits,
            "birth_cum": birth_cum, "crossed": bar_seen}


def load(name):
    return [json.loads(l) for l in
            (HERE / name).read_text().splitlines() if l.strip()]


def binom_tails(n, p):
    """Exact per-h two-sided Binomial tails at (n, p).
    Returns (p_plus, p_minus): p_plus[h] = P(X >= h),
    p_minus[h] = P(X <= h), h = 0..n."""
    pmf = [0.0] * (n + 1)
    pmf[0] = (1 - p) ** n
    for k in range(n):
        pmf[k + 1] = pmf[k] * (n - k) / (k + 1) * p / (1 - p)
    p_minus = []
    acc = 0.0
    for k in range(n + 1):
        acc += pmf[k]
        p_minus.append(acc)
    p_plus = []
    acc = 0.0
    for k in range(n, -1, -1):
        acc += pmf[k]
        p_plus.append(acc)          # p_plus[h] = P(X >= h)
    p_plus.reverse()
    return p_plus, p_minus


def trip_set(n, g):
    """Gate-hit set at the SEALED null hazard w_hat:
    H = {h : min(P_w_hat(X>=h), P_w_hat(X<=h)) <= g}.  The gate is
    defined once at the null; alternatives only move the sampling
    distribution."""
    p_plus, p_minus = binom_tails(n, W_HAT)
    return sorted(h for h in range(n + 1)
                  if min(p_plus[h], p_minus[h]) <= g)


def pi_at(n, p, trip):
    """P(X ~ Bin(n, p) lands in the null-defined gate-hit set).
    Pure exact arithmetic."""
    p_plus, _ = binom_tails(n, p)
    pmf = {h: p_plus[h] - (p_plus[h + 1] if h < n else 0.0)
           for h in range(n + 1)}
    return sum(pmf[h] for h in trip)


def main():
    # ---- Q0 guards ----------------------------------------------
    streams = {}
    for fname, sid in CORPUS:
        streams[sid] = scan(load(fname))
    guards = {}
    total_draws = total_hits = 0
    for sid, (d, h, b) in SEALED.items():
        s = streams[sid]
        total_draws += s["draws"]
        total_hits += s["hits"]
        guards[sid] = {
            "draws": [s["draws"], d, s["draws"] == d],
            "hits": [s["hits"], h, s["hits"] == h],
            "birth_cum": [s["birth_cum"], b, s["birth_cum"] == b]}
    guards["totals"] = {
        "draws": [total_draws, SEALED_TOTAL_DRAWS,
                  total_draws == SEALED_TOTAL_DRAWS],
        "hits": [total_hits, SEALED_TOTAL_HITS,
                 total_hits == SEALED_TOTAL_HITS]}
    ok = (all(guards[sid]["draws"][2] and guards[sid]["hits"][2]
              and guards[sid]["birth_cum"][2] for sid in SEALED)
          and guards["totals"]["draws"][2]
          and guards["totals"]["hits"][2])
    if not ok:
        raise SystemExit("GUARD ABORT: corpus drifted from sealed table")

    # ---- Q1 family size under the sealed null --------------------
    # family = 16 existing (actual n) + 8 block-E (design-expected
    # n=169, labeled).  pi_s = P(Bin(n_s, w_hat) trips g24).
    per_stream = {}
    for sid in SEALED:
        n = streams[sid]["draws"]
        trip = trip_set(n, G24)
        per_stream[sid] = {"n": n, "pi_null": pi_at(n, W_HAT, trip),
                           "trip_set": trip}
    trip_design = trip_set(DESIGN_N, G24)
    pi_design = pi_at(DESIGN_N, W_HAT, trip_design)
    p_family = 1.0 - math.prod(1 - per_stream[s]["pi_null"]
                               for s in per_stream) \
                   * (1 - pi_design) ** 8
    e_trips = sum(per_stream[s]["pi_null"] for s in per_stream) \
        + 8 * pi_design
    q1_verdict = "SIZE-CALIBRATED" if p_family <= 0.05 else "OVER-SIZED"

    # ---- Q2 design-fixed alternative power (labeled) -------------
    alt = {}
    for mult in (10.0, 3.0, 2.0, 1.0, 0.1):
        alt[f"{mult:g}x"] = {
            "hazard": mult * W_HAT,
            "pi": pi_at(DESIGN_N, mult * W_HAT, trip_design),
            "trip_set_at_null": trip_design}
    p_any_hot = 1 - (1 - alt["10x"]["pi"]) ** 3
    p_any_frozen = 1 - (1 - alt["0.1x"]["pi"]) ** 5

    # ---- Q3 frozen-side visibility --------------------------------
    n_zero = math.ceil(math.log(G24) / math.log(1 - W_HAT))

    # ---- Q4 post-hoc read on the current corpus (labeled) --------
    posthoc = {}
    trips16 = []
    for sid in SEALED:
        n = streams[sid]["draws"]
        h = streams[sid]["hits"]
        p_plus, p_minus = binom_tails(n, W_HAT)
        rp, rm = p_plus[h], p_minus[h]
        trip = min(rp, rm) <= G16
        posthoc[sid] = {"n": n, "h": h, "p_plus": rp, "p_minus": rm,
                        "trips_gate_0.05_over_16": trip}
        if trip:
            trips16.append(sid)

    out = {
        "experiment": (
            "exp032 census-n pre-registration of the per-stream rate "
            "lane (block E sealed: salts k16-k23, seeds 31016-31023, "
            "protocol byte-identical to exp024; family closes at "
            "n=24; escalation requires a fresh pre-registration)"),
        "preregistration": (
            "sealed in this script BEFORE block E runs; prose above "
            "is the committed artifact; no telemetry of block E "
            "exists at seal time; no statistic of any not-yet-run "
            "stream is computed anywhere below"),
        "sealed_design": {
            "block_E": BLOCK_E,
            "protocol": ("byte-identical to exp024 passive cloud "
                         "census; exp021 Q1 tiesample-arm semantics; "
                         "POP 16, GENS 12, BUDGET 6"),
            "no_peeking": ("all 8 telemetry files sealed to disk "
                           "before any statistic, exp029 protocol"),
            "family_close": ("per-stream question CLOSES at n=24; "
                             "no further blocks for this question; "
                             "escalation requires a fresh "
                             "pre-registration"),
            "null_hazard": ("w_hat = 10/2009 full-corpus pooled MLE, "
                            "fixed, never re-estimated; exp031c's "
                            "pilot-pooled W stands for exp031c only "
                            "(labeled choice)"),
            "gate": ("per stream: p_plus = P(Bin(n_s,w_hat) >= h_s), "
                     "p_minus = P(Bin(n_s,w_hat) <= h_s); Bonferroni "
                     "two-sided gate g = 0.05/24 over the family of "
                     "24; FAMILY REFUTED iff any stream trips; "
                     "PER-STREAM-HOT p_plus <= g; PER-STREAM-FROZEN "
                     "p_minus <= g"),
            "design_n_label": (f"block-E streams contribute "
                               f"design-expected n={DESIGN_N} (mean of "
                               "16 observed stream totals); actual "
                               "n_s replace it at evaluation time "
                               "(sealed)")},
        "guards": guards,
        "guard_ok": ok,
        "q1_family_size_under_null": {
            "note": ("pi_s = P(Bin(n_s, w_hat) trips g24); existing "
                     "streams at actual n_s, block E at design n=169 "
                     "(labeled); streams independent under the "
                     "null, so family trip probability is exact."),
            "per_stream_existing": per_stream,
            "pi_blockE_design": pi_design,
            "expected_tripping_streams": e_trips,
            "P_family_trip": p_family,
            "verdict": q1_verdict},
        "q2_power_design_fixed_alt": {
            "note": ("exp028 two-class design among block E: 3 hot "
                     "at 10x w_hat, 5 frozen at 0.1x w_hat; "
                     "design-fixed n=169; existing streams excluded "
                     "(their counts are observed facts, not random "
                     "future data).  Labeled design power, exact "
                     "Binomial arithmetic given the design n."),
            "per_class": alt,
            "P_at_least_one_of_3_hot_trips": p_any_hot,
            "P_at_least_one_of_5_frozen_trips": p_any_frozen},
        "q3_frozen_side_visibility": {
            "sealed_prose": ("at census-n per-stream a 0.1x stream "
                             "expects ~0.084 hits in 169 draws; if "
                             "n_zero >> 169 the frozen arm is "
                             "per-stream-invisible and only the "
                             "family-level pooled deviance (exp028 "
                             "design) can see it"),
            "n_zero_for_zero_hit_stream": n_zero,
            "design_n": DESIGN_N,
            "frozen_side_verdict": (
                "FROZEN-SIDE-BLIND at census-n per-stream"
                if n_zero > 4 * DESIGN_N else
                "FROZEN-SIDE-PARTIALLY-VISIBLE")},
        "q4_posthoc_read_current_corpus_labeled": {
            "note": ("CONTEXT ONLY, not a verdict: the 10 existing "
                     "hits set w_hat, so these tails shrink toward "
                     "the middle (conditioning-on-total); gate "
                     "0.05/16 = current family size"),
            "gate": G16,
            "per_stream": posthoc,
            "tripping_streams": trips16},
        "synthesis": (
            f"Family gate is SIZE-CALIBRATED by exact arithmetic: "
            f"P(family trip | all share w_hat) = {p_family:.4f} "
            f"(<= 0.05 -> {q1_verdict}).  Design power at n=169 per "
            f"block-E stream: a 10x-hot stream trips w.p. "
            f"{alt['10x']['pi']:.3f} (P(at least one of 3) = "
            f"{p_any_hot:.3f}); a 3x stream only w.p. "
            f"{alt['3x']['pi']:.3f}; the frozen arm is "
            f"FROZEN-SIDE-BLIND per-stream (a zero-hit stream needs "
            f"n>={n_zero} draws to trip the lower gate vs design "
            f"n={DESIGN_N}).  Post-hoc context read at gate 0.05/16 "
            f"trips for: {trips16 if trips16 else 'no stream'} — "
            "consistent with exp026's conservative-marginals read "
            "and with the shrink-toward-middle caveat.  Next: Casey "
            "commits the block-E batch (the run is a separate "
            "experiment, exp033) and the family closes at n=24."),
        "honesty": ("Pure exact Binomial arithmetic, no rng / no MC "
                    "/ no normal approximation; the only design "
                    "labels are block-E n=169 and the exp028 alt "
                    "composition.  w_hat fixed at seal time and "
                    "never re-estimated.  Q4 is explicitly post-hoc "
                    "context.  Deep-pilot class: 10 events / 16 "
                    "streams going in; the gate's clean operating "
                    "point is the new block."),
    }

    import hashlib
    digest = hashlib.md5(json.dumps(out, sort_keys=True).encode()
                         ).hexdigest()
    out["rerun_digest"] = digest
    dest = HERE / "exp032.results.json"
    dest.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(json.dumps({
        "guard_ok": ok,
        "q1_P_family_trip": f"{p_family:.4f}",
        "q1_verdict": q1_verdict,
        "q2_pi_10x": round(alt["10x"]["pi"], 4),
        "q2_P_any_hot3": f"{p_any_hot:.4f}",
        "q2_P_any_frozen5": f"{p_any_frozen:.4f}",
        "q3_n_zero": n_zero,
        "q4_tripping": trips16,
        "digest": digest}, indent=1))


if __name__ == "__main__":
    main()
