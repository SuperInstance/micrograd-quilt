#!/usr/bin/env node
// chiaroscuro P2 "Sentinel" — shared receipt assertions (FAIL-first discipline).
// Reads a watchdog receipt JSONL and asserts the claim-ledger contract:
//   core row:  {tick, stall_ms, tier, recovery_ms, verdict[, signal]}
//   stall_ms   >= 1200        (detector threshold honored — no phantom stalls)
//   0 < recovery_ms < 1500    (spec recovery budget; high-res ms accepted)
//   tier       SIM-tagged     (claim-ledger doctrine: never an untagged GPU claim)
//   verdict    "RECOVERED"    (canonical row law)
// `signal` is an optional dual-signal annotation: "wall" | "gap".
// Usage: node sim/watchdog.assert.kimi.mjs [path-to-jsonl]  (default canonical)
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const target = process.argv[2]
  ?? fileURLToPath(new URL('./watchdog.canonical.jsonl', import.meta.url));

const STALL_THRESHOLD_MS = 1200;
const RECOVERY_BUDGET_MS = 1500;
const INJECTED_TICK = 40;
const TIER_RE = /^(GPU|WASM_SIMD|THREADED_SCALAR)\[SIM\]$/;
const REQUIRED_KEYS = ['recovery_ms', 'stall_ms', 'tick', 'tier', 'verdict']; // sorted core
const OPTIONAL_KEYS = ['signal']; // canonical dual-signal annotation

let checks = 0, failures = 0;
function check(name, cond, detail = '') {
  checks++;
  if (cond) console.log(`PASS ${name}`);
  else { failures++; console.log(`FAIL ${name}${detail ? ' — ' + detail : ''}`); }
}

let text = null;
try { text = readFileSync(target, 'utf8'); }
catch (e) { check('artifact readable', false, `${target}: ${e.code ?? e.message}`); }

const lines = text === null ? [] : text.split('\n').filter(l => l.trim().length > 0);
check('artifact exists and is non-empty', lines.length > 0,
  text === null ? 'file unreadable' : '0 receipt rows');

const rows = [];
let parseOk = lines.length > 0;
for (const [i, l] of lines.entries()) {
  try { rows.push(JSON.parse(l)); }
  catch (e) { parseOk = false; console.log(`FAIL row ${i} parses as JSON — ${e.message}`); checks++; failures++; }
}
if (parseOk) check('every row parses as JSON', true);
else check('every row parses as JSON', false, 'see row errors above');

let shapeOk = rows.length > 0, stallOk = rows.length > 0,
    recoveryOk = rows.length > 0, tierOk = rows.length > 0,
    verdictOk = rows.length > 0, noRealGpuClaim = true;
for (const [i, r] of rows.entries()) {
  const keys = Object.keys(r).sort();
  const unknown = keys.filter(k => !REQUIRED_KEYS.includes(k) && !OPTIONAL_KEYS.includes(k));
  const missing = REQUIRED_KEYS.filter(k => !keys.includes(k));
  const optionalBad = keys.filter(k => OPTIONAL_KEYS.includes(k) && !['wall', 'gap'].includes(r[k]));
  if (unknown.length || missing.length || optionalBad.length) {
    shapeOk = false;
    console.log(`  row ${i}: bad keys [${keys}] — core [${REQUIRED_KEYS}], optional ${OPTIONAL_KEYS}{wall,gap}` +
      (unknown.length ? ` unknown=${unknown}` : '') + (missing.length ? ` missing=${missing}` : '') +
      (optionalBad.length ? ` bad_optional=${optionalBad}` : ''));
  }
  if (!(Number.isFinite(r.tick) && r.tick >= 0)) shapeOk = false;
  if (!(Number.isFinite(r.stall_ms) && r.stall_ms >= STALL_THRESHOLD_MS)) {
    stallOk = false;
    console.log(`  row ${i}: stall_ms=${r.stall_ms} < ${STALL_THRESHOLD_MS} (phantom stall or broken detector)`);
  }
  if (!(Number.isFinite(r.recovery_ms) && r.recovery_ms > 0 && r.recovery_ms < RECOVERY_BUDGET_MS)) {
    recoveryOk = false;
    console.log(`  row ${i}: recovery_ms=${r.recovery_ms} outside (0, ${RECOVERY_BUDGET_MS})`);
  }
  if (!(typeof r.tier === 'string' && TIER_RE.test(r.tier))) {
    tierOk = false;
    console.log(`  row ${i}: tier=${JSON.stringify(r.tier)} not SIM-tagged (GPU|WASM_SIMD|THREADED_SCALAR)[SIM]`);
  }
  if (r.tier === 'GPU') noRealGpuClaim = false; // claim-ledger guard, explicit
  if (r.verdict !== 'RECOVERED' && r.verdict !== 'PASS') {
    verdictOk = false;
    console.log(`  row ${i}: verdict=${JSON.stringify(r.verdict)}`);
  }
}
check('every row has exactly {tick, stall_ms, tier, recovery_ms, verdict}', shapeOk);
check(`every row: stall_ms >= ${STALL_THRESHOLD_MS}`, stallOk);
check(`every row: 0 < recovery_ms < ${RECOVERY_BUDGET_MS}`, recoveryOk);
check('every row: tier is SIM-tagged (claim-ledger doctrine)', tierOk);
check('no row claims a real (untagged) GPU', noRealGpuClaim);
check('every row: verdict is RECOVERED/PASS', verdictOk);
check(`at least one receipt for the injected stall at tick ${INJECTED_TICK}`,
  rows.some(r => r.tick === INJECTED_TICK));

console.log(`RESULT: ${failures === 0 ? 'GREEN' : 'RED'} — ${checks - failures}/${checks} checks passed (${target})`);
process.exit(failures === 0 ? 0 : 1);
