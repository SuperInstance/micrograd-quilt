#!/usr/bin/env node
// Minimal agent-side board reader for the quilt-canvas bridge protocol.
// Sends {type:ready}, receives hello update, sends a VIEW opcode, records
// the update stream to a transcript file with a fnv1a-64 receipt chain.
import net from "node:net";
import fs from "node:fs";

const SOCK = "/tmp/quilt-canvas/socks/live.sock";
const OUT = process.argv[2];
const FNV_PRIME = 435n + (1n << 40n); // matches fleet fnv1a-64 convention
const FNV_OFFSET = 0xcbf29ce484222325n;

function fnv1a64(str) {
  let h = FNV_OFFSET;
  for (let i = 0; i < str.length; i++) {
    h ^= BigInt(str.charCodeAt(i) & 0xff);
    h = (h * FNV_PRIME) % (1n << 64n);
  }
  return h.toString(16).padStart(16, "0");
}

const conn = net.createConnection(SOCK);
const rows = [];
let genesis = "quilt-canvas-board-read-2026-10-03";
let prev = fnv1a64(genesis);
let sawHello = false, sawView = false;

conn.on("connect", () => {
  conn.write(JSON.stringify({ type: "ready", pid: process.pid, role: "agent-board-reader" }) + "\n");
});

conn.on("data", (d) => {
  const lines = d.toString("utf8").split("\n").filter((l) => l.trim());
  for (const ln of lines) {
    let msg; try { msg = JSON.parse(ln); } catch { continue; }
    const payload = JSON.stringify(msg);
    const id = fnv1a64(prev + payload);
    rows.push({ receipt_id: id, prev, n: rows.length, payload: msg });
    prev = id;
    if (msg.type === "update" && msg.hello) sawHello = true;
    if (msg.type === "update" && msg.inspector) sawView = true;
    if (sawHello && sawView) {
      conn.end();
    }
  }
});

conn.on("close", () => {
  fs.writeFileSync(OUT, JSON.stringify({
    genesis,
    rows: rows.length,
    receipts_ok: rows.every((r, i) => r.receipt_id === fnv1a64((i ? rows[i-1].receipt_id : fnv1a64(genesis)) + JSON.stringify(r.payload))),
    saw_hello: sawHello,
    saw_view: sawView,
    chain_tip: prev,
    transcript: rows,
  }, null, 2));
  process.exit(sawHello && sawView ? 0 : 1);
});

conn.on("error", (e) => { console.error("conn error:", e.message); process.exit(2); });

// after hello, send a VIEW opcode
setTimeout(() => {
  if (sawHello) conn.write(JSON.stringify({ type: "opcode", op: "VIEW", cell: "A1", args: {} }) + "\n");
}, 300);
setTimeout(() => { console.error("timeout"); process.exit(3); }, 8000);
