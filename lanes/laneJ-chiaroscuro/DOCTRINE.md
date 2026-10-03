# CHIAROSCURO DOCTRINE — foundational synthesis (supplemental, 2026-10-03 ~03:50)

This document is the broader foundational understanding the lane keeps
returning to. It is iterated, not finished. Everything load-bearing carries a
claim tag: FOUND (verified by running/reading), ASSUMED (design wager),
UNVERIFIED (asserted by a source we could not test on this host).

## 1. The convergence thesis (FOUND — three independent directions, one law)

On the night of 2026-10-03 the org pulse and frontier watch produced three
independent arrivals at the same architectural law:

1. **Org-internal**: `receiptd` ("fleet trust layer" — append-only JSONL hash
   chain, INCONCLUSIVE as a first-class verdict) and `quilt-float` (git-agent
   teaching loop using a sha256 receipt chain as its synchrony primitive).
2. **Academic**: PoEM (arXiv 2608.16032) — the FARMA attack forges
   "already-done" memory entries; stronger models fall harder (98–100%
   acceptance). The paper's defense is an independent HMAC-chained execution
   ledger. Note the threat-model difference from ours: keyed HMAC vs our
   unkeyed fnv1a-64 + optional Ed25519 — limit #1 stands, but the *law*
   (execution ledger over claimed memory) is identical.
3. **Standards**: IETF draft-sharif-agent-audit-trail (now -06; our hedge
   cited -00 — drift noted, cite-version discipline matters).

**The law**: agents cannot be trusted to report their own past. Any system
that lets them is exploitable (PoEM) or unauditable (everything else). The
only stable foundation is a receipt surface that records effects on the
effect path, with discharge-requires-reason and tamper-evidence as axioms.
The chiaroscuro lane's bivariate lattice is one instance of this law; the
warp platform's verdict-gated WAL is another; receiptd/quilt-float are
third and fourth. Consume-don't-rival: cite and differentiate, never fork.

## 2. The claim-ledger method (FOUND — validated repeatedly tonight)

- Every claim carries FOUND / ASSUMED / UNVERIFIED. "60 FPS" without a GPU is
  UNVERIFIED; "18.3ms first tick" with a console capture is FOUND.
- FAIL-first pins are the epistemic unit: the RED trip is evidence, the
  green run is only the second half. Tonight's captures: `.mjs` ESM/require
  mismatch; F32 body misalignment; silent envelope truncation; 8 RED trips
  in the warp platform suite; the nb localStorage quota wrap.
- Honest blockers are named, never hidden: GPU/WebRTC/camera (no hardware),
  Cloudflare binding, inference endpoint, zcode remote-exec removal,
  push credentials. A named blocker is a queued lane, not a failure.

## 3. The substrate mapping (ASSUMED — the design wager under test)

| Seed vision | Fleet-native reading | Status |
|---|---|---|
| Bivariate cell lattice | Receipt surface: cell states append-only = WAL ticks | FOUND conceptually; sufficiency of 2 vars ASSUMED |
| Characters as opcodes | Capabilities-as-verbs (warp platform contract) | FOUND in warp platform core |
| Dual-rate loop (reflex/planning) | Fast cells = receipts, slow models = adjudicators | ASSUMED |
| Vision-teacher GAN | VLM as receipt-checking discriminator | UNVERIFIED (no endpoint) |
| Self-evolving JIT shaders | EvolutionAgent pruning = extraction-with-trace | FOUND as doctrine; GPU path UNVERIFIED |
| `.pai` portable identity | Codec = envelope + integrity hash + provenance | FOUND locally (4/4 pins, 0.209 µs/cell) |

## 4. Measured baselines (FOUND, 2026-10-03)

- phase1 sim first tick: **18.3 ms** (CPU procedural, 96×42 glyph viewport).
- P2 canonical watchdog: 60 frames, 1 firing @ tick 40, **0 false positives**,
  stall 1352 ms detected via dual signal, recovery within budget.
- Competing-coders race (zcode vs kimi-code 2.1.1): both PASS judge re-runs;
  tie — kimi edges measurement rigor (0/59 FP control, gap corroboration),
  zcode edges spec fidelity (throttle stats). Receipt: RECEIPTS/race-2026-10-03.md.
- P4 codec: 88.1 KiB envelope, 12.02 B/cell, encode 0.209 µs/cell, decode
  0.164 µs/cell (implied), identity hash tamper-flip verified.
- Warp platform: 10/10 pins green (P8–P10 in flight via subagent tonight).

## 5. The assistant-lane doctrine (FOUND as operating rule, 02:23)

Lanes serve project engineers, not the void. Instantiations:
laneJ-P2 → warp platform engineer (host crash recovery); omz-assist →
upstream maintainers (README patch inventory); nb digest → canvas-viz
engineer; exp003 → backward-holdem experiment engineer. New lanes must name
their engineer in the first paragraph of their SPEC or queue entry.

## 6. Open wagers (ASSUMED/UNVERIFIED — what would falsify or confirm)

1. Bivariate sufficiency: does [luma, θ, mag] carry enough signal for a
   useful substrate? Falsified if a phase-N task needs >2 vars to hit its
   pin; confirmed by a full sim→identity roundtrip.
2. Receipt-density cost: how much of the 4 MB quilt budget should be
   receipts vs state? Measure when P3 lands.
3. VLM-discriminator quality: UNVERIFIED until an endpoint exists; the
   harness slot is codec.p4.cjs's identity hash seam.
4. zcode remote path: dropped by 0.16.9; if it returns, exp003 unblocks.
