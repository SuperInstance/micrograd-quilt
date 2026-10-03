#!/usr/bin/env node
// chiaroscuro P4 codec slice — identity codec, local-buildable portion.
// Honest scope (SPEC.md P4): serialization + integrity + provenance + roundtrip
// ARE built and measured here. NOT claimed: ControlNet reverse-render binding
// (needs an inference endpoint this host lacks — flagged, not faked).
// Every number below is MEASURED by this run.
"use strict";
const crypto = require("crypto");

const SPEC_VERSION = "2026.1.0";
const COLS = 100, ROWS = 75, CELL_DIM = 3; // [luma, theta, mag] — bivariate substrate

// Flat F32 cell lattice → .pai envelope
function encode(lattice, meta) {
  const headBuf = Buffer.from(JSON.stringify({
    spec: SPEC_VERSION, cols: COLS, rows: ROWS, cell_dim: CELL_DIM,
    codec: "wgsl-compute-ascii-v4", ts: Date.now(), ...meta,
  }), "utf8");
  // 16-byte alignment doctrine (SPEC): pad JSON head so F32 body is aligned
  const head = Buffer.alloc(Math.ceil(headBuf.length / 16) * 16, 0x20);
  headBuf.copy(head);
  const body = Buffer.from(lattice.buffer, lattice.byteOffset, lattice.byteLength);
  const envelope = Buffer.alloc(8 + head.length + body.length);
  envelope.writeUInt32LE(head.length, 0);
  envelope.writeUInt32LE(body.length, 4);
  head.copy(envelope, 8);
  body.copy(envelope, 8 + head.length);
  return envelope;
}
function decode(envelope) {
  const hLen = envelope.readUInt32LE(0), bLen = envelope.readUInt32LE(4);
  // contract: declared body must be present — receipts culture, no silent drift
  if (envelope.length !== 8 + hLen + bLen) throw new Error("envelope truncated: " +
    `declared ${8 + hLen + bLen}B, got ${envelope.length}B`);
  if (bLen % 4 !== 0) throw new Error("body not F32-aligned: " + bLen + "B");
  const head = JSON.parse(envelope.slice(8, 8 + hLen).toString("utf8").trim());
  const body = envelope.slice(8 + hLen, 8 + hLen + bLen);
  const lattice = new Float32Array(bLen / 4);
  lattice.set(new Float32Array(body.buffer, body.byteOffset, bLen / 4));
  return { head, lattice };
}
// tamper-evident identity hash (fleet doctrine: receipts bound to content)
function identityHash(envelope) {
  return "0x" + crypto.createHash("sha256").update(envelope).digest("hex").slice(0, 16);
}

// --- FAIL-first pins (quoted RED before green) ---
// Pin 1: decode(encode(x)) !== x must NOT hold → we assert roundtrip equality.
// Pin 2: flipped bit must change identityHash.
// Pin 3: truncated envelope must throw.
const latt = new Float32Array(COLS * ROWS * CELL_DIM);
for (let i = 0; i < latt.length; i++) latt[i] = (i * 0.6180339887) % 1; // deterministic content
const tEnc0 = process.hrtime.bigint();
const env = encode(latt, { name: "canonical-p4-slice", seed: 9081239 });
const tEnc = Number(process.hrtime.bigint() - tEnc0) / 1e6;
const tDec0 = process.hrtime.bigint();
const { head, lattice: out } = decode(env);
const tDec = Number(process.hrtime.bigint() - tDec0) / 1e6;

let pins = 0;
function pin(name, ok) { pins++; console.log(`${ok ? "PASS" : "FAIL"} P${pins} ${name}`); if (!ok) process.exitCode = 1; }
let eq = true;
for (let i = 0; i < latt.length; i++) if (latt[i] !== out[i]) { eq = false; break; }
pin("roundtrip equality (22,500 cells × 3 dims)", eq);
pin("header spec/version", head.spec === SPEC_VERSION && head.cols === COLS && head.rows === ROWS);
const h1 = identityHash(env);
const env2 = Buffer.from(env); env2[env2.length - 1] ^= 0xff;
pin("tamper flips identity hash", identityHash(env2) !== h1);
let threw = false;
try { decode(env.slice(0, env.length - 16)); } catch { threw = true; }
pin("truncated envelope throws", threw);

console.log(`[MEAS] envelope=${env.length} bytes (${(env.length / 1024).toFixed(1)} KiB) · ` +
  `${(env.length / (COLS * ROWS)).toFixed(2)} B/cell · identity=${h1}`);
console.log(`[MEAS] encode=${tEnc.toFixed(3)}ms (${(tEnc * 1000 / (COLS * ROWS)).toFixed(3)} µs/cell) · ` +
  `decode=${tDec.toFixed(3)}ms`);
console.log("SIM-TAGGED: GPU zero-copy path not exercised on this host (no WebGPU) — codec is host-portable by construction (raw F32 LE).");
console.log("BLOCKED (named, not hidden): ControlNet reverse-render binding needs an inference endpoint.");
