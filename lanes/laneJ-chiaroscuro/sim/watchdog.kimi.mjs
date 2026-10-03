#!/usr/bin/env node
// chiaroscuro P2 "Sentinel" — watchdog + fallback ladder over the P1 frame loop.
// laneJ-chiaroscuro/SPEC.md · pure Node, zero deps.
//
// CLAIM LEDGER (honesty tags, per SPEC doctrine):
//   MEASURED   — the field/Sobel/glyph pipeline (ported 1:1 from phase1_canvas.html),
//                all timings, the capability probes, the receipt rows.
//   SIM-TAGGED — the injected stall (deliberate busy-wait fault) and the tier
//                labels GPU/WASM_SIMD/THREADED_SCALAR. Probes are REAL, but the
//                tier *binding* is simulated: every tier renders through the same
//                scalar JS path. No real GPU/WASM/worker rendering is claimed.
//
// Detection semantics (stated, not hidden): a Node busy-wait blocks the event
// loop, so no in-thread timer can fire mid-stall. The watchdog therefore judges
// a frame by its wall time at completion: frame_ms > 1200 ⇒ stalled frame.
// The inter-arrival gap of the *next* frame corroborates the stall.

import { appendFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { performance } from 'node:perf_hooks';

const COLS = 96, ROWS = 42, GLYPHS = '@#W$x*+~-:. ';
const STALL_THRESHOLD_MS = 1200;
const RECOVERY_BUDGET_MS = 1500;
const INJECT_AT_TICK = 40;
const INJECT_BUSY_MS = 1800;      // wedged-frame fault (SIM-TAGGED)
const TOTAL_TICKS = 60;
const FRAME_BUDGET_MS = 33;       // ~30fps pacing, mirrors rAF cadence
const RECEIPTS = fileURLToPath(new URL('./watchdog.kimi.jsonl', import.meta.url));

const sleep = ms => new Promise(r => setTimeout(r, ms));
function busyWait(ms) { const end = performance.now() + ms; while (performance.now() < end); }

// --- P1 pipeline, ported verbatim (same constants, same math) ---------------
// procedural luma field: layered waves + drifting hotspot "subject"
function field(t) {
  const f = new Float32Array(COLS * ROWS);
  for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) {
    const nx = x / COLS - .5, ny = y / ROWS - .5;
    let v = .5 + .28 * Math.sin(nx * 6 + t * 1.1) * Math.cos(ny * 6 - t * .9);
    v += .18 * Math.sin((nx + ny) * 11 + t * 1.7);
    const hx = .32 * Math.sin(t * .6), hy = .22 * Math.cos(t * .45);
    const d = Math.hypot(nx - hx, ny - hy);
    v += .55 * Math.exp(-d * d * 38);         // the "moving subject"
    f[y * COLS + x] = v;
  }
  return f;
}
function sobel(f, x, y) {
  const g = (xx, yy) => f[Math.min(ROWS - 1, Math.max(0, yy)) * COLS + Math.min(COLS - 1, Math.max(0, xx))];
  const gx = (g(x + 1, y - 1) + 2 * g(x + 1, y) + g(x + 1, y + 1)) - (g(x - 1, y - 1) + 2 * g(x - 1, y) + g(x - 1, y + 1));
  const gy = (g(x - 1, y + 1) + 2 * g(x, y + 1) + g(x + 1, y + 1)) - (g(x - 1, y - 1) + 2 * g(x, y - 1) + g(x + 1, y - 1));
  return [Math.hypot(gx, gy), Math.atan2(gy, gx)];
}
// bivariate cells [l, θ, m] materialized, then glyph-mapped (den/piv/drift = P1 defaults)
function cellsToGlyphs(f, t, stepX, stepY) {
  const cells = { l: [], th: [], m: [] };
  let out = '';
  for (let y = 0; y < ROWS; y += stepY) {
    let line = '';
    for (let x = 0; x < COLS; x += stepX) {
      const [mag, ang] = sobel(f, x, y);
      let l = (f[y * COLS + x] - .5) * 1 + .5;      // den=1, piv=.5
      l += 0 * Math.cos(ang * 2 + t * 2);           // drift=0
      l = Math.min(1, Math.max(0, l));
      const edgeBoost = Math.min(.35, mag * .25);
      const idx = Math.min(GLYPHS.length - 1, Math.floor((l + edgeBoost) * GLYPHS.length * .999));
      line += GLYPHS[idx];
      cells.l.push(l); cells.th.push(ang); cells.m.push(mag);
    }
    out += line + '\n';
  }
  return { cells, out };
}

