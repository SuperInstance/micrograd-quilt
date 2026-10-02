#!/usr/bin/env bash
# readyz — pre-flight check for the /srv/fleet/ws scout workspace.
# AX pattern: clone-once-bind-many; this script proves the once-clones are
# intact and at the scout-pinned commits before a lane binds a worktree.
# Exit 0 = READY, exit 1 = NOT READY (stderr says why). Receipts over claims.
set -u
WS=/srv/fleet/ws
fail=0

check() { # name dir pinned_commit
  local name="$1" dir="$2" pin="$3" head
  if [ ! -d "$dir/.git" ]; then echo "NOT-READY: $name missing ($dir)" >&2; fail=1; return; fi
  head=$(git -C "$dir" rev-parse HEAD 2>/dev/null) || { echo "NOT-READY: $name not a git repo" >&2; fail=1; return; }
  if [ "${head:0:${#pin}}" != "$pin" ]; then
    echo "NOT-READY: $name at ${head:0:12}, expected $pin (pin moved — re-scout before binding)" >&2; fail=1
  else
    echo "OK: $name @ ${head:0:8} (pinned)"
  fi
}

check ax          "$WS/ax"          ac23328
check adk-python  "$WS/adk-python"  49bf291

# dirty-tree warning: bindings must start clean (a dirty base clone poisons every worktree)
for d in "$WS"/ax "$WS"/adk-python; do
  if [ -n "$(git -C "$d" status --porcelain 2>/dev/null)" ]; then
    echo "WARN: $(basename "$d") has uncommitted changes (scout edits?)" >&2
  fi
done

[ "$fail" -eq 0 ] && echo "READY: ws intact, bind with: git -C /srv/fleet/ws/<repo> worktree add ../bindings/<lane> -b <lane>"
exit $fail
