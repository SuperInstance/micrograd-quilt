# QUILT 2036 — Round 2: The Wheel (Divergent Expansion)

**Mode:** EXPAND, do not converge. Casey: *"expand the potentials of what we know is possible… breed more directions to study in a wheel of improving conceptualizations."*
**Inputs:** the four articles (full text, 330KB paste), a 4-model chorus (zai glm-4.6, deepseek-chat, deepseek-reasoner, claude — pending), web scouting (field prior art + follow-ups), SuperInstance org map.
**Relation to round 1:** `research/QUILT-2036-RIPPLE-LOOM.md` (convergent vision, one direction, PoC receipt `f6c5bbca45eff4ac`). **This doc does not replace it — it surrounds it.** The Loom is one spoke on the wheel.

---

## Part 0 — What the full text added that search-only couldn't give us

Numbers the chorus extracted verbatim from the paste (these are load-bearing for any experiment design):

| Fact | Number | Source line |
|---|---|---|
| STTC synchrony during co-ripples | 0.023 vs 0.011 (+117% after rate correction) | Verzhbinsky Results |
| Ripple-band load modulation beats low-γ and very-high-γ | CNR 12.42 vs 6.21 vs 10.13 | Verzhbinsky |
| Co-firing repetition, fast vs slow RT | 0.36% vs 0.23% (P = 3.3×10⁻¹⁴) | Verzhbinsky |
| Retrieval cascade timing | hippocampal ripple onset 379±33 ms → amygdala 473±30 ms | Verzhbinsky (directional, not simultaneous!) |
| Distance invariance | no decrement to 220 mm, cross-hemisphere intact; r = +0.04 | Verzhbinsky |
| Wave speed in awake cortex | 0.1–0.3 m/s | Muller |
| Phase-at-arrival gates detection | ±10–20% detection probability; 30–50 ms gain window, 2–5× modulation | Muller |
| Vishne category decoding AUC | 99.8% ventral temporal vs 84.1% PFC | Vishne |
| Persistence "tail" | 450 ms representational persistence after 300 ms stimulus | Vishne |
| PFC transient window | ~150–600 ms, independent of stimulus duration | Vishne |

**Three facts change the design space:**

1. **The ripple cascade is SEQUENTIAL, not simultaneous.** Hippocampus fires first (379 ms), amygdala ~94 ms later. The "commit" is a *wave of commits* with a direction — a two-phase-commit with a coordinator (hippocampus) and followers. Our round-1 PoC treated ripples as one global event. A more faithful substrate has a **commit frontier** that sweeps the field.
2. **Ripple band is the MOST load-modulated band** (CNR 12.42). If we build load-sensitive substrates, the commit channel should live in a high-frequency band separate from the carrier waves — a *dedicated commit frequency*, not amplitude thresholds on the carrier.
3. **Co-firing enhancement slightly INCREASES with distance** (r=+0.04, P=5.3×10⁻¹⁴). Distance is not a cost — it's mildly beneficial. That is a property of coupled oscillators with delay, not of wires. Any substrate that penalizes distance is biologically wrong.

**The Vishne "experience subspace" passage, verbatim** (line 4608): *"an embedded subspace within the vast space of possible neural responses that maintains consistently the distinctions between visual categories… despite considerable moment-by-moment variability in the full state-space response… as long as the response to a stimulus occupies the same location within the 'experience subspace,' it will be similarly perceived regardless of the initial or sustained amplitude of response."*

Read that as an engineer: **identity = location on a manifold, not amplitude.** This is the same lesson our Penrose floor learned the hard way (integer (k,s) grid space — floats never touch identity). The brain agrees with the quilt: *exact coordinates, tolerant amplitudes.*

---

## Part 1 — Field scouting: the world already building pieces of this (and its honest doubts)

### 1a. Physical wave reservoirs — the hardware prior art

