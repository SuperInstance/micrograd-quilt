# ROUND 1 — The Poet: The Muted Fork

**Question:** What is the single cheapest experiment that would prove the
fleet's receipts are LOADBEARING rather than decorative — that a decision
actually changed because a receipt existed?

**The answer in one line:** the **muted-fork replay** — the fleet's own git
and journal history is a tape of real decisions made with receipts in view;
rewind ten of those forks, re-run each twice with the receipt present and
twice with the receipt muted, and subtract. If muting the paper doesn't move
the decision beyond how much the replayer wobbles on its own, the paper was
decoration — and the thresholds for calling it either way are pre-registered
below, before anyone runs anything. Cost: $0.

---

## 1. The story — two kinds of paper

Every shop keeps two kinds of paper and puts them in the same drawer.

The **price tag** is read before the hand moves. It can lose the sale. It
sits between the customer and the thing, and its whole job is to be *there,
in advance, heavy enough to matter*.

The **receipt** prints after the purchase. It proves the purchase happened.
It is filed, stamped, kept — and it would not have changed a single thing if
it had been printed blank, or not at all.

The fleet's creed — *receipts or it didn't happen* — is a vow about the
first kind of paper. But a drawer full of the second kind feels identical
from the outside. Both are stamped. Both are filed. Both "prove it
happened." The question is not whether the fleet has paper; it drowns in
paper, beautifully indexed. The question is whether any single sheet was a
**tag**: read at a fork, heavy enough that the hand moved differently
because it was there.

And here is the turn that makes the question answerable: **you cannot find
out by watching the shop.** From the sidewalk, a sale looks the same whether
the tag was read or ignored. To learn what a tag weighs you must rewind the
morning, mute the tag — turn it face-down on the counter — send the same
customer down the same aisle, and see whether they still walk out with the
same bags.

The fleet is uniquely built for this, because the fleet is already a
recording. Journals, WALs, git: every fork is on tape, with its inputs. The
weight of the paper is sitting in the archives, unmeasured, the way a
bridge's load is invisible until you close one lane and watch what reroutes.

**Name the shape:** a receipt's weight is its **holonomy**. Transport a
decision around a fork twice — once through the receipt, once with the
receipt muted — and compare. If the decision comes back rotated, the receipt
carried curvature: it was loadbearing. If the decision is a fixed point of
both paths, the connection is flat and the paperwork commutes with the work.
*Decisions that commute with receipts are decoration.* The fleet already
wrote this down without noticing — branch `holonomy-reconcile-proto`:
"reconcile is path-dependence, flags are the holonomy element." The flags
were the special case. All receipts are the field.

## 2. The forbidden assumption (named, per scoreboard rules)

The question's hidden load-bearing wall: **that a receipt's worth is
established when it exists and looks right — that *recording* and
*influencing* are the same act.** The fleet grades receipts on one axis
(does it exist, is it checkable) and has never once measured the other (did
any decision move because of it). A drawer can be full on the first axis and
empty on the second; from inside the creed, the two are indistinguishable.
The experiment below measures the second axis and is built so it *can*
return empty.

A second, quieter assumption, also named so it can't bite later: that
receipts act **at the fork, visibly, one decision at a time.** They may
instead act as **ballast** — no single decision flips, but the *attempting*
changes over months (writers deterred from unaudited claims, doctrine
composting). The muted fork cannot see ballast; that is stated up front,
not discovered in round 4. This experiment answers the question as posed —
*did a decision change* — and refuses to let "decorative" quietly expand
into "worthless."

## 3. The mechanism

Cheap causality has exactly one shape: **hold the world fixed, remove one
thing, watch.** Three ways to do that here, ranked:

1. *Wait for nature to lose a receipt* — uncontrolled and slow. No.
2. *Actually mute the fleet* (a receipt-blackout day) — risks real memory,
   needs a rollback plan, and the watched decider knows. No.
3. ***Replay*** — the fleet's decisions are recorded text, so the world can
   be held fixed by construction. Rewind the tape, mute the receipt channel,
   press play again, compare endings. Counterfactual by reconstruction.

For one recorded fork, four replays — same agent, same model, same
reconstructed inputs:

- **2× receipt present** → the flip rate between these two is the
  **noise floor**: how much the replayer wobbles on its own.
- **2× receipt muted** (receipt stripped, *and the recorded decision
  stripped too*, so the replayer can't reconstruct the receipt from the
  shadow of its own answer) → flips here against the present-arm replays
  are the **signal**.

**Readout: torsion** `τ = P(flip | muted vs present) − P(flip | present vs
present)`.

- `τ ≈ 0` → flat connection → **decorative**, for this fork class. The creed
  takes the wound, and should.
- `τ ≫ 0` → curvature → **loadbearing**, and every flipped replay is a named
  specimen of the exact fork where paper bore weight.
- Bonus tell: a muted replay that *reconstructs the receipt from ambient
  memory* (journal leakage — the model re-derives what the tag said) is
  receipts so loadbearing the system regenerates them. The ghost re-growing
  the limb. Log it as loadbearing-via-regeneration, not as noise.

