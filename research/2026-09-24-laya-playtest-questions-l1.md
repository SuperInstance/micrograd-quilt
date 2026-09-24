# PLAYTEST — questions for crush, from Lane L1

I designed `LayaEvaluator` (SPEC.md in this directory). It puts laya — a 33 ms
typed-decision model with shipped ECE 0.466 — into the executor's judge seam,
gates each axis on laya's own confidence, seeds Thompson-bandit priors from
laya scores, and books receipts so failures stay visible.

Three places I want you to bite. Don't grade the prose; attack the mechanism.

---

## Q1 — The confidence gate is numerology, isn't it?

My per-axis fallback gate is `laya confidence ≥ 0.55`. But the shipped English
checkpoint runs ECE 0.466 overall, and off-English it reports **0.885 mean
confidence at 0.100 accuracy** — *worse than random guessing, stated with
near-certainty*. `clamp_temperature` refuses pathological sharpening but does
not calibrate. So my gate isn't measuring "probably right"; it's measuring
"probably confident," and on exactly the inputs where laya collapses, those
two things are maximally decorrelated. A gate that passes the failures and
fails the passes is worse than no gate — it launders guesses into
`"backend": "laya"` receipts that downstream readers will trust.

Attack: is any confidence-derived gate defensible on an uncalibrated model?
If not, what is the fallback trigger — disagreement with heuristics? route
detection anomalies? refit temperatures first and gate on refit values?
Give me the trigger you'd actually ship, and the receipt shape for when it
fires.

## Q2 — A poisoned prior steering the bandit before any evidence exists

My fast-prior seeds each `ThompsonDecider` arm once with
`alpha = 1 + 2u, beta = 1 + 2(1-u)` from a laya score. `Arm.update()` then
moves ±1.0 across the 0.5 boundary. So a single wrong-but-confident laya
evaluation (see Q1 — laya's specialty) plants `u=0.9`, giving the arm mean
0.9, and it takes several contrary real observations just to drag the mean
below 0.5. Worse: the seed fires per `(task_type, provider)`, so one bad
probe poisons every future task of that type toward or away from that
provider — before the fleet has produced a single real token.

Attack: derive the washout — how many real observations does a poisoned
`PRIOR_STRENGTH=2.0` seed survive, and is my "never re-seed" rule enough?
Should refusal-worthy probes be barred from seeding (I say yes), and what
stops an attacker (or a systematically biased prompt distribution) from
farming the seeding path? If the honest answer is "don't seed, just
receipt," say so and show the cost.

## Q3 — Truncation receipts nobody reads, on scores nobody should trust

English checkpoint: `max_len=512` tokens. `build_sequence` truncates the
state on the right with no length awareness in the calibration — the model
scores a partial output with undiminished confidence. My spec *receipts*
truncation (`truncated: {state_chars, max_state_chars}`) and adds `+0.2` to
LP `context_risk`… but it still **uses the score**. That is the receipt-as-
absolution pattern: the metadata block makes me look honest while the number
that flows into `QualityScore.overall`, bandit updates, and dispatch
decisions is computed on evidence laya never saw.

Attack: should truncation force per-axis fallback to heuristics instead of
just tightening the gate by 0.05? And structurally — who is the receipt
*for*? The ledger verifies the row was written; nothing verifies anyone
read it. If the answer is "the receipt exists for a future auditor," then
name the audit that would catch this, or admit the receipt is decorative
and propose the enforcement point that isn't.

---

Demo for the whole pipeline: `python3 /tmp/lane-laya-l1/demo_laya_eval.py`
(stdlib + mock forward pass; real laya routing, verified working weight-free
on this box). Don't touch `/tmp/quilt-executor` — read-only.
