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

# P10 unicode roundtrip: CJK + emoji in the spec seal/check GREEN, and a
# CJK --note lands RAW in the ledger row (ensure_ascii=False). Raw matters:
# fleet-witness L1 anchors hash row BYTES — an escaping dump would fork the
# byte convention from canon() and break cross-tool root agreement.
cat > "$T/uni.json" <<'EOF'
{"spec": "pins.unicode", "version": 1,
 "invariants": [
   {"id": "地板-下限", "metric": "数值 🔬", "floor": ">= 2"}]}
EOF
OUT=$(python3 "$TOOL" seal "$T/uni.json" --ledger "$T/l10.jsonl" --note '备注🔬') \
  && OUT2=$(python3 "$TOOL" check "$T/uni.json" --ledger "$T/l10.jsonl") \
  && echo "$OUT2" | grep -q GREEN \
  && python3 - "$T/l10.jsonl" <<'EOF' \
  && ok P10 || bad P10 "unicode roundtrip: $OUT / $OUT2"
import json, sys
raw = open(sys.argv[1], "rb").readline()
assert "备注🔬".encode("utf-8") in raw, "ledger row is not raw UTF-8"
json.loads(raw.decode("utf-8"))  # still parses
EOF

# P11 nested reorder-stable: DEEP object key reorder -> same seal matches
# (P3 covered top-level only; canon sorts recursively).
cat > "$T/deep.json" <<'EOF'
{"spec": "pins.deep", "version": 1,
 "invariants": [
   {"id": "d1", "metric": "m", "floor": ">= 1",
    "meta": {"alpha": 1, "beta": {"x": 2, "y": 3}}}]}
EOF
python3 "$TOOL" seal "$T/deep.json" --ledger "$T/l11.jsonl" --note deep >/dev/null
cat > "$T/deep2.json" <<'EOF'
{"version": 1, "spec": "pins.deep",
 "invariants": [
   {"floor": ">= 1", "id": "d1", "meta": {"beta": {"y": 3, "x": 2}, "alpha": 1},
    "metric": "m"}]}
EOF
OUT=$(python3 "$TOOL" check "$T/deep2.json" --ledger "$T/l11.jsonl") \
  && echo "$OUT" | grep -q GREEN \
  && ok P11 || bad P11 "deep reorder should still match: $OUT"

# P12 deep array order sensitive: nested array swap -> BREACH
# (arrays stay ordered at EVERY depth; only objects get sorted).
cat > "$T/deep3.json" <<'EOF'
{"spec": "pins.deep", "version": 1,
 "invariants": [
   {"id": "d1", "metric": "m", "floor": ">= 1",
    "meta": {"alpha": 1, "beta": {"x": 2, "y": 3}, "seq": ["a", "b"]}}]}
EOF
python3 "$TOOL" seal "$T/deep3.json" --ledger "$T/l12.jsonl" --note deepseq >/dev/null
cat > "$T/deep4.json" <<'EOF'
{"spec": "pins.deep", "version": 1,
 "invariants": [
   {"id": "d1", "metric": "m", "floor": ">= 1",
    "meta": {"alpha": 1, "beta": {"x": 2, "y": 3}, "seq": ["b", "a"]}}]}
EOF
OUT=$(python3 "$TOOL" check "$T/deep4.json" --ledger "$T/l12.jsonl"); RC=$?
[ $RC -eq 1 ] && ok P12 || bad P12 "deep array reorder must diverge: rc=$RC $OUT"

# P13 multi-spec ledger: two specs seal to ONE ledger; both check GREEN at
# their own lines; chain covers 2 rows (revision/append is the lifecycle law).
python3 "$TOOL" seal "$T/spec.json" --ledger "$T/l13.jsonl" --note spec-a >/dev/null
python3 "$TOOL" seal "$T/uni.json" --ledger "$T/l13.jsonl" --note spec-b >/dev/null
OUT=$(python3 "$TOOL" verify --ledger "$T/l13.jsonl") \
  && echo "$OUT" | grep -q "2 rows" \
  && OUTA=$(python3 "$TOOL" check "$T/spec.json" --ledger "$T/l13.jsonl") \
  && OUTB=$(python3 "$TOOL" check "$T/uni.json" --ledger "$T/l13.jsonl") \
  && echo "$OUTA" | grep -q "line 1" && echo "$OUTB" | grep -q "line 2" \
  && ok P13 || bad P13 "multi-spec ledger: $OUT / $OUTA / $OUTB"

# P14 semantics-blindness boundary (docstring limit #3, PINNED so no future
# 'fix' silently adds validation): a spec with DUPLICATE invariant ids seals
# and checks GREEN — reading/enforcing semantics is the reader's job, not the
# tool's. The hash binds bytes, not meaning.
cat > "$T/dup.json" <<'EOF'
{"spec": "pins.dupids", "version": 1,
 "invariants": [
   {"id": "same", "metric": "m", "floor": ">= 2"},
   {"id": "same", "metric": "m", "floor": "<= 9"}]}
EOF
OUT=$(python3 "$TOOL" seal "$T/dup.json" --ledger "$T/l14.jsonl" --note dupids) \
  && OUT2=$(python3 "$TOOL" check "$T/dup.json" --ledger "$T/l14.jsonl") \
  && echo "$OUT2" | grep -q GREEN \
  && ok P14 || bad P14 "semantics-blind boundary moved: $OUT / $OUT2"

# P15 BOM-prefixed spec -> REFUSED exit 2, nothing sealed (Windows-Notepad
# edge; encoding='utf-8' keeps the BOM and json.load refuses it. Documented,
# not fixed: silent BOM-stripping would change spec_bytes semantics).
printf '\xef\xbb\xbf{"spec": "pins.bom", "version": 1, "invariants": []}' > "$T/bom.json"
OUT=$(python3 "$TOOL" seal "$T/bom.json" --ledger "$T/l15.jsonl"); RC=$?
[ $RC -eq 2 ] && [ ! -e "$T/l15.jsonl" ] && echo "$OUT" | grep -q REFUSED \
  && ok P15 || bad P15 "BOM edge moved: rc=$RC $OUT"

echo "----"
echo "pins_spec_prereg: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ]
