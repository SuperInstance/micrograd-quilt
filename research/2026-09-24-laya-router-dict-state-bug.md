# laya4quilt Router: dict-state language misroute (upstream bug report)

Date: 2026-09-24
Upstream: https://github.com/NandhaKishorM/laya (SuperInstance/laya4quilt fork, sync 0.3.20 landed as 9e72571)
Status: REPRODUCED first-hand 2026-09-24 (~16:00 GMT+8), on laya 0.3.20.

## Repro

```python
from laya import Router
Router.route({'message': "Mein Konto wurde zweimal belastet"}, {})
```

## Observed

- Language verdict: `english` with `language_undecided: true`.
- Router then dispatches to a checkpoint whose score on that German input is
  **0.10** — a near-floor routing on text the checkpoint cannot read.
- String input for the same sentence routes correctly (German checkpoint,
  healthy score). The failure is specific to the dict-state form.

## Why it matters (quilt-executor context)

quilt-executor's SPEC v2 evaluator routes typed questions through the Router;
executor states arrive as dicts (task envelope shape), so the dict-state path
is the PRODUCTION path, not an edge case. A 0.10-confidence route silently
degrades every non-English dict-state task. Our gate formula
(`p* = 1 − C/L` on calibrated strata) would decline the arm, but the
underlying misroute still burns a pull and pollutes washout statistics.

## Suspected cause

The Router's language-detection seam appears to serialize/inspect only string
fields (or the first field) of a dict state, yielding `language_undecided`,
and the undecided fallback resolves to the default `english` arm instead of
refusing or embedding the full payload. Spec-side fix candidates:
(1) dict-state: concat all string values before language detection;
(2) `language_undecided` should be a typed refusal (`noul_ambiguity`), not a
silent default-arm fallback.

## Doctrine note

Booked in quilt-executor terms: this is exactly the "router misfire
self-confirming starvation" lie shape (crush C1 memo) — the router's own
wrong answer starves the correct arm of bandit pulls. Recorded here so the
upstream issue and our evaluator spec stay cross-linked.