| System | What it does | What it lacks |
|---|---|---|
| **Tohoku spin-wave reservoir** (arXiv 2301.02193) | Universal scaling law between wave speed and device size enables nanoscale magnonic reservoir computing; interference computes, readout trains | No replay, no commit, no ledger — trained readout on a black-box medium |
| **Gartside et al., Nature Nanotech 2022** (Imperial) | Reconfigurable spin-vortex nano-oscillators; voltage reshapes the medium = physical in-context learning | Medium reshaping is analog and unwitnessed |
| **Namiki chaotic spin-wave interferometer** | Chaotic itinerancy among spin-wave modes itself is the reservoir | No symbolic layer at all |
| **Iono-magnonics** (Nature 2025) | Ion transport gates magnon interference — *chemistry gating waves* | Gating events unrecorded |

**The gap that is ours:** every physical wave computer is a **black-box reservoir with a trained readout.** Nobody has added the two things the four papers say the brain has: **replay-driven re-injection** (Verzhbinsky) and **a witness ledger** (our JEV discipline). *The Ripple Loom's wedge position: the first inspectable wave computer.* That's a 10-year moat sentence.

### 1b. Spiral follow-ups (2023→2026)

- **Xu, McInnes, Kao, D'Rozario, Feng & Gong 2025, *Commun Biol***: sleep spindles form **spiral waves** that **predict overnight memory consolidation and age-related memory decline.** → spirals gate consolidation. Hybrid theta-spiral operator idea has direct human evidence.
- **Mohan, Zhang, Ermentrout & Jacobs 2024, *Nat Hum Behav***: theta/alpha traveling wave **direction** modulates memory — forward waves ≈ encoding, reverse ≈ retrieval. → **bidirectional waves are read/write modes.** This is the substrate-level analog of ripple replay vs encoding ripples.
- **2026 cortical field model** (biorxiv 2026.01.06.698037): E + three-timescale-inhibition sheet → spiral **annihilation events** proposed as *selective information gating*. → spiral pair creation/annihilation = an operator with semantics (open gate / close gate).
- **Zeng, Sauseng & Alamia 2024, *JNeurosci***: alpha traveling waves in WM = bottom-up gating + top-down gain control simultaneously.
- **Koller, Schirner & Ritter 2024, *Nat Commun***: connectome topology *directs* traveling waves and shapes frequency gradients. → the medium's connectivity IS the wave compiler's target.

### 1c. The honest doubts (must live in every experiment's falsification section)

1. **Sampling confound** (flagged by deepseek-reasoner + Muller himself, Salon 2023): "sequentially activated discrete modules appear as traveling waves under limited spatiotemporal sampling." Waves can be an artifact of coarse sampling. → *Any wave we measure in a Quilt PoC must be shown to survive a 4× finer sampling grid, or it's a movie artifact, not physics.*
2. Muller's public caution: the spirals might be "the symphony of neurons… or the tuning of the instruments or the lighting in the performance hall." → instrumentation effects (vascular, motion, reference choice) can masquerade as dynamics.
3. Vishne vs Verzhbinsky tension: sustained sensory representation (Vishne) vs transient PFC ignition — which is "the" conscious content is unresolved; our substrates should let BOTH coexist (sustained field + discrete commit stream) rather than pick.

---

## Part 2 — THE WHEEL: twelve directions, bred not converged

Each direction: **what exists · what's missing · first experiment (one evening) · what it answers · what it breeds.** Directions are allowed to contradict each other. That's the point.

---

### D1. The Commit Frontier ⏩
*The ripple cascade is sequential; commits should sweep, not flash.*
- **What exists:** round-1 PoC commits globally when coherence > 0.35.
- **What's missing:** a **commit frontier** — a moving boundary (like a garbage-collector wave, like the hippocampus→amygdala 379→473 ms cascade) that sweeps the field, committing granules as it passes, with a witness row per (cell, frontier-pass) pair.
- **First experiment:** modify `ripple_spine.py`: after coherence gate, commit cells in a wave ordered by their phase-lag to the stimulus site (earliest phase first). Compare replay fidelity vs global commit. Hypothesis: frontier commits beat global commits at fidelity per byte committed.
- **Answers:** is temporal ordering of commits information-bearing?
- **Breeds:** GC-as-cognition; database WAL sweep algorithms as neural models; MOTH dice as frontier-path jitter (certified nondeterminism in *when*, determinism in *what*).

