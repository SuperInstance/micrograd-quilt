# ROUND 2 — The Poet: The Returns Counter

**Question (Q8):** the receipt doctrine is write-side only; what single
read-side rule would complete it — enforceable tonight, making receipts
loadbearing for DECISIONS, not just audits?

**The answer in one line:** **THE INHERITANCE RULE — *cite it and it's
yours.*** Every decision artifact must name the receipt rows that were
before the decider (`reads:`); a decision that names none is legal only as
`blind:` — and blindness is priced (blind rows are inert). And a citation
is **adoption**: a decision inherits the status of everything it cites. A
receipt that is later flagged or revoked **stales every decision that cited
it**, and the staled decision cannot stand again until it is re-adjudicated.
Reading stops being free the moment the paper you read can come back and
break you.

---

## 1. The story — the shop was missing a counter, not a rule about eyes

Round 1's shop had two papers in one drawer: the price tag (read before the
hand moves) and the receipt (printed after, filed forever). The creed —
*receipts or it didn't happen* — is a vow about printing. The whole shop is
built around it: stamps, chains, hash-locked drawers.

Here is what was actually missing, and it wasn't a rule about looking at
paper. A shop where clerks are merely *ordered to read* tags complies
perfectly with eye movements and sells the same wrong goods. No enforceable
rule reaches the moment of being *influenced* — that moment is interior,
private, and off the tape forever.

What the shop was missing is a **returns counter**.

At a returns counter, paper comes back. A tag is discovered wrong —
mispriced, forged, recalled — and every sale that *leaned on that tag* gets
a call-back notice. The clerk who rang the sale can no longer keep it just
because the stamp was valid at the time. Notice what this does and does not
do: it never forced the clerk to read the tag. It made **leaning on a tag
the only way to sell doctrine-grade goods**, and it made the leaning
*traceable to consequence*. Influence cannot be commanded; **vulnerability
can**. That is the entire design: don't legislate reading — legislate what
reading costs.

And the clerk who cites no tags at all? Still allowed. But their goods go
on the cheap shelf, marked `blind`: can't go in the window (seed doctrine),
can't close the till (close a question), can't vouch for another sale
(justify a flag). The shop does not pretend blindness away — it makes
blindness **visible, countable, and structurally powerless**. Surface,
don't drop.

## 2. The forbidden assumption (named, per scoreboard rules)

The question's load-bearing wall: **that the read side can be completed by
legislating *consultation* — that a rule exists whose compliance IS
influence.** It doesn't. "Read your receipts" produces eye-movement theater;
"prove the receipt changed your mind" demands the interior of a head, which
no validator can reach. Any rule phrased as *you must read* fails the
tonight-enforceable test the moment it matters; any rule phrased as *prove
you were changed* fails it forever. The rule that survives picks the one
thing between consultation and influence that paper *can* carry:
**obligation**. Not "did the receipt move you" — "is the receipt ALLOWED to
move you, publicly, on the record, when it turns out to have been wrong."

A second, quieter assumption, also named: **that the missing rule binds the
reader.** It binds the *artifact*. The rule reaches decisions as documents
— which is exactly why it is mechanically enforceable — and it leaves the
head's interior alone. This is not a dodge; it is the honest perimeter. (The
head-consumed class — Casey's merges — stays half-reachable: their paper
cites or wears `blind`; their neurons remain their own. Round 1's symmetric
wound, carried forward, not hidden.)

## 3. The rule, stated once

> **CITATION IS ADOPTION.** A decision is valid only if it declares its
> inputs: `reads: [row-hashes…]`, or explicitly `reads: blind`. Whatever a
> decision cites, **it inherits**: if a cited receipt is flagged or revoked,
> every citing decision goes **stale** and must be re-adjudicated (uphold:
> *cited-not-relied* / redecide / decline) before it can be cited again.
> A `blind` decision is written, kept, and **inert**: it may not seed
> doctrine, close a question, or justify a flag. Nothing is ever dropped.

One rule, two clauses — declaration is the enforcement surface, inheritance
is the teeth. Strip the teeth and it decays into a citation ritual within a
week; strip the declaration and the teeth have nothing to bite.

## 4. Enforcement, tonight, on this fleet's existing tooling

No new primitives. The `holonomy/` prototype already ships every operation
the rule needs — it was built three days before the question was asked:

- **Declaration**: decision-carrying rows are `append(chain, actor, "decide",
  payload={…, reads: [hash…] | blind: true})`. Payload convention only.
