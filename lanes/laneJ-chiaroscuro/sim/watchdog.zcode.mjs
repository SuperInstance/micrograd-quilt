#!/usr/bin/env node
// laneJ-chiaroscuro · P2 Sentinel — Node reproduction of the P1 canvas frame loop
// (sim/phase1_canvas.html) wrapped in a stall watchdog with a 3-tier fallback ladder.
//
// Claim ledger for this file (SPEC.md doctrine — MEASURED vs SIM-TAGGED):
//   MEASURED   : frame/field/render timings, watchdog detection gap + latency,
//                ladder probe durations, recovery interval, receipt rows.
//   SIM-TAGGED : the three fallback tiers. This host has no GPU, no WASM in the
//                loop, and the render path is single-threaded. "GPU[simulated]",
//                "WASM_SIMD[simulated]", "THREADED_SCALAR[simulated]" are LABELS over
//                the same plain-JS renderer; tier ids carry the [simulated] tag inline
//                so no receipt can be read as a real-GPU/WASM/threading claim.
//
// Watchdog shape: a real worker_threads Worker samples a SharedArrayBuffer heartbeat
// (BigInt64 Date.now(), Atomics) every WATCHDOG_SAMPLE_MS. A busy-wait on the main
// thread blocks main-thread timers, so only the concurrent worker can observe the
// gap crossing STALL_THRESHOLD_MS *during* the stall. The worker's detection message —
// never the injector — triggers the fallback ladder and frame resumption.
import { Worker, isMainThread, parentPort, workerData } from 'node:worker_threads';
import { appendFileSync, existsSync, readFileSync } from 'node:fs';

// ---- P1 constants (verbatim from phase1_canvas.html:51) ------------------------
const COLS = 96, ROWS = 42, GLYPHS = "@#W$x*+~-:. ";

// ---- P2 sentinel constants -----------------------------------------------------
const FRAME_MS = 16;               // rAF stand-in pacing
const STALL_THRESHOLD_MS = 1200;   // watchdog fires when frame gap exceeds this
const WATCHDOG_SAMPLE_MS = 25;     // sentinel sample period (worker thread)
const INJECT_AT_TICK = 40;         // SIMULATED stall injection point (proof of detection)
const INJECT_BUSY_MS = 1300;       // busy-wait duration — must exceed STALL_THRESHOLD_MS
const RECOVERY_BUDGET_MS = 1500;   // verdict PASS iff recovery_ms < this
const TOTAL_TICKS = 60;
const RECEIPT_URL = new URL('./watchdog.zcode.jsonl', import.meta.url);
const RECEIPT = RECEIPT_URL.pathname;

