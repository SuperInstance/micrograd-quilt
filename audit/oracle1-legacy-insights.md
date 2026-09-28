# LEGACY-INSIGHTS — oracle1-workspace → today
*Scout: kimi1 · 2026-09-26 · sources: /tmp/o1w clone (332MB, older-generation fleet archive)*

## The 10 insights that survive

1. **Query the substrate, don't rebuild it** (`lessons/the-oom-that-wasnt.md`). A subagent OOM-killed parsing 1,276 MIDI files that PLATO had already decomposed into rooms. Lesson: "The shell knows what the claw needs." → TODAY: before any fleet build, query tidepool / quilt WAL / receipts / existing tiles first. Violation is still our #1 waste mode.
2. **The gauge that couldn't cross** (`ai-writings/THE-GAUGE-THAT-COULDN'T-CROSS.md`). Identical math, two formats, misalignment "exactly the distance between two engineers who never met." → TODAY: receipts v1/v2, jev states, tidepool row shapes, quilt WAL — same bridge-gap disease, quarter-inch adapters everywhere, nobody measuring them.
3. **Synergy discipline** (`fleet-synergies.md`): every module should ride an existing published package (tensor-spline, plato-types, plato-sdk) instead of re-implementing. Written as "SYNERGY: same lattice. Import, don't rebuild." → TODAY: cortex moth + jev receipts + tidepool clients each reinvent packet/row shapes.
4. **Lock Algebra** (`docs-lock-algebra-synthesis.md`): a lock L=(T,O,C) = trigger pattern, opcode mapping, consistency predicate; composition theorems for sequential/parallel/conditional. → TODAY: a jev-quilt receipt IS a lock (trigger=decision, opcode=state transition, consistency=validate_receipt). We have the instances, lack the algebra.
5. **Six-Plane Stack** (`docs-paper-abstraction-planes.md`): agents degrade non-linearly outside their native plane (Intent/Domain/IR/Bytecode/Native/Metal); "an agent should inhabit one plane." → TODAY: subagent task design (moth scientists drifted between planes mid-experiment; plane-stamped task templates would prevent it).
6. **The on-ramp gap** (`ROADMAP-2026-H2.md` Milestone 1.2, dated 2026-05-13): "5-minute newcomer demo — curl|bash → local PLATO room → live tiles." **Never built.** → TODAY: the quilt ecosystem has 30+ deployed sites and still no 5-minute join path. The milestone is 4.5 months overdue.
7. **"22 papers nobody read"** (ROADMAP exec summary). → TODAY: ai-writings canon has thousands of pieces; the cure isn't more writing, it's machine-checkable canon — canon-or-it-didn't-happen receipts. (Our current doctrine is the right evolution; keep it.)
8. **Health dashboard for services** (ROADMAP Milestone 1.3; taskboard "fleet dashboard cron job — run every hour" still 🟡 medium): 9 systemd services, no unified status. → TODAY: we have no dashboard for PR CI / CF deploys / broken links / subagent lanes. I did tonight's CF sweep BY HAND.
9. **Secret-scanning-zero as Day-1 milestone** (ROADMAP Milestone 1.1). → TODAY: still live — credentials in git history blocked pushes for 12 days then; we handled credential material in chat tonight with no scanning tool. Institutionalize.
10. **Taskboard discipline with owner + verification per item** (`taskboard.md`: "Wire AI Director… — Navigator assigned", each item has owner + verification). → TODAY: our open-TODO lists are good, but items lack owners and verification steps; adopt the format.

## 5 concrete repo improvements (ranked)

1. **quilt-cortex moth.mjs — measured bugs from Scientist A's lane (filed as issue).** `persist()` crashes when cachePath dir missing (no mkdir -p); cache rewrite is O(n²) JSON (20k packets = 9 min disk vs 2.6s memory); `weightedQuantumPick` reuses `floats[0]` for both proposal steering and acceptance — an entanglement bug.
2. **jev-quilt — receipts as locks.** Formalize `validate_receipt` as a consistency predicate C with sequential/parallel composition from Lock Algebra; gives free property: composed receipts compose their proofs.
3. **quilt-studio — plane-stamped packages.** Mark each package's native plane (floor=IR, view=Domain/IR, commensurate=Domain math, twistfield=Domain physics); subagents and newcomers stop operating at the wrong plane.
4. **tidepool — SDK-shaped client.** One client module shared by cortex/jev/hermit (legacy lesson: "all PLATO interaction should go through plato_sdk"), instead of three hand-rolled fetch shapes.
5. **quilt-show — E5 "The Gauge" episode.** The quarter-inch adapter story, told with a real cross-repo format-diff instrumented live (receipt v1 vs v2 vs tidepool row, one canonical bridge shown).

## 5 missing tools we would use ourselves (devy, ranked)

| # | Tool | What it does | Home |
|---|------|-------------|------|
| 1 | **gauge** | Cross-repo format conformance linter: parse each repo's receipt/WAL/row shapes, diff them, report quarter-inch misalignments as build failures. Lock Algebra made executable. | NEW REPO `SuperInstance/gauge` |
| 2 | **fleet-lighthouse** | Cron monitor: PR CI status, CF deployment drift (branch vs live), broken links across the 30 sites, tile/canon freshness — one digest to Casey, red-alert on regression. (Resurrects the legacy lighthouse-monitor idea — it scanned, never digested.) | NEW REPO `SuperInstance/fleet-lighthouse` |
| 3 | **quilt-hello** | The 4.5-month-overdue Milestone 1.2: `curl | bash` → local Penrose floor + one agent + one instrument in the browser, <5 min, zero fleet knowledge. | NEW REPO `SuperInstance/quilt-hello` |
| 4 | **receipt-vault** | WAL/receipt replay viewer: walk any jev/quilt history as a room graph with diffs, undo links, proof status. (A2UI-style human walk through receipts.) | NEW REPO `SuperInstance/receipt-vault` |
| 5 | **moth-lab** | The scientist-lane harness, institutionalized: seeded experiments, honest mock labels, negative-result-first reporting, KS tests built in. A/B/C lanes just proved the pattern works — make it rerunnable. | NEW REPO `SuperInstance/moth-lab` |

## The one-line verdict
Oracle1's fleet died of **bridge gaps and missing gauges, not bad math** — and the same disease is our biggest risk today. Build `gauge` and `fleet-lighthouse` first.