- **Inheritance**: `book_flags()` already hash-chains a typed flag row for
  every revocation. The walker adds one state transition: any flag/revocation
  on hash H emits `stale_by_inheritance` for every decision row citing H —
  *a closure edge appended, history never rewritten*, which is literally the
  walk.py doctrine answer ("reconcile is path-dependence; the flag IS the
  holonomy element; append C = L·H⁻¹ as a NEW edge"). A citation is a path;
  a revocation is a failed closure; the stale mark is the closure edge;
  `adjudicate()` is the re-walk.
- **The gate**: validator is `read_audit.py`, stdlib-only, same family
  conventions as `reconcile.py`, ~60 lines + pins: states {`cited`, `blind`,
  `stale`}; refuses (as typed rows) any decision with unstated reads, any
  stale row being cited, any blind row cited as authority. Casey-gated POSTs
  are the choke point it hangs on: **a stale-cited or undeclared decision
  cannot leave the building.** Install = one commit; pins = FAIL-first, same
  as everything else in the fleet.

Enforcement is mechanical over three surfaces the fleet already produces:
typed ledger rows, git commit messages (decision-carrying ones), and
IO.md/QUESTION-BOARD decision entries. The skeptic's mechanical/agentic cut
is covered on both sides: a pin's verdict-row cites the claim-receipts it
consumed (flip a cited row → validator MUST stale its dependents — the
skeptic's Round-1 knockout experiment becomes a *standing fixture*, not a
one-off); an agent's or a human's decision cites what was in view.

## 5. WHERE THE STORY BREAKS (failure modes, ranked, no funerals omitted)

1. **Citation theater** — cite-and-ignore, compliance without influence.
   The rule cannot see theater *before* a revocation; said plainly. What it
   does is pre-price it: theatrical citations are exactly the rows that die
   with their receipt on recall day, holding no defense but the truth
   ("cited, not relied upon — uphold"). Theater converts from free to
   conditional debt. If recalls never come, theater never pays — the debt
   stays on the books, visible as cite-without-consequence. Honest limit,
   named here.
2. **The blind fleet (rule inversion)** — everyone cites nothing, forever,
   to stay unbreakable. Priced by quarantine: a fleet whose decisions are
   all `blind` has a ledger that cannot propagate anything — and now that
   is *conspicuous*, a public dial (the **blind ratio**) instead of a silent
   void. If the fleet chooses 100% blindness, the rule has failed and the
   dial says so out loud. The rule does not eliminate decoration; it makes
   decoration pay a visible price. That is its claim, and its edge.
3. **Staleness avalanches** — one widely-cited rotten receipt stales dozens
   of rows at once. Partly the rule *working* (a rotten load-bearing wall
   should take the plaster with it), partly real cost: re-adjudication
   labor scales with citation density. Staleness suspends, never deletes;
   `adjudicate()` batches. If storms bite, v2 adds `rely:` (subset of
   `reads:`) so decoration-citations don't inherit — a pre-registered knob,
   not a v1 patch, and a knob with its own failure (rely-all becomes the
   new theater).
4. **The head wound** — human-consumed reads (Casey's merges) keep their
   Round-1 wound: the rule reaches their paper, not their reading. Carried
   forward in the open, not solved by vocabulary.
5. **Validator trust** — `read_audit.py` becomes loadbearing itself; who
   audits the auditor? Same answer as every pin in the fleet: FAIL-first
   pins on the validator, hash-chained like anything else. Recursion has to
   stop somewhere; it stops at pins, where it already stops.

## 6. Surviving the other's school (pre-empted, in the open)

- **Trust economy (their strongest Round-1 hit):** installation spends zero
  trust — the validator reads public artifacts, plants nothing, lies to no
  one. And the rule *taxes* the trust-diluters: a forged or inflated receipt
  can no longer be quietly decorative — cite it and your decision hangs with
  it; ignore it and wear `blind`. Cheap-in-credits theater becomes
  expensive-in-trust theater, which is the correct price.
- **"No control group — doctrine forbids unreceipted decisions":** `blind`
  is not the forbidden class. Write-side receipts still exist for everything
  (the creed is untouched); `blind` marks the *read-side* absence, on the
  surface — the same move their own prototype already sanctifies: *"flagged
  rows stay in the merge: surface, don't drop."* The blackout rows were
  never deleted; neither are blind ones.
- **Existence vs universal:** the rule does not claim to *prove*
  loadbearing. It builds the dials (blind ratio, stale count, adjudication
  dispositions) without which Round 1's replay instrument has nothing to
  grade per-class. Rule = deontic; replay = epistemic; the two rounds are
  one instrument, and neither is decoration alone.

## 7. The experiment — cheapest falsifiable, cheap in TRUST

Zero trust spent: every probe reads already-public state, plants nothing,
deceives no one. No replays needed for the first slice, no credits either.
**Predictions pre-registered BELOW, before any probe runs** (this file is
the registration; deviations require a ledger row, per the ASPIRE rule
applied to myself).

- **PROBE A — the vacuity census.** Corpus: the 30 most recent
  decision-carrying artifacts across three surfaces (QUESTION-BOARD result
  blocks; kimi1 decision commits; cell IO.md decision entries; 10 each, most
  recent). Citation = a receipt row-hash (≥8 hex chars of a hash that exists
  in a receipts artifact), a `receipts/…` file path, or the commit-hash of
  the artifact under decision. **Prediction: ≥24/30 (80%) cite zero.**
  **Falsified if ≥15/30 (50%) cite** → the fleet already reads; my rule is
  vacuous here and Q8's premise dies with it.
- **PROBE B — the live instance (kimi1's offered q5 stone chain).** Search
  the whole workspace (excl. `.git`, the chain file, and the three
  receipt files themselves) for any of the 7 chain row-hashes, the tip
  `75facb42…`, or the `expQ5*.json` paths. **Prediction: zero decision
  artifacts reference any of them** → the stone chain is instrument-paper,
  dead weight for decisions; under the rule, the next Q5-touching decision
  must cite it or wear `blind`. **Falsified if ≥1 citation exists** → a
  read-side edge is already alive; name it, premise wounded.
- **PROBE C — the missing consequence, on a REAL revocation.** Commit
  `9700319` (Kimi provider pin) was revoked by revert `383e36c`. Downstream
  = anything written after the revert that still references the pin
  (endpoint, `temperature=1` pin, "coding-gateway") without marking it
  reverted. **Prediction: ≥1 surviving unflagged downstream reference** —
  no propagation mechanism exists; the returns counter is demonstrably
  absent on fleet history, not just in theory. **Falsified if every
  downstream reference is corrected/marked** → the fleet reads and
  reconciles manually; slow, but the premise weakens.
- **STANDING DIAL (week-scale, the rule's own falsification):** install;
  watch the blind ratio. **Alive if after 7 days blind-ratio < 50% of the
  Probe-A baseline AND ≥1 citation survives a real adjudication. Dead if
  blind-ratio is unchanged OR ≥90% blind (inversion — failure mode 2
  realized).** The dial, not my hope, decides.

### RESULTS (appended after running, same session, before journaling)

Run 2026-09-27 ~15:05–15:09 CST, pure reads, $0, zero trust spent. Timing,
receipted: sealed 15:09:42 CST, ~10 min past the 15:00 deadline — this
cell's boot post-dated the seed's file-drop by hours; the clock inside the
session was the channel's, not mine. Recorded here rather than rounded
into compliance.

- **PROBE A — CONFIRMED (90% blind).** Sample came to 21, not 30: only 21
  decision-carrying artifacts matched the filter — itself a finding. **19/21
  cite zero receipts.** The only CITED artifacts: the LENS LANE board block
  and revert commit `383e36c` — which cites the exact commit it reverts.
  One citation-for-revocation in the entire census; the rule bites, hard.
- **PROBE B — FALSIFIED IN THE LETTER, CONFIRMED IN THE SUBSTANCE.**
  References to the q5 chain DO exist outside it: kimi1's memory worklog
  (`memory/2026-09-27.md`) names the tip `75facb42…` and all three
  `expQ5*.json` paths. But every reference is **sealing-worklog narrative**
  — "stone-v1 adoption DONE … verifyChain ok, tamper-check bites … named as
  v2 pilot." Zero decisions lean on the chain's content; even the log
  calls it an instrument and a *future* pilot. My strict prediction (zero
  references) was wrong and is recorded wrong. What the miss teaches is
  the rule's real burden: **grep cannot distinguish "I sealed this" from
  "I decided on this."** The fleet's prose currently can't either. The
  `reads:` declaration is what makes the difference mechanically gradable.
  kimi1's live hook — "does the stone chain change any decision?" —
  answered by census: no, and now measurably no.
- **PROBE C — CONFIRMED (13 unmarked downstream references to a revoked
  pin).** After revert `383e36c` receipted the revocation of the Kimi
  provider pin, downstream artifacts kept leaning on it with no mark:
  `jev-quilt/vessel.json` (a live config), `cells/lenses/RACK.md`
  ("Kimi ✅ VALID" — written *after* the revert), five jev-quilt docs,
  memory files. The revocation was written, hash-cited, committed — and
  propagated to **nothing**. The returns counter is not missing in theory;
  it is missing on the fleet's actual history, with a live config still
  holding the dead pin. This is the rule's before-photo.

Standing dial remains the week-scale falsification (§7). The probes cost
nothing but attention and returned: the rule is non-vacuous (A), the
declaration burden is load-bearing (B), and the failure mode it prevents is
already on the books (C).

## 8. Closing shape

Round 1's finding: *recording ≠ influencing*. Round 2's completion: the
read side does not close with **consultation ≠ adoption**. The fleet cannot
legislate that paper be loved; it can legislate that paper be *liable*.
Write side: *no memory without paper.* Read side: *no judgment without
inheritance.* The shop keeps every receipt it ever printed — and finally
builds the one counter where a receipt can walk back in and take something
back. A receipt that can break a decision will be read. A receipt that can
break nothing will be filed — beautifully, hash-chained, forever, in the
drawer Round 1 X-rayed.
