"""exp033 — the RUN of the sealed block-E census batch (pre-
registration exp032, sealed 2026-09-30 BEFORE this batch ran).

Doctrine chain under test:
  exp029  pooled exact conditional deviance p=0.003256 REFUTES
          one-shared-desert-hazard (sealed RULE DECISION), but NO
          individual stream has been named hot/frozen by a
          pre-registered gate; Bonferroni diagnostic-only.
  exp031a non-crosser ceiling INCOMPATIBLE with pooled hazard.
  exp031b exogenous allocation side CLOSED (all probes silent).
  exp031c endogenous side CLOSED (exp027 set surprise was
          truncation-dominated; exposure rank ORDINARY 0.219).
  exp032  census-n PRE-REGISTRATION of the per-stream rate lane:
          block E sealed (salts k16-k23, seeds 31016-31023,
          protocol byte-identical to exp024; ONE committed batch,
          NO PEEKING — all 8 telemetry files sealed to disk
          before any statistic), family CLOSES at n=24,
          escalation requires a fresh pre-registration; sealed
          null hazard w_hat = 10/2009 fixed; sealed per-stream
          test = two-sided exact Binomial, Bonferroni gate
          g = 0.05/24; FAMILY REFUTED iff any stream trips;
          HOT iff p_plus <= g; FROZEN iff p_minus <= g.

THIS experiment:
  1. Guard: instrumented census loop reproduces exp001
     byte-identical (census ACTIVE), as in exp024/exp029.
  2. Census the pre-committed block E: salts k16-k23, seeds
     31016-31023, exp021 Q1 tiesample-arm semantics, POP 16,
     GENS 12, BUDGET 6 — byte-identical protocol to exp024.
     Determinism verified: the batch is re-run in-memory and
     asserted byte-equal to the written telemetry BEFORE any
     statistic is computed.  NO PEEKING honored structurally:
     all 8 telemetry files sealed to disk first.
  3. Guard: the 16 corpus streams re-derived from raw telemetry
     and checked against exp032's sealed table (totals 2009/10;
     per-stream draws/hits/birth_cum) — abort on drift.
  4. SEALED DECISION applied verbatim, per stream, at the SEALED
     null hazard w_hat = 10/2009 and gate g = 0.05/24 over the
     family of 24:
        p_plus(s)  = P(Bin(n_s, w_hat) >= h_s)
        p_minus(s) = P(Bin(n_s, w_hat) <= h_s)
     FAMILY: all-share-w_hat REFUTED iff any stream trips
     min(p_plus, p_minus) <= g.
     PER-STREAM-HOT: p_plus <= g (named).  PER-STREAM-FROZEN:
     p_minus <= g (named).
  5. Honesty: the 16 existing hits set w_hat, so the existing
     streams' tails shrink toward the middle (conditioning-on-
     total); their reads are labeled POST-HOC context.  The 8
     block-E streams contributed nothing to w_hat — their gate
     reads are the design's clean operating point (exp032 Q2:
     10x-hot stream trips w.p. 0.9268 at design n=169; frozen
     arm per-stream-invisible: n_zero = 1238 >> 169).
     After this run the family has n = 24 and the per-stream
     question CLOSES (exp032 seal): no further blocks for this
     question; escalation requires a fresh pre-registration.

Pure exact Binomial arithmetic for the gate (direct summation,
no rng / no MC / no normal approximation); the only rng in the
experiment is the sealed census protocol itself.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from exp029_adjudication_census import (
    run_tiebreak_census,
    run_guard_default,
    derive_stream,
    load_telemetry,
)

TL = Path(__file__).resolve().parent

BAR = 0.45
W_HAT = 10 / 2009          # sealed null hazard (exp032), fixed
G24 = 0.05 / 24            # sealed Bonferroni per-stream gate
ALPHA = 0.05

# --- the pre-committed block E (exp032 SEALED before any run) ---
BLOCK_E = {f"k{16 + i}": {"seed": 31016 + i} for i in range(8)}

# sealed 16-stream corpus (exp032 Q0 guards, verbatim)
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


def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def scan(rows):
    """exp027/exp032 scan semantics: desert window (until first bar
    cell), birth cum-draws, per-stream desert totals."""
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


def binom_tails(n, p):
    """Exact per-h Binomial tails: p_plus[h] = P(X >= h),
    p_minus[h] = P(X <= h), h = 0..n.  Direct summation."""
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
        p_plus.append(acc)
    p_plus.reverse()
    return p_plus, p_minus


def main():
    # ---- guard: instrumented loop reproduces exp001 ----------------
    guard = run_guard_default(7, generations=8, pop=16, shots=512,
                              train_seed=101, verify_seed=202)
    exp001 = json.loads((TL / "exp001.results.json").read_text())
    control_ok = (guard["curve"] == exp001["curve"]
                  and guard["champion"].genome
                  == exp001["champion_genome"])
    print("control reproduces exp001 (census active):", control_ok)
    if not control_ok:
        raise SystemExit("FATAL: instrumented loop diverges")

    # ---- STEP 1: census the pre-committed block E, seal telemetry --
    # NO PEEKING, structural: all 8 files on disk before any
    # statistic below executes.
    block_telemetry = {}
    for name, spec in BLOCK_E.items():
        telem = TL / f"exp033.telemetry.{name}.jsonl"
        if telem.exists():
            telem.unlink()
        run_tiebreak_census(spec["seed"], str(telem))
        block_telemetry[name] = telem
        print(f"census sealed: {name} (seed {spec['seed']})")

    # determinism: re-run the batch in-memory, assert byte-equal to
    # the sealed telemetry BEFORE any statistic is computed.
    determinism = {}
    for name, spec in BLOCK_E.items():
        rerun = run_tiebreak_census(spec["seed"], None)
        disk = load_telemetry(block_telemetry[name])
        same = (len(rerun["census"]) == len(disk)
                and all(rerun["census"][i] == disk[i]["census"]
                        and rerun["curve"][i] == disk[i]["curve"]
                        for i in range(len(disk))))
        determinism[name] = same
        if not same:
            raise SystemExit(f"FATAL: determinism drift on {name}")
    print("determinism re-run byte-equal, all 8 streams:",
          all(determinism.values()))

    # ---- STEP 2 (post-seal): corpus + block-E desert facts ---------
    corpus_streams = {}
    for fname, sid in CORPUS:
        rows = load_telemetry(TL / fname)
        corpus_streams[sid] = scan(rows)
    guards = {}
    total_draws = total_hits = 0
    for sid, (d, h, b) in SEALED.items():
        s = corpus_streams[sid]
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
        raise SystemExit("GUARD ABORT: corpus drifted from exp032 "
                         f"sealed table: {guards}")
    print("corpus re-derivation guard vs exp032 sealed 2009/10: PASS")

    block_streams = {}
    for name in BLOCK_E:
        rows = load_telemetry(block_telemetry[name])
        block_streams[name] = scan(rows)

    # ---- STEP 3: the SEALED per-stream gate over the family of 24 --
    per_stream = {}
    hot, frozen, trippers = [], [], []
    for sid in list(corpus_streams) + list(block_streams):
        s = corpus_streams.get(sid) or block_streams[sid]
        n, h = s["draws"], s["hits"]
        p_plus, p_minus = binom_tails(n, W_HAT)
        rp, rm = p_plus[h], p_minus[h]
        trips = min(rp, rm) <= G24
        cohort = ("corpus" if sid in corpus_streams else "blockE")
        per_stream[sid] = {
            "cohort": cohort, "n": n, "hits": h,
            "p_plus": rp, "p_minus": rm,
            "trips_gate_0.05_over_24": trips,
            "birth_cum": s["birth_cum"], "crossed": s["crossed"]}
        if trips:
            trippers.append(sid)
            if rp <= G24:
                hot.append(sid)
            if rm <= G24:
                frozen.append(sid)

    family_refuted = bool(trippers)
    block_tot = {"draws": sum(s["draws"] for s in block_streams.values()),
                 "hits": sum(s["hits"] for s in block_streams.values()),
                 "crossers": sum(1 for s in block_streams.values()
                                 if s["crossed"])}

    result = {
        "experiment": (
            "exp033 block-E census batch RUN + sealed per-stream "
            "gate evaluation (pre-registration exp032, sealed "
            "2026-09-30 BEFORE this batch ran)"),
        "preregistration": (
            "exp032 (sealed): block E = salts k16-k23, seeds "
            "31016-31023, protocol byte-identical to exp024; ONE "
            "committed batch, NO PEEKING (all 8 telemetry files "
            "sealed to disk before any statistic); sealed null "
            "hazard w_hat = 10/2009 fixed; per-stream two-sided "
            "exact Binomial, Bonferroni gate g = 0.05/24 over the "
            "family of 24; FAMILY REFUTED iff any stream trips; "
            "HOT p_plus <= g; FROZEN p_minus <= g; family CLOSES "
            "at n=24, escalation requires a fresh pre-registration"),
        "design": (
            "exp001 instrument guard byte-identical (census "
            "ACTIVE); exp021 Q1 tiesample semantics POP16 GENS12 "
            "BUDGET6; determinism verified by in-memory re-run "
            "before any statistic; corpus re-derived from raw "
            "telemetry and guarded vs exp032 sealed table (abort "
            "on drift)"),
        "honesty": (
            "the 16 corpus hits set w_hat, so corpus-stream tails "
            "shrink toward the middle (conditioning-on-total); "
            "their gate reads are labeled POST-HOC context.  The "
            "8 block-E streams contributed NOTHING to w_hat — "
            "their gate reads are the design's clean operating "
            "point (exp032 Q2: 10x-hot trips w.p. 0.9268 at "
            "design n=169; frozen arm per-stream-invisible, "
            "n_zero=1238 >> 169).  After this run the per-stream "
            "question CLOSES at n=24 per the exp032 seal.  Pure "
            "exact arithmetic for the gate; the only rng is the "
            "sealed census protocol itself."),
        "guards": {
            "exp001_reproduced_byte_identical": control_ok,
            "determinism_rerun_byte_equal_all_8": all(
                determinism.values()),
            "corpus_rederivation_vs_exp032_sealed": guards,
        },
        "blockE_census_facts": {
            name: {
                "seed": BLOCK_E[name]["seed"],
                "desert_draws": block_streams[name]["draws"],
                "desert_hits": block_streams[name]["hits"],
                "birth_cum": block_streams[name]["birth_cum"],
                "crossed": block_streams[name]["crossed"],
            } for name in BLOCK_E},
        "blockE_totals": block_tot,
        "family_of_24": {
            "null_hazard": W_HAT,
            "gate": G24,
            "alpha": ALPHA,
            "corpus_labeled_posthoc": True,
            "per_stream": per_stream,
            "tripping_streams": trippers,
            "named_HOT": hot,
            "named_FROZEN": frozen,
            "FAMILY_VERDICT": (
                "ALL-SHARE-W_HAT REFUTED" if family_refuted
                else "ALL-SHARE-W_HAT RETAINED"),
            "question_closed_at_n24": True,
        },
        "synthesis": (
            f"Block E executed under seal: 8 streams, "
            f"{block_tot['draws']} desert draws, {block_tot['hits']} "
            f"desert hits, {block_tot['crossers']} crossers.  "
            f"Family of 24 at gate 0.05/24 vs w_hat=10/2009: "
            f"tripping streams = {trippers if trippers else 'NONE'}"
            + (f" — named HOT {hot}, named FROZEN {frozen}.  "
               if trippers else ".  ")
            + f"FAMILY VERDICT: "
            + ("ALL-SHARE-W_HAT REFUTED — consistent with exp029's "
               "pooled deviance refutation, now with named streams "
               "under a pre-registered gate."
               if family_refuted else
               "ALL-SHARE-W_HAT RETAINED at the per-stream gate — "
               "the exp029 pooled deviance refutation (10 events) "
               "does not decompose into any individually-nameable "
               "stream at census-n; read as a small-cluster/"
               "interaction signature, per-stream resolution needs "
               "the fresh pre-registration the seal requires.")
            + "  Corpus-stream reads are post-hoc context "
              "(shrink-toward-middle).  The per-stream question "
              "CLOSES at n=24 per the exp032 seal."),
    }

    digest = hashlib.md5(json.dumps(result, sort_keys=True).encode()
                         ).hexdigest()
    result["rerun_digest"] = digest
    dest = TL / "exp033.results.json"
    dest.write_text(json.dumps(result, indent=1, sort_keys=True),
                    encoding="utf-8")
    print(json.dumps({
        "blockE_totals": block_tot,
        "tripping_streams": trippers,
        "named_HOT": hot,
        "named_FROZEN": frozen,
        "FAMILY_VERDICT": result["family_of_24"]["FAMILY_VERDICT"],
        "digest": digest}, indent=1, sort_keys=True))
    print("wrote", dest)


if __name__ == "__main__":
    main()
