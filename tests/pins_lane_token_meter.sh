#!/usr/bin/env bash
# pins_lane_token_meter.sh — P1-P4 pins for tools/lane-token-meter.py
# Convention (fleet doctrine): FAIL-first. Run with PIN_FAILFIRST=1 to
# demonstrate each pin's RED state, then normal run = all GREEN.
# One demonstrated-RED pin required (Mavis doctrine: a canary that cannot
# fail is worse than no canary). Here P2 is the demonstrated canary.
set -u
METER="$(cd "$(dirname "$0")/.." && pwd)/tools/lane-token-meter.py"
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
export TOKEN_METER_LOG="$T/meter.jsonl"
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1 — $2"; }

# P1: record -> verify OK, totals sum correctly
python3 "$METER" record --lane p1 --model m --input-tokens 100 --output-tokens 50 >/dev/null \
  && python3 "$METER" verify 2>&1 | grep -q "verify OK: 1 lines" \
  && [ "$(python3 "$METER" totals | python3 -c 'import json,sys; print(json.load(sys.stdin)["p1"]["input_tokens"])')" = "100" ] \
  && ok P1 || bad P1 "record/verify/totals broken"

# P2 (CANARY, RED demonstrated): tamper one byte in a recorded line -> verify names the line
python3 "$METER" record --lane p2 --model m --input-tokens 1 --output-tokens 1 >/dev/null
if [ "${PIN_FAILFIRST:-0}" = "1" ]; then
  # RED state: mutate input_tokens in place; verify MUST catch it
  sed -i '2s/"input_tokens": 1,/"input_tokens": 999,/' "$TOKEN_METER_LOG"
  python3 "$METER" verify 2>&1 | grep -q "TAMPER line 2" && ok P2-RED || bad P2-RED "canary did not fire"
  exit $(( FAIL > 0 ? 1 : 0 ))
else
  # normal run: verify chain is intact (line 2 untampered)
  python3 "$METER" verify >/dev/null 2>&1 && ok P2 || bad P2 "chain broken without tamper"
fi

# P3: order-sensitive — appending after a gap in prev is caught (replay a stale line)
python3 "$METER" record --lane p3a --model m --input-tokens 10 --output-tokens 0 >/dev/null
python3 - "$TOKEN_METER_LOG" <<'EOF'
import json, sys
rec = json.loads(open(sys.argv[1]).readline())
rec["note"] = "stale replay"
with open(sys.argv[1], "a") as f:
    f.write(json.dumps(rec) + "\n")
EOF
python3 "$METER" verify 2>&1 | grep -q "TAMPER line" && ok P3 || bad P3 "stale-line replay accepted"

# P4: negative token counts REFUSED, not recorded
python3 "$METER" record --lane p4 --model m --input-tokens -5 --output-tokens 0 >/dev/null 2>&1 \
  && bad P4 "negative counts accepted" || ok P4

echo "-- $PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
