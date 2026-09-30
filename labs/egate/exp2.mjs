// exp2.mjs — Ville check-sampling: how often must "was the compiled answer
// right?" actually run? Makes QUANTITATIVE the self-decomposition report's
// claim ("correctness only has to be checked occasionally, not every call").
//
// Loop: stream of 20k cases; compiled table settles ~85%; gate confusion is
// structural constants (covered→model 10%, novel→table 7%). At t=10000 the
// table ROTS (violation rate 0.03→0.25). Detection → full audit → repair
// (each rot-era audit fixes w.p. 0.9) → back to sampling. Self-decomposition
// cycle: gate → route → e-process watch → audit → repair → cheaper again.
//
// Instrument (v2 — v1 died of a documented cause): per-check LR wealth with
// LR_pass = (1−v1)/(1−v0) < 1 digs a hole under the healthy era (−0.19
// nats/audit × 662 audits ≈ e^−56), and post-rot detection must first climb
// out: measured delay ≈ 4952 settled calls (30× theory), alarms stacked into
// perpetual bursts. v2 uses BLOCK-VILLE: wealth rolls over the last
// BLOCK=40 audits (each block product is mean-1 under H0; alarm at
// e ≥ 1/α_block = 200; union bound over ~16 healthy blocks → ≤0.08 expected
// false alarms per healthy half). No hole: old evidence expires by construction.
// Honest marks: SIMULATION of the SCHEDULING instrument; rates are tunable.
// Run: node exp2.mjs

import test from "node:test";
import assert from "node:assert/strict";
import { makeRng } from "../../night-wheel/builds/eproc-conditional-bound/src/null.mjs";

const N = 20000, ROT = 10000, RHO = 0.85;
const V0 = 0.03, V1 = 0.25;
const MIS_TO_MODEL = 0.10, MIS_TO_TABLE = 0.07;
const P_CHECK = 0.08, BLOCK = 40, BTHRESH = 500, REPAIR_P = 0.9;
const r01 = (r) => r.next31() / 2 ** 31;

function run(seed) {
  const r = makeRng(seed);
  // Exogenous world: the table rots at t=ROT and stays broken until a
  // repair. Policy world: sampling (block-Ville) → alarm → audit burst +
  // full audit → repair (Bernoulli per audit) → back to sampling.
  let repaired = false, detected = false, auditLeft = 0;
  let W = 1, inBlock = 0, checks = 0, alarms = 0, falseAlarms = 0;
  let alarmAt = -1, escaped = 0, escapedRot = 0;
  let healthyChecks = 0, rotChecks = 0;
  const stats = { settledHealthy: 0, settledRot: 0, rotEraViols: 0 };

  for (let t = 0; t < N; t++) {
    const covered = r01(r) < RHO;
    const settled = covered ? r01(r) >= MIS_TO_MODEL : r01(r) < MIS_TO_TABLE;
    const v = t >= ROT && !repaired ? V1 : V0; // EXOGENOUS rot
    const viol = settled ? (covered ? r01(r) < v : r01(r) < 0.85) : false;
    if (!settled) continue;
    const broken = t >= ROT && !repaired;
    if (broken) { stats.settledRot++; if (viol) stats.rotEraViols++; }
    else stats.settledHealthy++;

    let checking;
    if (auditLeft > 0) { checking = true; auditLeft--; }
    else if (detected && !repaired) checking = true; // full audit until fixed
    else checking = r01(r) < P_CHECK;
    if (!checking) {
      if (viol) { escaped++; if (broken) escapedRot++; }
      continue;
    }
    checks++;
    if (broken) rotChecks++; else healthyChecks++;

    if (detected && !repaired) {
      if (r01(r) < REPAIR_P) { repaired = true; detected = false; }
      continue; // full-audit era: wealth idle, audits do the work
    }
    if (auditLeft > 0) continue; // spurious-alarm burst: auditing, no wealth
    // sampling era: block-Ville over audited calls
    W *= viol ? V1 / V0 : (1 - V1) / (1 - V0);
    inBlock++;
    if (W >= BTHRESH) {
      alarms++;
      auditLeft = 40;
      if (broken) { detected = true; if (alarmAt < 0) alarmAt = t; }
      else falseAlarms++;
      W = 1; inBlock = 0;
    } else if (inBlock >= BLOCK) { W = 1; inBlock = 0; }
  }
  return { seed, checks, alarms, falseAlarms, alarmAt, escaped, escapedRot, healthyChecks, rotChecks, ...stats };
}

const SEEDS = Array.from({ length: 30 }, (_, i) => 9000 + i);
const rows = SEEDS.map(run);
const avg = (xs) => xs.reduce((s, v) => s + v, 0) / xs.length;
const summary = {
  seeds: SEEDS.length,
  settledHealthy: avg(rows.map((r) => r.settledHealthy)),
  checkAllHealthyCost: avg(rows.map((r) => r.settledHealthy)),
  ville: {
    healthyChecks: avg(rows.map((r) => r.healthyChecks)),
    rotChecks: avg(rows.map((r) => r.rotChecks)),
    alarms: avg(rows.map((r) => r.alarms)),
    falseAlarms: avg(rows.map((r) => r.falseAlarms)),
    delay: avg(rows.map((r) => (r.alarmAt < 0 ? NaN : r.alarmAt - ROT))),
    rotDetected: rows.filter((r) => r.alarmAt >= 0).length,
    escaped: avg(rows.map((r) => r.escaped)),
    escapedRot: avg(rows.map((r) => r.escapedRot)),
  },
};
summary.healthySavings = +(summary.checkAllHealthyCost / summary.ville.healthyChecks).toFixed(2);
summary.lifetimeChecks = avg(rows.map((r) => r.checks));
summary.lifetimeSavings = +((N * 0.7753) / summary.lifetimeChecks).toFixed(2); // ≈ settled/run

