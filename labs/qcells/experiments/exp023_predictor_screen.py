"""exp023 — desert-break predictor screen: does ANY pre-break signal
distinguish the exp022 crossing band (k3/k5/k6) from the contrast
streams (k4 near-miss / k7 dead)?

Doctrine chain under test:
  exp018  FITNESS DESERT AT THE BIRTH CLOUD (hard roots): winning
          move class = 2q gate touching wire 2 (win2).
  exp020  TIE-BAND-DIVERSITY: tie-sampling alone converts 2/3 hard
          roots; 31 stayed closed.
  exp021  RATE NOT WALL: 31 resistance = per-stream desert-break
          rate (3/8 salted streams), not a wall.
  exp022  TRAIN-VISIBLE TIE-BREAK-INVARIANT: crossing streams birth
          a train 0.498 / verify 0.482 cell at ONE desert-break gen
          (k3 g0, k5 g3, k6 g8) picked with window 0; k4 (0.418)
          and k7 (0.0) never birth one.

Open question THIS experiment seals:
  exp022 named it: 'exp023 desert-break predictor — what
  distinguishes break streams pre-break?'  Is the break visible
  BEFORE it happens, or is it a pure per-gen birth event?

DESIGN: pure analysis of the SEALED exp022 telemetry (no re-run, no
rng, no new sims — the predictor question is answerable only from
cloud rows that already exist; running new streams would change the
question from 'pre-break signal' to 'new data').

Windows (pre-registered, applicable-set stated per window):
  W1 AT-BIRTH: gen 0 cloud only. Applicable to all 5 streams
     (for k3, gen 0 IS the break gen — the at-birth read asks
     whether the break cell's CONTEXT at birth differs; labeled).
  W2 PRE-PEAK: gens strictly before the first gen at which the
     stream's eventual max train_p appears (crossers: the break
     gen; non-crossers: the near-miss/dead peak gen). k3's peak
     is at g0 -> W2 window EMPTY -> reported 'undefined', leaving
     W2 at n=4 (k5/k6 vs k4/k7); labeled as the honest limit it is.

Candidate predictors (numbered BEFORE computing, each from a named
doctrine step, threshold frozen pre-run):
  C1 WIN2PRESENCE: any non-champion cloud cell in window carries a
     2q gate touching wire 2 (exp018's winning move class present
     in the exploitable form pre-break).
  C2 NEARBAR40: max non-champion train_p in window >= 0.40
     (exp022's k4 near-miss 0.418 defines the just-under-BAR band;
     if k4 trips C2 the predictor cannot separate and that is the
     honest negative).
  C3 TIEWIDTH4: max n_tied in window >= 4 (exp020/exp022 read: a
     wide desert-floor tie band pre-exists the break; exp022 k3
     g1 n_tied=4 observed post-break).
  C4 ACTIVITY3: >= 3 DISTINCT non-champion genomes with train_p > 0
     appear in the window (desert activity: some signal-born cells
     pre-exist even when nothing promotes).

Verdict conditions (pre-registered):
  SEPARATES(W) = all applicable crossers trip AND no applicable
  non-crosser trips.
  NOT-SEPARABLE = anything else; read: the desert break is a
  per-gen BIRTH event invisible pre-break (exp018 doctrine holds
  at stream level); prediction must target birth-cloud composition
  per-draw odds, not trajectories.
Honesty: post-hoc-free candidate list (each cites its doctrine
step); windows symmetric across classes; undefined windows named
never silently dropped; n=5 / n=4 stated as pilot class — any
SEPARATES verdict is a HYPOTHESIS requiring the exp024 validation
(census the 3 remaining exp021 Q1 salts k0/k1/k2 and test the
surviving predictor(s) blind against their break status).
"""

import json
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
EXP022 = LAB / "experiments" / "exp022.results.json"
TL = LAB / "experiments"

STREAMS = {
    "k3": {"class": "crossing"},
    "k4": {"class": "contrast_near_miss"},
    "k5": {"class": "crossing"},
    "k6": {"class": "crossing"},
    "k7": {"class": "contrast_dead"},
}


def load_stream(name):
    rows = []
    with open(TL / f"exp022.telemetry.{name}.jsonl",
              encoding="utf-8") as fh:
        for line in fh:
            rows.append(json.loads(line))
    return rows


def win2_present(cloud):
    """Any non-champion cell carrying a 2q gate touching wire 2."""
    for cell in cloud:
        if cell["is_champion"]:
            continue
        for gate in cell["genome"]:
            if len(gate) >= 3 and 2 in gate[1:]:
                return True
    return False