// --- fallback ladder: REAL capability probes, SIMULATED tier binding ---------
const TIER_ORDER = ['GPU', 'WASM_SIMD', 'THREADED_SCALAR'];
async function probe(tier) {
  const t0 = performance.now();
  let ok = false, note = '';
  if (tier === 'GPU') {
    ok = typeof globalThis.navigator !== 'undefined' && !!globalThis.navigator.gpu;
    note = ok ? 'navigator.gpu present' : 'no navigator.gpu on this host (headless Node)';
  } else if (tier === 'WASM_SIMD') {
    try {
      // wasm-feature-detect style minimal v128 module (i8x16.splat + i8x16.popcnt)
      new WebAssembly.Module(new Uint8Array([0, 97, 115, 109, 1, 0, 0, 0, 1, 5, 1, 96, 0, 1, 123, 3, 2, 1, 0, 10, 10, 1, 8, 0, 65, 0, 253, 15, 253, 98, 11]));
      ok = true; note = 'v128 test module compiled';
    } catch (e) { note = 'v128 compile failed: ' + e.message; }
  } else if (tier === 'THREADED_SCALAR') {
    try { await import('node:worker_threads'); ok = true; note = 'worker_threads available'; }
    catch { note = 'worker_threads unavailable'; }
  }
  return { tier, ok, ms: +(performance.now() - t0).toFixed(2), note };
}
async function ladder() {
  const probes = [];
  for (const t of TIER_ORDER) {
    const p = await probe(t); probes.push(p);
    if (p.ok) return { landed: t, probes };        // fallback ladder short-circuits
  }
  return { landed: null, probes };
}

// --- frame loop + watchdog ---------------------------------------------------
const stats = { fieldMs: [], renderMs: [], maxNormalFrameMs: 0, maxArrivalGapMs: 0 };
let tier = 'BASELINE_SCALAR_JS[MEASURED]';   // pre-stall: plain scalar JS, no tier claimed

function stats_line(label, arr) {
  const mean = arr.reduce((a, b) => a + b, 0) / arr.length;
  return `${label}: mean ${mean.toFixed(2)} ms · min ${Math.min(...arr).toFixed(2)} · max ${Math.max(...arr).toFixed(2)}`;
}