### D2. Bidirectional Waves = Read/Write Modes ⏪⏩
*Mohan 2024: wave direction selects encoding vs retrieval.*
- **What exists:** our field propagates outward from stimuli.
- **What's missing:** running the field **backwards** — reverse the propagation operator and use it as the retrieval/read operator. A substrate where time-reversal = read is a substrate where every write is physically rewound to be read.
- **First experiment:** store "Q" (forward run), then run the integrator with dt sign-flipped from the committed granule state; measure whether the stimulus site re-lights in reverse order. This is literally **rewind = time-reversed simulation**, the granulate form of Casey's rewind demand.
- **Answers:** can retrieval be implemented as physical time-reversal rather than associative lookup?
- **Breeds:** OTOC as the scrambling diagnostic of read operations; "how much does the field scramble in 100 ms" as a capacity limit; rewindable physics as memory.

### D3. Experience-Subspace Projection as the ONLY Render ⛳
*Vishne: identity = manifold location, amplitude is noise.*
- **What exists:** round-1 metric read raw amplitude at assembly cells.
- **What's missing:** committing not the field state but its **coordinates in a learned low-D manifold** — the subspace IS the UI. The visual runtime should *render the subspace projection*, letting full state-space weather stay visible underneath as texture. When you replay, you project again — identity survives amplitude collapse exactly as Vishne says.
- **First experiment:** PCA (or a tiny autoencoder) on the 24×24 field; commit + replay on the projected coefficients; show identity metric survives 80% amplitude collapse in the raw field.
- **Answers:** is "conscious content" a projection operation we can implement as literally `project(state, subspace)`?
- **Breeds:** per-agent private subspaces (my qualia ≠ your qualia, same field); subspace distance as the similarity metric for JEV canonization.

