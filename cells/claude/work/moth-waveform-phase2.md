# moth-waveform Phase 2 — duck-sensitivity receipts
**Design, claude cell, 2026-09-27. Grounded in:** the live README
(SuperInstance/moth-waveform@main, pushed 2026-09-26T18:46Z, tree verified via
`gh api`), Phase 1 calibration numbers (entropy 1.98/4.54/3.98 of 6 bits,
thresholds `_EAR_STRUCTURE_MAX = 3.0`, `_EAR_NOISE_MIN = 3.5`, swap overlaps
0.967/0.101), and the live MOTHquantum engine catalogue
(`work/mothquantum-api.md`).

## 0. The one-sentence goal

Phase 1 hears *whether* the board sings; Phase 2 names *which duck* makes it
sing — with a per-duck receipt that would fail loudly if the instrument went
deaf.

## 1. The two kick operators (time is the protagonist, value is the control)

The README's thesis: knots are temporal variables, moving one reshapes the
local temporal neighborhood. So Phase 2 defines **two** operators and refuses
to conflate them:

- **K_T (temporal kick):** `t_i → t_i + δ·Δ_i`, Δ_i = mean gap to neighboring
  knots. This moves the duck *in time* — the operator the thesis is about.
- **K_V (value kick):** `y_i → y_i + δ·σ_y`, σ_y = series std. Control. If a
  duck responds equally to K_T and K_V, the ear is hearing *data perturbation*,
  not *time geometry* — that is a named finding against the thesis, and the
  receipt must be able to say so.

δ sweep: `{−0.5, −0.25, +0.25, +0.5}` (fractions of local spacing/σ). The
sweep is not decoration — it yields the **asymmetry receipt** below.

## 2. Three instruments per (duck, δ)

For each kick: recompute the curvature field from the perturbed knots, build
the WH power spectrum, prepare as amplitudes via the `value_setting()` seam
(QPAM `encode()` stays banned — Phase 1 scar), measure.

1. **ΔH_i(δ)** — signed entropy shift of the spectrum, bits (of 6).
   Sign is interpreted: kicked carrier ducks of a periodic regime should
   *raise* entropy (scramble phase); a duck whose kick *lowers* entropy is a
   smoothing duck (it was fighting the regime). Signed receipts, not magnitudes.
2. **E_i(δ)** — echo overlap: measured swap test between pre-kick spectrum
   state ψ and post-kick state φ, `overlap = 2·P(ancilla=0) − 1`. E ≈ 1 → the
   kick didn't bend the board; E → 0 → that duck *is* the spectrum. This makes
   the sensitivity measurement quantum-native (interference, not a dot
   product) and reuses Phase 1's swap machinery verbatim.
3. **Reach vector r_i** — which WH bins moved beyond the noise floor,
   renormalized. This is the bridge to hardware: it has the shape of an
   otoc-echo tap profile (§5).

## 3. The noise floor is measured in-run, never assumed

This is the fleet-murmur lesson transposed: pins that don't arm a live peer
pass vacuously; a floor that's a constant can't catch a broken instrument.

Per report, before any kick:

- **σ_H (shot noise):** std of H over R re-preparations of the *unchanged*
  state (fresh circuits, different shot seeds; R = 8 to start).
- **No-op kick:** run the full kick pipeline with δ = 0 (parse → decompose →
  prepare → measure). If |ΔH_noop| > k·σ_H, the pipeline itself is leaking
  signal → the whole report is REFUSED with `reason: "no-op kick produced
  signal {value} > floor {value}; instrument broken"`. The report carries the
  no-op value either way — a receipt that hides its null run is a phantom.
- **Floor:** `floor = k·σ_H`, k = 2 named. A kick "counts" iff
  `|ΔH_i(δ)| > floor` **and** `E_i(δ) < 1 − floor_E` (both instruments must
  agree; `floor_E` = 2·σ_E measured the same way from E of repeated
  preparations).

## 4. Verdicts — every one names its reason

```
CARRIER            — exactly one duck clears floor on both instruments.
                     Receipt names duck, δ, ΔH (signed), E, reach ‖.
MULTI-CARRIER      — ≥2 ducks clear floor within floor of each other.
                     Receipt names the tie set + each member's margin.
DISTRIBUTED        — no duck clears floor. The regime is genuinely spread.
                     This is a finding, not a failure.
VALUE-CARRIER      — top duck clears K_V but not K_T: the regime hangs on a
                     data outlier, not a temporal variable. Direct test of
                     the thesis; receipt states which operator heard it.
REFUSED (pre)      — past_entropy ≥ _EAR_NOISE_MIN: no structure to
                     attribute (why attribute what the ear can't hear?).
REFUSED (inst)     — no-op kick leaked signal, or E/ΔH instruments disagree
                     on the top duck. Instrument indictment, named.
```

Plus the **asymmetry receipt** per counted duck:
`A_i = |ΔH(+δ_max) − ΔH(−δ_max)| / max(|ΔH(+δ_max)|, |ΔH(−δ_max)|)`.
A_i near 0 → linear responder; A_i near 1 → the duck sits on a curvature
cliff (one direction re-smooths, the other scrambles). Cliff ducks are named
as such — they are exactly the "where the data forces hard bends against the
board" the README points at.

