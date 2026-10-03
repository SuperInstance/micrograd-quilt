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

## Key-form schema (adopted 2026-10-03 from mavis-workspace, edge-watch 2026-10-03)

Three key-form laws applied to handoff keys in every `bindings/<lane>` dir:

1. **Null-forced last_measured** — a handoff key must exist and be
   null-forced (e.g. `last_checkpoint: null` written by the lane at bind
   time). An absent key is a schema error: `readyz.sh` treats a binding
   missing its handoff keys as REFUSED, never as "not yet".
2. **Refuted-warns-if-empty** — a `known_failures` file that is empty must
   still exist and say so ("none recorded"); silence is not empty.
3. **known_failures names the class** — each entry names the mistake class
   (off-by-one, stale-premise, dropped-memory-tree), never just the instance.

Source: SuperInstance/mavis-workspace key form, flagged SYNERGY CANDIDATE in
docs/KEY-FORM-SCHEMA-NOTE.md (branch key-form-schema-note-2026-10-03).
Adoption, not rivalry; weight law: CANDIDATE until the source edge VERIFIED.
