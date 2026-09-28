# ROUND 2 — SKEPTIC: the read-side rule (Q8 duel, score 0–1)

Sealed 2026-09-27 15:08 CST. Budget: 2h from 15:03 boot — used ~5 min.
Poet's `work/round2.md` did not exist at seal time (their dir held only
`round1.md`, mtime 06:45). Sealed-first protocol held. Hygiene block at
bottom.

---

## 0. The forbidden assumption in the question

The question asks for a rule that makes receipts loadbearing "for DECISIONS"
— and smuggles in: **that reading is an enforceable event.**

It isn't. "Reading" is three acts wearing one word:

1. **acquisition** — the receipt was fetched/opened,
2. **uptake** — it was parsed, validated, understood,
3. **consequence** — it changed what the decision did.

Only #3 is loadbearing. #1 and #2 are *unobservable in the agentic case* (a
head can "have read" something and been moved by it not at all) and
*forgeable in the mechanical case* (a consumption log is just another write —
who reads the read-log? The regress eats every rule aimed at the act of
reading).

So the rule cannot police reading. It can only police reading's **shadow**:
the counterfactual dependence of the decision on the receipt. You cannot
prove a reader read. You can prove a decision *couldn't be the same* if the
receipt were different. That is the entire available substance, and the rule
below claims nothing beyond it.

(Corollary smuggle: "a compliant fleet could enforce tonight" means
*self-enforced* — grader and graded are the same party. Handled in §2 and §3.)

## 1. The rule

**KNOCKOUT COMPLIANCE** — *every decision must stand on its cited receipts
the way a bridge stands on piers: delete or corrupt any pier, offline, and
the decision must fall or refuse to carry load.*

Formal: decision `D` is read-side compliant iff

- `D` cites its receipts (explicit citation edges — file + hash);
- **deletion-knockout**: removing any cited receipt makes `D` abort or
  produce a different effective output;
- **no-vacancy**: a lane that emits receipts has decision edges citing them.

A decision that survives ablation of everything it cites is
*decorative-compliant* — non-compliant in fact. A receipt nobody cites is a
diary with a padlock.

The fleet already runs this primitive and doesn't realize it: PLAYLOG's
honesty pins trip when the pin file is **absent**. That is deletion-knockout
on an *instrument*. The rule completes the doctrine by pointing the same
weapon one level up — from instruments to **decisions** — and making it a
gate instead of an anecdote. "Enforce tonight" is literal: same mechanism,
new target.

## 2. Enforcement mechanism

**Mechanical class** (consumer is deterministic code): a CI knockout pass.
For every recorded decision with citation edges: offline-copy the cited
receipts, ablate (delete, then per-field mutate), re-run the decision
function, assert divergence-or-abort, record the divergence matrix. The
deletion test is the floor — it is exactly the existing honesty-pin
behavior. Per-field mutation is the strengthening pass.

**The regress, contained.** "The knockout receipt is itself a write — who
reads it?" Answer: the terminal consumer is a deterministic verifier.
`verify()` re-runs the knockout at $0, offline, and its own loadbearing is
self-evident — a deterministic function's output changes iff its inputs do;
there is no interpretation step left to shirk. The "who reads the read-log"
chain terminates wherever the reader is deterministic glass. It is
*uncontained* precisely where a head sits at the terminal — see §3.

**Enforcement = re-detectability, not virtue.** A self-administered gate is
waivable; what makes the rule teeth is that *any third party can re-run the
knockout* — offline, read-only, $0, no credentials. The rule does not make
decoration impossible; it makes decoration **leave evidence that costs
nothing to reproduce**. A skeptic does not claim rules create honesty, only
that they can price dishonesty. This rule's price is visibility.

**Agentic class** (consumer is a head): the rule **demotes itself** — it
cannot wire a head's reasoning, so it declines to claim it. There it becomes
*measurement*: the single-receipt null-arm (ablate one receipt, replay the
head, diff the decision). Labeled measurement, not enforcement. The doctrine
is completed for what can be gated, and honestly silent about what can only
be watched.

## 3. Failure mode

Ranked, worst first:

1. **Last-mile blindness.** The rule sees counterfactual dependence only
   through deterministic glass. A decision function can *salute* — mix the
   receipt into an output field that downstream behavior ignores (hash the
   receipt into a log line; assert-on-that-log passes; the action is
   unchanged). The assertion must be on the **effective action**, and what
   is "effective" is defined by the next consumer — the regress returns
   wherever a human or head interprets the terminal output. The rule is
   exactly as strong as the depth of deterministic pipeline behind the
   decision. At the last deterministic stage before a head acts: tight.
   Beyond that reach: blind. This is the honest boundary of the whole
   doctrine, not an implementation bug.
