# 2026-09-24 — HolonomyConsensus reconcile: offline-revocation prototype (queue #4)

Queue #4 (adopt agent-provenance `reconcile.py` into HolonomyConsensus) was twice
skipped as a >15 min build. This is the deliberate small slice: **the two-log
reconciliation core only**, as a dependency-free prototype, with the semantics
hammered out by pins, not assumed.

## Source design (research/2026-09-24-tooling-catalog.md)

surroundapps/agent-provenance: append-only hash-chain ledger, revocable
credentials, and a **two-log reconciliation** whose key move is: when an offline
node acts on a credential that the hub revoked during the sync gap, the merged
timeline **flags `acted_during_blackout_on_revoked`** — the conflict is surfaced,
not silently accepted and not silently dropped.

## What shipped

`holonomy/reconcile.py` (~120 lines, stdlib-only):

- Family conventions from quilt-executor: canonical JSON
  (sort_keys, `separators=(',',':')`, ensure_ascii=False), strings hash raw
  utf-8, FNV-1a-64 receipts, `verify_chain()` re-derives every row.
- `reconcile(local, hub)` → `(merged, flags)`:
  - **Sync anchor by hash, never by seq.** Seq numbers are per-log and collide
    after divergence; hashes don't. Anchor = newest hub row whose hash the
    local log also holds. (This was the first bug the pins caught: seq-based
    membership classified post-divergence rows as "synced".)
  - **Blackout** = local rows the hub has never seen by hash. Acts under a
    credential whose revocation has hub-seq > anchor get
    `acted_during_blackout_on_revoked` — act receipt hash, revoker, and revoke
    seq all preserved in the flag.
  - **Flagged rows stay in the merge.** Surface, don't drop (the deletion test:
    receipts nobody reads are decorative — a flag with no flagged row is the
    same disease).
  - **`revoked_credential_reused`** — an act under a credential that exists only
    in the local log (never merged, never revoked on the hub): the rogue-credential case.
  - **Fork** is flagged ONLY at genesis mismatch (zero shared rows). With any
    common anchor, same-seq-different-hash is one-sided news (blackout), not a
    fork — precedence rule forced by pin "one-sided unseen rows never
    misflagged as fork".

`holonomy/test_reconcile.py`: 12 pins, all green (run `python3 holonomy/test_reconcile.py`).

## Hard-won semantics (don't re-derive)

1. **Seqs lie after divergence; hashes don't.** Any membership test ("has the
   hub seen this?") must be hash-based or it classifies the adversary's new
   rows as your own synced state.
2. **Fork vs blackout is an anchor question, not a hash question.** Two chains
   that share ANY row are one timeline that diverged (one-sided view each);
   only zero shared rows means two timelines.
3. **The merge is the audit artifact.** Every flag carries enough hashes to
   re-derive the conflict from the merged log alone.

## Next slices (each independently committable)

- DONE (slice 2): flags booked as typed hash-chained rows + adjudication
  receipts (`book_flags`, `adjudicate`; unknown decisions refused not
  booked).
- DONE (final slice): `holonomy/walk.py` — GL(9) zero-holonomy framing,
  exact GF(7) arithmetic. `chain_intact` ≡ zero holonomy on the 1-D path;
  `reconcile` ≡ path-dependence between local and hub paths
  (`deviation = H⁻¹·L`); the flag IS the holonomy element; the doctrine
  answer is re-walk — closure edge `C = L·H⁻¹` appended as a NEW edge,
  history never rewritten (pin 9/10 verify original rows untouched).
  Non-abelian lesson the pins forced: `deviation⁻¹ ≠ L·H⁻¹`; the closure
  edge and the inverse deviation differ unless the group element commutes.
  11/11 pins (`python3 holonomy/test_walk.py`).
