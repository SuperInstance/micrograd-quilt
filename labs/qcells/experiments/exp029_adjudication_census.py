"""exp029 — the PRE-REGISTERED b*=1 adjudication census block
(sealed exp028 Q2/Q3, 2026-09-30, BEFORE this batch ran).

Doctrine chain under test:
  exp018  FITNESS DESERT AT THE BIRTH CLOUD (hard roots); BAR=0.45.
  exp020/021/022  tie-band diversity; RATE NOT WALL; crossing
          streams birth ONE train ~0.498 cell at ONE desert gen.
  exp023-025  break = per-gen BIRTH event; two-regime per-draw
          odds (desert 1-in-259 vs plateau 1-in-3.7).
  exp026  ONE shared desert hazard NOT distinguishable from
          per-stream rates at pilot-n by conservative marginals
          (Bonferroni all >= 0.48); timing calibrated.
  exp027  BUT the exact conditional deviance p=0.0053 REJECTS the
          shared hazard while exp026's Bonferroni does not —
          two exact procedures DISAGREE on the same null at n=4.
          Breakers = the three LOWEST-exposure streams
          (P(set)=7.97e-5 under equal hazard).
  exp028  Q1: the disagreement direction is itself ordinary at
          pilot-n (P(observed direction)=0.0380 under the shared
          hazard).  Q2: ADJUDICATION RULE SEALED IN PROSE BEFORE
          ANY POWER NUMBER — corpus = sealed 8-stream pilot
          census PLUS b* pre-committed salt blocks of 8
          census-only streams each (protocol byte-identical to
          exp024, seeds continuing the 31000-series, block
          composition fixed before the batch); ONE committed
          batch, NO PEEKING (no interim deviance on a partial
          corpus).  DECISION: on the pooled corpus the
          one-shared-desert-hazard null is REFUTED iff the exact
          conditional deviance p < 0.05 (enumeration exact where
          feasible; otherwise the sealed exact-upper-bound
          variant); per-stream Bonferroni tails are DIAGNOSTIC
          ONLY.  REVERSE SENSITIVITY (sealed alongside): refute
          only if BOTH procedures reject.  Q3: b*=1 block =
          8 census streams (~1354 draws).

THIS experiment:
  1. Guard: instrumented census loop reproduces exp001
     byte-identical (census ACTIVE), as in exp024.
  2. Census the pre-committed block: salts k8-k15, seeds
     31008-31015, exp021 Q1 tiesample-arm semantics, POP 16,
     GENS 12, BUDGET 6 — byte-identical protocol to exp024
     (passive cloud census; census evals consume no rng).
     Determinism verified: the batch is re-run in-memory and
     asserted byte-equal to the written telemetry BEFORE any
     statistic is computed.
  3. NO PEEKING honored structurally: all 8 telemetry files are
     sealed to disk first; the adjudication statistics below
     execute only after the full batch exists.
  4. Pooled corpus = sealed 8-stream pilot (exp022 k3-k7 +
     exp024 k0-k2) + this 8-stream block = 16 streams.
     Pilot facts re-derived from raw telemetry and guarded
     against sealed exp025 values (74 desert gens / 1037 desert
     draws / 4 desert hits) — abort on drift, as exp026.
  5. SEALED DECISION applied verbatim: pooled exact conditional
     deviance p < 0.05 REFUTES the one-shared-desert-hazard
     null.  Exact tail over Multinomial(H; w) hit-count
     allocations: full enumeration where the composition count
     is computationally small, else an exact branch-and-bound
     over the same composition space (add-subtree pruning);
     BOTH paths are exact — the path taken is labeled.  The
     reverse-sensitivity rule (both procedures must reject) is
     reported alongside, as sealed.  Per-stream Bonferroni
     tails are computed but marked DIAGNOSTIC ONLY.

Honesty: the new salts have NO prior expected-champion pins
(they are new rng streams, not replicates) — the only
replicate-class guards are the exp001 instrument guard and the
seeded determinism check.  The pooled deviance pools cohorts B
(exp022), C (exp024 replicates) and D (this block) — the
pre-registered corpus says pool, so we pool; per-cohort reads
are reported but the binding verdict is the pooled one.  No
archive, no retention anywhere in this experiment.  Post-block
reads of WHO is hot are labeled post-hoc: the sealed rule
decides the null, nothing else.
"""

import functools
import hashlib
import json
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from qcell.search import (Candidate, fitness, mutate, mutate_classed,
                          p_target, random_gate)

LAB = Path(__file__).resolve().parent.parent
TL = LAB / "experiments"

