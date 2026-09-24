# Far-Future Users, Looking Forward (reverse-actualization pulse)

Casey directive 2026-09-24 13:44: imagine future users looking forward, diffuse their
behavior backward to infer shapes of components yet to be described; smallest-build
the missing pieces.

Method: write four short POV fragments from users ~2-5 years out, each behaving as if
the ecosystem already exists. Then diffuse backward: what component shapes does their
behavior imply? Then pick the smallest buildable missing piece.

---

## POV 1 — Mara, fleet auditor (2029)

"I don't read code anymore. I ask the fleet for its *chain of custody*: every decision
the fleet made this week, with the receipt hash, the provider, the counterfactual that
was declined, and the lie-detector score. If a receipt won't verify, the lane that
produced it is quarantined automatically — I just sign the quarantine order."

**Backward diffusion:**
- Chain of custody = quilt-executor's BIND/EFFECT/REFUSED ledger, but *verifiable by an
  outsider without the executor's state*. Today's verify() re-derives from local state.
  Missing piece: **portable receipt bundle** — a signed, self-contained export
  (receipts + canon hashes + provider pubkeys) that verifies standalone.
- Quarantine = a consumer of verify() failures. Missing piece: **quarantine watcher** —
  a small daemon tailing the ledger, auto-branching a lane on verification failure.

## POV 2 — Deniz, quilt composer (2028)

"I lay a seam between two repos the way I'd solder a joint. I don't write glue code;
I state the tension (what each side refuses to do) and the seam materializes as a
tested harness. My job is choosing where the tension should live."

**Backward diffusion:**
- Seams are first-class artifacts with named tension. We have SEAM specs as markdown.
  Missing piece: **seam registry** — a machine-readable index of declared seams across
  SuperInstance repos (issue-linked), so a composer can query "who refuses to do X?"
- "Tested harness materializes" — today a seam is prose + hand-built harness. Missing
  piece: **seam scaffold generator** — from a refusal-shape spec, emit the harness
  skeleton + the test that fails until both sides connect.

## POV 3 — The young-posterior alarm (fleet self-knowledge)

"The fleet tells me when it's *young*, not just when it's wrong. A lane under 5
observations on a task type wears a visible youth badge, and its suggestions are priced
as speculation, not judgment. Nobody gets fired for trusting an old posterior; people
get fired for trusting a young one."

**Backward diffusion:**
- youth_discount already exists in decider.py (n<5 shrink). But it's *internal*. Missing
  piece: **youth surfacing** — receipts carry `youth: true` flag + observation count;
  the ledger viewer renders badges. Tiny change to ledger.py schema, huge honesty gain.

## POV 4 — Retro-user archeology (2031)

"New members onboard by *diffing against canon*: they pick a receipt from years ago,
re-run it, and read the drift. Drift isn't a bug here; it's the curriculum."

**Backward diffusion:**
- Canon hash + target drift already observed (0x7d8d… live vs 0xbf27… target). Missing
  piece: **receipt replay tool** — fetch receipt by hash, re-execute against current
  canon, emit a diff report (drift curriculum).

---

## Smallest buildable missing piece: **youth surfacing**

Rationale: quilt-executor is fresh, 5 commits, green pins; a one-file change there is a
small committable unit. The other four imply new services — follow-up pulses.

Shape:
1. `decider.py`: expose `is_young(task_type, provider)` (n < floor) alongside the
   existing discount.
2. `ledger.py`: BIND receipts gain optional `meta["youth"] = {"young": bool, "n": int}`.
3. `verify()`: unchanged (meta is advisory, not part of the hash) — canon stays stable.
4. One pin test: young suggestion → receipt carries badge; verify still green.

Next pulses (ranked): receipt replay tool → quarantine watcher → portable receipt
bundle → seam registry/scaffold.
