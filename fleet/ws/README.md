# /srv/fleet/ws — pre-warmed scout workspace (queue item c, 2026-10-03)

Clone-once-bind-many per the AX workspace pattern (scout-ax 2026-10-03 §2).
Lanes must NOT re-clone upstream sources; they bind a worktree against the
single verified clone here.

- `ax/` — google/ax @ ac23328 (scout-pinned; .fleet-scout marker)
- `adk-python/` — google/adk-python @ 49bf291 (scout-pinned; .fleet-scout marker)
- `bindings/` — per-lane worktrees live here, one dir per lane
- `bin/readyz.sh` — pre-flight: pins intact + clean tree before binding

Usage:
    /srv/fleet/ws/bin/readyz.sh            # exit 0 = safe to bind
    git -C /srv/fleet/ws/ax worktree add ../bindings/mylane -b mylane

Rules: never commit inside the base clones (bind a worktree); never `git pull`
in a base clone (a moved pin invalidates every binding — readyz catches it);
suspend/resume state lives in the lane's binding dir, not here.
