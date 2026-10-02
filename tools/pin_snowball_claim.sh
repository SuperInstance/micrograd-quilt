#!/usr/bin/env bash
# pin_snowball_claim.sh — RED->GREEN pins for snowball-claim.sh.
# P1: competing pulse REFUSED while claim held (the duplicate-PR fix).
# P2: owner release frees the item; third pulse can then claim.
# P3: non-owner release REFUSED.
# P4: stale claim stealable only after TTL.
set -u
DIR=$(cd "$(dirname "$0")" && pwd)
CL="$DIR/snowball-claim.sh"
export SNOWBALL_CLAIM_ROOT=$(mktemp -d)
export SNOWBALL_CLAIM_TTL_SEC=2
PASS=0; FAIL=0
ok()  { PASS=$((PASS+1)); echo "ok   - $1"; }
bad() { FAIL=$((FAIL+1)); echo "FAIL - $1"; }
chmod +x "$CL"

# P1: pulse A claims; pulse B refused
OUT=$("$CL" claim demo-item pulse-A 2>&1) && ok "P1a pulse-A claimed: $OUT" || bad "P1a claim failed"
if "$CL" claim demo-item pulse-B >/dev/null 2>&1; then
  bad "P1b pulse-B was NOT refused (collision class unfixed)"
else
  ok "P1b pulse-B REFUSED while held"
fi

# P2: owner release, then pulse C claims
"$CL" release demo-item pulse-A >/dev/null 2>&1
if "$CL" claim demo-item pulse-C >/dev/null 2>&1; then
  ok "P2  pulse-C claimed after owner release"
else
  bad "P2  claim after release failed"
fi

# P3: non-owner release refused
if "$CL" release demo-item pulse-A >/dev/null 2>&1; then
  bad "P3  non-owner release NOT refused"
else
  ok "P3  non-owner release REFUSED"
fi

# P4: stale steal — pulse-C dies, wait past TTL, pulse-D steals
sleep 3
if "$CL" steal demo-item pulse-D >/dev/null 2>&1; then
  ok "P4  stale claim stolen by pulse-D after TTL"
else
  bad "P4  steal of stale claim failed"
fi

rm -rf "$SNOWBALL_CLAIM_ROOT"
echo "$PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