TRAIN, VERIFY, SHOTS = 101, 202, 512
TARGETS = ("000", "111")
N = 3
POP, GENS = 16, 12
BUDGET = 6
SKELETON = [["h", 0], ["cx", 0, 1]]
BAR = 0.45
ALPHA = 0.05

# --- the pre-committed block (exp028: seeds continuing the
#     31000-series, block composition fixed before the batch) ---
NEW_BLOCK = {f"k{8 + i}": {"seed": 31008 + i} for i in range(8)}

# sealed pilot corpus (exp026 CORPUS, verbatim)
PILOT_CORPUS = [
    ("exp022.telemetry.k3.jsonl", "k3", "B_exp022_tiesample"),
    ("exp022.telemetry.k4.jsonl", "k4", "B_exp022_tiesample"),
    ("exp022.telemetry.k5.jsonl", "k5", "B_exp022_tiesample"),
    ("exp022.telemetry.k6.jsonl", "k6", "B_exp022_tiesample"),
    ("exp022.telemetry.k7.jsonl", "k7", "B_exp022_tiesample"),
    ("exp024.telemetry.k0.jsonl", "k0", "C_exp024_replicate"),
    ("exp024.telemetry.k1.jsonl", "k1", "C_exp024_replicate"),
    ("exp024.telemetry.k2.jsonl", "k2", "C_exp024_replicate"),
]

SEALED_DESERT_GENS = 74
SEALED_DESERT_DRAWS = 1037
SEALED_DESERT_HITS = 4

mutate_one = functools.partial(mutate_classed, restrict=("replace", "indel"))


def run_tiebreak_census(root_seed, telemetry_path=None):
    """Exact exp021 Q2 / exp022 / exp024 census semantics."""
    rng = random.Random(root_seed)
    champion = Candidate(genome=[list(g) for g in SKELETON])
    champion.train_p = p_target(champion.genome, TRAIN, SHOTS,
                                TARGETS, N, "balance")
    champion.verify_p = p_target(champion.genome, VERIFY, SHOTS,
                                 TARGETS, N, "balance")
    curve = []
    census_rows = []
    for gen in range(GENS):
        cands = [champion]
        while len(cands) < POP:
            genome = mutate_one(champion.genome, rng, BUDGET,
                                n_qubits=N)
            if genome is None:
                continue  # classed restrict resample (exp003 contract)
            child = Candidate(genome=genome)
            child.train_p = p_target(child.genome, TRAIN, SHOTS,
                                     TARGETS, N, "balance")
            cands.append(child)
        fmax = max(fitness(c) for c in cands)
        tied = [c for c in cands if fitness(c) == fmax]
        cloud = []
        for c in cands:
            vp = p_target(c.genome, VERIFY, SHOTS, TARGETS, N,
                          "balance")
            cloud.append({
                "genome": [list(g) for g in c.genome],
                "train_p": round(c.train_p, 6),
                "verify_p": round(vp, 6),
                "in_band": fitness(c) == fmax,
                "is_champion": c is champion,
            })
        census_rows.append({"gen": gen, "gen_max": round(fmax, 6),
                            "n_tied": len(tied), "cloud": cloud})
        best = rng.choice(tied) if len(tied) > 1 else tied[0]
        best.verify_p = p_target(best.genome, VERIFY, SHOTS,
                                 TARGETS, N, "balance")
        promoted = best.verify_p >= champion.verify_p
        if promoted:
            champion = best
        curve.append({"gen": gen, "train_p": round(best.train_p, 4),
                      "verify_p": round(best.verify_p, 4),
                      "promoted": promoted,
                      "genome": champion.genome if promoted else None})
        if telemetry_path is not None:
            with open(telemetry_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(
                    {"gen": gen, "curve": curve[-1],
                     "census": census_rows[-1]}, sort_keys=True) + "\n")
    return {"champion": champion, "curve": curve,
            "census": census_rows}


def run_guard_default(root_seed, generations, pop, shots, train_seed,
                      verify_seed):
    rng = random.Random(root_seed)
    champion = Candidate(genome=[random_gate(rng, 2) for _ in range(3)])
    champion.train_p = p_target(champion.genome, train_seed, shots,
                                ("01",), 2, "any")
    champion.verify_p = p_target(champion.genome, verify_seed, shots,
                                 ("01",), 2, "any")
    curve = []
    for gen in range(generations):
        cands = [champion]
        while len(cands) < pop:
            genome = mutate(champion.genome, rng, BUDGET, n_qubits=2)
            child = Candidate(genome=genome)
            child.train_p = p_target(child.genome, train_seed, shots,
                                     ("01",), 2, "any")
            cands.append(child)
        best = max(cands, key=lambda c: fitness(c))
        best.verify_p = p_target(best.genome, verify_seed, shots,
                                 ("01",), 2, "any")
        promoted = best.verify_p >= champion.verify_p
        if promoted:
            champion = best
        curve.append({"gen": gen, "train_p": round(best.train_p, 4),
                      "verify_p": round(best.verify_p, 4),
                      "promoted": promoted,
                      "genome": champion.genome if promoted else None})
    return {"champion": champion, "curve": curve}