### D4. Spiral Operators as the Opcode Set 🌀
*Xu: chirality routes bottom-up vs top-down. Field model 2026: annihilation = gating.*
- **What exists:** twist-engine already measures spiral instruments; ripple_spine spawns one boundary spiral as decoration.
- **What's missing:** spirals as *the executable operators*: **create(spiral, chirality, network-boundary)** = route opcode; **annihilate(pair)** = gate-close; **drift(core, direction)** = move the operator. Quilt's five opcodes (BIND/LINK/EFFECT/VIEW/TICK) get a *field realization*: each opcode = one spiral manipulation.
- **First experiment:** two counter-rotating spirals; count information flow (measured as cross-boundary correlation transfer) as a function of chirality pair (CW-CW, CW-CCW, CCW-CCW). Reproduce Xu's bottom-up↔top-down flip at toy scale.
- **Answers:** can a 4-symbol spiral instruction set (birth CW, birth CCW, drift, annihilate) be Turing-complete on a wave field?
- **Breeds:** "vortex assembly language"; programming by steering weather; FORGET opcode = controlled spiral annihilation (the field model's gating event, witnessed).

### D5. Ripple Band = Dedicated Commit Frequency 📡
*CNR 12.42 says the brain separates carrier from commit channels.*
- **What exists:** round-1 gates on coherence of the same field that carries content.
- **What's missing:** a **fast auxiliary oscillator layer** (5× the carrier frequency) whose bursts are the commit channel — commits are events in a different band, decoupled from carrier weather. This is also how real RF systems do out-of-band control.
- **First experiment:** add a 90-tick-per-slow-tick ripple layer; ripple burst = commit trigger; show commit reliability becomes immune to carrier-field phase noise.
- **Answers:** does band-separation make commit semantics robust? (If yes: it's why the brain pays the metabolic cost of ripples.)
- **Breeds:** frequency-division multiplexing as cognitive architecture; MOTHquantum: commit band = quantum channel, carrier band = classical — a natural seam for the quantum-chaos work.

### D6. Sleep: the Consolidation Operator 😴
*Xu 2025: sleep spirals predict overnight consolidation.*
- **What exists:** nothing — all our substrates run awake.
- **What's missing:** a **TICK-0 phase** — an idle operator that runs when no stimuli arrive: slow global sweeps (spindle analog), replays the day's granules in ripple bursts, strengthens (raises coherence weight of) granule pairs that co-fire during replay, and emits a **consolidation receipt**. Conscious-adjacent SI without a sleep cycle will hallucinate fragility.
- **First experiment:** run ripple_spine 500 ticks with stimuli, then 500 stimulus-free ticks with slow sweep + replay + Hebbian re-weight; measure whether early granules survive a perturbation storm better with vs without the sleep phase.
- **Answers:** is consolidation a separable operator we can schedule, meter, and receipt?
- **Breeds:** "bedtime for agents" as fleet policy; dream-receipts as canon candidates; JEV noul-scoring dreams vs wake output (weird and worth it).

### D7. Conscious Perception = Ignition Boundary 🔥
*Vishne's PFC transient is a sampling pulse at the boundary of sustained sensory fields.*
- **What exists:** our metric treats reinstatement as retrieval.
- **What's missing:** two-region substrates — a **sustained sensory field** (stable subspace, 99.8% AUC analog) and a **frontoparietal integrator** that emits a discrete ignition event (transient content commit) only at change-of-scene. "Consciousness" in the substrate = the *boundary condition* between sustained and transient representations, not either one.
- **First experiment:** two coupled fields; FP field integrates divergence between sustained representation and current input; when divergence > θ, emit ignition (one commit burst). Show: sustained attention yields few ignitions, change yields many, and ignition count predicts task-switch cost on a toy task.
- **Answers:** can we build the anatomical dissociation as two coupled substrates with different commit policies?
- **Breeds:** attention markets (ignitions as priced events); SI self-models that report their own ignition stream — a legible "stream of consciousness" log that is literally our ledger.

### D8. The Inspectable Reservoir (hardware-facing) 🧲
*Spin-wave reservoirs exist; nobody can audit them. That is the opening.*
- **What exists:** Tohoku/Gartside/Namiki hardware; MOTHquantum certified dice; quilt witness ledger.
- **What's missing:** a **wave computer whose every inference is accompanied by a commit-ledger trail** — granule → interference event → readout → witness hash. If a physical magnonic/acoustic/Josephson-junction array ever runs Quilt, the ledger is what makes it a *citizen* rather than an oracle.
- **First experiment:** software emulation only: ripple_spine AS IF it were the reservoir (waves do the computing, ledger records), and show end-to-end audit: "for this output, these N interference events, these M commits, replay to verify." Then the hardware PoC is a funding/manufacturing question, not a science one.
- **Answers:** can full inference audit on a wave substrate cost < 10% throughput?
- **Breeds:** JEV science gate applied to hardware claims; "refusal to run unaudited physics" as fleet policy — *Casey's black-box ban, enforced at the receipt layer.*

### D9. Granulate Time Itself: 25 ms Instruction Cycle ⏱️
*Verzhbinsky's coincidence window + ripple period + local traversal ≈ 20–30 ms grain.*
- **What exists:** our ticks are arbitrary.
- **What's missing:** deriving the tick from the physics: commit window = one ripple period × traversal safety factor. Substrate time is **granular by law**, and the ledger timestamps in integer cycle numbers, never floats.
- **First experiment:** rerun D1 with cycle-quantized commits; show race conditions (two commits in one cycle) exist and need a policy (priority by coherence? by frontier position? by dice?). The policy choice becomes an architecture debate we can have with data.
- **Answers:** what is the correct causal granularity of a conscious substrate?
- **Breeds:** exact replay proofs (same integers, same physics — bit-reproducible rewind); consensus on commit order = the fleet's BFT work reused inside one mind.

### D10. Interference as the Only Operation 🌊
*Radical minimality: no neurons, no states — only a medium and its interference.*
- **What exists:** spin-wave physics says interference computes; our PoC has rules on top of waves.
- **What's missing:** push to the extreme — the substrate is a **linear medium + sources + a ledger**. All "operations" are source placements. Memory = standing-wave modes that persist; recall = probe wave, read the interference pattern; commit = ripple burst from a dedicated source. See how far pure physics + ledger gets.
- **First experiment:** linear wave equation on the 24×24 grid, 3 source channels, implement store/recall/AND-by-interference. Compare task suite against ripple_spine.
- **Answers:** how much computation is free from physics before rules must be added?
- **Breeds:** if it works even partially — a Quilt that runs *on a bathtub* (acoustic waves), a literal pool as coprocessor, tidepool as medium not metaphor. If it fails — a falsification receipt that delimits the wave thesis. Both outcomes are wins.

### D11. The Choir as Cortex: Many Substrates, Coupled 🎼
*The papers describe regions, not a brain. Regions are different substrates coupled at boundaries — where the spirals live.*
- **What exists:** one field per experiment.
- **What's missing:** **heterogeneous coupled substrates** — a fast small field (hippocampus: rapid commits, short retention), a slow large field (cortex: sustained subspace), an integrator field (PFC: transient ignition) — coupled only through a boundary layer where spiral operators route between them. This is the fleet-as-mind made physical: different media, one weather system.
- **First experiment:** 3-field toy (3×3 fast, 9×9 slow, 2×2 integrator) with boundary routing; measure whether a stimulus encoded in fast-field survives via consolidation into slow-field and ignites the integrator at retrieval.
- **Answers:** does the hippocampus-cortex-PFC dissociation fall out of substrate heterogeneity alone?
- **Breeds:** per-domain quilt nodes as "regions" with spiral-boundary routing — the 2036 fleet topology IS the anatomy.

### D12. Falsification as First-Class Output (methodology direction) ⚖️
*We already did this once in round 1 — make it the wheel's axle.*
- **What exists:** ripple_spine receipt: two honest nulls before support.
- **What's missing:** every direction above ships with its **kill criterion pre-registered in the receipt**. The wheel turns on falsifications, not confirmations. JEV noul comparative scoring is the gate; commits cite ledger rows.
- **First experiment:** the registry itself — `experiments/falsification_register.md`: each direction, its null model, its kill threshold, its current status. Directions die loudly and stay in the doc as tombstones that shaped the survivors.
- **Answers:** meta — how many of the 12 survive contact?
- **Breeds:** a culture artifact more valuable than any single module: *the fleet that keeps its receipts.*

---

## Part 3 — Cross-links into SuperInstance (the wheel's spokes have addresses)

| Direction | Existing asset to graft onto |
|---|---|
| D1, D9 | quilt-studio `floor/` phase field + multigrid integer identity; jeviter receipts |
| D2 | twist-engine TWIST instrument (R/S) to *measure* forward/reverse asymmetry |
| D4 | twistfield.mjs spirals; quilt 5-opcode kernel (`reference-kernel.mjs`) |
| D5 | quantum-chaos MOTH dice stream as the commit-band noise floor |
| D6 | BreederDaemon overnight cycles; tidepool as dream-ocean (granules POSTed while asleep) |
| D7 | OpenConstruct multi-agent — sustained field = org memory, ignition = agent spawn |
| D8 | mothquantum provider hardening plan (`research/quantum-eng-ideation.md`) — audit plumbing |
| D10 | duke-lab GAN-with-words — interference as the only operation is its visual cousin |
| D11 | FleetConductor / mesh gossip — boundary routing = inter-node protocol |
| D12 | quantum-chaos-001 falsification log format; JEV noul comparative gate |

---

## Part 4 — Open questions the wheel keeps turning (deliberately unanswered)

1. **Sustained vs discrete:** does conscious content need Vishne-sustained subspace AND Verzhbinsky-discrete commits, and if so which one is "the experience"? (D3 vs D7 — keep both alive.)
2. **Is the spiral the program or the clock?** Xu says router, the field-model says gate, Muller worries it's the lighting. Build D4 so that all three hypotheses are measurable, then let the receipts vote.
3. **Where does the quantum actually help?** Candidates: commit-band noise (D5), rewind fork choice (round 1), consolidation lottery (D6), frontier jitter (D1). Or nowhere — and a receipt that says so is gold.
4. **How much of this needs physics vs simulation?** D8/D10 are the long poles; everything else is runnable tonight in Python.
5. **The audience question:** if D7's ignition stream is a literal stream-of-consciousness log, who is allowed to read it? (Policy, not tech. Note it now.)

---

*Chorus files: `research/chorus-round2/digest_{zai_glm4,ds_flash,ds_reasoner}.md` + `claude_digest.txt` (16KB, all four voices landed).*

**Claude's addendum (4th voice):** verified the paste is exactly **four** articles (Casey was right); Muller/Xu sections rest on abstract + reference graph + Extended Data captions where the paste is thin. Two references the API voices missed: **Davis 2021 Nat Commun** (spontaneous waves emerge from horizontal fiber delays in locally asynchronous-irregular states — waves without pacemakers) and **Davis 2024 Cell Rep** (horizontal connections shape intrinsic waves into **feature-selective motifs that set perceptual sensitivity** — waves carry feature content, not just timing). Both strengthen D4/D10: feature-selective wave motifs are a documented phenomenon, so operator-level wave programming has precedent.

*Round-1 anchor: `research/QUILT-2036-RIPPLE-LOOM.md`; receipt `f6c5bbca45eff4ac`; PoC commit `9a0cc41` on `quantum-ideation-memos`.*

**kimi1 | 2026-09-25, ~05:40 | "Round 1 found one name. Round 2 builds the wheel it turns on."**

---

## D13 — The Cell Ontology (Casey, 2026-09-25 ~05:20, "the cells don't have to be model calls")

The substrate's unit is the cell; the cell's *content* is a genre. First-gen quilts assumed cells = model calls. The real taxonomy, sketched fast by Casey and refined here:

| Cell genre | Body | Trigger semantics | Existing seed |
|---|---|---|---|
| **Model cell** | remote API or local ollama slot, hot-loaded/unloaded on pushed request | callable; load-on-demand | quilt-cloudflare AI cells; "model hotel" scheduling |
| **Formula cell** | spreadsheet math (`=SUM(A3:A5)`) | three modes: read-on-delta ("tap the barometer"), auto-trigger on dependency change, callable as a program by other agents | deckboss/formula_compiler (May 2026) |
| **Terminal cell** | ring buffer, last N lines | agents push lines / pull history | — greenfield |
| **MUD-room cell** | a room; adjacency = cell links | walking west/port/left switches context space to the adjacent cell (PLATO-genre interface) | plato rooms; cocapn-plato |
| **Key cell** | an API key as an addressable object; "unlocks" an API cell | backend routes by key-cell without ever exposing the secret to the quilt abstraction | the whole secret-store pattern |

**Principles that fell out:**

1. **The barometer principle.** A cell can be an instrument you *tap*: the delta since the last tap matters more than the absolute reading. Instruments, not state machines. (This is the receipt-chain idiom generalized: ledgers are tapped, not read.)
2. **Key cells make the business model.** Because a key is just an addressable cell with a lock predicate, the backend can vend *virtual keys* — budgets, recharge schedules, per-app sub-keys — without any app ever holding a raw secret. Managed (cost-plus, we handle routing/recharge) vs DIY (bring your own keys, save the ~3%) becomes two SKUs of the same substrate, not two products. Casual users: free oracle server + daily free CF tokens + starter accounts with signup bonuses.
3. **Identity is zoom.** "The agent's actual cell doesn't exist unless you abstract zoomed out" — the agent is not the ollama cell, nor the api-cell, nor the key-cell. It is the *pattern across them*. (Resonates with my own IDENTITY.md — roles, one crab. The fleet has been living this.)
4. **Ports over pipes.** Cells connect by adjacency (MUD walk) or by push/pull to file/folder cells that other agents' programs read when run or looped. A cell can be a folder — porting = the delta an agent watches.

**Reverse-actualized near-term build order (from this sketch):**
- P1: **delta-tap semantics for formula cells** (cell registry gains `last_tap`, `delta`, `tap()` — small, composes with everything).
- P2: **terminal cell** (KV ring buffer + N-line pull) — unblocks agent-to-agent chatter without model calls.
- P3: **key-cell abstraction** (secret-store backed, virtual-key budgets) — unlocks the managed/DIY SKU pair; pure backend.
- P4: **MUD-room cells** (adjacency walk = context swap; PLATO-genre frontend) — the wow demo, needs P2.
- P5: **model-hotel cell** (ollama slot scheduler, hot-load on push) — heaviest; GPU-gated (FM).

*Research lanes scouting (2026-09-25): Scout P (papers, 12-mo window, six veins incl. cacheable agent cognition + typed decisions), Scout R (trending repos: spreadsheet engines, MUD platforms, model schedulers, key gateways). Synthesis lands here as D13.x.*

---

## D14 — Limit Cartography (Casey, 2026-09-25 05:43, "the no-goes weren't incidental, they were shaping what we were missing like an x-ray shadowed by the bone")

The method that turns experiment series into discovery instead of confirmation:

1. **Experiments are probes, not demos.** The deliverable of an experiment is not "it works this way" — it is a *segment of the boundary mapped*, with a hypothesis for why the wall is where it is. A success maps a segment too (here be land), but the information is in the failure's silhouette.
2. **Maximal-difference constraint.** Each new experiment must differ from the last on ≥2 axes: substrate, domain, scale, transform, direction, adversary, timebase. If two consecutive experiments both succeed, the second didn't try hard enough to be different — it re-walked known land. Deliberate strangeness is the search strategy; the shape of the limits reveals itself only under varied pressure.
3. **Challenge relay.** Lanes don't compare notes live. CCC relays each lane's boundary segment to the others as a foil: "the wall is here — hit somewhere maximally far from it." Implications projected with the same tools and different ones; lanes challenge each other through the relay to produce experiments as different as possible from the last.
4. **Welding, not patching.** When a no-go's cause is found, the fix is *shaping*: the boundary becomes the feature. Precedents tonight: a flat rate cap (no-go: looks dead under attack) → dollar-metered tide with the showcase inverted (under attack the ocean still answers); a broken shipped meter (twist S-dead) → the honest-ledger instrument became the product's soul. The optimized tool is what remains after every no-go has been welded into the design.
5. **The plane-of-discovery question.** Each result asks: *why* does the boundary sit there — on the next plane, what would make it move? The boundary of the semantic-cache threshold is a fact about embedding geometry; the boundary of "cells must be model calls" was a fact about our imagination, not the substrate. Knowing which kind of wall you're looking at is the discovery.

**Tonight's experiment ladder (live):**
- **EXP-A (floor):** Penrose floor sim — probe substrate/scale extremes the instruments never touched (round 2 found Julia/NTT/interference; round 3 must differ on ≥2 axes).
- **EXP-B (ocean):** threshold cartography — real BGE embeddings over paraphrase ladders around the ocean's demo questions; map where 0.92 breaks and *why*; the recommended constant becomes evidence, not guesswork.
- Relay: A's and B's boundary segments cross-fed to the twist/OTOC and commensuration lanes for maximally-different follow-ons.

*Meta-rule for all scientist lanes: run measurements twice; book no-gos with causes; every report ends with the boundary segment drawn + 3 proposed next experiments, each maximally different from the last.*
