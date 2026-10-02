# Phase-aligner spec — NETF Tier 2 (async τ-cone discipline for pulses)

Status: SPEC v1, sealed 2026-10-03. Source lane: lanes/ABSTRACTION-LANDING.md Tier 2.
Build target: tools/phase_aligner.py (reference implementation) + tools/pins_phase_aligner.sh.

## Problem

The fleet runs a two-clock system:

- **Synchronous foliation** — the pulse (snowball cron, edge-watch). Strict
  tick, ordered consumption of the queue.
- **Asynchronous cones** — subagent completions, Casey pushes/merges, gateway
  events. Each carries a latency τ relative to the pulse that issued it.

Without a gate, cones collide with the sync tick: on 2026-10-02 a spawn-cone
burst (6 timeouts, 20+ min) coincided with the pulse; the session-registry lock
(held 26974ms) wedged the registry; the compaction crash killed the frame.
Decoherence, receipted.

## Law 1 — every async event carries {arrival_tick, τ, deadline}

- `arrival_tick`: integer pulse tick at which the event was ISSUED (not when it
  lands — landing time is wall-clock noise, arrival is causal).
- `τ`: expected latency class of the cone (seconds, honest estimate, may be
  wrong — being wrong is data, see Law 4).
- `deadline`: `arrival_tick + ceil(τ / tick_period)` in tick units. An event
  MAY carry an explicit absolute deadline instead; explicit beats derived.

Events lacking any of the three fields are not events — they are un-booked
claims and are refused at intake (witness law: the field must be provable).

## Law 2 — the pulse consumes strictly in arrival order

Per tick, the pending buffer is sorted by arrival_tick; ties broken by
issuing-lane name (lexicographic, deterministic). No reordering by urgency,
size, or perceived importance — urgency reordering is how cones collided on
10/2. Strict order, always.

## Law 3 — over-deadline cones book a REFUSED row, never a silent drop

When the pulse reaches an event whose deadline < current tick, the event is
NOT executed. It books a REFUSED row:

```
{"row": "REFUSED", "event_id", "lane", "arrival_tick", "deadline",
 "consumed_tick", "reason": "over-deadline", "detail": "<why it missed>"}
```

- `reason` is MANDATORY and must be one of the sealed vocabulary:
  `over-deadline` | `un-booked-fields` | `cone-violation` | `superseded`.
  Unreasoned refusal = blindness again (doubt-ledger doctrine).
- The row is appended to the tick's receipt chain (fnv1a-64, genesis-anchored,
  order-sensitive — doubt-ledger grammar). A refusal is a receipt, not an
  apology.
- The refused work returns to the QUEUE as a fresh event with a NEW
  arrival_tick if still wanted — it does not resurrect its old cone.

## Law 4 — τ is a prediction; measure it

Every closed cone books a CLOSED row with actual_latency. Per-lane running
{τ_estimate, τ_p50, τ_max} is recomputed at each tick from CLOSED rows only
(REFUSED rows never enter the τ estimator — they are missing data, not slow
data). Estimates that miss by >2× three ticks running are flagged
`cone-violation` on the next refusal of that lane's events.

## Law 5 — the aligner never blocks on a cone

Intake, ordering, refusal, and closing are all in-pulse operations on buffered
state. If a cone has not landed by its deadline, the REFUSED row fires WITHOUT
waiting. Async means async; blocking the foliation on a cone re-creates the
10/2 lock wedge.

## Honest limits (sealed with the spec)

1. Tick granularity is coarse: an event 1ms under deadline and one 1ms over
   are treated identically per tick. Fine-grained fairness is out of scope.
2. τ estimates are lane-level aggregates; individual cones vary. The aligner
   discriminates lanes, not events.
3. The reference implementation is single-process stdlib; the fleet's real
   buffer lives in the queue file + cron, so this tool is the DISCIPLINE made
   executable and testable, not a daemon.
4. `cone-violation` flagging (Law 4) is advisory — it names a lane, it does
   not punish one. Judges of record stay human/ledger, not tooling (KS2 law).

## Failure modes this spec exists to prevent (receipted)

| Incident | Date | What the spec does about it |
|---|---|---|
| Spawn-cone burst wedged registry lock 26974ms | 2026-10-02 | Law 5: no blocking; Law 3: missed cones REFUSED with reason |
| Queued-message backlog delivered as shockwave after the tear | 2026-10-02 | Law 2: strict arrival order, no replay surprises |
| Duplicate-PR collision (two lanes took same queue item) | 2026-10-02 | out of scope here — closed by claim locks (e793b5e) |
| 6 sessions_spawn cones never resolved, ~110 min silent | 2026-10-02 night | Law 4: cones that never close stop poisoning τ estimates after one refusal cycle |

## Pins

tools/pins_phase_aligner.sh — FAIL-first culture; every pin has a named RED
state. Run from repo root.
