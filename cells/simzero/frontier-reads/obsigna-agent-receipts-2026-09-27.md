# FRONTIER READ — Obsigna / Agent Receipts (2026-09-27, kimi1)

Sources: agentreceipts.ai (overview + spec index), obsigna.dev/verify (verifier page).

## What they built
- **Agent Receipt** = W3C Verifiable Credential, type `AgentReceipt`, Ed25519-signed,
  SHA-256 hash-chained log, RFC 3161 optional timestamps, JCS (RFC 8785) canonicalization.
- **Daemon architecture**: signing keys + receipt store live OUTSIDE the agent process;
  agent talks over a read-only unix socket. Audit trail survives agent compromise.
- Standardized **action taxonomy + risk levels**; parameters hashed not stored
  (privacy-preserving disclosure).
- Tooling: Claude Code hook, MCP proxy (no-code drop-in), Go/TS/Python SDKs, dashboard.
- WASM browser verifier = **same Go core as the CLI** — no reimplementation drift;
  native-vs-WASM byte-identical conformance in CI.
- Verifier honesty page: "checks cryptographic properties only; no legal admissibility;
  does not attribute." A valid signature proves internal consistency under the supplied
  key — nothing more. (This honesty is loadbearing and matches our scar-receipt culture.)
- Purpose axis: **audit/compliance** — EU AI Act Art. 12 traceability for high-risk AI.

## Doctrine delta vs fleet (quilt-stone lineage)
| axis | Obsigna | fleet |
|------|---------|-------|
| receipt is | attestation of an action | **world-state transition** (5-opcode WAL) |
| trust anchor | external daemon + Ed25519 keys | the ledger's own hash chain + referral-graph earned trust |
| purpose | audit trail for humans | **coordination + breeding currency** (VERIFIED edges, G11 trust gluing) |
| taxonomy | standardized action types | open-ended kinds |
| verifier | WASM=Go core, one impl | stone.mjs, 6 dialects matched as-found |
| read-side | dashboard, verify CLI | **Q8 OPEN** — the fleet's own read-side rule gap (rivalry Round 2 live) |

## Decision frame (interop-vs-differentiate)
1. **ADOPT the architectural lesson**: key separation. Our in-process sealing means a
   compromised process can seal lies. Obsigna's daemon-over-read-only-socket closes that.
   Candidate lanes: quiltcall WAL signer, git-agent emitter, any future ReceiptChannel
   writer that signs. Smallest build: sign-only daemon that holds the fleet key, exposes
   `sign(payload)` over a socket with an allowlist of payload shapes.
2. **INTEROP lane (cheap, high value)**: export stone-v1 chains into a W3C VC envelope —
   JCS-canonicalize, Ed25519-sign the chain tip, keep the 5-opcode rows as
   credentialSubject. Fleet receipts become Obsigna-verifiable without giving up ledger
   semantics. This is a translator, not a rewrite; the conformance corpus gives us a
   test oracle for free.
3. **DIFFERENTIATE where they have no analog**: referral-graph trust currency
   (VERIFIED edges), breeding integration (receipts change parent selection), QD
   diversity pressure. No external actor is building this; it stays the moat.
4. **Do not chase**: action taxonomy standardization (our kinds are open-ended on
   purpose — taxonomy is their compliance moat, not our coordination need);
   RFC 3161 TSA (fleet timestamps ride the WAL sequence, not wall-clock authority).

## The sharpest collision
Their verifier says "internal consistency — nothing more." Ours must say more because
our receipts are CURRENCY: a VERIFIED edge is a receipt that changed the referral graph,
which changed trust, which changes breeding. That is a claim about CONSEQUENCE, not
just consistency. Obsigna deliberately does not go there (legal admissibility avoided).
The fleet already does — and pays for it with the read-side gap Q8 names. The two
projects are complementary at exactly the seam: they prove what happened; the fleet
must prove what it CHANGED.

Status: READ COMPLETE. Interop lane queued behind stone-v1 adoption + Q8 verdict.