## 5. The OTOC bridge — why this shape matters for Phase 4

The influence matrix `C[i, bin] = reach vector of duck i` is the classical
cousin of the out-of-time-order correlator `⟨[V_i(t), W_j(0)]²⟩`: perturb at
site i, read the response at delayed positions. The live API
(`work/mothquantum-api.md`) confirms `otoc-echo-v1` (1 credit — the cheapest
quantum engine on the board) parameterizes *exactly* this protocol:
`kick_site`, `depth` (tap time slots), `include_taps`, `min_tap_level`,
`disorder` ("localises the echo; the only lever that makes `seed` matter" —
the API's own param description), `exact: true` on aer (infinite-shot
expectation values).

**Mapping table (ship it in the receipt):** duck i ↔ `kick_site`;
curvature WH bin t ↔ tap depth t; δ sweep ↔ kick amplitude; A_i ↔
disorder sensitivity. Consequence: a Phase 2 report's reach profile is
directly comparable to a Phase 4 hardware run, and **one** `otoc-echo-v1` run
reads all taps at once — on hardware, the whole per-duck sweep collapses to
kicks × 1 job. Design the classical matrix in tap shape now so the Phase 4
diff is meaningful.

## 6. Planted calibration — the instrument earns trust first

Doctrine: the planted protocol must REFUTE planted noise before fleet data.
Pins (FAIL-first, `tests/test_sensitivity.py`), same seeds/shots discipline
as Phase 1 (42/1/13, 2000 shots):

| # | Planted truth | Must happen | Catches |
|---|---|---|---|
| P1 | Regime generated by one duck: periodic structure whose *phase is set by knot 7's time position* (displacing it shifts every phase; displacing others locally re-smooths) | verdict CARRIER, duck = 7 | a deaf meter returning DISTRIBUTED |
| P2 | Smooth spline noise, no carrier | DISTRIBUTED or REFUSED(pre), never a named carrier | false attribution |
| P3 | **δ=0 no-op run must show \|ΔH\| ≤ floor, measured in-run** | report refuses itself if the null leaks | vacuous-pass trap: gate that "passes" without a live floor measurement must fail the test |
| P4 | Regime hanging on a value outlier (one y_i off-tension) | VALUE-CARRIER via K_V, K_T silent on that duck | K_T/K_V conflation — the thesis hearing itself everywhere |
| P5 | Phase-shuffled P1 (Phase 1's own scar: shuffled strains the board *more*) | pre-entropy already ≥ noise band or carrier set differs from P1; receipt must not silently inherit P1's carrier | threshold inherited from Phase 1 without re-derivation on kicked geometry |

Named expected margins (to be verified, not asserted): on planted P1,
carrier |ΔH| should exceed runner-up by ≥1 bit (Phase 1 saw >2-bit gaps
between structure and noise; per-duck gaps will be smaller — the test asserts
what the calibration run actually measures, and the receipt quotes those
numbers as the threshold's provenance, exactly like `_EAR_STRUCTURE_MAX`
quotes its table).

## 7. Cost & module layout

**On Aer (Phase 2, this build):** per duck, 4 δ × 2 operators × (2 state preps
+ swap circuits) at 6 qubits × 2000 shots — same order as Phase 1's calibration
table, minutes not hours. Seeds recorded per circuit in the receipt (replay
doctrine).

- `moth_waveform/sensitivity.py`:
  - `kick_duck(dec, i, delta, operator="temporal"|"value") -> Decomposition`
  - `duck_sensitivity(dec, shots=2000, deltas=(−.5,−.25,.25,.5), r_floor=8, k=2.0)
     -> SensitivityReport` (runs no-op + σ_H first; refuses itself per §3)
  - `SensitivityReport.receipt() -> dict` — FINDING/v1-compatible
    (quilt-doctor format): subject, operators, deltas, floor measurement
    {σ_H, σ_E, k, noop_ΔH}, per-duck {signed ΔH per δ, E, reach, A_i,
    verdict}, verdict block with named reason, otoc-echo mapping table,
    seeds, shots, calibration pointer ("thresholds derived this run; Phase 1
    calibration: README table").
- `tests/test_sensitivity.py`: P1–P5 pins, FAIL-first.

**Explicitly out of scope for Phase 2:** any POST to MOTHquantum (otoc-echo
run is Phase 4, Casey-gated, 1 credit); comet-qrng-v1 seeds for planted
inputs (certified randomness would be nice-to-have provenance, 5 credits/run,
also Casey-gated — deterministic seeds are the receipts-doctrine default
because replay beats attestability).

## 8. What would falsify Phase 2 (pre-registered)

- P1 fails to isolate the planted duck → the per-duck attribution doesn't
  resolve at 6 qubits / these margins; escalate qubits or report the
  instrument's resolution limit as the finding.
- K_T and K_V indistinguishable on *all* planted cases → the temporal-variable
  thesis itself takes the hit, and the receipt says so. The instrument serves
  the doctrine, not the reverse.
