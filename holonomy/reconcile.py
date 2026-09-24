"""HolonomyConsensus reconcile — offline-revocation reconciliation for receipt chains.

Design ported from surroundapps/agent-provenance's two-log reconciliation
(research/2026-09-24-tooling-catalog.md): a fleet node acts on a credential
DURING a sync blackout; the hub revokes that credential mid-gap. On merge the
surface must FLAG `acted_during_blackout_on_revoked`, not silently accept and
not silently drop — the merged timeline is the audit artifact.

Doctrine conventions (quilt-executor family):
  - canonical JSON: sort_keys, separators=(',',':'), ensure_ascii=False
  - strings hash raw utf-8; dicts hash canonical json
  - FNV-1a-64 receipts; verify() re-derives every row; revert-not-rewrite
"""

import json

FNV_OFFSET = 0xCBF29CE484222325
FNV_PRIME = 0x100000001B3
MASK64 = 0xFFFFFFFFFFFFFFFF


def fnv1a64(data: str) -> int:
    h = FNV_OFFSET
    for b in data.encode("utf-8"):  # bytes-law: raw utf-8, no JSON quotes on strings
        h ^= b
        h = (h * FNV_PRIME) & MASK64
    return h


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def row_hash(row) -> int:
    return fnv1a64(canonical({k: row[k] for k in ("seq", "actor", "op", "payload", "prev")}))


def append(chain, actor, op, payload=None):
    prev = chain[-1]["hash"] if chain else 0
    r = {"seq": len(chain), "actor": actor, "op": op, "payload": payload or {}, "prev": prev}
    r["hash"] = row_hash(r)
    chain.append(r)
    return r


def verify_chain(chain) -> bool:
    for i, r in enumerate(chain):
        if r["seq"] != i:
            return False
        if r["prev"] != (chain[i - 1]["hash"] if i else 0):
            return False
        if r["hash"] != row_hash(r):
            return False
    return True


def reconcile(local, hub):
    """Merge a node log into the hub log; surface offline-revocation conflicts.

    Returns (merged, flags):
      merged — union of both logs ordered by (seq, source); forks keep both rows.
      flags  — one row per surfaced anomaly, typed, never laundered:
        acted_during_blackout_on_revoked | revoked_credential_reused | fork
    Blackout = local rows with seqs the hub has not seen (hub chain is the
    sync anchor). A hub revocation whose seq > local's last synced hub seq
    happened INSIDE the gap; local actions after that credential's issue but
    unseen by the hub are flagged, kept in the merge, and left for adjudication.
    """
    flags = []
    hub_hashes = {r["hash"] for r in hub}
    local_hashes = {r["hash"] for r in local}
    # sync anchor: hub seq of the newest row BOTH logs hold by hash.
    # Seq numbers are per-log and collide after divergence — hashes don't.
    last_common_seq = max((r["seq"] for r in hub if r["hash"] in local_hashes), default=-1)
    # fork: ONLY when there is no common anchor at all (genesis mismatch /
    # unrelated chains). With any shared row, same-seq-different-hash means
    # one-sided news (blackout/divergence), not a fork — precedence matters.
    local_by_seq = {r["seq"]: r for r in local}
    if last_common_seq == -1:
        for hrow in hub:
            lrow = local_by_seq.get(hrow["seq"])
            if (lrow and lrow["hash"] != hrow["hash"]
                    and lrow["hash"] not in hub_hashes and hrow["hash"] not in local_hashes):
                flags.append({"type": "fork", "seq": hrow["seq"],
                              "local_hash": lrow["hash"], "hub_hash": hrow["hash"]})
    # revocations the hub knows about, mapped to the credential they revoke
    revoked = {r["payload"]["revoked"]: r for r in hub if r["op"] == "revoke"}
    # credential rows per actor (both logs; credentials are pre-blackout facts)
    creds = {}  # cred_hash -> (actor, issue_seq, source)
    for src, log in (("hub", hub), ("local", local)):
        for r in log:
            if r["op"] == "credential":
                creds[r["hash"]] = (r["actor"], r["seq"], src)
    # local actions inside the blackout (rows the hub has never seen by hash)
    for lrow in local:
        if lrow["hash"] in hub_hashes or lrow["op"] != "act":
            continue
        # which credential was this actor acting under?
        # convention: act rows carry payload.under = hash of credential row
        under = lrow["payload"].get("under")
        actor = lrow["actor"]
        issue = creds.get(under)
        rev = revoked.get(under)
        if rev is None:
            # actor may hold a credential that was NEVER valid on the hub:
            # unmerged credential + no revocation -> reusable-credential flag once
            if issue and issue[2] == "local":
                key = ("revoked_credential_reused", actor, under)
                if not any(f.get("_k") == key for f in flags):
                    flags.append({"type": "revoked_credential_reused", "actor": actor,
                                  "act_seq": lrow["seq"], "credential": under, "_k": key})
            continue
        # revocation with hub seq beyond the common anchor = inside the gap
        if rev["seq"] > last_common_seq:
            flags.append({"type": "acted_during_blackout_on_revoked", "actor": actor,
                          "act_seq": lrow["seq"], "act_hash": lrow["hash"],
                          "revoked_by": rev["actor"], "revoke_seq": rev["seq"],
                          "credential": under})
    merged = sorted(
        [{"source": "hub", **r} for r in hub] + [{"source": "local", **r} for r in local
         if r["hash"] not in hub_hashes],
        key=lambda r: (r["seq"], r["source"]),
    )
    for f in flags:
        f.pop("_k", None)
    return merged, flags