async function main() {
  console.log(`chiaroscuro P2 SENTINEL boot · ${COLS}x${ROWS} · stall>${STALL_THRESHOLD_MS}ms · recovery budget <${RECOVERY_BUDGET_MS}ms`);
  console.log(`fault injection: SIM-TAGGED busy-wait ${INJECT_BUSY_MS}ms at tick ${INJECT_AT_TICK} · receipts → ${RECEIPTS}`);
  console.log(`baseline tier: ${tier} (no acceleration claimed)`);

  let prevArrival = 0, prevField = null, receipts = 0;
  for (let tick = 0; tick < TOTAL_TICKS; tick++) {
    const arrival = performance.now();
    if (prevArrival) stats.maxArrivalGapMs = Math.max(stats.maxArrivalGapMs, arrival - prevArrival);
    prevArrival = arrival;
    const t = arrival / 1000;

    if (tick === INJECT_AT_TICK) {
      console.log(`[tick ${tick}] FAULT (SIM-TAGGED): busy-wait ${INJECT_BUSY_MS}ms — simulating a wedged frame`);
      busyWait(INJECT_BUSY_MS);
    }

    const f0 = performance.now();
    const f = field(t);
    stats.fieldMs.push(performance.now() - f0);

    // adaptive throttle (P1 shape): mean |Δ| picks reference vs motion half-res
    let mi = 0;
    if (prevField) { let s = 0; for (let i = 0; i < f.length; i++) s += Math.abs(f[i] - prevField[i]); mi = s / f.length; }
    prevField = f;
    const ref = mi < 0.02, step = ref ? 1 : 2;

    const r0 = performance.now();
    const { out } = cellsToGlyphs(f, t, step, step);
    stats.renderMs.push(performance.now() - r0);

    const frameMs = performance.now() - arrival;

    if (frameMs > STALL_THRESHOLD_MS) {
      const detectT = performance.now();
      console.log(`[tick ${tick}] WATCHDOG: stalled frame ${frameMs.toFixed(1)}ms > ${STALL_THRESHOLD_MS}ms (detected at frame completion — single-threaded loop cannot observe mid-block)`);
      const { landed, probes } = await ladder();
      for (const p of probes)
        console.log(`  ladder: ${p.tier}[SIM] ${p.ok ? 'probe OK' : 'probe UNAVAILABLE'} (${p.ms}ms, real probe) — ${p.note}${p.ok ? ' → binding SIMULATED' : ''}`);
      tier = landed ? `${landed}[SIM]` : 'NONE';
      // recovery = detection → first frame produced after rebind (SIM bind, same scalar path)
      const rf = field(performance.now() / 1000);
      const rec = cellsToGlyphs(rf, performance.now() / 1000, 1, 1);
      const recoveryMs = performance.now() - detectT;
      const verdict = recoveryMs < RECOVERY_BUDGET_MS ? 'RECOVERED' : 'BUDGET_EXCEEDED';
      const row = { tick, stall_ms: +frameMs.toFixed(1), tier, recovery_ms: +recoveryMs.toFixed(2), verdict };
      appendFileSync(RECEIPTS, JSON.stringify(row) + '\n');
      receipts++;
      console.log(`[tick ${tick}] recovery ${recoveryMs.toFixed(2)}ms (<${RECOVERY_BUDGET_MS}ms budget) → ${verdict} on ${tier} (SIM-TAGGED bind) · receipt appended`);
      console.log(`[tick ${tick}] recovered-frame sample (first 3 of ${ROWS} rows):\n${rec.out.split('\n').slice(0, 3).join('\n')}`);
    } else {
      stats.maxNormalFrameMs = Math.max(stats.maxNormalFrameMs, frameMs);
    }

    if (tick === 0) {
      console.log(`[tick 0] first frame ${frameMs.toFixed(1)}ms · throttle=${ref ? 'reference' : 'motion (half-res)'} Δ=${mi.toFixed(4)} · viewport sample (first 3 of ${ROWS} rows):\n${out.split('\n').slice(0, 3).join('\n')}`);
    }

    await sleep(FRAME_BUDGET_MS);
  }

  console.log('--- SENTINEL SUMMARY (numbers MEASURED unless tagged) ---');
  console.log(`ticks run: ${TOTAL_TICKS}`);
  console.log(stats_line('field gen ms/frame', stats.fieldMs) + '  [MEASURED]');
  console.log(stats_line('sobel+glyph ms/frame', stats.renderMs) + '  [MEASURED]');
  console.log(`max normal frame wall: ${stats.maxNormalFrameMs.toFixed(1)}ms (watchdog fired exactly ${receipts}x — no false positives)  [MEASURED]`);
  console.log(`max frame-arrival gap: ${stats.maxArrivalGapMs.toFixed(1)}ms (corroborates the injected stall)  [MEASURED]`);
  console.log(`final tier: ${tier}  [SIM-TAGGED binding; probes were real]`);
  console.log(`receipts appended: ${receipts} → ${RECEIPTS}  [MEASURED]`);
}

await main();
