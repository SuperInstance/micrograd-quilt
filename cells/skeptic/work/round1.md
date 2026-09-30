# ROUND 1 — the Skeptic's answer

**Question:** What is the single cheapest experiment that would prove the
fleet's receipts are LOADBEARING rather than decorative — i.e., that a
decision actually changed because a receipt existed?

**School method: kill the premise first.** The interesting version of this
question is the one I'm about to try to make false. If it survives, it earns
a hearing.

> **Note:** intended for `work/round1.md`, but `cells/skeptic/` is root-owned
> and this cell runs as uid 1000 (`cell`) — no write access, no passwordless
> sudo. Following the probe precedent, the deliverable lives here in
> `/tmp/skeptic-work/round1.md` until Casey `chown`s the cells tree.

---

## 0. KILL THE PREMISE FIRST

The question is mis-set. Three kills, in order of depth.

### Kill 1 — "loadbearing" is not a property of the receipt. It's a property of the read.

A receipt is loadbearing iff some **later** decision branches on its content.
The receipt alone tells you nothing about that. The fleet's entire doctrine
— "receipts or it didn't happen" — is a **write-side rule**: it forces the
emission of receipts. It contains **zero read-side rule**: nothing requires
that a receipt be read, and nothing requires that a read receipt change a
decision. A perfectly-compliant fleet can be 100% write-side and 0%
loadbearing: every agent writes receipts, nobody's decision ever depends on
one. So you cannot answer the question by looking at receipts — their
existence, volume, quality, hash-chain integrity, or VERIFIED_CLAIMS count.
You can only answer it by looking at **decisions**.

### Kill 2 — "prove loadbearing" is an existence claim; "prove decorative" is universal. They are not symmetrical.

"Prove loadbearing" needs **one** clean case: one decision that demonstrably
changed because a receipt existed. Cheap, in principle. "Prove decorative"
needs an exhaustive negative: *no* receipt ever changed a decision. That
cannot be proven cheaply, or at all, from a finite record. The question asks
for the cheap experiment that proves **loadbearing** — so the right target is
one clean existence proof, not a survey. But note the trap: a single
loadbearing receipt proves the *existence* of loadbearing, **not** that the
system is loadbearing in general. (Flagged again in §4.)

### Kill 3 — the naive control is definitionally empty.

The textbook experiment is A/B: same decision, receipt present vs receipt
absent, diff the outcome. That experiment **cannot run in this fleet**,
because the doctrine collapses the "absent" arm to zero. "Receipts or it
didn't happen" means a decision without a receipt is not a decision — it
didn't happen. There is no control group of "decisions made without
receipts." So the premise "compare a decision with a receipt to the same
decision without one" smuggles in a state that the fleet's own ontology
forbids. The experiment must vary the receipt's **content**, not its
presence.

---

## 1. FORBIDDEN ASSUMPTION NAMED

> **That a receipt matters by being *written* rather than by being *read*.**

The fleet has treated "receipts or it didn't happen" as if it were also
"receipts ⇒ it changed something." It isn't. The doctrine is a production
rule with no consumption rule, and the entire loadbearing question is a
consumption question. Everything downstream — the hash chains, the honesty
pins, the VERIFIED_CLAIMS ledger — certifies that receipts are *real and
unforgeable*. None of it certifies that receipts *do anything*. A receipt
whose truth is perfectly certified and whose read never happens is the
fleet's most expensive decoration.

Corollary forbidden assumption, the one I think the Poet will rely on:
**that "cheap" is measured in credits.** It is not. The fleet's receipts are
a *credibility economy*; the one asset that makes a receipt worth anything is
trust. Any experiment that spends trust is not cheap, no matter how few
credits it burns. I will return to this — it is where the whole answer turns.

---

## 2. THE FLEET'S RECEIPTS ARE TWO CLASSES, AND ONLY ONE HAS A CHEAP ANSWER

Reading the actual receipts (pong-quilt PLAYLOG, honesty pins, REFUSAL
vocabulary), they split cleanly:

- **Mechanical receipts** — honesty pins, VERIFIED_CLAIMS, FAIL-first pins,
  the `verify()` two-way match, the doctor's tamper→`hash_mismatch`. These
  feed a **deterministic consumer**: a pin is a function from claim-state to
  PASS/FAIL. Flip the claim, the pin trips. Here "decision" means "the
  verifier's verdict."
- **Agentic receipts** — journal entries, findings, "REFUSAL: engine params
  must be wrapped," a PLAYLOG line a human (Casey) is supposed to read and
  then decide "merge / don't merge / refactor / don't." Here "decision"
  means a **person's or agent's choice**, and the consumer is a head, not a
  function.

This distinction is the whole argument. The question as posed is really two
questions wearing one coat:

1. *Do the mechanical receipts change a deterministic verdict?* — **Already
   answered, and answered cheaply, and the fleet didn't notice it had proved
   the point.**
2. *Do the agentic receipts change a human decision?* — **This is the actual
   open question, and for it there is no cheap experiment.** Naming that is
   the Skeptic's contribution.

---

## 3. THE SINGLE CHEAPEST EXPERIMENT

**Flip one field in one receipt, offline, and replay the consumer. Diff the
decision.**

This is the fleet's own FAIL-first doctrine aimed at the receipt system
itself, instead of at the claims the receipts *report*. It is **$0, zero
new infrastructure, zero hash-chain breach, and zero trust spent** — because
you never touch the live WAL and never ask a live agent to decide on
poisoned input.

Concretely, three steps:

1. **Pick the highest-stakes receipt→decision edge in the fleet.** The best
   candidate is a *mechanical* edge where a deterministic consumer already
   exists: a VERIFIED_CLAIMS pin whose PASS/FAIL a later artifact (a count
   pin, a page-glue pin, a gate, a merge rule) depends on. The pong-quilt
   honesty-pin is the canonical example — the pin that trips when a claim
   names a file that doesn't exist.
2. **Flip exactly one field of the receipt's loadbearing claim to its
   opposite**, in an **offline copy**. Change `perms === n!` to a Monte-Carlo
   impostor. Change the named file's hash. Change `success_rate` to its
   complement. Hold every other bit fixed.
3. **Replay the consumer and diff the verdict.** Run the pin / `verify()` /
   the consuming gate once on the real receipt, once on the poisoned receipt.

**Interpretation table (this is the falsifiable payoff):**

| Replay outcome | What it proves |
|---|---|
| Verdict **flips** with the field | The receipt is **loadbearing**. The decision is a pure function of receipt content — the receipt caused the verdict, because the only thing that changed was the receipt. Existence proven, $0 spent. |
| Verdict **does not flip** | That receipt is **decorative**: the consumer doesn't actually branch on the field you flipped. Either the field wasn't loadbearing, or nothing consumes it. |

For the mechanical class, note the embarrassing fact: **the fleet already ran
this experiment and logged the loadbearing result.** PLAYLOG: "FAIL-first
verified by running: pin file absent on pristine origin/main → honesty
two-way pin trips." That is a knockout on a receipt's backing — delete the
thing the receipt certifies, and the verdict flips. That is *already* a
$0-proof that mechanical receipts are loadbearing. The cheapest new
experiment is just the generalized, field-level version of it.

---

## 4. HOW THIS COULD BE WRONG (mandatory)

**This is where the answer is most likely to die. Kill it properly.**

**(a) Existence ≠ prevalence.** One flipped verdict proves *one* receipt is
loadbearing. It proves nothing about whether the fleet's receipts are
loadbearing *in general* — and the question, read generously, asks about the
system, not one pin. My experiment is the cheapest thing that proves the
*narrow* claim ("a decision actually changed because a receipt existed") and
silent on the broad claim ("the receipts are loadbearing"). If the judges
score the broad claim, I have under-answered; I am betting the narrow claim
is what "prove" was actually pointing at.

**(b) The mechanical/agentic cut may be doing the real work, and it flatters
me.** I picked the mechanical class because that's where a cheap decisive
test exists. But the *interesting* receipts — the ones the question is
really about, the ones a Poet would sing about — are the **agentic** ones,
and my experiment **cannot touch them.** You cannot replay Casey's head.
For the agentic class the only decisive test is a **live planted-false
receipt**: seed a receipt that asserts the opposite of truth at a real
decision point and watch whether the downstream human/agent decision follows
the receipt or the truth. And that experiment is not cheap, for the reason in
(c).

**(c) The hidden cost is trust, and trust is the one asset the economy runs
on.** The planted-false test is cheap in credits — a single local write,
zero API spend — but it is the **most expensive experiment the fleet can
run**, because it spends credibility. A silent false receipt corrupts a
hash-chained WAL and is itself an unreceipted act (the doctrine's cardinal
sin). A *declared* false receipt triggers an observer effect: the
decision-maker, warned there's a poison in the stream, scrutinizes receipts
they would normally trust — so you measure suspicious reading, not normal
reading. Either way you burn the exact thing you're trying to value. **This
is the real forbidden assumption, doubled: the cheapest-in-credits
experiment is the most-expensive-in-trust experiment, and the question's use
of "cheapest" silently assumes the two are the same.** They are not, here,
and naming that is the whole answer.

**(d) "Decision changed" is under-specified and I may have changed the
subject.** The question says "a decision actually changed." I have equated
"the deterministic consumer's verdict flipped" with "a decision changed."
A pin's PASS→FAIL is a verdict, not necessarily a *decision* in the sense
the question means (a merge, a refactor, a human choosing). If the judges
mean human decisions, then my $0 mechanical experiment answers a different
question, and the honest answer to the *original* question is: **there is no
cheap experiment for the agentic case — the cheapest decisive test costs
trust, and trust is not cheap.** I am making that trade explicit rather than
hiding it behind a mechanical proxy.

**(e) The flip might not hit a loadbearing field, and I'd misread a miss.**
If I flip a field the consumer happens not to use, "verdict doesn't flip"
tells me only that *that* field is inert, not that the receipt is
decorative. The experiment's power is entirely in *which* field I flip — I
must flip the field that is *claimed* to be the loadbearing one, not any
field. Get that wrong and a loadbearing receipt will read as decorative.
This is the experiment's sharp edge and its failure mode simultaneously.

**(f) The "already answered" claim could be wrong.** I read PLAYLOG's
"pin file absent → pin trips" as proof of mechanical loadbearing. But that
only proves the pin is *sensitive to its own claim's backing* — it does not
prove the pin's verdict *changed any downstream decision*. The pin could
trip and everyone could ignore the red. That gap — between "a verifier
noticed" and "someone acted on the notice" — is exactly the agentic
remainder in (b), and my "already answered" confidence may be smuggling it
across.

---

## 5. THE ONE-LINE ANSWER

The cheapest experiment that proves a decision changed because a receipt
existed is **the offline one-field knockout: flip the loadbearing field of
the highest-stakes receipt, replay its consumer, and watch the verdict flip
— $0, no WAL breach, no trust spent.** And the reason it's the answer is
also the reason it's a warning: it only works where the consumer is a
function. Where the consumer is a head, cheap vanishes — the cheapest
decisive test costs trust, and the fleet's receipts are a trust economy, so
the question's "cheapest" was already the forbidden assumption.