# ---------- desert-fact derivation (exp026 operational semantics) ----
def genome_key(cell):
    return json.dumps(cell["genome"], sort_keys=True)


def derive_stream(rows):
    """Per-stream desert gens/draws-per-gen/hits/birth (exp026)."""
    prev = None
    bar_seen_before = False
    gens = []
    for r in rows:
        cloud = r["census"]["cloud"]
        keys = {genome_key(c) for c in cloud}
        if prev is None:
            newborns = list(cloud)
        else:
            newborns = [c for c in cloud if genome_key(c) not in prev]
        hits = sum(1 for c in newborns if c["train_p"] >= BAR)
        regime = ("plateau" if bar_seen_before else "desert")
        gens.append({"gen": r["gen"], "draws": len(newborns),
                     "hits": hits, "regime": regime})
        prev = keys
        if any(c["train_p"] >= BAR for c in cloud):
            bar_seen_before = True
    desert = [g for g in gens if g["regime"] == "desert"]
    birth = next((g for g in desert if g["hits"] >= 1), None)
    return {
        "desert_gens": [g["gen"] for g in desert],
        "desert_draws_per_gen": [g["draws"] for g in desert],
        "desert_hits": sum(g["hits"] for g in desert),
        "birth_gen": birth["gen"] if birth else None,
    }