// ---- P1 pipeline, ported line-for-line ----------------------------------------
// procedural luma field: layered waves + drifting hotspot "subject" (html:62-74)
function field(t) {
  const f = new Float32Array(COLS * ROWS);
  for (let y = 0; y < ROWS; y++) for (let x = 0; x < COLS; x++) {
    const nx = x / COLS - .5, ny = y / ROWS - .5;
    let v = .5 + .28 * Math.sin(nx * 6 + t * 1.1) * Math.cos(ny * 6 - t * .9);
    v += .18 * Math.sin((nx + ny) * 11 + t * 1.7);
    const hx = .32 * Math.sin(t * .6), hy = .22 * Math.cos(t * .45);
    const d = Math.hypot(nx - hx, ny - hy);
    v += .55 * Math.exp(-d * d * 38);          // the "moving subject"
    f[y * COLS + x] = v;
  }
  return f;
}
// Sobel with clamped boundary sampling (html:75-80)
function sobel(f, x, y) {
  const g = (xx, yy) => f[Math.min(ROWS - 1, Math.max(0, yy)) * COLS + Math.min(COLS - 1, Math.max(0, xx))];
  const gx = (g(x + 1, y - 1) + 2 * g(x + 1, y) + g(x + 1, y + 1)) - (g(x - 1, y - 1) + 2 * g(x - 1, y) + g(x - 1, y + 1));
  const gy = (g(x - 1, y + 1) + 2 * g(x, y + 1) + g(x + 1, y + 1)) - (g(x - 1, y - 1) + 2 * g(x, y - 1) + g(x + 1, y - 1));
  return [Math.hypot(gx, gy), Math.atan2(gy, gx)];
}
// bivariate cell [l,θ,m] → glyph (html:100-106), adaptive throttle (html:88-94)
function renderMatrix(f, t, S, forceStep) {
  let mi = 0;
  if (S.prev) { let s = 0; for (let i = 0; i < f.length; i++) s += Math.abs(f[i] - S.prev[i]); mi = s / f.length; }
  const step = forceStep ?? (mi < 0.02 ? 1 : 2); // reference vs motion: half-res sampling (forceStep: tier probes)
  const out = [];
  for (let y = 0; y < ROWS; y += step) {
    let line = "";
    for (let x = 0; x < COLS; x += step) {
      const [mag, ang] = sobel(f, x, y);
      let l = (f[y * COLS + x] - S.piv) * S.den + S.piv;
      l += S.drift * Math.cos(ang * 2 + t * 2);
      l = Math.min(1, Math.max(0, l));
      const edgeBoost = Math.min(.35, mag * .25);       // edges lean to ramp start
      const idx = Math.min(GLYPHS.length - 1, Math.floor((l + edgeBoost) * GLYPHS.length * .999));
      line += GLYPHS[idx];
    }
    out.push(line);
  }
  return { text: out.join("\n"), meanDelta: mi, ref: step === 1 };
}

// ---- SIM-TAGGED fallback ladder -------------------------------------------------
// Each tier probe does real, timed work; only the GPU tier's *verdict* is a simulated
// decision (the injected stall stands in for a hung render device — no GPU exists on
// this host; SPEC claim-table row "WGSL single-pass Sobel+JEPA on real GPU": UNVERIFIED).
const TIER_PROBE_BUDGET_MS = 25;
function probeRender(t, step) {
  const t0 = performance.now();
  const f = field(t);
  const r = renderMatrix(f, t, { den: 1, piv: .5, drift: 0, prev: null }, step);
  return { ms: performance.now() - t0, cells: r.text.replace(/\s/g, '').length };
}
const TIERS = [
  {
    id: 'GPU[simulated]',
    probe() {
      const t0 = performance.now();
      // SIM: device-lost decision — a label, not a measurement of any GPU.
      return { ok: false, ms: performance.now() - t0, note: 'SIM device-lost (stall stands in for a hung device)' };
    }
  },
  {
    id: 'WASM_SIMD[simulated]',
    probe() {
      const r = probeRender(performance.now() / 1000, 2);   // real half-res render, timed
      return { ok: r.ms < TIER_PROBE_BUDGET_MS, ms: r.ms, note: `real half-res render, ${r.cells} glyph cells; SIMD itself is SIM (plain JS underneath)` };
    }
  },
  {
    id: 'THREADED_SCALAR[simulated]',
    probe() {
      const r = probeRender(performance.now() / 1000, 4);   // real quarter-res render, timed
      return { ok: r.ms < TIER_PROBE_BUDGET_MS, ms: r.ms, note: `real quarter-res render, ${r.cells} glyph cells; threading itself is SIM (single thread)` };
    }
  },
];
function runLadder() {
  const trace = [];
  for (const tier of TIERS) {
    const r = tier.probe();
    trace.push({ tier: tier.id, ok: r.ok, ms: r.ms, note: r.note });
    if (r.ok) return { adopted: tier.id, trace };
  }
  return { adopted: null, trace };   // full descent failure — caller records FAIL
}

// ---- worker branch: the sentinel sampler ----------------------------------------
if (!isMainThread) {
  const hb = new BigInt64Array(workerData.sab);
  let latched = false;
  setInterval(() => {
    const last = Number(Atomics.load(hb, 0));
    if (!last || latched) return;                 // uninitialized heartbeat, or already fired
    const gap = Date.now() - last;
    if (gap > workerData.threshold) {
      latched = true;
      parentPort.postMessage({ type: 'stall', detectedAt: Date.now(), gapAtDetection: gap });
    }
  }, workerData.sample);
  parentPort.on('message', m => { if (m.type === 'rearm') latched = false; });
} else {
  await main();
}

