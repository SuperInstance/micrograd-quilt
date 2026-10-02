#!/usr/bin/env python3
"""lane-token-meter.py — per-lane token accounting, host-scale JSONL.

ADK EvalSet efficiency-evaluator reproduction (scout: memory/research/scout-adk-2026-10-03.md §4):
ADK reports per-type token usage; we had NO token accounting per lane and kimi-code
quota kills were unmeasured. This is the smallest build: one append-only JSONL event
per lane/pulse with input/output token counts, fnv1a-64 receipt chain
(genesis-anchored, order-sensitive — doubt-ledger grammar) so the meter log itself
is tamper-evident. Stdlib only; no model in this loop (KS2 law: meter never judges,
it only counts).

Usage:
  lane-token-meter.py record --lane LANE --model MODEL --input-tokens N --output-tokens N [--cost-usd X] [--note S]
  lane-token-meter.py verify            # recompute chain over the log; name the bad line on tamper
  lane-token-meter.py totals [--lane L] # per-lane sums (reporting only, not a receipt)

Env:
  TOKEN_METER_LOG  default: <repo>/data/lane-token-meter.jsonl

Receipts doctrine: this log is FORENSIC, not a judge of record. Queue lines stay
the currency; this answers "what did that pulse cost" with a verifiable number.
"""
import argparse
import json
import os
import sys
import time

FNV_PRIME = 0x100000001B3  # 2**40 + 435, computed not commented (pin lesson: comments don't execute)
FNV_OFFSET = 0xCBF29CE484222325
MASK64 = (1 << 64) - 1


def fnv1a64(s: str) -> int:
    h = FNV_OFFSET
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return h


DEFAULT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "lane-token-meter.jsonl")
LOG = os.path.abspath(os.environ.get("TOKEN_METER_LOG", DEFAULT_LOG))

GENESIS = {"ts": 0.0, "lane": "genesis", "model": "-", "input_tokens": 0, "output_tokens": 0,
           "cost_usd": None, "note": "genesis anchor", "prev": 0, "checksum": 0}


def tip(log_path=LOG):
    """Return (last_line_checksum, line_count). Empty log -> genesis."""
    last, n = fnv1a64(json.dumps(GENESIS, sort_keys=True)), 0
    if not os.path.exists(log_path):
        return last, n
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            last = json.loads(line)["checksum"]
            n += 1
    return last, n


def cmd_record(a):
    if a.input_tokens < 0 or a.output_tokens < 0:
        print("REFUSED: token counts must be >= 0", file=sys.stderr)
        return 2
    prev, n = tip()
    rec = {"ts": time.time(), "lane": a.lane, "model": a.model,
           "input_tokens": a.input_tokens, "output_tokens": a.output_tokens,
           "cost_usd": a.cost_usd, "note": a.note, "prev": prev}
    rec["checksum"] = fnv1a64(json.dumps(rec, sort_keys=True))
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    print(f"recorded line {n + 1}: lane={a.lane} in={a.input_tokens} out={a.output_tokens} checksum={rec['checksum']:016x}")
    return 0


def cmd_verify(_a):
    expected, n = fnv1a64(json.dumps(GENESIS, sort_keys=True)), 0
    if not os.path.exists(LOG):
        print("verify OK: empty log (genesis only)")
        return 0
    with open(LOG, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            n += 1
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print(f"TAMPER line {i}: invalid JSON")
                return 1
            if rec.get("prev") != expected:
                print(f"TAMPER line {i}: prev mismatch (expected {expected:016x}, got {rec.get('prev')})")
                return 1
            saved = rec["checksum"]
            rec_check = {k: v for k, v in rec.items() if k != "checksum"}
            if fnv1a64(json.dumps(rec_check, sort_keys=True)) != saved:
                print(f"TAMPER line {i}: checksum mismatch — content altered")
                return 1
            expected = saved
    print(f"verify OK: {n} lines, tip {expected:016x}")
    return 0


def cmd_totals(a):
    agg = {}
    if os.path.exists(LOG):
        with open(LOG, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if a.lane and rec["lane"] != a.lane:
                    continue
                s = agg.setdefault(rec["lane"], {"lines": 0, "input_tokens": 0, "output_tokens": 0})
                s["lines"] += 1
                s["input_tokens"] += rec["input_tokens"]
                s["output_tokens"] += rec["output_tokens"]
    print(json.dumps(agg, indent=2, sort_keys=True))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record")
    r.add_argument("--lane", required=True)
    r.add_argument("--model", required=True)
    r.add_argument("--input-tokens", type=int, required=True)
    r.add_argument("--output-tokens", type=int, required=True)
    r.add_argument("--cost-usd", type=float, default=None)
    r.add_argument("--note", default="")
    r.set_defaults(fn=cmd_record)
    v = sub.add_parser("verify"); v.set_defaults(fn=cmd_verify)
    t = sub.add_parser("totals"); t.add_argument("--lane", default=None); t.set_defaults(fn=cmd_totals)
    a = p.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
