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

- Wire `reconcile()` output flags into typed ledger rows (REFUSED-adjacent
  family) so the executor's tick cron can crosscheck fleet logs.
- Adjudication policy: who may clear an `acted_during_blackout_on_revoked` row,
  and how the clearance itself becomes a receipt (chain, not edit).
- GL(9) zero-holonomy framing from research/2026-09-24-quilt-organism-scout.md:
  `chain_intact()` is a 1-D zero-holonomy check; reconcile is the 2-log case of
  the same walk — revoked witness → re-walk, don't rewrite.
