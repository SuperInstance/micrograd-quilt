#!/usr/bin/env bash
# pins_spec_prereg.sh — FAIL-first pins for tools/spec_prereg.py
# Negative pins (P2,P4..P7) demonstrate RED on the REAL tool by design
# (refusal/breach paths). P9 is the canary: a chain-check-disabled copy of the
# tool must turn P7 RED — a pin that cannot fail is worse than no pin.
set -u
cd "$(dirname "$0")/.."
TOOL=tools/spec_prereg.py
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "PASS $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL $1 — $2"; }

cat > "$T/spec.json" <<'EOF'
{"spec": "pins.demo.invariants", "version": 1,
 "invariants": [
   {"id": "demo-floor", "metric": "demo value", "floor": ">= 2"},
   {"id": "demo-ceiling", "metric": "demo value", "floor": "<= 9"}]}
EOF

# P1 seal -> check roundtrip green
OUT=$(python3 "$TOOL" seal "$T/spec.json" --ledger "$T/l.jsonl" --note pins) \
  && echo "$OUT" | grep -q SEALED \
  && OUT2=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/l.jsonl") \
  && echo "$OUT2" | grep -q GREEN \
  && ok P1 || bad P1 "roundtrip not green: $OUT / $OUT2"

# P2 tampered spec -> BREACH exit 1 naming divergence
sed -i 's/>= 2/>= 5/' "$T/spec.json"
OUT=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/l.jsonl"); RC=$?
[ $RC -eq 1 ] && echo "$OUT" | grep -q "matches NO seal row" \
  && ok P2 || bad P2 "tamper not caught: rc=$RC $OUT"
sed -i 's/>= 5/>= 2/' "$T/spec.json"

# P3 canon reorder-stable: reversed top-level key order -> same seal matches
python3 - "$T/spec.json" <<'EOF'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
d2={"invariants": d["invariants"], "version": d["version"], "spec": d["spec"]}
json.dump(d2, open(p,"w"), indent=3)
EOF
OUT=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/l.jsonl") \
  && echo "$OUT" | grep -q GREEN \
  && ok P3 || bad P3 "reordered spec should still match seal: $OUT"

# P4 array-order sensitive: swap invariant array order -> different spec_sha
python3 - "$T/spec.json" <<'EOF'
import json,sys
p=sys.argv[1]; d=json.load(open(p))
d["invariants"]=[d["invariants"][1],d["invariants"][0]]
json.dump(d, open(p,"w"))
EOF
OUT=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/l.jsonl"); RC=$?
[ $RC -eq 1 ] && ok P4 || bad P4 "array reorder must diverge: rc=$RC $OUT"

# P5 missing ledger -> REFUSED exit 2
OUT=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/absent.jsonl"); RC=$?
[ $RC -eq 2 ] && echo "$OUT" | grep -q REFUSED \
  && ok P5 || bad P5 "missing ledger not refused: rc=$RC $OUT"

# P6 unparseable spec -> REFUSED exit 2, ledger NOT created
echo '{broken' > "$T/bad.json"
OUT=$(python3 "$TOOL" seal "$T/bad.json" --ledger "$T/l6.jsonl"); RC=$?
[ $RC -eq 2 ] && [ ! -e "$T/l6.jsonl" ] && echo "$OUT" | grep -q REFUSED \
  && ok P6 || bad P6 "bad spec not refused or ledger polluted: rc=$RC $OUT"

# P7 chain tamper -> verify names the LINE
cp "$T/l.jsonl" "$T/l7.jsonl"
python3 - "$T/l7.jsonl" <<'EOF'
import sys
p=sys.argv[1]; lines=open(p).readlines()
row=lines[0]
lines[0]=row.replace('"note": "pins"','"note": "PINSPINSP"')
open(p,"w").writelines(lines)
EOF
OUT=$(python3 "$TOOL" verify --ledger "$T/l7.jsonl"); RC=$?
[ $RC -eq 1 ] && echo "$OUT" | grep -q "line 1" \
  && ok P7 || bad P7 "chain tamper not named: rc=$RC $OUT"

# P8 duplicate seal -> REFUSED, ledger stays 1 row
python3 "$TOOL" seal "$T/spec.json" --ledger "$T/l8.jsonl" >/dev/null
OUT=$(python3 "$TOOL" seal "$T/spec.json" --ledger "$T/l8.jsonl"); RC=$?
[ $RC -eq 2 ] && [ "$(wc -l < "$T/l8.jsonl")" -eq 1 ] \
  && echo "$OUT" | grep -q "already sealed" \
  && ok P8 || bad P8 "duplicate seal not refused: rc=$RC $OUT"

# P9 CANARY RED: chain-verify-disabled tool copy must go RED here.
# Demonstrated RED state: pin expectation (rc=1 on tampered ledger) FAILS
# against the broken copy — proof P7 is non-decorative.
python3 - "$TOOL" "$T/brokentool.py" <<'EOF'
import sys
src=open(sys.argv[1]).read()
broken=src.replace(
  '        if got != expected:',
  '        if False:  # CANARY: comparison disabled')
assert broken != src, "canary patch did not apply"
open(sys.argv[2],"w").write(broken)
EOF
cp "$T/l7.jsonl" "$T/l9.jsonl"
OUT=$(python3 "$T/brokentool.py" verify --ledger "$T/l9.jsonl"); RC=$?
if [ $RC -eq 0 ]; then
  echo "canary RED demonstrated: chain-disabled copy exits 0 on tampered ledger (pin expectation rc=1 fails against it)"
  OUT=$(python3 "$TOOL" verify --ledger "$T/l9.jsonl"); RC=$?
  [ $RC -eq 1 ] && ok P9 || bad P9 "real tool did not catch tampered ledger: rc=$RC $OUT"
else
  bad P9 "broken tool already refuses — canary mutation ineffective: rc=$RC $OUT"
fi

echo "----"
echo "pins_spec_prereg: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