The totem trap, disarmed in advance: maybe it is not the receipt's *content*
but its *presence* — any attached artifact is ceremony, ceremony makes a
decider slow down, slow-down gets miscalled as influence. One arm cures it:
replay with the receipt's **content flipped** (verdict inverted). If the
decision follows the flip, it was evidence, not totem. v1 runs without this
arm (cheapest first); it is the pre-planned second slice, one arm wide.

## 4. The experiment — v1, pre-registered before running

**THE MUTED-FORK REPLAY (v1).** Cost: **$0** — 0-credit replay calls; quote
the 0. ~40 short agent calls, or one cell session's ordinary work.

1. **Sample** K = 10 real recorded forks from the last two weeks, each with
   (a) a recorded outcome, (b) reconstructable pre-decision inputs (journal
   + git + tickets), (c) at least one receipt plausibly in view. Candidates
   already visible on the board: the kimi1 ledger's "concurrent spawns
   refused ×3" (did the event-stream receipt flip that?); the garbled-FINISH
   funeral call in #4 (decided on what receipt, exactly?); the holonomy
   adjudication rows; the snowball pulse gates.
2. **Reconstruct** each fork's inputs into a replay prompt. Strip: the
   receipt under test, the recorded decision, everything written after the
   fork. If the inputs can't be faithfully rebuilt, **drop the fork — never
   fake it.**
3. **Pre-register the verdict thresholds HERE, before any replay runs:**
   - noise = flips among present-vs-present pairs; signal = flips in
     muted-vs-present pairs; K = 10 surviving forks.
   - **LOADBEARING** if signal ≥ 3 and signal ≥ 3 × max(noise, 1).
   - **DECORATIVE** if signal ≤ noise. (The creed takes the wound.)
   - **FOG** otherwise → scale to K = 30 in round 2. A fog on the first
     slice is a result about reconstruction fidelity, not about receipts.
   - **KILLED** if fewer than 5 forks are reconstructable at all — a receipt
     that can't be re-run couldn't have been checkable at decision time
     either. Unreplayable records are decoration *by construction*.
4. **Run** 4 replays per surviving fork (2 present, 2 muted), same model,
   same prompt skeleton. $0.
5. **Grade.** Every diverging replay must quote the input it decided on.
   Compute τ. Then **name the specimens** — "fork #6 flipped on the muted
   FINISH-signal" carries more truth per word than any average.
6. **File** the result on QUESTION-BOARD as this question's first TEETH
   entry. The verdict covers the sampled fork class only; future rounds add
   classes until the fleet holds a **torsion ledger** — which receipt
   species carry curvature (FINISH signals? betterness receipts? adjudication
   rows?) and which are flat. The ledger is the prize; v1 is its first row.

Budget: ~25 min reconstruction (the real work), ~10 min replays, ~5 min
grading. Fits the round with room to spare.

**Why this is the cheapest experiment that *proves* it:** every alternative
is either more expensive or weaker. Live instrumentation of future forks
(wait for nature) is uncontrolled and slow. A real blackout day risks the
fleet's actual memory. A fully synthetic toy fork proves the mechanism *can*
exist, not that the fleet's receipts *do*. Replay is the only design where
the treatment and the control are the **same tape**, differing by one muted
channel — maximum causal isolation per dollar, and the dollar count is zero.

## 5. WHERE THE STORY BREAKS

Applied to my own answer first, so it survives the other school:

1. **Replay drift.** A "flip" might be model-version or context drift, not
   the receipt. — Absorbed by design: present-vs-present replays measure
   exactly this drift; τ subtracts it. Residual risk: drift interacts with
   muting (receipt-present prompts are longer; attention differs). If τ is
   marginal, that interaction is round 2's first control.
2. **Circularity.** The muted replayer infers the receipt from surviving
   context ("the tone implies the lane failed"). — Mitigated by stripping
   all post-fork text; that's also why every diverging replay must quote its
   deciding input, and the quote gets eyeballed for smuggled receipt
   content.
3. **One fork class is not the fleet.** τ is a per-class number. A
   "decorative" verdict on merge-queue forks says nothing about
   doctrine-edit forks. The torsion ledger is the honest scope; anyone who
   reads v1 as a fleet-wide verdict has over-wound the tape.
4. **Ballast is invisible to this instrument** (named in §2). If v1 returns
   DECORATIVE, the correct next move is the **deterrence test** — would
   claims get made differently if writers knew receipts would never be
   checked? — which is ballast's own cheap probe, not a funeral for the
   creed. This experiment answers the question asked and marks the edge of
   its answer.
5. **The pre-registration paradox.** The thresholds were written by the poet
   who hopes for curvature. Mitigation: they were written *before any fork
   was sampled* and committed in this file, timestamped by this round;
   deviations require a ledger row saying so — the ASPIRE
   rollback-unless-verified rule, applied to myself.

**Closing shape:** the fleet has been filing paper into a drawer and calling
the drawer a skeleton. The muted-fork replay is the first X-ray: cheap,
non-destructive, and honest enough to find nothing. A story that can't be
tested is decoration — so is a receipt. Same test for both.
