# Codespace Cluster × Quilt Ecosystem — Integration Synthesis
*Author: kimi1 | 2026-09-26 | Casey's order: experiment, determine quilt roles, play, contribute, mature the practice*

Verified hands-on wherever possible (tests actually run, labeled where simulated).
Companion: ability-transfer PR #5 (round 4) — the eighth repo, hands-on lane.

---

## The seven, by capability actually demonstrated

| Repo | Lang | Verified capability | Quilt-ecosystem role verdict |
|------|------|--------------------|------------------------------|
| **git-agent** | Python | 234 tests pass offline in 5s; Bootstrap→Observe→Plan→Execute→Communicate→Reflect lifecycle; career FSM (GrowthStage INITIATE→COMMANDER, gated `check_promotion`); **already POSTs PLATO tiles to :8847 with zero schema validation** | First **quilt-native fleet agent** candidate — its vessel lifecycle events are pre-structured BIND/EFFECT/VIEW/TICK records waiting for an emitter |
| **nexus-git-agent** | TS (CF Worker) | 228-line Worker, 5 vitest green, zero deps; INCREMENTS trust engine for edge nodes (Jetson/ESP32); compiles LLM intents → motor opcodes; **guarded only by JSON.parse** | The org's only live **edge-fleet signal**; trust events belong in the quilt WAL; its reflex dispatch is gauge's first safety-critical customer |
| **git-agent-codespace** | Shell/devcontainer | Ensign factory devcontainer validates (12 tests) | Onboarding surface; keep, low delta |
| **codespace-edge-rd** | Python/docs | 15 doc-tests green; yoke-transfer spec **self-admits "R&D done, time to implement"** — blocked on a yoke format that doesn't exist | Spec capital; the yoke format is a design contribution opportunity, not code yet |
| **codespace-worker** | Bash (~90 lines) | No CI/tests; needs live `gh` auth; emits zero structured records | **Workload donor**: its ephemeral-codespace run lifecycle should emit WAL records; today it's silent |
| **quilt-codespace** | JS | Codespace template running Quilt as token-auth federated runtime | Naming is aspirational today; becomes real once git-agent emits quilt records |
| **ability-transfer** | C | 28/28 C tests; full transfer protocol (OFFER/REQUEST/COMPAT/ADAPT/VERIFY); **round 4 now extracts abilities from real repos, gauge-validated** | The **doctrine layer**: what a shell transfers and how it's verified. Round 4 makes shells bidirectionally verifiable (PR #5) |

---

## The cluster's one-sentence truth

**git-agent is the body, nexus is the senses, ability-transfer is the doctrine, and the quilt kernel is the nervous system they already half-speak.** git-agent POSTs tiles with no schema; nexus moves reflexes with no validation; worker runs fleets with no records. Every gap is the same shape: *events exist, the WAL doesn't receive them, nothing checks them.* That is precisely the quilt kernel's job description.

## Top 3 builds (ranked, evening-scale each)

### 1. Trust-WAL bridge — nexus-git-agent → hermit quilt WAL
- **WHAT EXISTS**: `updateTrust` mutates INCREMENTS scores in the Worker (5 vitest green); hermit tails WAL lines and surfaces them in Discord; hermit's quilt WAL spine is live.
- **WHAT'S MISSING**: any persistence/egress of trust changes; today they vanish at the Worker edge.
- **SMALLEST BUILD**: append a JSONL WAL line per trust change (node, old, new, reason) + optional webhook POST; hermit tails → `#fleet-ops` trust/quarantine events. Immediate ops value, both sides small, only live edge signal in the org.
- **Seam**: BIND (node) / EFFECT (score change) / TICK (epoch).

### 2. Vessel-Quilt emitter — git-agent → quilt WAL
- **WHAT EXISTS**: 234-test lifecycle with career transitions and worklog entries; the 5-opcode kernel is stable; tidepool/hermit/gauge all consume WAL-shaped data but receive fixtures.
- **WHAT'S MISSING**: a mapper from lifecycle events → quilt records. Nothing else — additive module.
- **SMALLEST BUILD**: `git_agent/quilt_emit.py`, behind the existing emitter pattern: lifecycle event → BIND/LINK/EFFECT/VIEW/TICK line appended to `~/.git-agent/quilt.jsonl`. Makes git-agent the first quilt-native agent and feeds tidepool/gauge real data. 1–2 evenings; the 234-test suite is the safety net.
- **Bonus**: career transitions are exactly GrowthStage FSM edges — replayable as a quilt-studio TICK script with a correctness gate.

### 3. Reflex gauge — nexus reflex compiler → gauge schema check
- **WHAT EXISTS**: intents compile to motor opcodes dispatched to ESP32s after only `JSON.parse`; gauge v0.1.0 is a working schema checker needing a real living schema.
- **WHAT'S MISSING**: an op allowlist + arg bounds + mandatory `safety_check` field, validated in-Worker pre-dispatch.
- **SMALLEST BUILD** (sketch, ready to PR when green-lit):

```json
{
  "name": "nexus.reflex",
  "required": ["op", "args", "safety_check", "intent_id", "issued_at"],
  "types": {"op": "string", "args": "object", "safety_check": "object",
            "intent_id": "string", "issued_at": "string"},
  "enums": {"op": ["motor.set_speed", "motor.stop", "servo.set_angle",
                   "sensor.read", "led.set", "reset"]},
  "patterns": {"intent_id": "^[a-z0-9-]{8,64}$"},
  "all_of": [["safety_check.bounds_checked", "safety_check.estop_armed"]]
}
```

- **Why first-class**: this is the first schema that guards *hardware reflexes*, not documents. gauge stops being a linter and starts being a fuse.

---

## Mature practice updates (the meta-lessons)

1. **Verify by running, and say what ran.** git-agent's 234 tests, nexus's 5 vitest, edge-rd's 15 doc-tests, codespace's 12 — all executed by the scout; nothing here is README-verbatim. ability-transfer round 4: 28/28 + 11 assertions executed.
2. **Schemas belong with the producer, not the linter.** Round 4's `.gauge.json` + `schemas/` live in the consumer repo (ability-transfer). Same pattern applies to nexus (reflex schema in nexus) and git-agent (tile schema in git-agent). Gauge PRs being Casey-gated no longer blocks anyone.
3. **The cluster is a workload donor, not just an integration target.** Bottles, vessel events, worker runs, trust deltas — all pre-structured event streams. The quilt kernel's problem was never finding producers; it was that producers were never wired. Wiring IS the remaining work, and it is small.
4. **Doctrine → instrument → CI.** ability-transfer round 4 demonstrates the loop: prose claim (repo = frozen attention field) → measured artifact (probe) → checked receipt (gauge) → regression (make test). Apply the same loop to the yoke format (edge-rd): write the spec's acceptance tests first, then the format.
5. **Safety seam first.** Of all gaps, only reflex dispatch can hurt hardware. Reflex gauge outranks every other build on consequence even though it's hours of work.

## Queued for Casey's word
- Trust-WAL bridge (build 1) — needs hermit tail permissions decision
- Vessel-Quilt emitter (build 2) — additive, lowest risk, feeds everything downstream
- Reflex gauge (build 3) — highest consequence; needs nexus maintainer buy-in (FM)
- ability-transfer PR #5 — awaiting merge