// ---- main thread: frame loop + stall handling ------------------------------------
async function main() {
  if (process.argv.includes('--selftest')) {      // probe all tiers, write no receipts
    console.log('[SELFTEST] tier probes (real timed work, sim-tagged claims):');
    for (const tier of TIERS) {
      const r = tier.probe();
      console.log(`  ${tier.id.padEnd(24)} ok=${r.ok}  ${r.ms.toFixed(3)}ms  ${r.note}`);
    }
    process.exit(0);
  }

  const sab = new SharedArrayBuffer(8);
  const hb = new BigInt64Array(sab);
  let lastBeatWall = Date.now();
  Atomics.store(hb, 0, BigInt(lastBeatWall));      // heartbeat valid before worker starts

  const sentinel = new Worker(new URL(import.meta.url), {
    workerData: { sab, threshold: STALL_THRESHOLD_MS, sample: WATCHDOG_SAMPLE_MS }
  });

  const S = { den: 1, piv: .5, drift: 0, prev: null };
  const stats = { fieldMs: [], renderMs: [], throttleRef: 0, throttleMotion: 0 };
  let tickCount = 0;            // frames successfully delivered (withheld frame not counted)
  let stallHandled = false;
  let activeTier = 'GPU[simulated]';
  let finalVerdict = 'NO_STALL';  // becomes the receipt verdict; drives exit code
  let stallFailsafe = null;       // watchdog-of-the-watchdog: never hang silently

  console.log(`chiaroscuro P2 sentinel boot · ${COLS}x${ROWS} cells · ramp "${GLYPHS}"`);
  console.log(`[SIM] tier ladder: ${TIERS.map(t => t.id).join(' -> ')} — all tiers SIMULATED on this host (SPEC: no GPU/WASM/render threads here)`);

  function busyWait(ms) {
    // Deliberate spin: blocks the main thread AND its timers, so only the worker
    // watchdog can observe the frame gap. This is the simulated device hang.
    const end = Date.now() + ms;
    while (Date.now() < end) { /* spin */ }
  }

  function deliverFrame() {
    const now = performance.now();
    const t = now / 1000;
    const tf0 = performance.now();
    const f = field(t);
    const tf1 = performance.now();
    const tr0 = performance.now();
    const r = renderMatrix(f, t, S);
    const tr1 = performance.now();
    S.prev = f;
    stats.fieldMs.push(tf1 - tf0);
    stats.renderMs.push(tr1 - tr0);
    r.ref ? stats.throttleRef++ : stats.throttleMotion++;
    tickCount++;
    lastBeatWall = Date.now();
    Atomics.store(hb, 0, BigInt(lastBeatWall));   // frame delivered → heartbeat
    return r;
  }

  function scheduleTick() { setTimeout(tickFn, FRAME_MS); }

  function tickFn() {
    if (!stallHandled && tickCount === INJECT_AT_TICK) {
      console.log(`[SIM] tick ${INJECT_AT_TICK}: injecting SIMULATED stall — busy-wait ${INJECT_BUSY_MS}ms, frame ${INJECT_AT_TICK} withheld (no render, no heartbeat, no reschedule)`);
      busyWait(INJECT_BUSY_MS);
      stallFailsafe = setTimeout(() => {          // only reachable if the sentinel failed to detect
        console.log(`[FAIL] sentinel did not detect the ${INJECT_BUSY_MS}ms injected stall within the failsafe window — watchdog broken`);
        sentinel.terminate();
        process.exit(2);
      }, 2000);
      return;                                     // sentinel worker must catch this and drive recovery
    }
    const r = deliverFrame();
    if (tickCount === 1) {
      console.log(`[MEAS] frame 0: ${stats.fieldMs[0].toFixed(2)}ms field + ${stats.renderMs[0].toFixed(2)}ms render — measured, not asserted`);
      console.log(`--- frame 0 viewport (tier ${activeTier}) ---\n${r.text}\n--- end frame 0 ---`);
    }
    if (tickCount >= TOTAL_TICKS) finish();
    else scheduleTick();
  }

  sentinel.on('message', (m) => {
    if (m.type !== 'stall') return;
    if (stallFailsafe) { clearTimeout(stallFailsafe); stallFailsafe = null; }
    const { detectedAt, gapAtDetection } = m;
    const detectedDuringSpin = (detectedAt - lastBeatWall) < INJECT_BUSY_MS;  // true ⇒ worker fired while main was still spinning
    console.log(`[MEAS] STALL DETECTED by sentinel worker: frame gap ${gapAtDetection.toFixed(1)}ms > ${STALL_THRESHOLD_MS}ms threshold${detectedDuringSpin ? ' (detected DURING the busy-wait — concurrent watchdog)' : ''}`);

    const ladder0 = performance.now();
    const { adopted, trace } = runLadder();
    const ladderMs = performance.now() - ladder0;
    for (const s of trace) console.log(`[MEAS] ladder tier ${s.tier}: ok=${s.ok} probe=${s.ms.toFixed(3)}ms — ${s.note}`);
    activeTier = adopted ?? 'NONE';

    setTimeout(() => {                            // resume: deliver the withheld frame
      const recoveredRender0 = performance.now();
      const r = deliverFrame();
      const recoveredRenderMs = performance.now() - recoveredRender0;
      stallHandled = true;

      const stallTotalMs = lastBeatWall - (detectedAt - gapAtDetection);  // last good frame → recovered frame
      const recoveryMs = lastBeatWall - detectedAt;                       // detection → recovered frame
      finalVerdict = recoveryMs < RECOVERY_BUDGET_MS ? 'PASS' : 'FAIL';
      const row = {
        tick: INJECT_AT_TICK,
        stall_ms: Math.round(stallTotalMs * 10) / 10,
        tier: activeTier,
        recovery_ms: Math.round(recoveryMs * 10) / 10,
        verdict: finalVerdict,
      };
      appendFileSync(RECEIPT, JSON.stringify(row) + '\n');
      const totalRows = readFileSync(RECEIPT, 'utf8').split('\n').filter(l => l.trim()).length;

      console.log(`[MEAS] recovery: ladder descent ${ladderMs.toFixed(1)}ms, recovered frame rendered in ${recoveredRenderMs.toFixed(2)}ms on ${activeTier}`);
      console.log(`[MEAS] stall_ms(total frame gap)=${row.stall_ms} · detection gap=${gapAtDetection.toFixed(1)}ms · detection latency from last good frame=${gapAtDetection.toFixed(1)}ms`);
      console.log(`[MEAS] recovery_ms=${row.recovery_ms} (detection → recovered frame, budget ${RECOVERY_BUDGET_MS}ms) → verdict ${finalVerdict}`);
      console.log(`[RECEIPT] ${JSON.stringify(row)} -> ${RECEIPT} (total rows: ${totalRows})`);
      console.log(`--- recovered frame (tick ${INJECT_AT_TICK}, tier ${activeTier}) ---\n${r.text}\n--- end recovered frame ---`);

      sentinel.postMessage({ type: 'rearm' });
      if (tickCount >= TOTAL_TICKS) finish();
      else scheduleTick();
    }, 0);
  });

  function finish() {
    const avg = a => a.reduce((s, v) => s + v, 0) / a.length;
    const max = a => Math.max(...a);
    console.log(`[MEAS] run summary: ${tickCount} frames delivered · field gen avg ${avg(stats.fieldMs).toFixed(3)}ms/frame (max ${max(stats.fieldMs).toFixed(3)}ms) · sobel+glyph render avg ${avg(stats.renderMs).toFixed(3)}ms/frame (max ${max(stats.renderMs).toFixed(3)}ms) · throttle ref/motion ${stats.throttleRef}/${stats.throttleMotion} · final tier ${activeTier} · verdict ${finalVerdict}`);
    sentinel.terminate();
    process.exit(finalVerdict === 'PASS' ? 0 : 1);
  }

  scheduleTick();
}
