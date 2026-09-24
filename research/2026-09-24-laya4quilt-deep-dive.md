# laya4quilt × quilt-executor — where the project leads (kimi1's perspective)

Date: 2026-09-24, on Casey's "where did this project lead?" + "wire it concretely."

## The arc in one paragraph

Universal Translator brief (14:16) → Universal Executor born (quilt-executor, 5
commits, 18 pins, live Kimi smoke) → CI/CD perception ticks (14:36 directive —
executor as an organ of the larger quilt) → **laya4quilt lands as the missing
System-1 organ.** Each step abstract ("compare continuously, let the bandit
decide") keeps resolving into a concrete dependency, and this one was already
built by FM's ecosystem: a 33ms non-autoregressive typed-decision engine with
honesty-native training and a per-request router. The evaluator layer stops
being my hand-rolled heuristics + occasional LLM judge and becomes a
measurement instrument.

## Why laya is exactly our pattern (not a metaphor — a homology)

| Universal Executor layer | laya4quilt concrete piece | Homology |
|---|---|---|
| Evaluator (quality scoring) | typed `choice`/`score`/`noul` questions, one forward pass, 33ms | Same job, 60x faster, nothing to parse |
| Honesty doctrine | RLCD: RL against **strictly proper scoring rules** | Proper scoring makes lying suboptimal — crush's receipt doctrine as a *training objective* |
| Decider (router) | `laya/router.py` checkpoint selection per request | Thompson Sampling's fast little sibling |
| REFUSAL rows | `noul` typed questions ("should this be refused?") | A refusal-native output type, first-class |
| Multilingual fleet | 100+ languages, mmBERT checkpoint | The translator brief's axis survives |
| Rivalry preserved | repo benchmarks **against TypeSafe Jev** | The cheap/expensive dual-run pair already exists |

The kicker: it benchmarks against Jev. Our MarginalGainRouter and the
dual-run lie detector (crush's memo) need exactly two arms — a cheap fast one
and an expensive slow one. **laya is the cheap arm; Jev is the expensive arm;
the lie detector (mean realized Δ among declined escalations) becomes
measurable in milliseconds.**

## Concrete wiring (the build order this implies)

1. **W1 — `LayaEvaluator` backend** in `executor/evaluator.py`: typed questions
   (correct? complete? honest? refusal-worthy?) as laya `score`/`noul` calls;
   fallback chain laya → heuristics → LLM judge, each fallback receipted.
2. **W2 — fast prior for the bandit**: laya Router proposals warm-start
   Thompson arms; slow ground truth (tests, judge) still does the updating.
   System-1 proposes, System-2 disposes, receipts arbitrate.
3. **W3 — fleet_router LP features**: laya's per-task typed scores become
   utility features in the cuOpt-style 0-1 LP (task fitness per provider).
4. **W4 — perception at machine speed**: the 4h cron tick (15:53) becomes
   cheap enough to run every few minutes; TICK rows now carry ms latencies —
   **time-as-first-class**: the reflex table gains a latency column, MOTH
   models the temporal patterns of when quality degrades (seasons).
5. **W5 — JEV/MOTH as hyper-intelligence tooling**: Jev as the expensive arm
   in dual-runs; MOTH as the seasonal router (which task_types degrade in
   which conditions); their relational wiring = the router's feature graph.

## The competition structure (Casey 15:36)

- Lane L1 (subagent): read laya source (`laya/quilt.py`, `docs/QUILT.md`,
  `presets.py`, `router.py`, `agent.py`) → integration spec + runnable demo
  against quilt-executor's evaluator interface.
- Lane C1 (crush): receipts-doctrine critique — where does a 33ms
  properly-scored System-1 organ *lie*? What censors? What does its REFUSAL
  row look like? What must never be delegated to it?
- SWAP: L1 play-tests C1's memo; C1 play-tests L1's demo. Iterate.
- Scout lane: org repos (last 14 days) + cutting-edge externals for hidden
  tooling feeding the same four layers.

## What I refuse to claim

That laya replaces the LLM judge. Proper scoring constrains the scorer's
incentive, not the world's messiness — ambiguous tasks stay judge-shaped.
And 33ms decisions over 512-token contexts can't see a 5k-line diff. The
homology is real; the hierarchy (fast proposes, slow disposes) is the point,
not the speed.
