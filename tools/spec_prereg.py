#!/usr/bin/env python3
"""spec_prereg.py — hash-bound pre-registration of expectation specs.

Adoption, not rivalry: SuperInstance/unspoken-resonance (3ad67d4 -> 48dcd93)
and SuperInstance/madlibs-jev (ee7b73a -> 9baec4f) both run spec_sha-bound
pre-registration; this tool ports the mechanism into fleet house style
(stdlib-only, fnv1a-64 order-sensitive receipt chain per doubt-ledger grammar).

Mechanism (shared shape, all three implementations):
  spec       = a JSON document of EXPECTATIONS, committed/sealed BEFORE the run
  spec_sha   = sha256(canon(spec)) — canon is key-order/whitespace-insensitive,
               value-sensitive (arrays stay ordered)
  seal       = append {kind:seal, spec_sha, ...} to an append-only ledger
               (genesis-anchored chain; tamper names the line)
  check      = recompute spec_sha; refuse loudly when the spec diverges from
               its seal, when the seal is missing, or when the chain broke.
  refusal    = exit 2 (REFUSED, nothing written); breach at check = exit 1.

Honest limits (kept first-class, receipts-culture law):
  1. sha256 here binds CONTENT, not AUTHORSHIP. A party who can rewrite the
     ledger can re-seal a mutated spec. Forensic integrity, not adversarial
     forgery resistance — same law as doubt-ledger limit #1. The chain makes
     tampering LOUD, not impossible.
  2. canon sorts OBJECT keys; ARRAY order is semantic (sibling-identical).
  3. The hash binds BYTES, not meaning. A spec that says "stdev >= 0.5x" is
     only as good as the reader enforcing it. This tool guarantees the spec
     you READ is the spec that was SEALED — nothing more.

Usage:
  spec_prereg.py seal SPEC [--ledger L] [--note NOTE]
  spec_prereg.py check SPEC [--ledger L]
  spec_prereg.py verify [--ledger L]          # chain-only

Exit codes: 0 green / 1 breach (named) / 2 REFUSED (missing/malformed input).
"""

import argparse
import hashlib
import json
import os
import sys
import tempfile

FNV_PRIME = 1099511628211
FNV_OFFSET = 14695981039346656037
FNV_MASK = (1 << 64) - 1

LEDGER_DEFAULT = "receipts/spec-prereg.jsonl"


def fnv1a64(data: bytes) -> int:
    h = FNV_OFFSET
    for b in data:
        h ^= b
        h = (h * FNV_PRIME) & FNV_MASK
    return h


def fnv1a64_hex(data: bytes) -> str:
    return f"{fnv1a64(data):016x}"


def canon(spec) -> str:
    """Canonical form: sorted object keys, compact separators, arrays ordered."""
    return json.dumps(spec, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False)


def spec_sha(spec) -> str:
    return hashlib.sha256(canon(spec).encode("utf-8")).hexdigest()


def chain_hash(prev: str, row: dict) -> str:
    """Order-sensitive chain over the row's canonical content + prev hash.

    The row's OWN chain field is always excluded from the payload — it did
    not exist at seal time and must not exist at verify time either.
    """
    body = {k: v for k, v in row.items() if k != "chain"}
    payload = prev + canon(body)
    return fnv1a64_hex(payload.encode("utf-8"))


def load_ledger(path: str):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append((lineno, json.loads(line)))
            except json.JSONDecodeError as exc:
                raise SystemExit(
                    f"CHAIN BROKEN at line {lineno}: unparseable row ({exc})")
    return rows


def verify_chain(rows) -> str:
    """Walk genesis-anchored chain. Returns tip hash. Breach -> exit 1 named."""
    prev = "genesis"
    for lineno, row in rows:
        expected = chain_hash(prev, row)
        got = row.get("chain")
        if got != expected:
            print(f"CHAIN BROKEN at line {lineno}: "
                  f"expected {expected}, row carries {got}")
            sys.exit(1)
        prev = got
    return prev


def find_seal(rows, sha: str):
    for lineno, row in rows:
        if row.get("kind") == "seal" and row.get("spec_sha") == sha:
            return lineno, row
    return None, None


def cmd_seal(args) -> int:
    if not os.path.exists(args.spec):
        print(f"REFUSED: spec file missing ({args.spec})")
        return 2
    try:
        with open(args.spec, "r", encoding="utf-8") as fh:
            spec = json.load(fh)
    except json.JSONDecodeError as exc:
        print(f"REFUSED: spec is not parseable JSON ({exc}); nothing sealed")
        return 2

    rows = load_ledger(args.ledger)
    tip = verify_chain(rows) if rows else "genesis"
    sha = spec_sha(spec)

    lineno, prior = find_seal(rows, sha)
    if prior is not None:
        print(f"REFUSED: spec_sha {sha[:16]}… already sealed at "
              f"{args.ledger} line {lineno}; ledger is append-only")
        return 2

    row_body = {
        "kind": "seal",
        "spec_sha": sha,
        "spec_path": os.path.basename(args.spec),
        "spec_bytes": os.path.getsize(args.spec),
        "note": args.note or "",
    }
    row = dict(row_body)
    row["chain"] = chain_hash(tip, row_body)

    os.makedirs(os.path.dirname(args.ledger) or ".", exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(args.ledger) or ".")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        if os.path.exists(args.ledger):
            with open(args.ledger, "r", encoding="utf-8") as src:
                fh.write(src.read())
        fh.write(json.dumps(row, sort_keys=True) + "\n")
    os.replace(tmp, args.ledger)
    print(f"SEALED {sha} (ledger {args.ledger}, tip {row['chain']})")
    return 0


def cmd_check(args) -> int:
    for path, label in ((args.ledger, "ledger"), (args.spec, "spec")):
        if not os.path.exists(path):
            print(f"REFUSED: {label} missing ({path}); nothing to check")
            return 2
    rows = load_ledger(args.ledger)
    verify_chain(rows)
    with open(args.spec, "r", encoding="utf-8") as fh:
        try:
            spec = json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"BREACH: spec no longer parseable ({exc})")
            return 1
    sha = spec_sha(spec)
    lineno, row = find_seal(rows, sha)
    if row is None:
        print(f"BREACH: spec_sha {sha} matches NO seal row in "
              f"{args.ledger}; spec diverged from its pre-registration "
              f"(or was never sealed)")
        return 1
    print(f"GREEN: {args.spec} matches seal at line {lineno} "
          f"(spec_sha {sha[:16]}…, chain tip intact)")
    return 0


def cmd_verify(args) -> int:
    if not os.path.exists(args.ledger):
        print(f"REFUSED: ledger missing ({args.ledger})")
        return 2
    rows = load_ledger(args.ledger)
    tip = verify_chain(rows)
    print(f"GREEN: {len(rows)} rows, chain tip {tip}")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    ps = sub.add_parser("seal")
    ps.add_argument("spec")
    ps.add_argument("--ledger", default=LEDGER_DEFAULT)
    ps.add_argument("--note", default="")
    ps.set_defaults(func=cmd_seal)

    pc = sub.add_parser("check")
    pc.add_argument("spec")
    pc.add_argument("--ledger", default=LEDGER_DEFAULT)
    pc.set_defaults(func=cmd_check)

    pv = sub.add_parser("verify")
    pv.add_argument("--ledger", default=LEDGER_DEFAULT)
    pv.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
