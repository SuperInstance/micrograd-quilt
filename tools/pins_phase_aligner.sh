#!/usr/bin/env bash
# pins_phase_aligner.sh — FAIL-first pins for tools/phase_aligner.py
# Every pin names its RED state. Run from repo root: bash tools/pins_phase_aligner.sh
# Note: events must be ONE JSON object per line (JSONL), matching the tool's stdin contract.
set -u
PY=${PYTHON:-python3}
TOOL=tools/phase_aligner.py
PASS=0; FAIL=0

ok()   { PASS=$((PASS+1)); echo "PASS $1"; }
bad()  { FAIL=$((FAIL+1)); echo "FAIL $1 — $2"; }

# --- P1: Law 2 strict arrival order (RED state: consumption order != arrival order)
out=$(printf '%s\n' \
  '{"event_id":"b","lane":"z","arrival_tick":2,"tau":5}' \
  '{"event_id":"a","lane":"m","arrival_tick":1,"tau":5}' | $PY $TOOL tick 3)
order=$(printf '%s\n' "$out" | $PY -c 'import sys,json
print("".join(json.loads(l)["event_id"] for l in sys.stdin if json.loads(l)["row"]=="CLOSED"))' 2>/dev/null)
[ "$order" = "ab" ] && ok P1-order || bad P1-order "got '$order' want 'ab'"

# --- P2: Law 3 over-deadline books REFUSED with reason (RED: event executed anyway / no reason)
out=$(printf '%s\n' '{"event_id":"late","lane":"m","arrival_tick":1,"deadline":2}' | $PY $TOOL tick 5)
n_refused=$(printf '%s\n' "$out" | grep -c '"row": "REFUSED"')
[ "$n_refused" = "1" ] && ok P2-refused-row || bad P2-refused-row "no REFUSED row (out: $out)"
printf '%s\n' "$out" | grep -q '"reason": "over-deadline"' \
  && ok P2-reason-mandatory || bad P2-reason-mandatory "reason missing"
printf '%s\n' "$out" | grep -q '"row": "CLOSED"' \
  && bad P2-not-executed "over-deadline event was CONSUMED" || ok P2-not-executed

# --- P3: Law 1 un-booked fields refused at intake (RED: event with no tau/deadline consumed)
out=$(printf '%s\n' '{"event_id":"ghost","lane":"m","arrival_tick":1}' | $PY $TOOL tick 1)
printf '%s\n' "$out" | grep -q '"reason": "un-booked-fields"' \
  && ok P3-intake-gate || bad P3-intake-gate "un-booked event not refused (out: $out)"
printf '%s\n' "$out" | grep -q '"row": "CLOSED"' \
  && bad P3-not-consumed "un-booked event was CONSUMED" || ok P3-not-consumed

# --- P4: Law 4 REFUSED rows never enter tau (RED: refused cone closed or wrong latency)
out=$(printf '%s\n' \
  '{"event_id":"ok1","lane":"m","arrival_tick":1,"tau":9}' \
  '{"event_id":"late","lane":"m","arrival_tick":1,"deadline":1}' | $PY $TOOL tick 6)
closed=$(printf '%s\n' "$out" | grep '"row": "CLOSED"')
lat=$(printf '%s\n' "$closed" | grep -o '"actual_latency": [0-9]*' | grep -o '[0-9]*')
[ "$lat" = "5" ] && ok P4-tau-excludes-refused || bad P4-tau-excludes-refused "latency '$lat' != 5 (out: $out)"
printf '%s\n' "$closed" | grep -q '"event_id": "late"' \
  && bad P4-refused-not-closed "refused cone leaked into CLOSED" || ok P4-refused-not-closed

# --- P5: receipt chain order-sensitive (RED: same-row chains produce identical tips)
row1=$(printf '%s\n' '{"event_id":"a","lane":"m","arrival_tick":1,"tau":9}' | $PY $TOOL tick 1)
row2=$(printf '%s\n' '{"event_id":"b","lane":"m","arrival_tick":1,"tau":9}' | $PY $TOOL tick 1)
r1=$(printf '%s\n' "$row1" | grep -o '"receipt": "[0-9a-f]*"' | sed 's/.*"\([0-9a-f]*\)"/\1/')
r2=$(printf '%s\n' "$row2" | grep -o '"receipt": "[0-9a-f]*"' | sed 's/.*"\([0-9a-f]*\)"/\1/')
[ -n "$r1" ] && [ -n "$r2" ] && [ "$r1" != "$r2" ] \
  && ok P5-chain-order-sensitive || bad P5-chain-order-sensitive "tips '$r1' vs '$r2'"

echo "---"
echo "pins: $PASS pass / $FAIL fail"
[ "$FAIL" = "0" ]
