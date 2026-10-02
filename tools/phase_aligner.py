#!/usr/bin/env python3
"""phase_aligner — reference implementation of specs/phase-aligner-spec.md.

NETF Tier 2: async cones carry {arrival_tick, tau, deadline}; the pulse
consumes strictly in arrival order; over-deadline cones book REFUSED rows
with a mandatory reason from the sealed vocabulary. Stdlib only.

The aligner never blocks (Law 5): everything here operates on buffered
events; a cone that has not landed by its deadline is REFUSED without wait.
"""

import json
import sys

REASONS = ("over-deadline", "un-booked-fields", "cone-violation", "superseded")

FNV_PRIME = 0x100000001B3
FNV_MASK = 0xFFFFFFFFFFFFFFFF
FNV_OFFSET = 0xCBF29CE484222325

FNV_GENESIS = "phase-aligner:genesis:2026-10-03"


def fnv1a64(s):
    h = FNV_OFFSET
    for ch in s:
        h = ((h ^ ord(ch)) * FNV_PRIME) & FNV_MASK
    return h


def receipt_hash(prev, row_obj):
    """Order-sensitive fnv1a-64 chain over canonical JSON rows (doubt-ledger grammar)."""
    canon = json.dumps(row_obj, sort_keys=True, separators=(",", ":"))
    return "%016x" % fnv1a64(prev + "\n" + canon)


def genesis():
    return receipt_hash("0" * 16, {"row": "GENESIS", "note": FNV_GENESIS})


def check_event(ev):
    """Law 1: refuse at intake if any of the three fields is missing."""
    missing = [k for k in ("event_id", "lane", "arrival_tick")
               if k not in ev or ev[k] in (None, "")]
    has_tau = "tau" in ev and ev["tau"] is not None
    has_deadline = "deadline" in ev and ev["deadline"] is not None
    if not (has_tau or has_deadline):
        missing.append("tau|deadline")
    elif has_tau and not has_deadline:
        ev["deadline"] = ev["arrival_tick"] + int(ev["tau"])  # tick units
    if missing:
        return "un-booked-fields: missing " + ",".join(missing)
    return None


def intake(events):
    """Law 1 gate. Returns (booked, refused_rows)."""
    booked, refused = [], []
    for ev in events:
        err = check_event(ev)  # mutates ev in place: derives deadline from tau (Law 1)
        if err:
            row = {"row": "REFUSED", "event_id": ev.get("event_id", "?"),
                   "lane": ev.get("lane", "?"),
                   "arrival_tick": ev.get("arrival_tick", -1),
                   "deadline": ev.get("deadline", -1),
                   "consumed_tick": None,
                   "reason": err.split(":")[0], "detail": err}
            refused.append(row)
        else:
            booked.append(ev)
    return booked, refused


def align(booked, refused_intake, current_tick):
    """Laws 2+3: strict arrival order; over-deadline cones book REFUSED rows."""
    # Law 2: arrival order, ties by lane name (deterministic)
    ordered = sorted(booked, key=lambda e: (e["arrival_tick"], e["lane"]))
    out_rows = list(refused_intake)
    consumed = []
    for ev in ordered:
        if ev["deadline"] < current_tick:  # Law 3: refused, never executed
            out_rows.append({"row": "REFUSED", "event_id": ev["event_id"],
                             "lane": ev["lane"], "arrival_tick": ev["arrival_tick"],
                             "deadline": ev["deadline"], "consumed_tick": current_tick,
                             "reason": "over-deadline",
                             "detail": "deadline %d < tick %d" % (ev["deadline"], current_tick)})
        else:
            consumed.append(ev)
    return consumed, out_rows


def close_cones(consumed, current_tick):
    """Law 4: CLOSED rows with actual_latency; REFUSED rows never enter tau."""
    closed = []
    for ev in consumed:
        lat = max(0, current_tick - ev["arrival_tick"])
        closed.append({"row": "CLOSED", "event_id": ev["event_id"], "lane": ev["lane"],
                       "arrival_tick": ev["arrival_tick"], "consumed_tick": current_tick,
                       "actual_latency": lat})
    return closed


def update_tau(closed_rows, tau_state):
    """Law 4: per-lane tau from CLOSED rows only, order-sensitive."""
    state = dict(tau_state or {})
    for row in closed_rows:
        lane = row["lane"]
        st = state.setdefault(lane, {"n": 0, "total": 0, "max": 0})
        st["n"] += 1
        st["total"] += row["actual_latency"]
        st["max"] = max(st["max"], row["actual_latency"])
        st["tau_estimate"] = st["total"] / st["n"]
    return state


def run_tick(events, current_tick, prev_tip, tau_state):
    """One pulse tick end-to-end. Returns dict with rows + new chain tip."""
    booked, refused_intake = intake(events)
    consumed, refused = align(booked, refused_intake, current_tick)
    closed = close_cones(consumed, current_tick)
    rows = refused + closed  # refusals booked before closures this tick
    tip = prev_tip
    for r in rows:
        r["receipt"] = receipt_hash(tip, r)
        tip = r["receipt"]
    return {"rows": rows, "tip": tip,
            "tau_state": update_tau(closed, tau_state),
            "consumed": [e["event_id"] for e in consumed]}


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "tick":
        sys.stderr.write("usage: phase_aligner.py tick TICK < events.jsonl\n")
        sys.exit(2)
    tick = int(sys.argv[2])
    events = [json.loads(l) for l in sys.stdin if l.strip()]
    prev_tip = genesis()
    # multi-tick chains: pass --tip FILE to persist/load chain tip
    if "--tip" in sys.argv:
        path = sys.argv[sys.argv.index("--tip") + 1]
        try:
            with open(path) as f:
                prev_tip = f.read().strip() or prev_tip
        except OSError:
            pass
        res = run_tick(events, tick, prev_tip, None)
        with open(path, "w") as f:
            f.write(res["tip"] + "\n")
    else:
        res = run_tick(events, tick, prev_tip, None)
    for r in res["rows"]:
        print(json.dumps(r, sort_keys=True))


if __name__ == "__main__":
    main()
