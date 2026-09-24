# 2026-09-24 — quilt-organism scout note (kimi1, snowball queue #5)

Scouted **SuperInstance/quilt-organism** (single commit `8830769`, ~1,800 LOC, Python 3.11+). Ran it first-hand: demo green (8 essays × 2 receivers = 16 receipts, chain intact); **18/18 tests pass via pytest** — see Findings.

## What it is

The organism layer of the substrate-walker fractal: walks a *corpus* (not one cell) and emits one `OrganismReceipt` per (item, receiver) pair, chained via `prev_witness_id`. Layers: substrate (corpus adapters: GitHub / filesystem / raw-text) → walker (`Organism.walk`) → receivers (CanonScore via JEV, Vectorize via Cloudflare, Orchestra-analyze) → chain → view. `scouts.py` is Casey's memoir directive as code: `Memoir` + `MomentumView` envelopes — scouts *write the felt sense of the work from the agent's POV*, not summaries. `docs/MEMOIR-mavis-2026-09-24.md` is the first instance (Mavis walking the fleet's last 14 days).

## Verified by running

- `examples/demo.py`: 16 receipts, `chain_intact: True`, canon polarity split plausible (essay-cathedral 0.8576 ACCEPT, essay-tide DRIFT).
- Receipt chain verify is O(n) re-link check — honest, cheap, no crypto.
- Faux fallbacks are deterministic (SHA-256 faux canon, faux embeddings) — tests never touch JEV/Cloudflare. Good doctrine, matches our node-pinned-units rule.

## Findings

1. **README test instructions are wrong (confirmed):** badge says 15/15 and instructs `python3 -m unittest discover tests -v` — but all 18 tests are pytest-style bare functions; unittest discovers 0. `pytest tests/` → 18 passed. Minor, but it's the kind of doc-lie our Round-2 meta-rule exists for.
2. **Witness hashes are not reproducible across runs:** `OrganismReceipt.build` hashes `ts = int(time.time())` into the witness payload, so witness_ids differ every run (faux and real alike). Same class as the arena playtest's elapsed-fields finding (8/13 verdict hashes varied). Consequence: no cross-run chain checkpointing — an "aging / refresh the canon" walk can never prove which receipts it replaced. Fix is one line: injectable clock (default fixed/omitted for hashing, wall ts kept outside the hashed body).
3. **`GitHubCorpusAdapter` is root-only, and silently lossy:** single non-recursive `contents/` listing, `return` (not raise) on any non-200, no pagination, `branch="master"` default while ai-writings' default branch differs (worked in demo only because raw.githubusercontent falls back… actually demo uses RawText adapter — the GitHub adapter is UNVERIFIED by the repo's own tests/demo).
4. **No persistence:** receipts live in memory; the chain dies with the process. "Self-reference" growth item (walk your own receipt log) needs a ledger file — that's exactly the seam where quilt-executor's `Ledger` (canonical JSON + FNV-1a-64, café-pin recipe) drops in: two hash families (their sha256-16 vs our fnv64) can co-exist via a substrate field, or organism switches to canonical-hash for cross-repo witness compat.

## Synergy candidates (ranked)

1. **quilt-executor as the organism's nervous system:** a `FleetScoutReceiver` that routes each walked item through the executor's MarginalGainRouter (cheap arm = faux canon, expensive arm = JEV/orchestra) — receipts doctrine already matches (ACCEPT/DRIFT/REFUSE ≈ EFFECT/DRIFT/REFUSED), and LayaSampledJudge's deterministic 10% sampling pattern is the template for dual-run canon scoring. This is queue item #1-of-organism, small.
2. **HolonomyConsensus adjacency (queue #4 skipped as >15min):** organism walks cycles through the fleet's repos the same way GL(9) zero-holonomy checks cycle-based trust over constraint systems — `chain_intact()` is a zero-holonomy check on a 1-D cycle. When #4 is picked up, reconcile.py's offline-revocation maps onto receipt invalidation: revoked witness → re-walk, don't rewrite (revert-not-rewrite doctrine).
3. **Aging/refresh via executor ticks:** the `executor-tick` cron (every 4h :53) could run a bounded organism walk (limit=N) and book the chain head as a TICK receipt — perception at machine speed, canon drift as a first-class signal.

## Doctrine echoes worth keeping

- "The organism is a process, not a thing" — matches our time-as-first-class (chain ticks authoritative).
- Scouts write memoirs, not logs — the answer to "journal, don't summarize" is a *schema* (`Memoir` envelope), not a prompt. We should adopt the envelope for snowball lane reports.
- The substrate walker pattern claimed "closed" at four scales (cell→tissue→organ→organism) — the closed claim is exactly where new seams hide (receipts-vs-persistence is the open one here).
