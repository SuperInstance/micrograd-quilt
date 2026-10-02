#!/usr/bin/env bash
# snowball-claim.sh — flock-style claim locks for snowball queue items.
# Direct fix for the duplicate-PR collision class: two parallel pulses
# grabbing the same queue item. Claim is atomic (mkdir), owner-stamped,
# and stale-claimable (TTL) so a dead pulse cannot wedge the queue.
#
# Usage:
#   snowball-claim.sh claim  <item-id> <owner>   # exit 0 = claimed, exit 1 = held by other
#   snowball-claim.sh release <item-id> <owner>  # only the owner may release
#   snowball-claim.sh status <item-id>           # print holder/age, exit 0 free / 1 held
#   snowball-claim.sh steal  <item-id> <owner>   # take a stale claim (age > TTL)
# Env:
#   SNOWBALL_CLAIM_TTL_SEC  default 7200 (2h)
set -u

CLAIM_ROOT="${SNOWBALL_CLAIM_ROOT:-$HOME/.openclaw/workspace/snowball-work/claims}"
TTL="${SNOWBALL_CLAIM_TTL_SEC:-7200}"
CMD="${1:-}"; ITEM="${2:-}"; OWNER="${3:-}"

die() { echo "snowball-claim: $*" >&2; exit 2; }
[ -n "$CMD" ] && [ -n "$ITEM" ] || die "usage: snowball-claim.sh {claim|release|status|steal} <item-id> [owner]"
case "$ITEM" in *[!a-zA-Z0-9._-]*) die "item-id must be [a-zA-Z0-9._-]";; esac

mkdir -p "$CLAIM_ROOT"
LOCK="$CLAIM_ROOT/$ITEM.lock"
HOLDER="$LOCK/holder"
NOW=$(date +%s)

age() { [ -f "$HOLDER" ] && echo $(( NOW - $(date -r "$HOLDER" +%s 2>/dev/null || echo "$NOW") )) || echo 0; }
print_holder() { local o t; o=$(cat "$HOLDER" 2>/dev/null || echo '?'); t=$(date -r "$HOLDER" '+%H:%M:%S' 2>/dev/null || echo '?'); echo "$ITEM held by $o since $t ($(age)s ago)"; }

case "$CMD" in
  claim)
    [ -n "$OWNER" ] || die "claim needs owner"
    if mkdir "$LOCK" 2>/dev/null; then
      printf '%s\n%s\n' "$OWNER" "$NOW" > "$HOLDER"
      echo "CLAIMED $ITEM by $OWNER"
      exit 0
    fi
    if [ "$(age)" -gt "$TTL" ]; then
      print_holder; echo "STALE (> ${TTL}s) — re-run with 'steal' to take it"
    else
      print_holder; echo "REFUSED"
    fi
    exit 1 ;;
  steal)
    [ -n "$OWNER" ] || die "steal needs owner"
    [ -f "$HOLDER" ] || { echo "$ITEM is free — use claim"; exit 1; }
    [ "$(age)" -gt "$TTL" ] || { print_holder; echo "NOT STALE — REFUSED"; exit 1; }
    print_holder
    rm -rf "$LOCK"
    mkdir "$LOCK" && printf '%s\n%s\n' "$OWNER" "$NOW" > "$HOLDER"
    echo "STOLEN $ITEM by $OWNER" ;;
  release)
    [ -n "$OWNER" ] || die "release needs owner"
    [ -f "$HOLDER" ] || { echo "$ITEM not held"; exit 0; }
    [ "$(head -n1 "$HOLDER")" = "$OWNER" ] || { print_holder; echo "REFUSED (not owner)"; exit 1; }
    rm -rf "$LOCK"; echo "RELEASED $ITEM" ;;
  status)
    if [ -f "$HOLDER" ]; then print_holder; exit 1; else echo "$ITEM free"; exit 0; fi ;;
  *) die "unknown command: $CMD" ;;
esac
