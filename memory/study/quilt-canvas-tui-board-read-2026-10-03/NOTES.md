# quilt-canvas-tui live board read — 2026-10-03 (queue item 5)

Protocol: bridge/controller.mjs unix socket (JSONL, newline-delimited), QUILT_SOCK env.
Controller seeds Fabric with FIXED_6OP script; canvas/agent peers connect, send
{type:ready} -> hello update (full cells+links+ledger), then {type:opcode,op,cell,args}.

Live read executed against /tmp/quilt-canvas (controller pid live, socket socks/live.sock):
- HELLO: tick=1, cells A1 dials[2,1] + B1 dials[2], link A1-B1, ledger ok=true len=7 tip 2af64f84a7d6e0fb
- VIEW A1: inspector {dials:[2,1], neighbors:[B1], version:4, state_digest 129656b79f81c5b3};
  ledger grew to len=8 tip c95230a62b607854 — VIEW seals its own receipt row (verified live)
- Agent-side transcript carries its own fnv1a-64 receipt chain (genesis-anchored, order-sensitive,
  doubt-ledger grammar): 2 rows, recompute-verified ok, tip 9e0affbe16ddcabb

Honest limits: socket is localhost-only filesystem socket with NO auth (controller log says so) —
any local process can emit opcodes; PoEM gate (BIND/LINK/EFFECT/TICK run only if ledger verifies)
is the only mutation guard, FORGET/VIEW direct. Read-only lane, no quilt repo mutated.
Gotcha recorded: cell addrs are A1/B1 style, not "cell0"; my first VIEW returned MISSING_CELL.
