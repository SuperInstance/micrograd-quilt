# NovaFabric / Run Capsules — arXiv 2609.12582 frontier read (2026-10-02 21:0x CST)

Source: https://arxiv.org/abs/2609.12582 (v1, 2026-09-11, Seyedkazemi Ardebili et al.)

## What it is
Audit-grade execution evidence for agent runs, no agent-logic modification. A run is
recorded into a portable **Run Capsule** (15-entity schema), sealed with holistic
**DSSE signature** + **RFC 3161 timestamp** + **Merkle log** + **redaction attestation**.
Sealed runs are **re-executable** under a four-mode replay protocol and exportable as an
**Evidence Bundle** for third-party verification with stock tooling (specified, not evaluated).
Integration paper, not new crypto: OpenTelemetry + DSSE/in-toto + W3C PROV.

## Honest numbers worth citing
- Mocked replay: every model response served from capsule (10/10) — offline w.r.t. models, not the network.
- **Only 2/10 tool-using workloads completed replay** — gap = missing tool-response substitution. Replay of tool-using agents is UNSOLVED by them.
- Tampering rejected across 3 tested classes.
- **Declared-stream completeness 0.652 ± 0.064** — they publish an incomplete-coverage number, not a 1.0 claim.
- Repaired rule pack redacts 14/14 credential types, preserves 9/9 decoys; diff localizes 140/140 mutations.
- Blast-radius: 45.5ms p99 @10M edges (3.3x vs columnar), 167.9ms @100M.
- 314-machine ten-region ingest lossless but capped 61.6 req/s (p99 26.8s) by per-worker serialization.
- Six defects found in own system+corpus: 4 fixed, 1 withdrawn, 1 open — receipts culture, external.
- Verification conditional on a stated trusted computing base (TCB) — honest boundary.

## Relationship to our lanes (doubt-ledger / frozen-clock-lab / qmr1 receipts / tidepool)
- **Same problem space, different layer.** NovaFabric = run-observability capsules (OTel
  instrumentation, heavyweight PKI stack). Ours = git-native, stdlib-only fnv1a-64 receipt
  chains over artifacts/ledger entries (doubt-ledger), clock fault-injection (frozen-clock-lab),
  qmr1 sha256+HMAC chains (quilt-mcp-receipts). Not rivals; a possible **consumer/adapter edge**:
  a quilt receipt could wrap/anchor a NovaFabric capsule hash the same way we anchor anything else.
- **Differentiators we keep first-class:**
  1. *Replay vs provenance.* Their core is re-execution; ours is provenance/lineage.
     Our receipts are explicitly NOT replayable — order-sensitive fnv1a-64 chain is
     provenance-only by design (doubt-ledger limit #1). No conformance claim either direction.
  2. *Weight.* DSSE+RFC3161+OTel+W3C PROV vs our ~200-line stdlib JSONL. Air-gap / bare-clone
     settings run ours, not theirs.
  3. *Their 2/10 tool-replay gap* = our wave-4 query/attest lane's honest boundary is shared:
     recording what was emitted ≠ being able to re-execute it. Tidepool moat note ("local
     receipt proves what was emitted, not that the pool accepted it") is the same shape.
  4. *Redaction attestation* parallels doubt-ledger wave-2 selective-disclosure export —
     vocabulary now externally owned (they publish it); if we ever build redaction attestation,
     cite/differentiate rather than coin new terms.
  5. *Completeness 0.652 honesty* — reinforces our receipts-over-claims doctrine: they ship a
     measured <1.0 coverage number. Fleet pin doctrine already demands demonstrated-RED canaries;
     coverage claims should likewise be measured, never assumed 1.0.
- **No vocabulary emergency** (unlike PAM/IETF-AAT which already got hedges #5/#6/#12):
  "Run Capsule / Evidence Bundle" lives at the observability layer, not the ledger layer.
  WATCH: if a quilt lane ever ingests OTel traces, cite this as the capsule format rather
  than inventing one.

## Candidate follow-ons (not this pulse)
- Consume-don't-rival referral note in doubt-ledger wave-3 (capsule-hash anchoring adapter sketch).
- Frozen-clock-lab: their replay gap (2/10 tool workloads) is a target-shaped hole a
  tool-response-substitution stub could demo against — bounded, future.