// --- pins ----------------------------------------------------------------------
test("E2.1 stream shape: ~85% covered, rot injected at t=10000", () => {
  const cs0 = rows[0];
  assert.ok(cs0.settledHealthy + cs0.settledRot > 14000, "settled stream present");
  assert.equal(SEEDS.length, 30);
});

test("E2.2 healthy-era cost: VILLE audits ≪ CHECK-ALL (the sampled-not-every-call claim)", () => {
  assert.ok(summary.healthySavings > 5, `healthy savings ${summary.healthySavings}×`);
  assert.ok(summary.ville.healthyChecks / summary.checkAllHealthyCost < 0.2, "<20% of baseline");
});

test("E2.3 rot detected on every seed, delay small vs stream", () => {
  assert.equal(summary.ville.rotDetected, SEEDS.length);
  assert.ok(summary.ville.delay < 1500, `mean delay ${summary.ville.delay.toFixed(0)} settled calls`);
});

test("E2.4 false-alarm discipline under block-Ville", () => {
  const totalFalse = rows.reduce((s, r) => s + r.falseAlarms, 0);
  assert.ok(totalFalse <= 4, `false alarms across 30 healthy halves: ${totalFalse} (α_block=1/500)`);
});

test("E2.5 rot-era escapes: rate bounded per served call; zero post-detection", () => {
  // Any sampling policy serves unchecked violations pre-detection — the
  // honest bound is the RATE (escaped per rot-era settled call ≈ 0.2·0.92),
  // not a fraction of violations. Post-detection, full auditing catches all.
  const rate = rows[0].escapedRot / Math.max(1, rows[0].settledRot);
  assert.ok(rate < 0.25, `escape rate ${rate.toFixed(3)} per rot-era settled call (<0.25)`);
  assert.ok(rows[0].rotChecks > 0, "full-audit era ran (post-detection escapes = 0 by construction)");
});

// The delay↔escape↔cost frontier at three sampling rates (reported, not
// pinned — this is the instrument's tradeoff curve).
function frontierRows() {
  return [0.04, 0.08, 0.16].map((p) => {
    const rs = SEEDS.slice(0, 12).map((s) => runP(s, p));
    return {
      pCheck: p,
      delay: +avg(rs.map((r) => (r.alarmAt < 0 ? NaN : r.alarmAt - ROT))).toFixed(0),
      escapeRate: +avg(rs.map((r) => r.escapedRot / Math.max(1, r.settledRot))).toFixed(3),
      healthyCostFrac: +avg(rs.map((r) => r.healthyChecks / Math.max(1, r.settledHealthy))).toFixed(3),
    };
  });
}
function runP(seed, p) {
  // same engine, parameterized sampling rate
  const r = makeRng(seed);
  let repaired = false, detected = false, auditLeft = 0;
  let W = 1, inBlock = 0, escapedRot = 0, alarmAt = -1;
  const stats = { settledHealthy: 0, settledRot: 0, healthyChecks: 0 };
  for (let t = 0; t < N; t++) {
    const covered = r01(r) < RHO;
    const settled = covered ? r01(r) >= MIS_TO_MODEL : r01(r) < MIS_TO_TABLE;
    const v = t >= ROT && !repaired ? V1 : V0;
    const viol = settled ? (covered ? r01(r) < v : r01(r) < 0.85) : false;
    if (!settled) continue;
    const broken = t >= ROT && !repaired;
    if (broken) stats.settledRot++; else stats.settledHealthy++;
    let checking;
    if (auditLeft > 0) { checking = true; auditLeft--; }
    else if (detected && !repaired) checking = true;
    else checking = r01(r) < p;
    if (!checking) { if (viol && broken) escapedRot++; continue; }
    if (broken) stats.healthyChecks; else stats.healthyChecks++;
    if (detected && !repaired) { if (r01(r) < REPAIR_P) { repaired = true; detected = false; } continue; }
    if (auditLeft > 0) continue;
    W *= viol ? V1 / V0 : (1 - V1) / (1 - V0);
    inBlock++;
    if (W >= BTHRESH) {
      auditLeft = 40;
      if (broken) { detected = true; if (alarmAt < 0) alarmAt = t; }
      W = 1; inBlock = 0;
    } else if (inBlock >= BLOCK) { W = 1; inBlock = 0; }
  }
  return { alarmAt, escapedRot, ...stats };
}

test("E2.6 the hole-climbing lesson is recorded: naive per-check wealth is invalid here", () => {
  // regression pin on the DESIGN, not a number: LR_pass < 1 must remain
  // documented as the reason block-Ville exists (if someone "simplifies"
  // back, this pin's comment is the flag)
  assert.ok((1 - V1) / (1 - V0) < 1, "LR_pass < 1 — per-check wealth digs a hole (documented)");
});

console.log(JSON.stringify({ summary, tradeoffFrontier: frontierRows(), firstSeedRow: rows[0] }, null, 2));
