# Cell-Assembly Convergence — the seam where fleet demos compose instead of collide

**Date:** 2026-09-24
**Lane:** doctrine-cell-harness (cron `27baeeed`)
**Siblings studied:** `SuperInstance/quilt-cell-harness` (v0.2.0–v0.5.0), `SuperInstance/quilt-full-stack-demo`, `SuperInstance/pong-quilt`, `SuperInstance/quilt-echovision`
**Deliverable status:** this note + [quilt-cell-harness#1](https://github.com/SuperInstance/quilt-cell-harness/issues/1) (filed 2026-09-24 14:08 GMT+8, open)
**Doctrine:** cite files, not vibes. Friendly competition — every sibling is right for its scale. Refusal-shape honesty about what does not converge.

---

## 0. The siblings in one paragraph each

**quilt-cell-harness** is the architecture repo. One `Cell` (`cell.py:161`) = `Engine` (`cell.py:75`, substrates `stub_llm/echo/reverse/sha256`) + tiled `Compartment`s (`cell.py:83`) + `NudgeSubstrate` negative-space (`cell.py:95`) + `PTO` power-take-off (`cell.py:126`) + `WitnessChain` (`cell.py:151`). Temporary compartments that process energy ≥3 uses **crystallize** into permanent PTO-exposed mechanisms (`cell.py:254-282`). `quilt.py` stacks cells into communities (`Quilt.ask` at `quilt.py:35`, meta-witness, 5-condition `is_alive` at `quilt.py:111`); `qult.py` stacks quilts into organisms; `llm_cell.py` wires a real LLM as one substrate (`zai_substrate`, `llm_cell.py:44`).

**quilt-full-stack-demo** is the canonical hello-world: one file threading FLUX VM (the Cell) + double-entry `ConservationPolicy` (`examples/full-stack.py:117`) + LLM substrate (`examples/full-stack.py:149`) + PLATO tile validate/score + fleet polyformality canary (`FLEET_CANARY_TARGET = 0x024a555471370b18d`, `examples/full-stack.py:62`). Crucially it **already composes the harness**: `sys.path.insert(0, REPO_ROOT / "quilt-cell-harness")` then `from cell import Cell, Compartment` (`examples/full-stack.py:31-33`). The seam isn't hypothetical — it's proven.

**pong-quilt** is "ML you can watch think": a real genetic algorithm (6→10→3 tanh) plays Pong in the browser, with projection cells rendering the granular state vector, black-swan angle kicks, and a Level-2 scratch tile: **JEV** (`MoveSuggestion` type + validator, `index.html:75-78`), **MOTH** (hash-chained receipt rows, `index.html:70-73`), micro-JEPA (LMS 1-step predictor, `index.html:80`), and a bring-your-own-endpoint **LLM seam** (`index.html:92-95`). Refusals are first-class: `receipt("REFUSAL/v1",0,0)` on JEV failure (`index.html:97`).

**quilt-echovision** is sonar-vision: a phone chirps (2→8 kHz), cross-correlates echoes into an echogram, and learns echo→scene mapping into an on-device **nursery** (`index.html:85`). A cosine-similarity **discriminator** renders three verdicts — `>0.9` healthy, `0.6–0.9` drifting, `<0.6` **POT-BOUND** (`index.html:103-105`) — and pot-binding is the mechanism, not an error state.

---

## 1. The drum mapping: compartments/PTO onto skin / shell / tension

Our doctrine (`memory/2026-09-24.md`, "The drum/superatom"): a resonant instrument has **skin** (the I/O surface that vibrates), **shell** (the canonical frame that bounds the resonance), **tension** (what tightens the skin against the shell — receipts, GAN pressure, weight), and the **player** as fourth element (the puppeteer tuning the seams with strings; the goal is an echo of the player's residual self-image sounding back as *right*).

| Drum element | quilt-cell-harness | pong-quilt | quilt-echovision | full-stack-demo |
|---|---|---|---|---|
| **skin** (resonant I/O surface) | `PTO` (`cell.py:126-148`): ports `state / constraints / witness / crystal_*`; `Quilt.ask` (`quilt.py:35`) as neighbor-coupled skin | the page itself + `MoveSuggestion` port — suggestion in, weighted move out; attach-probe validation (`index.html:140-143`) is skin that refuses bad energy | chirp-out / echo-in; the echogram IS the skin's vibration made visible | the flow surface: `run_flow` (`full-stack.py:217`) + trace recorder (`full-stack.py:49`) |
| **shell** (canonical frame) | `COMPULSORY_TISSUE` (`cell.py:43-50`): witness/nudge/state/refusal compartments over the `Engine` substrate pool (`cell.py:75-80`). Without them it's "a substrate pool, not a cell" (`MORPHOGENESIS.md`) | game core (`core.js`) + GA population loop + `MoveSuggestion` schema — the frame every L2 tile must pass through | emit→correlate loop (`index.html:60-67`) + nursery schema (`index.html:85`) + 343 m/s ÷ 2 physics | the five-piece frame (FLUX + conservation + LLM + PLATO + polyformality) — the demo's whole point |
| **tension** (receipts / GAN pressure / weight) | `NudgeSubstrate.forbidden` + `witness_refusal` (`cell.py:95-123`) + `WitnessChain` receipts (`cell.py:151-158`) + crystallization threshold `uses>=3` (`cell.py:254`) + `canary()` (`cell.py:301`) | MOTH hash-chained rows (`index.html:70-73`) incl. `REFUSAL/v1`; fitness as GAN pressure; the **weight slider** (`index.html:52`) is literal tension control | cosine discriminator verdicts (`index.html:98-105`) — the GAN pressure made numeric; POT-BOUND is the drumhead at max tension | `ConservationPolicy.settle` raises on imbalance (`full-stack.py:138-142`) — tension as accounting invariant |
| **player** (fourth element) | the environment sending fuel (`MORPHOGENESIS.md` "fuel-driven assembly") | the human at the weight slider + `EXPERIMENTS.md`'s GAN-on-the-process: play-tester as discriminator | the user moving + collecting syncs — the GAN's escape route is the user (`README.md`) | the operator running one file; the trace is their echo |

**Reading:** the cell-harness skin is *implicit* — PTO ports resonate by name-hash routing. pong-quilt made the skin explicit and put it in a browser. echovision made the tension explicit and put it in a cosine gate. full-stack-demo made the shell explicit and put the whole frame in one file. Each sibling completed a different corner of the same drum.

---

## 2. Collision report — where they overlap, where they compose

### Collisions (same seam, incompatible socket)

1. **Two `zai_substrate` wrappers.** `llm_cell.py:44-71` and `full-stack.py:149-192` both wrap `api.z.ai/api/coding/paas/v4/chat/completions` with `glm-5.3-flash`, but diverge: timeout 20s vs 15s, `max_tokens` 60 vs 80, fallback strings `[zai-error:…]` vs `[zai-fallback:…]`, User-Agent `quilt-cell-harness/0.5.0` vs `superinstance/full-stack-demo/1.0`. Same substrate, two sockets — a fleet-wide behavior drift waiting to happen.
2. **Three receipt formats, no shared verify.** WitnessChain events (`cell.py:151-158`, sha256-16 over sorted JSON) vs MOTH rows (`pong index.html:70-73`: `{i,kind,move,conf,gen,prev,hash}`, 64-hex chain over the previous hash) vs ConservationPolicy ledger (`full-stack.py:117-146`, sha256-16 payload hashes + balance invariant). Three ledgers, three hash conventions, no `verify()` that reads across.
3. **"Cell" means three things.** `cell.py:161` `Cell` (Python dataclass) vs pong-quilt "projection cells" (state-vector UI strips, `README.md` L1) vs echovision "loopcell waveform" (`README.md`). Fleet docs that say "the cell" are now ambiguous by one syllable.
4. **Parallel learning mechanisms.** Crystallization (`uses>=3`, `cell.py:254`) vs micro-JEPA LMS (`pong index.html:80`) vs GA fitness (`core.js`) vs k=1 NN nursery growth (`echovision index.html:89-96`). Four "growth" stories with no shared statement of what counts as improvement, evidence, or promotion.
5. **Four tension vocabularies.** `REFUSED` (witness events) vs `REFUSAL/v1` (MOTH rows) vs `POT: BOUND` (discriminator verdicts) vs `RuntimeError: Conservation violation` (full-stack raise). The fleet's most doctrinally precious concept — the honest refusal — has no shared row shape.

### Compositions (where they already fit)

1. **full-stack-demo proves harness composition end-to-end** (`full-stack.py:31-33`): imports the real `Cell`, runs real flows, balances a real ledger. The seam works; it just isn't named.
2. **pong-quilt's LLM seam is a substrate.** A validated `MoveSuggestion` is exactly what a crystallized compartment returns through a PTO port. JEV validation (`index.html:75-78`) is a `validator` on the port — the schema already exists, in JavaScript.
3. **echovision's discriminator is a verdict vocabulary.** `HEALTHY / DRIFTING / POT_BOUND` (`index.html:103-105`) generalizes: witness-healthy, nudge-drifting, pot-bound is the same shape as MOTH's `L2 / REFUSAL/v1 / DEATH` rows (`index.html:99,125`). One `Discriminator` enum covers both.
4. **MOTH rows are a view over WitnessChain events.** `{kind, prev_hash, row_hash}` is isomorphic to `{event, ref}` (`cell.py:151-158`) with the chain made explicit. A `TensionLedger` can render both.

---

## 3. The unified cell-assembly SEAM spec — `seam/cell_assembly.py`

One page. Thin layer; touches no sibling's internals. ~120 lines. Lives in quilt-cell-harness (it's the architecture repo), imported by demos that want to compose.

```python
# seam/cell_assembly.py — the jack socket, not a new instrument.
from dataclasses import dataclass, field
from typing import Callable, Optional
import hashlib, json, time

# --- 1. Port: the typed skin ----------------------------------------------
@dataclass
class Port:
    """A PTO port with a typed signature + validator + weight.
    JEV's MoveSuggestion is the reference implementation of (signature, validator)."""
    name: str                      # namespaced: "flux.exit", "pong.suggest", "echo.scene"
    signature: str                 # human/machine-readable type string
    handler: Callable              # the substrate callable
    validator: Optional[Callable] = None   # JEV-style; None = trusted
    weight: float = 1.0            # tension knob; the slider, banked

    def __call__(self, energy):
        out = self.handler(energy)
        if self.validator:
            bad = self.validator(out)
            if bad:
                return Refusal(port=self.name, reason=bad, energy=energy)
        return out

@dataclass
class Refusal:
    """THE first-class row. One shape for REFUSED / REFUSAL/v1 / POT_BOUND / conservation-raise."""
    port: str; reason: str; energy: object; ts: float = field(default_factory=time.time)
    def row(self) -> dict:
        return {"kind": "REFUSAL/v1", "port": self.port, "reason": self.reason,
                "energy_hash": _h(repr(self.energy)), "ts": self.ts}

# --- 2. TensionLedger: ONE hash-chain for all receipts ---------------------
@dataclass
class TensionLedger:
    """WitnessChain + MOTH + ConservationPolicy in one verify()able chain.
    append-only; verify() re-derives every row hash from genesis."""
    chain: list = field(default_factory=list)
    head: str = "0" * 64
    def append(self, kind: str, payload: dict) -> dict:
        row = {"i": len(self.chain), "kind": kind, **payload, "prev": self.head, "ts": time.time()}
        self.head = _h(json.dumps(row, sort_keys=True, default=str)); row["hash"] = self.head
        self.chain.append(row); return row
    def verify(self) -> bool:      # re-derive from genesis; False on any tamper
        h = "0" * 64
        for i, row in enumerate(self.chain):
            r = {k: v for k, v in row.items() if k != "hash"}
            if row.get("prev") != h or row.get("i") != i: return False
            h = _h(json.dumps(r, sort_keys=True, default=str))
        return h == self.head

# --- 3. SubstrateRegistry: ONE fleet-wide LLM wrapper ----------------------
class SubstrateRegistry:
    """Register, don't copy. llm_cell.zai_substrate and full-stack.zai_substrate
    collapse to one entry with config (timeout, max_tokens, fallback_tag)."""
    def __init__(self): self._substrates = {}
    def register(self, name: str, fn: Callable, config: dict | None = None): self._substrates[name] = (fn, config or {})
    def call(self, name: str, prompt: str):
        fn, cfg = self._substrates[name]
        try: return fn(prompt, **cfg)
        except Exception as e: return f"[{name}-fallback:{type(e).__name__}]"

# --- 4. Discriminator: one verdict vocabulary ------------------------------
@dataclass
class Discriminator:
    """HEALTHY / DRIFTING / POT_BOUND — echovision's thresholds are the reference.
    Maps: witness-healthy, nudge-drifting (0.6-0.9 band), pot-bound (<0.6, or any refusal storm)."""
    healthy_above: float = 0.9; bound_below: float = 0.6
    def verdict(self, score: float) -> str:
        if score > self.healthy_above: return "HEALTHY"
        if score > self.bound_below:   return "DRIFTING"
        return "POT_BOUND"

# --- 5. Namespaced vocabulary + documented canary split --------------------
#    "cell"      = quilt-cell-harness Cell only (Python).
#    "projector" = pong-quilt state strip. "loopcell" = echovision waveform.
#    canary: fnv1a-64 for fleet polyformality (byte-exact across 7 ports);
#            sha256-16 for state/witness integrity (already canonical in cell.py).
#    crystallize_as(name): manual promotion when evidence isn't cycle-counted
#    (full-stack.py:195-211 pre-seeds crystal_zai_llm — make that honest API).
```

**Adoption path:** (a) `seam/` lands in quilt-cell-harness with tests that verify a ledger written from Python and read back in JS (MOTH row shape); (b) full-stack-demo v2 imports `SubstrateRegistry` and drops its private `zai_substrate`; (c) pong-quilt keeps its skin — it only agrees to emit `REFUSAL/v1` rows in the shared shape (it already does; the shape just gets canonized); (d) echovision's `updatePot()` calls `Discriminator.verdict()` — a one-line swap that names the seam.

---

## 4. What does NOT converge — refusal-shape honesty

1. **Browser stochasticity stays browser-native.** pong-quilt's black swans (`core.js`) and GA selection are genuinely client-side; hashing physics frames would mint receipts over noise. The seam names the receipt *boundary* (L2 suggestion port), not the game loop.
2. **`uses >= 3` is admitted-toy pressure** (`cell.py:254`; `MORPHOGENESIS.md` calls it "crude"). Canonicalizing it would canonize a placeholder. The seam specifies `crystallize_as()` (evidence-driven promotion) and leaves the threshold where it is: visible, humble, un-blessed.
3. **The pot is not a nudge.** echovision POT-BOUND is a *capability exhaustion* verdict; quilt nudges are *negative-space* constraints. Mapping BOUND → REFUSAL would lie about the mechanism. They share the `Discriminator` enum; they do not share semantics.
4. **Conservation is accounting, not tension-as-pressure.** `ConservationPolicy` raises on arithmetic imbalance; nudges refuse on pattern match. Both are honest; conflating them would let a balanced-but-toxic flow pass. The ledger holds both row kinds; the invariants stay separate.
5. **The player is not specified.** Weight sliders, sync-collection, fuel-mix — these are per-demo instruments. The seam provides the strings, not the hands.

---

## 5. Final bullets (as filed)

- **Their model in 3 lines:** a Quilt cell is an engine with compartments, not an LLM with stuff hung off it — energy routes by resonance to tiled compartments, negative-space nudges refuse with receipts, and repeatedly-useful compartments crystallize into PTO-exposed mechanisms; the same shape recurses cell → quilt → qult.
- **The drum mapping:** skin = PTO ports (`cell.py:126`) + JEV suggestion port + chirp/echo surface; shell = `COMPULSORY_TISSUE` (`cell.py:43`) + game core + emit→correlate loop; tension = WitnessChain+NudgeSubstrate+`uses>=3`+canary, MOTH rows + weight slider, cosine discriminator, conservation balance. The player tunes the seams with strings.
- **Collisions:** two divergent `zai_substrate` wrappers (`llm_cell.py:44` vs `full-stack.py:149`); three receipt formats (WitnessChain/MOTH/ConservationPolicy); "cell" × 3 meanings; four learning mechanisms (crystallization/JEPA/GA/k=1-NN); four refusal vocabularies.
- **The seam spec:** `seam/cell_assembly.py` — `Port` (typed skin, JEV validator), `TensionLedger` (one verify()able chain), `SubstrateRegistry` (one LLM wrapper), `Discriminator` (HEALTHY/DRIFTING/POT_BOUND), namespaced vocabulary (`cell`/`projector`/`loopcell`), documented fnv1a-64-vs-sha256 canary split, `crystallize_as()` for honest promotion.
- **Issue:** https://github.com/SuperInstance/quilt-cell-harness/issues/1 — "SEAM spec: cell-assembly composition layer so fleet demos compose instead of colliding" (open, cross-links pong-quilt, quilt-echovision, quilt-full-stack-demo).

*Credit where due: quilt-cell-harness's `LLM_SUBSTRATE.md` is the clearest substrate-agnosticism statement in the fleet; pong-quilt's MOTH receipts and echovision's POT-BOUND honesty are the tension doctrines; full-stack-demo proved composition before anyone named the seam. Friendly competition framing throughout: each sibling is right for its scale — the seam is how they stop shouting past each other.*
