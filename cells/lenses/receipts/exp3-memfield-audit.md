# LENS RECEIPT
- model: deepseek-flash
- endpoint: https://api.deepseek.com/anthropic/v1/messages
- request_id: bd98ce7b-b4d9-4603-83ec-29ce5df6f513
- usage: in=639 out=6835
- cost_credits: quoted-at-publish-rates:deepseek-chat≈$0.00769 (sub-cent; standing ambient order; quoted not billed)
- sha256_of_analysis: caf80868ac5b6766
- at: 2026-09-26T23:44:00.824836+00:00

## THROUGH THE LENS — what this school sees in the piece that a neutral reading misses (be specific, cite lines).
Neutral reads a market survey; SCHOOL sees vendor gravity — mem0 repeated in lines 2, 3, and 7 — market sizing in line 6, and only lines 8–10 are receipt-shaped. The real threats are not “which framework” but “status=completed filter mandatory for P2P reads” (1), “memory contamination… silent drift” (9), and “one deliberate-deletion test” (10).

1. UNVERIFIABLE-FROM-TEXT — ranksquire blueprint’s Redis+Qdrant+Pinecone stack, $106–146/mo, and divergence_threshold 0.15 are digest-only and uncalibrated.  
2. PLAUSIBLE — 6,956 tokens/retrieval vs ~26,000 full-context on LoCoMo is specific, but self-reported through mem0’s state-of-2026 digest.  
3. PLAUSIBLE — “context is not memory” and context rot are coherent; the four-layer taxonomy and ~54K stars are uncited.  
4. PLAUSIBLE — Letta self-editing memory blocks and Cognee graph+vector MCP match known patterns, but no benchmark or failure data.  
5. PLAUSIBLE — framework comparison categories are sensible; “pgvector default” is an adoption claim, not evidence.  
6. UNVERIFIABLE-FROM-TEXT — $6.27B→$28.45B at 35% CAGR is single-source market forecasting with no methodology.  
7. PLAUSIBLE — cross-agent memory pools and procedural memory are plausible trends; “mem0 owns integration layer” is vendor positioning.  
8. PLAUSIBLE — “a folder of markdown files scores 74% on LoCoMo, takes an afternoon” is concrete but lacks harness/receipt; the identity-continuity/navigation critique is the strongest lens hit.  
9. PLAUSIBLE — contamination and silent drift are known failure modes, unquantified here, but directly receipt-able.  
10. PLAUSIBLE — memory contract, shadow path, 20 historical questions, and deliberate-deletion test are concrete and auditable; ranking/prices remain unverified.  

Ranked most worth acting on: 10, then 9, then 8 — deletion/shadow eval, contamination/drift detection, and markdown-canon baseline plus identity-continuity navigation.  
What the field gets wrong that receipts solve: it optimizes mutable retrieval scores, not verifiable lineage, deletion, replay, and identity continuity.

## LOWER-LEVEL ACTIONS — exactly 3 concrete actions this lens renders the piece INTO: builds, experiments, or cell tasks, each one line, each falsifiable or receipt-able.
1. Build a `locomo-receipt` cell: load markdown canon, run claim-10’s 20-question suite incl. deliberate deletion, emit fnv1a WAL receipt per read/write; falsified if no receipt proves deleted memory never resurfaces or 74% cannot be reproduced.  
2. Add a `drift-contamination` job: hash each vector-ocean hit to its WAL receipt lineage and flag confidence repeats lacking source receipt; falsified if known poisoned entries produce no flags or clean entries produce flags.  
3. Implement P2P `status=completed` gate: require receipt chain and divergence ≤0.15 before swarm scratchpad merge; falsified if any unreceipted/uncompleted memory passes or if calibrated canon reads are blocked.