def nearbar40(cloud):
    vals = [c["train_p"] for c in cloud if not c["is_champion"]]
    return (max(vals) if vals else 0.0) >= 0.40


def tiewidth4(row):
    return row["census"]["n_tied"] >= 4


def activity3(cloud):
    genomes = set()
    for c in cloud:
        if c["is_champion"] or c["train_p"] <= 0:
            continue
        genomes.add(json.dumps(c["genome"], sort_keys=True))
    return len(genomes) >= 3


def window_rows(rows, lo, hi):
    return [r for r in rows if lo <= r["gen"] < hi]


def main():
    exp022 = json.load(open(EXP022, encoding="utf-8"))

    report = {}
    for name, meta in STREAMS.items():
        rows = load_stream(name)
        crossed = meta["class"] == "crossing"
        # break/peak gen = first gen whose gen_max equals the
        # stream's eventual max train_p (exp022 pinned semantics)
        eventual = max(r["census"]["gen_max"] for r in rows)
        peak_gen = next(r["gen"] for r in rows
                        if r["census"]["gen_max"] == eventual)

        w1 = window_rows(rows, 0, 1)
        w2 = window_rows(rows, 0, peak_gen)  # empty iff peak_gen == 0

        def screen(win):
            if not win:
                return "undefined"
            cloud = [c for r in win for c in r["census"]["cloud"]]
            return {
                "C1_win2presence": win2_present(win[0]["census"]["cloud"])
                if len(win) == 1 else any(
                    win2_present(r["census"]["cloud"]) for r in win),
                "C2_nearbar40": any(
                    nearbar40(r["census"]["cloud"]) for r in win),
                "C3_tiewidth4": any(tiewidth4(r) for r in win),
                "C4_activity3": activity3(cloud),
            }

        report[name] = {
            "class": meta["class"],
            "crossed": crossed,
            "break_or_peak_gen": peak_gen,
            "W1_at_birth": screen(w1),
            "W2_pre_peak": screen(w2),
        }

    # verdicts per window per candidate over applicable streams
    def verdict(window_key, cand):
        trips = {n: r[window_key][cand]
                 for n, r in report.items()
                 if r[window_key] != "undefined"}
        if not trips:
            return "no_applicable_streams"
        cross = all(v for n, v in trips.items() if report[n]["crossed"])
        noncross_any = any(v for n, v in trips.items()
                           if not report[n]["crossed"])
        sep = cross and not noncross_any and \
            any(report[n]["crossed"] for n in trips)
        return {"separates": sep, "trips": trips}

    candidates = ["C1_win2presence", "C2_nearbar40",
                  "C3_tiewidth4", "C4_activity3"]
    verdicts = {w: {c: verdict(w, c)
                    for c in candidates}
                for w in ("W1_at_birth", "W2_pre_peak")}

    any_sep = any(v["separates"] is True
                  for w in verdicts.values() for v in w.values()
                  if isinstance(v, dict))
    result = {
        "experiment": "exp023 desert-break predictor screen",
        "design": "pure analysis of sealed exp022 telemetry; no re-run, "
                  "no rng, no new sims; candidate predictors numbered "
                  "pre-run from named doctrine steps; windows symmetric "
                  "across classes; undefined windows named",
        "honesty": "n=5 (W1) / n=4 (W2) PILOT class: any SEPARATES "
                   "verdict is a hypothesis requiring exp024 blind "
                   "validation on the 3 remaining exp021 Q1 salts "
                   "(k0/k1/k2, census lane); k3 W1 window IS its "
                   "break gen (at-birth context read, labeled); "
                   "k3 W2 undefined (peak at g0)",
        "streams": report,
        "verdicts": verdicts,
        "overall_verdict": ("PREDICTOR_SEPARATES_HYPOTHESIS"
                            if any_sep else
                            "NOT_SEPARABLE_AT_AVAILABLE_N — "
                            "desert-break is a per-gen birth event "
                            "invisible pre-break; exp018 doctrine "
                            "holds at stream level; prediction must "
                            "target birth-cloud per-draw odds"),
        "next": "exp024: census remaining exp021 Q1 salts k0/k1/k2 "
                "(seeds 31000/31001/31002), test surviving "
                "predictor(s) blind against break status",
    }
    out = TL / "exp023.results.json"
    out.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n",
                   encoding="utf-8")
    print(json.dumps(verdicts, indent=1, sort_keys=True))
    print("OVERALL:", result["overall_verdict"])
    print("wrote", out)


if __name__ == "__main__":
    main()
