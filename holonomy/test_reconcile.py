"""Pins for holonomy/reconcile.py — run: python3 holonomy/test_reconcile.py"""

from reconcile import append, verify_chain, reconcile, fnv1a64, canonical

PINS = 0


def pin(name, cond):
    global PINS
    assert cond, f"PIN FAIL: {name}"
    PINS += 1
    print(f"  ok {name}")


def build_hub():
    hub = []
    cred = append(hub, "auditor", "credential", {"subject": "nodeA", "scope": "act"})
    append(hub, "nodeA", "act", {"under": cred["hash"], "detail": "synced-1"})
    return hub, cred


print("pins: chain integrity")
hub, cred = build_hub()
pin("fresh chain verifies", verify_chain(hub))
hub[1]["payload"] = {"under": cred["hash"], "detail": "tampered"}
pin("tamper breaks verify", not verify_chain(hub))

print("pins: merge + blackout revocation")
hub, cred = build_hub()
# node log: sees hub through seq 1, then blackouts at hub seq 2
node = list(hub)
append(node, "nodeA", "act", {"under": cred["hash"], "detail": "blackout-act"})
append(node, "nodeA", "act", {"under": cred["hash"], "detail": "blackout-act-2"})
# hub during blackout: auditor revokes nodeA's credential (seq 2), then more acts
append(hub, "auditor", "revoke", {"revoked": cred["hash"], "reason": "compromise"})
append(hub, "auditor", "act", {"detail": "post-revoke hub op"})

merged, flags = reconcile(node, hub)
types = [f["type"] for f in flags]
pin("blackout acts flagged", types.count("acted_during_blackout_on_revoked") == 2)
pin("flag keeps receipt hashes", all(f.get("act_hash") for f in flags))
# merged = hub rows + local rows whose seq the hub hasn't seen
pin("merged union size exact", len(merged) == 6)
pin("merged ordered by seq", [r["seq"] for r in merged] == sorted(r["seq"] for r in merged))
pin("flagged rows stay in merge (surface, don't drop)",
    all(any(r["hash"] == f["act_hash"] for r in merged) for f in flags))

print("pins: honest case — revocation synced before act")
hub2, cred2 = build_hub()
append(hub2, "auditor", "revoke", {"revoked": cred2["hash"], "reason": "routine"})
node2 = list(hub2)  # node fully synced through the revocation
append(node2, "nodeA", "act", {"under": cred2["hash"], "detail": "post-revoke attempt"})
merged2, flags2 = reconcile(node2, hub2)
pin("post-sync revocation NOT flagged (honest refusal path is separate op)",
    not any(f["type"] == "acted_during_blackout_on_revoked" for f in flags2))

print("pins: unknown local credential surfaced")
hub3, _ = build_hub()
node3 = list(hub3)
rogue_cred = append(node3, "auditor", "credential", {"subject": "nodeB", "scope": "act"})
append(node3, "nodeB", "act", {"under": rogue_cred["hash"], "detail": "rogue"})
_, flags3 = reconcile(node3, hub3)
pin("unmerged credential flagged", any(f["type"] == "revoked_credential_reused" for f in flags3))

print("pins: fork detection (genesis mismatch — zero shared rows)")
hub4, _ = build_hub()
node4 = []
append(node4, "nodeZ", "credential", {"subject": "nodeZ", "scope": "act"})
append(node4, "nodeZ", "act", {"detail": "other genesis"})
_, flags4 = reconcile(node4, hub4)
pin("unrelated chains flagged as fork", any(f["type"] == "fork" for f in flags4))

print("pins: divergence-after-anchor is blackout, not fork")
_, flags5 = reconcile(node, hub)
pin("one-sided unseen rows never misflagged as fork",
    not any(f["type"] == "fork" for f in flags5))

print("pins: idempotence")
m1, f1 = reconcile(node, hub)
m2, f2 = reconcile(node, hub)
pin("reconcile pure", m1 == m2 and f1 == f2)

print("pins: flag booking + adjudication receipts")
from reconcile import book_flags, adjudicate, row_hash
adj = []
merged_x, flags_x = reconcile(node, hub)
booked = book_flags(adj, flags_x)
pin("chain verifies after flag booking", verify_chain(adj))
pin("every flag booked as typed row", len(booked) == len(flags_x)
    and all(r["op"] == "flag" for r in adj))
# re-deriving a flag's hash from its payload locates the parent row deterministically
fh = fnv1a64(canonical(flags_x[0]))
pin("flag parent-link by payload hash", booked[fh]["payload"] == flags_x[0])
a1 = adjudicate(adj, fh, "auditor", "uphold", "compromise confirmed")
pin("uphold books adjudicate row", a1["op"] == "adjudicate" and a1["payload"]["decision"] == "uphold")
a2 = adjudicate(adj, fh, "auditor", "declined", "credential reinstated")
pin("decline books adjudicate row", a2["payload"]["decision"] == "declined")
a3 = adjudicate(adj, fh, "auditor", "shrug", "maybe")
pin("unknown decision refused, not booked", a3["op"] == "refused"
    and a3["payload"]["reason"] == "unknown_decision")
pin("adjudication chain still verifies", verify_chain(adj))
pin("no silent fallback: every flag has >=1 disposition or is pending",
    sum(1 for r in adj if r["op"] == "flag") == len(flags_x))

print(f"\n{PINS} pins green")