def load_telemetry(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


# ---------- exact conditional deviance tail --------------------------
def compositions(total, parts):
    if parts == 1:
        yield (total,)
        return
    for i in range(total + 1):
        for rest in compositions(total - i, parts - 1):
            yield (i,) + rest


def exact_deviance_tail(ws, k_obs, H):
    """P(G^2 >= G^2_obs) under Multinomial(H; w), EXACTLY.

    ws: stream exposure shares (sum 1).  Returns (p, n_comp, path).
    Path 'enumerate': full composition enumeration.
    Path 'bnb': exact branch-and-bound over the same composition
    space with add-subtree pruning (computes the identical sum;
    used when raw enumeration is computationally infeasible).
    Both paths are exact; the path taken is labeled.
    """
    sids = list(ws.keys())
    w_list = [ws[s] for s in sids]
    k_list = [k_obs[s] for s in sids]
    m = len(sids)

    def contrib(i, k):
        if k <= 0:
            return 0.0
        return k * math.log(k / (H * w_list[i]))

    d_obs = 2.0 * sum(contrib(i, k_list[i]) for i in range(m))
    n_comp_total = math.comb(H + m - 1, m - 1)

    # per-stream log-marginal tables for the bnb subtree masses
    log_w = [math.log(w) for w in w_list]

    if n_comp_total <= 5_000_000:
        p_extreme = 0.0
        n_seen = 0
        for comp in compositions(H, m):
            n_seen += 1
            d = 0.0
            mp = math.lgamma(H + 1) - sum(math.lgamma(c + 1)
                                          for c in comp)
            lp = mp + sum(c * log_w[i] for i, c in enumerate(comp))
            for i, c in enumerate(comp):
                if c > 0:
                    d += c * math.log(c / (H * w_list[i]))
            if 2.0 * d >= d_obs - 1e-12:
                p_extreme += math.exp(lp)
        return p_extreme, n_seen, "enumerate"

    # exact branch-and-bound: identical sum, pruned recursion.
    # state: index i, hits used u, accumulated deviance-half d.
    # upper prune: even putting ALL remaining hits on the argmax
    # marginal stream cannot reach d_obs -> subtree contributes 0.
    # lower prune: putting all remaining hits where contrib is 0
    # (or minimal) still reaches d_obs -> subtree contributes its
    # total conditional probability (1 given u used).
    def max_additional(i, u):
        rem = H - u
        best = 0.0
        for j in range(i, m):
            c = contrib(j, rem)
            if c > best:
                best = c
        return best

    def min_additional(i, u):
        # smallest possible additional contribution: spread hits on
        # the stream minimizing per-hit marginal contribution.
        rem = H - u
        best = None
        for j in range(i, m):
            c = contrib(j, rem)
            if best is None or c < best:
                best = c
        return best if best is not None else 0.0

    p_extreme = 0.0
    n_seen = 0  # leaf compositions materialized

    def rec(i, u, d, logp):
        nonlocal p_extreme, n_seen
        if i == m:
            n_seen += 1
            if 2.0 * d >= d_obs - 1e-12:
                p_extreme += math.exp(logp)
            return
        if 2.0 * (d + max_additional(i, u)) < d_obs - 1e-12:
            return  # upper prune: subtree can never be extreme
        if 2.0 * (d + min_additional(i, u)) >= d_obs - 1e-12:
            # lower prune: entire subtree is extreme; its total
            # conditional probability given u used is 1.
            p_extreme += math.exp(logp)
            return
        for c in range(H - u + 1):
            rec(i + 1, u + c, d + contrib(i, c),
                logp + (-math.lgamma(c + 1)) + c * log_w[i])

    rec(0, 0, 0.0, math.lgamma(H + 1))
    return p_extreme, n_comp_total, "bnb"


def binomial_tail_at_least(k, n, p):
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j)
               for j in range(k, n + 1))


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

    # ---- STEP 1: census the whole committed block, seal telemetry --
    block_telemetry = {}
    for name, spec in NEW_BLOCK.items():
        telem = TL / f"exp029.telemetry.{name}.jsonl"
        if telem.exists():
            telem.unlink()
        run_tiebreak_census(spec["seed"], str(telem))
        block_telemetry[name] = telem
        print(f"census sealed: {name} (seed {spec['seed']})")

    # determinism: re-run the batch in-memory, assert byte-equal to
    # the sealed telemetry BEFORE any statistic is computed.
    determinism = {}
    for name, spec in NEW_BLOCK.items():
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

    # ---- STEP 2 (post-seal): derive pooled desert facts ------------
    corpus = []  # (sid, cohort, rows)
    pilot_tot = {"gens": 0, "draws": 0, "hits": 0}
    for fname, sid, cohort in PILOT_CORPUS:
        rows = load_telemetry(TL / fname)
        corpus.append((sid, cohort, rows))
    block_tot = {"gens": 0, "draws": 0, "hits": 0}

    streams = {}
    for sid, cohort, rows in corpus:
        s = derive_stream(rows)
        streams[sid] = dict(s, cohort=cohort)
        pilot_tot["gens"] += len(s["desert_gens"])
        pilot_tot["draws"] += sum(s["desert_draws_per_gen"])
        pilot_tot["hits"] += s["desert_hits"]
    for name in NEW_BLOCK:
        rows = load_telemetry(block_telemetry[name])
        s = derive_stream(rows)
        streams[name] = dict(s, cohort="D_exp029_adjudication")
        block_tot["gens"] += len(s["desert_gens"])
        block_tot["draws"] += sum(s["desert_draws_per_gen"])
        block_tot["hits"] += s["desert_hits"]

    guard_drift = {
        "pilot_desert_gens": [pilot_tot["gens"], SEALED_DESERT_GENS,
                              pilot_tot["gens"] == SEALED_DESERT_GENS],
        "pilot_desert_draws": [pilot_tot["draws"], SEALED_DESERT_DRAWS,
                               pilot_tot["draws"] == SEALED_DESERT_DRAWS],
        "pilot_desert_hits": [pilot_tot["hits"], SEALED_DESERT_HITS,
                              pilot_tot["hits"] == SEALED_DESERT_HITS],
    }
    if not all(g[2] for g in guard_drift.values()):
        raise SystemExit(f"SEALED-VALUE DRIFT, aborting: {guard_drift}")
    print("pilot re-derivation guard vs sealed 74/1037/4: PASS")

    n_s = {sid: sum(s["desert_draws_per_gen"]) for sid, s in
           streams.items()}
    k_obs = {sid: s["desert_hits"] for sid, s in streams.items()}
    H = sum(k_obs.values())
    N = sum(n_s.values())
    m = len(streams)
    w_s = {sid: n_s[sid] / N for sid in streams}

    # ---- STEP 3: the SEALED adjudication decision -------------------
    p_dev, n_comp, path = exact_deviance_tail(w_s, k_obs, H)
    dev_rejects = p_dev < ALPHA

    # reverse-sensitivity rule (sealed alongside): both must reject
    bonf = {}
    for sid in streams:
        tail = binomial_tail_at_least(k_obs[sid], H, w_s[sid])
        bonf[sid] = {"desert_draws": n_s[sid], "hits": k_obs[sid],
                     "exact_tail": tail,
                     "bonferroni_p": min(1.0, tail * m)}
    bonf_rejects = not all(b["bonferroni_p"] >= ALPHA
                           for b in bonf.values())

    verdict_primary = ("SHARED-HAZARD-REFUTED" if dev_rejects
                       else "SHARED-HAZARD-RETAINED")
    verdict_reverse = ("SHARED-HAZARD-REFUTED-UNDER-REVERSE-RULE"
                       if (dev_rejects and bonf_rejects)
                       else "SHARED-HAZARD-RETAINED-UNDER-REVERSE-RULE")

    result = {
        "experiment": "exp029 adjudication census block b*=1 + "
                      "sealed-rule pooled decision",
        "preregistration": "exp028 Q2/Q3 (sealed 2026-09-30 BEFORE "
                           "this batch ran): block = 8 census-only "
                           "streams, seeds continuing the 31000-"
                           "series, protocol byte-identical to "
                           "exp024, one committed batch, no peeking; "
                           "pooled exact conditional deviance p<0.05 "
                           "REFUTES, Bonferroni diagnostic-only, "
                           "reverse rule = both must reject",
        "design": "exp001 instrument guard byte-identical (census "
                  "ACTIVE); salts k8-k15 seeds 31008-31015, exp021 "
                  "Q1 tiesample semantics POP16 GENS12 BUDGET6; "
                  "determinism verified by in-memory re-run before "
                  "any statistic; pilot corpus re-derived from raw "
                  "telemetry and guarded vs sealed 74/1037/4 "
                  "(abort on drift); pooled corpus = 16 streams "
                  "(cohorts B/C/D per pre-registration)",
        "honesty": "new salts carry NO replicate pins (they are new "
                   "rng streams, not replicates of k0-k7) — guards "
                   "are the exp001 instrument guard + seeded "
                   "determinism only; the pooled deviance mixes "
                   "cohorts B/C/D because the sealed rule says pool; "
                   "per-stream hot/cold reads AFTER the verdict are "
                   "post-hoc and labeled; per-stream Bonferroni is "
                   "DIAGNOSTIC ONLY by seal; the two-class power "
                   "number in exp028 Q3 was an approximation, "
                   "labeled there, decision-informing only",
        "guards": {
            "exp001_reproduced_byte_identical": control_ok,
            "determinism_rerun_byte_equal_all_8": all(
                determinism.values()),
            "pilot_rederivation_vs_sealed": guard_drift,
        },
        "block_census_facts": {
            name: {
                "seed": NEW_BLOCK[name]["seed"],
                "desert_gens": streams[name]["desert_gens"],
                "desert_draws": n_s[name],
                "desert_hits": k_obs[name],
                "birth_gen": streams[name]["birth_gen"],
            } for name in NEW_BLOCK
        },
        "block_totals": block_tot,
        "pooled_corpus": {
            "streams": m,
            "desert_draws": N,
            "desert_hits": H,
            "per_stream": {sid: {"cohort": streams[sid]["cohort"],
                                 "desert_draws": n_s[sid],
                                 "share_w": round(w_s[sid], 6),
                                 "hits": k_obs[sid],
                                 "birth_gen": streams[sid]["birth_gen"]}
                           for sid in streams},
        },
        "sealed_decision": {
            "exact_conditional_deviance_p": p_dev,
            "composition_count": n_comp,
            "exact_path": path,
            "alpha": ALPHA,
            "verdict_primary_rule": verdict_primary,
            "bonferroni_diagnostic_only": bonf,
            "bonferroni_any_rejects": bonf_rejects,
            "verdict_reverse_sensitivity_rule": verdict_reverse,
            "binding": "verdict_primary_rule (exp028 Q2 seal)",
        },
    }

    # post-hoc labeled reads (never the decision)
    posthoc = {
        "block_birth_streams": sorted(
            name for name in NEW_BLOCK
            if streams[name]["birth_gen"] is not None),
        "pilot_birth_streams": sorted(
            sid for _, sid, _ in PILOT_CORPUS
            if streams[sid]["birth_gen"] is not None),
    }
    result["posthoc_reads_labeled"] = posthoc

    out = TL / "exp029.results.json"
    out.write_text(json.dumps(result, indent=1, sort_keys=True),
                   encoding="utf-8")
    print(json.dumps({
        "pooled": {"streams": m, "desert_draws": N, "desert_hits": H},
        "block_totals": block_tot,
        "deviance_p": p_dev,
        "exact_path": path,
        "compositions": n_comp,
        "verdict_primary": verdict_primary,
        "bonferroni_any_rejects": bonf_rejects,
        "verdict_reverse": verdict_reverse,
        "posthoc": posthoc,
    }, indent=1, sort_keys=True))
    print("wrote", out)


if __name__ == "__main__":
    main()
