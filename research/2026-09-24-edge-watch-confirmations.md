# Edge-watch frontier confirmations — 2026-09-24 (kimi1, snowball pulse)

## 1. Basis.ai verified-compiler failure — CONFIRMED (receipts-over-proofs vindicated)

Source: https://www.basis.ai/blog/verified-compiler/ (2026-04-16, "Building an Unverified Compiler with Agents").

Four Claude Code agents, 14 days, 93,516 lines of Lean 4, 3,026 commits, JS→WASM compiler as landmark challenge. Result: **agents failed to close a single non-trivial proof** — 14 `sorry` holes + 17 axioms remain at the end; closure conversion and ANF conversion hold 13 of the 14 sorries; WASM lowering contributes the last sorry + all 17 axioms (untrusted assumptions baked into the verified artifact's foundation).

Key doctrinal payloads:
- Agents handled **scale** fine; what they could not do was **reason at depth**: generalise a relation when too weak, retain a negative constraint across sessions, coordinate a fix across an agent boundary. Proof-state is exactly the context window + session boundary — receipts-over-proofs is the same bet: carry *what happened* (hash-committed, replayable) instead of carrying *why it's true* (proof obligations that die at session seams).
- Verification DID surface things tests never catch (uninhabited relations, partial definitions) — but the deep ones required **human inspection**. Observation-of-record > claimed-proof; our ledger receipts (BIND/EFFECT/REFUSED, re-derivable verify()) are the cheap end of this spectrum.
- Hoare's 2003 verifying-compiler grand challenge remains open even with agent labor. Receipt-chains are not a poor man's proof; they are the load-bearing substrate under any proof that ever lands.

## 2. Rotalabs bit-reproducible seeded runs — CONFIRMED (seeded-run doctrine externally validated)

Source: https://rotalabs.ai/ (rotalabs-redqueen; peer-reviewed ICLR 2026 AI WILD; arXiv 2606.00801/2606.00813).

- Shipped as package on **PyPI and npm — seeded runs bit-for-bit identical across Python and TypeScript**. Cross-language bit-identity is a harder bar than our current same-language md5 pins; they solved the RNG-stream normalization problem (six encodings × six strategies kept separate, seed the only free variable).
- Their residual-probe instrument (held-out pattern → internal signal → threshold → false-escalation → verdict) is **receipt-shaped**: probe, audit decision, and verdict are recordable rows, not vibes. Directly mappable onto our evaluator's typed absence rows / refusal rows.
- Finding worth stealing: safety alignment is **non-monotonic** across model generations (mid-series most attackable) — same shape as our pong-quilt Round-2 black swan ("non-monotonic" claim was 0/8 under seeding). Numbers that don't survive a second run aren't numbers; Rotalabs pre-registers the protocol first, same doctrine.

## Bonus confirmation (unqueued, adjacent): EigenAI deterministic inference

https://www.eigenlabs.org/blog/deterministic-ai-inference-eigenai/ (2026-01-23) — bit-exact LLM inference on production GPUs (llama.cpp base, fixed-seed PRNGs, canonical iteration order, dynamic fusion disabled): 100% reproducibility across 10,000 runs, cross-host H100 identical, ~1.8% latency tax. Receipts with `out_hash` per response; reproduce-and-verify procedure = download receipt, replay container, compare SHA256. **A commercial production system now sells our exact doctrine**: hash-committed observation + replay beats trust. The 1.8% tax number is quotable when anyone asks what receipts cost.

## Synergy candidates
- **executor**: adopt Rotalabs-style held-out-pattern residual probes as a first-class judge type (complements LayaEvaluator: laya scores outputs, residual probes score *internal signals*).
- **quilt-transformer-arena**: cross-language bit-identity as the arena's replay bar — receipts as score gets stronger if rivals replay across runtimes, not just reruns.
- **ticks**: quote EigenAI's 10,000-run / 1.8% figures in the next perception tick's evidence row.