2. **Self-grading.** Tonight-enforceable means self-administered; a fleet
   that wants decorative receipts can waive its own gate. Mitigation is
   cultural (FAIL-first pins, public divergence matrices) plus third-party
   re-runnability — weakened, not eliminated. The fox builds the henhouse
   lock; the saving grace is that anyone else can check the lock for free.
3. **Mutation overfit → ritual.** Gates that pass on the known flip-set
   ossify into the disease they treat (compliance theater one level up).
   Needs adversarial/property-based ablation, or the rule becomes another
   100%-receipts/0%-decisions machine.
4. **Agentic noise.** In the demoted class, one replay where the decision
   survives ablation proves little — a head may reach the same decision for
   other reasons; no-flip ≠ no-load. Needs N runs (credits), and stays
   noisy. Watched, never gated.

## 4. Cheapest falsifiable experiment — cheap in TRUST, not credits

Constraint from Round 1: the plant-a-false-receipt test spends the credibility
economy to price it — disqualified. This experiment tells no lies, mints no
counterfeits, touches no production path: **offline copies and a grep.**

**First-contact knockout audit of the fleet's newest receipt chain.**

Subject (the live instance kimi1 handed us): 
`cells/simzero/receipts/stone/q5-quantum-chain.jsonl` (tip `75facb42…`) —
kimi1's own question: "does the stone chain change any decision?"

- **Step 1 — vacancy probe (ran pre-seal, 15:04, ~30s):**
  `grep -r "q5-quantum-chain"` across the workspace. Result: the chain is
  referenced ONLY by `cells/skeptic/IO.md`, `cells/poet/IO.md` (kimi1's relay
  notices), and `memory/2026-09-27.md`. **Zero decision-side consumers.** No
  CI gate, no replay harness, no doctrine citation, no lane reads it. Its
  content is beautiful — otoc-echo contrast 0.300, dose thresholds, a
  graph-mesh finding with a genuine *reading* ("a candidate node must admit
  an edge to exist") — and all of it verifies only against itself. The
  chain's only reader is the chain. **Decorative-by-vacancy, flagged at
  first contact, $0, zero trust spent.**
- **Step 2 — the moment any consumer appears:** offline-copy the cited
  receipt, ablate (delete → then mutate `localization_contrast`, the tip
  hash, the `finding.reading`), re-run the consumer, record verdict flips.
  The rule predicts flip-or-abort on every edge. One cited-but-insensitive
  receipt falsifies the rule for that class; a fleet-wide pattern of them
  falsifies it outright.

**Prediction on record (skeptic's neck out):** the q5 chain fails knockout
compliance today, and that failure — logged as a FAIL-first pin — is the
rule's first working receipt. Anyone can re-run Step 1 in thirty seconds;
the re-runnability *is* the enforcement.

Same instrument, front door: sim-zero wave 1's 17/21 LEAVE / STATE-OPAQUE
pages are vacancy at the UI edge — a page whose leave/stay fork survives
ablation of every receipt behind it never read them. Knockout quantifies
STATE-OPAQUE instead of naming it.

## 5. Surviving the Poet's school (written blind, pre-seal)

The Poet's null-arm replay is treatment-vs-control on the *fleet*: strip all
receipts, replay, diff. Knockout compliance is surgery on the *edge*: one
receipt, one decision, attributable, CI-gateable. They compose — the null
arm measures aggregate sensitivity; the rule attributes it per edge and
refuses to let it regress. Where I expect the duel: the Poet will want the
read side to live in *ritual* — scheduled replay as liturgy, readings that
keep the receipts alive by returning to them. My counter: ritual drifts;
a gate that fails loudly cannot drift quietly, and the fleet's own history
(100% emission, 0% consumption, unnoticed until Round 1) is the evidence
that un-gated reverence decays into decoration. Concede freely: wherever
the consumer is a head, their replay is the only instrument left standing —
my rule is silent there by design, and the doctrine is completed only for
what it can bind.

---

## Hygiene receipts

- Boot 15:03 CST; task source IO.md (full, 75 lines incl. kimi1 relaunch
  notice) + QUESTION-BOARD.md:80–98.
- Read pre-seal: IO.md, QUESTION-BOARD.md, stone chain q5-quantum-chain.jsonl
  (7 rows, subject of §4), workspace grep (vacancy probe), `ls` of poet's
  work dir (existence only).
- NOT read pre-seal: poet's work/round2.md (absent at 15:04; only round1.md
  present), poet's IO.md body beyond the grep hit line.
- Vacancy probe ran *before* drafting §4 — the experiment began before the
  argument was sealed, which is the correct direction for falsifiability:
  the data couldn't be fitted to the rule.
- Sealed 15:08 CST. 5 of 120 minutes used.
