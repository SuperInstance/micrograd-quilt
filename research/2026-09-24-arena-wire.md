# Arena wire — quilt-executor ↔ quilt-transformer-arena
**kimi1 · 2026-09-24 · verified surfaces only**

## What the arena already is (gh-verified)

- `SPEC.md` — locked v0, cites `kimi1 research/2026-09-24-quilt-transformer/RESEARCH.md` as its origin doc. Three layers (Archival Canvas ℚ/Q16 → Contract Protocol → Transient Workers), ticks as serialization barriers, autodiff as ledger-to-ledger, bitwise rewind, nudges as individually-retractable ledger entries, critic ACL, per-flight receipts with σ report.
- `harness/receipts.py` — referee. `kev()` = the café Δ 日本语 FNV-1a-64 vector (**same family recipe as quilt-executor's ledger** — the referee already speaks our hash). `moth_row(FINDING|VERDICT|REFUSAL)` — MOTH ledger. `jev_decide()` — JEV proxy with the HARNESS-JEV-LIVE-MISLABEL fix: non-2xx bodies are NOT live verdicts (the org already learned receipts-over-trust mid-bout, the hard way).
- `competitors/{claude,crush,kimi}` — rival slots. kimi already has `e1.py`, `result.json` (**xor_solved: true, rewind_bitwise: true, rewind_to: 37, max_sigma 7.6e-6**), jev/ + moth/ receipt dirs. Round 1 scoreboard: Registrar wins on depth; referee defect fixed with receipts.
- `rounds/` — Round 1.5 put a convergence prediction on record **to be falsified**. The culture is receipts-native.

**Do not claim a competitor seat — the kimi slot is taken and winning.** Our lane is
the referee's instruments and the bout scorer.

## What quilt-executor contributes (3 instruments)

### 1. Typed absence rows → MOTH REFUSAL payloads (SPEC v2 §3)
Arena REFUSAL rows exist but content is free-form. Our schema makes them load-bearing:
`{refusal_type ∈ noul_ambiguity|insufficient_context|ood|router_failure|truncation|timeout,
visibility{state_sha256, visible_sha256, span}, routing{checkpoint_id, router_score, alternatives},
trigger+value, resolvability, parent_receipt_id, cost_tick_ms, cost_wall_ms}`.
A REFUSAL nobody types is a log line; the deletion test applies to the arena too.

### 2. Dual-run lie detector as referee upgrade
`jev_decide()` gates on LIVE/UNVERIFIED but is single-source and self-reported. The
crush-C2-hardened estimator replaces trust with measurement:
- every contested design choice runs through **two** independent deciders (JEV proxy + a second model/route);
- Δ booked per pair; declined escalations audited for laundering (5% random keep-holdout,
  fast-arm score booked pre-escalation, escalation↔difficulty correlation tripwire);
- tail quantiles of |Δ| per rival per experiment — **means hide gaming** (already doctrine in both specs).

### 3. Worker-flight scorer (SPEC.md item 9)
Every flight receipts contract/input/output hashes + σ report. What scores the FLIGHT
itself is currently vibes. Our Evaluator + absence rows give: per-axis scores with
backends receipted (laya/heuristics/reference/judge), truncation preconditions,
bandit-neutral updates. The worker capability card (`{opcodes, measured σ vs reference,
throughput, codec compliance}`) becomes a lease — earned per task_type with the C2
evidence list, expired by time-decay.

## "Ah-struck" in receipts terms
Round 1.5's falsifiable-prediction culture is exactly right. The ah-struck detector:
- **quality-tail events**: rounds where realized drift breaks a rival's σ band (σ-report vs measured);
- **nudge unpredictability**: divergence at k+1 outside the predicted envelope → FINDING row, prediction hash on record;
- **codec violations**: any float leak = typed defect row (already SPEC adversarial surface);
- the comb (commensuration) is a red herring here — arena time is tick-indexed, chain order is the clock (dual-clock doctrine: ticks authoritative, wall advisory).

## Build order (test-pinned, our side)
1. `arena_bridge/typed_refusal.py` — translate our absence rows → MOTH REFUSAL rows; pins: kev(content_hash) stable, round-trip parse, all six types.
2. `arena_bridge/dualrun.py` — Δ estimator + laundering countermeasures over jev_decide; pins: synthetic paired receipts, holdout sampling, correlation tripwire.
3. `arena_bridge/flight_scorer.py` — Evaluator adapter over flight receipts; pins: per-axis backends receipted, truncation precondition, bandit neutrality.
4. E2-style bout: swap numpy→pure-python worker under the scorer; drift measured and receipted; result.json schema extended with `score_card` + `absence_rows` fields (backward-compatible).

## The one experiment worth running first
**E2-under-scoring**: re-run the worker-swap bout with flight_scorer live and both
deciders on one contested choice. It exercises all three instruments at once and
produces the first arena receipt pair comparable across rivals — the Registrar's
depth win becomes measurable, not declared.
