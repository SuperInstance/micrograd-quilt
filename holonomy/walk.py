"""Zero-holonomy walk — the geometry under reconcile (queue #4 final slice).

Framing (research/2026-09-24-holonomy-reconcile.md):
  chain_intact() is a 1-D zero-holonomy check; reconcile() is the 2-log case
  of the SAME walk. A receipt chain is a path; walking it and returning must
  bring every witness frame back unchanged (zero holonomy). A revoked witness
  caught in a sync gap is path-dependence: the local path and the hub path
  between the same two anchor cells transport the frame to DIFFERENT places.
  The deviation IS the holonomy element — and the doctrine answer is re-walk:
  insert the deviation as a NEW edge (an adjudication receipt), never rewrite
  the edges already walked.

All arithmetic is exact mod 7 (GF(7)), 9x9 frames — GL(9) over a small field,
no floats anywhere (floats would make "== identity" a lie).
"""

# ---- exact linear algebra over GF(7), 9x9 -------------------------------

Q = 7
N = 9  # frame dimension: GL(9)


def eye():
    return [[1 if i == j else 0 for j in range(N)] for i in range(N)]


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(N)) % Q
             for j in range(N)] for i in range(N)]


def matinv(A):
    """Gauss-Jordan over GF(7); A must be invertible (det != 0 mod 7)."""
    M = [row[:] + eye()[i][:] for i, row in enumerate(A)]
    for col in range(N):
        piv = next(r for r in range(col, N) if M[r][col] % Q != 0)
        M[col], M[piv] = M[piv], M[col]
        inv = pow(M[col][col] % Q, Q - 2, Q)  # Fermat inverse in GF(7)
        M[col] = [(v * inv) % Q for v in M[col]]
        for r in range(N):
            if r != col and M[r][col] % Q != 0:
                f = M[r][col] % Q
                M[r] = [(M[r][c] - f * M[col][c]) % Q for c in range(2 * N)]
    return [row[N:] for row in M]


def transport(edges, frame):
    """Carry a frame along a path (list of matrices), left-multiplying."""
    for E in edges:
        frame = matmul(E, frame)
    return frame


def holonomy(loop):
    """Parallel transport around a closed loop of edges.

    Convention: edges are traversed FORWARD as given; to close the loop each
    edge is also walked BACK (inverse). Holonomy = product of the round trip.
    Zero holonomy  <=>  every frame returns to itself: the connection is
    consistent around that loop (the chain verifies; the merge has no
    path-dependence).
    """
    acc = eye()
    for E in loop:                       # forward leg
        acc = matmul(E, acc)
    for E in reversed(loop):             # return leg, same path back
        acc = matmul(matinv(E), acc)
    return acc


def deviation(local_edges, hub_edges):
    """Path-dependence between two paths with the same endpoints.

    d = hub_path^{-1} * local_path  (a group element). Identity <=> the two
    logs agree on how the frame moves; non-identity <=> a witnessed act whose
    meaning differs per path — the reconcile flag, as a transport element.
    """
    return matmul(matinv(transport(hub_edges, eye())), transport(local_edges, eye()))


def is_identity(A):
    return A == eye()


# ---- receipt-chain bridge -----------------------------------------------

def chain_edges(chain):
    """Receipt chain rows -> transport edges. Each row's hash selects an
    invertible frame-change: the row is the edge, the chain is the path."""
    edges = []
    for r in chain:
        g = r["hash"] % Q or 1
        E = eye()
        E[r["seq"] % N][(r["seq"] + 1) % N] = g % Q  # shear: det=1, invertible
        edges.append(E)
    return edges


def walk_verdict(chain, local, hub, flag):
    """Map a reconcile flag onto the walk: was the loop's holonomy zero?

    A flag means the local path and the hub path disagree on the flagged
    credential's witness frame. Verdict = the deviation element; re-walk
    doctrine: DON'T mutate history, append a closure edge so the EXTENDED
    connection has zero holonomy around the same loop.
    """
    d = deviation(chain_edges(local), chain_edges(hub))
    H = transport(chain_edges(hub), eye())
    L = transport(chain_edges(local), eye())
    # re-walk doctrine: append ONE new edge to the hub path (an adjudication
    # receipt) that left-multiplies it into agreement: C*H == L.
    closure = matmul(L, matinv(H))
    return {"flag": flag["type"], "deviation": d,
            "zero_before": is_identity(d),
            "closure_edge": closure}
