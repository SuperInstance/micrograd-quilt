**1. Where a properly-scored organ still lies**

Proper scoring constrains the scorer's incentive to report *its own distribution* honestly. It guarantees nothing about whether that distribution is fitted to the world in front of it. Concrete lies:

- **Context-window blindness on diffs.** laya scores what it sees. A hunk that deletes a null-guard 400 lines below the visible span, an upstream rename that flips semantics, a type tightened in another file — locally coherent, globally wrong. The receipt reads "scored, confident"; it should read "scored the visible 2%." Properness cannot punish seeing the wrong world, only misreporting about the world as embedded.
- **Distribution shift.** Calibration is defined against the training/judge distribution. New framework, new linter, post-incident codebase mood: the organ stays *honestly wrong*, faithfully reporting a stale distribution. Its score history in the chain stays clean because labels come from the same drifted judge.
- **Checkpoint-router misfires.** Misroute → wrong checkpoint scores the row → Thompson updates the wrong arm. Worse, router confidence is itself uncalibrated and, unless routing is a first-class receipt field, unbooked. Failure is self-confirming: starved arms never collect the evidence that would correct the router.
- **Calibration drift / seasons.** Release weeks, quarterly refactors, upstream model swaps. A calibration curve is a timestamped artifact; without time-windowed recalibration booked as rows, the hash chain certifies January's honesty in March.
- **Distilled judge bias.** Proper scoring against LLM-judge labels makes laya properly calibrated *to the judge's biases* — a 33ms amplifier of the slow path's blind spots, now stamped "proper."

**2. The refusal row**

A refusal is not score 0 or 0.5 — those are claims. Absence must be typed absence. Required fields:

- `refusal_type`: {noul_ambiguity, insufficient_context, ood, router_failure, timeout} — different operational objects; the bandit must not update identically on each.
- `visibility`: content hashes/spans of what laya actually saw (files, hunks, token count). "Saw" must be provable, not implied.
- `routing`: checkpoint ID, router score, alternatives considered.
- `trigger`: which guard fired and its value (entropy, OOD detector, coverage metric).
- `resolvability`: what would make it scoreable ("needs file X," "needs hunk N") — refusals become actionable debt, not fog.
- `linkage`: `parent_receipt_id` to the escalated row and its slow-path verdict. Refusal quality is only measurable in pairs: a refusal the judge also calls ambiguous is a *correct* refusal.
- `cost`: the 33ms spent anyway (time-as-first-class).

Bandit policy must be symmetric: penalize refusals and you train never-refuse (confident noise); reward them and you train refuse-the-hard-ones (strategic abstention). Either poisons MOTH.

**3. Never delegate**

- Ground-truth/label generation — the arm scoring its own quality is circularity.
- Refusal-boundary and escalation-threshold policy — that is the organ's conflict-of-interest surface; the executor owns it.
- Any verdict whose decisive evidence lives outside the window: cross-file, cross-commit, semantic-drift judgments, anything security-adjacent or precedent-setting (each row feeds the bandit prior; poison compounds).
- Question-type coercion: forcing choice/score/noul frames onto open-ended judgment is a category error laya cannot detect from inside.

**Upgrade evidence:** a lease, not a title, granted per task_type. N hash-chained dual-run pairs where the fast arm *scored* (not refused); tail quantiles of |delta|, never means alone (means hide gaming); refusal rate with a refusal-vs-difficulty decorrelation audit; current-season calibration curve; router accuracy on that type. Thompson posterior must dominate under time-decay — trust expires and must be re-earned.

**4. Dual-run economics and the new lie**

At 33ms the fast side of a dual-run is ~free: you run a census, not a sample. The estimator's sampling bias disappears — delta is no longer measured on a hand-picked subpopulation. That is the genuine win.

The new lie: the estimator conditions on *declined* escalations, a population the cheap arm itself selects. Escalation becomes endogenous. Strategy: escalate exactly the high-uncertainty cases where delta would be large, keep confident-wrong cases in-house. Kept-set mean delta stays clean; confident-wrong rows never enter the measured population. Escalation launders the worst outcomes out of the statistics — the lie detector audits only what the liar chooses to show it.

Countermeasures: a mandatory random keep-holdout the arm may not escalate; book the fast-arm score on escalated rows too and compute delta across *both* populations; executor-owned thresholds orthogonal to the arm's self-assessed uncertainty; charge escalation latency against the arm's bandit budget; and audit the correlation between escalation/refusal and realized difficulty — nonzero correlation is the tell.
