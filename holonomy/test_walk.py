"""Pins for the zero-holonomy walk (queue #4 final slice).

FAIL-first: each pin forces a semantic the code must satisfy, not assume.
Run: python3 holonomy/test_walk.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from holonomy.reconcile import append, reconcile, verify_chain
from holonomy.walk import (Q, N, eye, matmul, matinv, transport, holonomy,
                           deviation, is_identity, chain_edges, walk_verdict)

PINS = 0


def check(name, cond):
    global PINS
    PINS += 1
    assert cond, f"PIN FAILED: {name}"
    print(f"  ok {PINS}. {name}")


def shear(i, j, g):
    E = eye()
    E[i][j] = g % Q
    return E


# 1. GF(7) exactness: no floats anywhere — identity is ==, not ~=
check("GF(7) identity is exact equality", is_identity(eye()))

# 2. Inverse law: A * A^-1 == I for a random-ish invertible shear product
A = matmul(shear(0, 1, 3), matmul(shear(2, 4, 5), shear(7, 8, 2)))
check("matmul(A, matinv(A)) == I exactly", is_identity(matmul(A, matinv(A))))

# 3. Zero holonomy on a flat loop: walk out and back on the SAME path
loop = [shear(0, 1, 3), shear(1, 2, 4), shear(2, 3, 2)]
check("same-path round trip = zero holonomy", is_identity(holonomy(loop)))

# 4. Path-dependence detected: two different paths, same endpoints, disagree
local_path = [shear(0, 1, 3), shear(1, 2, 4)]
hub_path = [shear(0, 2, 5)]                       # same span, different transport
d = deviation(local_path, hub_path)
check("disagreeing paths give non-identity deviation", not is_identity(d))

# 5. Deviation is a group element: closing with it restores agreement
L_t = transport(local_path, eye())
H_t = transport(hub_path, eye())
closure5 = matmul(L_t, matinv(H_t))  # left-applied to hub path: C*H == L
closed = matmul(matinv(matmul(closure5, H_t)), L_t)
check("closure edge restores agreement (C*H)^-1 * L == I", is_identity(closed))

# 6. Receipt chains ARE paths: a verified chain transports anywhere deterministically
chain = []
append(chain, "hub", "credential", {"scope": "repair"})
append(chain, "node", "act", {"under": chain[0]["hash"]})
assert verify_chain(chain)
e1, e2 = chain_edges(chain)
check("same chain -> same transport, every time",
      transport([e1, e2], eye()) == transport(chain_edges(chain), eye()))

# 7. The reconcile bridge: blackout act on revoked credential -> nonzero deviation
local, hub = [], []
append(hub, "ca", "credential", {"scope": "repair"})
append(hub, "ca", "revoke", {"revoked": hub[0]["hash"]})
append(local, "ca", "credential", {"scope": "repair"})   # same genesis row
append(local, "node", "act", {"under": local[0]["hash"]})  # inside blackout
merged, flags = reconcile(local, hub)
assert any(f["type"] == "acted_during_blackout_on_revoked" for f in flags), flags
v = walk_verdict(chain, local, hub, flags[0])
check("blackout-on-revoked => non-zero holonomy verdict", not v["zero_before"])
check("verdict names the flag type", v["flag"] == "acted_during_blackout_on_revoked")

# 8. Re-walk, don't rewrite: closure edge appended, original chain bytes untouched
before = [dict(r) for r in chain]
extended = chain + [{"seq": len(chain), "actor": "holonomy", "op": "adjudicate",
                     "payload": {"closure": True}, "prev": chain[-1]["hash"],
                     "hash": 0}]
check("original chain rows untouched by verdict", chain == before)
check("closure edge left-restores hub path (C*H == L)",
      matmul(v["closure_edge"], transport(chain_edges(hub), eye())) == transport(chain_edges(local), eye()))

# 9. Consistent logs -> zero deviation, no flag to walk
v2 = walk_verdict(chain, local, local, {"type": "none"})
check("identical logs => zero holonomy, nothing to adjudicate",
      v2["zero_before"] and is_identity(v2["deviation"]))

print(f"\n{PINS}/{PINS} pins green — zero-holonomy walk")
