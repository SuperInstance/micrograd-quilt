#!/usr/bin/env node
// P2 Sentinel receipt gate — FAIL-first contract check for sim/watchdog.zcode.jsonl.
// Written BEFORE the implementation (TDD/RED discipline): run this against a
// missing/empty artifact to see it fail, then implement until green.
//
// Contract (from the lane task + SPEC.md claim ledger):
//   - one JSON object per line, append-only
//   - each row has exactly the keys {tick, stall_ms, tier, recovery_ms, verdict}
//   - tick: integer >= 0
//   - stall_ms: finite number > 1200 (the watchdog detection threshold)
//   - tier: one of the SIMULATED fallback tiers, sim-tagged inline —
//     GPU[simulated] | WASM_SIMD[simulated] | THREADED_SCALAR[simulated]
//     (claim-ledger doctrine: untagged GPU/WASM/thread labels are forbidden)
//   - recovery_ms: finite number in [0, 1500)
//   - verdict: "PASS"
//   - at least one row from the injected stall at tick 40
import { readFileSync, existsSync } from 'node:fs';

const file = new URL('./watchdog.zcode.jsonl', import.meta.url);
const TIER_RE = /^(GPU|WASM_SIMD|THREADED_SCALAR)\[simulated\]$/;
const STALL_THRESHOLD_MS = 1200;
const RECOVERY_BUDGET_MS = 1500;
const INJECT_TICK = 40;
const KEYS = ['tick', 'stall_ms', 'tier', 'recovery_ms', 'verdict'];

let checks = 0, fails = 0;
function ck(name, cond, detail) {
  checks++;
  const line = `${cond ? '  ok   ' : '  FAIL '}${name}${detail ? ' — ' + detail : ''}`;
  console.log(line);
  if (!cond) fails++;
}

if (!existsSync(file)) {
  console.log(`RED: artifact missing: ${file.pathname}`);
  console.log(`ASSERTIONS 0/1 PASS — no receipt artifact to check (this is the failing state)`);
  process.exit(1);
}

const raw = readFileSync(file, 'utf8');
ck('artifact non-empty', raw.trim().length > 0, `${raw.length} bytes`);
ck('artifact newline-terminated', raw.endsWith('\n'));

const lines = raw.split('\n').filter(l => l.trim().length > 0);
let rows = [];
let jsonOk = true;
for (const l of lines) {
  try { rows.push(JSON.parse(l)); }
  catch (e) { jsonOk = false; console.log(`  FAIL unparseable line: ${l.slice(0, 80)} — ${e.message}`); }
}
ck('every line is valid JSON', jsonOk, `${rows.length} row(s)`);
ck('at least one receipt row', rows.length >= 1);

for (let i = 0; i < rows.length; i++) {
  const r = rows[i];
  const tag = `row[${i}]`;
  ck(`${tag} exact key set`,
     Object.keys(r).length === KEYS.length && KEYS.every(k => k in r),
     `keys=${JSON.stringify(Object.keys(r))}`);
  ck(`${tag} tick integer >= 0`, Number.isInteger(r.tick) && r.tick >= 0, `tick=${r.tick}`);
  ck(`${tag} stall_ms > ${STALL_THRESHOLD_MS}`,
     typeof r.stall_ms === 'number' && Number.isFinite(r.stall_ms) && r.stall_ms > STALL_THRESHOLD_MS,
     `stall_ms=${r.stall_ms}`);
  ck(`${tag} tier sim-tagged`, typeof r.tier === 'string' && TIER_RE.test(r.tier), `tier=${r.tier}`);
  ck(`${tag} recovery_ms in [0, ${RECOVERY_BUDGET_MS})`,
     typeof r.recovery_ms === 'number' && Number.isFinite(r.recovery_ms) &&
     r.recovery_ms >= 0 && r.recovery_ms < RECOVERY_BUDGET_MS,
     `recovery_ms=${r.recovery_ms}`);
  ck(`${tag} verdict PASS`, r.verdict === 'PASS', `verdict=${JSON.stringify(r.verdict)}`);
}
ck(`injected stall at tick ${INJECT_TICK} present`, rows.some(r => r.tick === INJECT_TICK));

console.log(fails === 0
  ? `ASSERTIONS ${checks}/${checks} PASS — receipt artifact satisfies the contract`
  : `ASSERTIONS ${checks - fails}/${checks} PASS — ${fails} FAILING`);
process.exit(fails === 0 ? 0 : 1);
