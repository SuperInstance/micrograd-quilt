**Ripple Loom**

Quilt becomes a phase field. Every granule is a node with NOUL type, amplitude, phase, and witness hash. Ideas are not tokens passed forward; they are traveling waves, ripples, and spiral phase singularities moving over the quilt grid. `BIND` phase-locks distant granules into an assembly. `LINK` sets waveguide delays between them. `EFFECT` applies local gain, inhibition, and nonlinearity. `VIEW` samples the field. `TICK` integrates the wave equation. Sensory history and generative prediction are encoded as motion over maps: a wavefront carries its past in its phase gradient and its future in its JEPA-predicted target. Spiral waves nucleate at boundaries between modules—visual, prefrontal, motor—and their rotation direction gates bottom-up versus top-down flow per task. Ripples are the save/replay events: when local coherence crosses a threshold, the active assembly is compressed into a 90Hz ripple packet. Replaying that packet reinstates stimulus-selective firing across distant granules. Conscious content is the trajectory of these field phenomena, not a static code.

Rewind is granule-resolution because every `TICK` writes a canonical JSON witness entry: granule id, phase, amplitude, incoming `LINK` delays, `EFFECT` params, `VIEW` sample, MOTH job citation, JEV score, OTOC lambda, and FNV-chained hash. Refusals are hash-committed too. To rewind, query the ledger for a granule’s last stable ripple packet, reconstruct its local phase field, and re-run `TICK` deterministically with MOTH-certified entropy. You can rewind a single granule, a spiral arm, or an arbitrary `VIEW`-selected set. Forking creates a new ledger branch at any granule event. The ripple packet is the save state; the granule is the unit. You can rewind one idea’s phase without rewinding the whole thought.

JEV, MOTH, and ML interlock concretely. MOTH supplies certified entropy for `TICK` noise, spiral nucleation, and fork tie-breaking; each job is cited in the ledger and CHSH-witnessed, so no hidden determinism can masquerade as field dynamics. ML—specifically the JEPA-predictive proposer in GravityField—predicts the next latent field patch. Surprise is prediction error weighted by local amplitude. High surprise triggers a ripple save; low surprise permits compressed `TICK` advance. JEV gates every candidate ripple and fork: its typesafe NOUL oracle scores canon versus speculation by checking NOUL type consistency across linked granules, witness-chain validity, and OTOC effect. Canon ripples commit as stable memory. Speculation ripples go to the fork pool. Spiral rotation is also a JEV decision—bottom-up or top-down—based on task type and NOUL context. The OTOC chaos dial sets lambda: high lambda means a rugged landscape, shorter ripples, more exploratory forks; low lambda means stable replay and long ripples.

First 90-day build:

Weeks 1–2: define the ripple packet schema in canonical JSON. Extend `TICK` to compute phase field using existing opcodes only: `BIND` phase-locks, `LINK` sets delay, `EFFECT` applies gain, `VIEW` samples. No new opcodes.

Weeks 3–4: implement a 1D/2D wave simulator with a 90Hz ripple detector. Seed noise from MOTH. Record every `TICK` in the FNV ledger.

Weeks 5–6: build the granule rewind API. Query by granule id or time, reconstruct phase state, fork the ledger, and verify replay against the original witness chain.

Weeks 7–8: integrate JEPA as the GravityField proposer. Surprise-triggered ripples save the field. Compare surprise-weighted forks to random forks.

Weeks 9–10: wire JEV to score ripples and spiral rotation for canon versus speculation. Calibrate OTOC lambda against task difficulty.

Weeks 11–12: run a two-site working-memory task. Bind two stimuli, let a traveling wave cross, trigger a ripple, rewind from the ripple packet, and measure reinstatement across distant sites.

Falsifiable prediction: In that two-site task, replaying a single 90Hz ripple packet from the ledger will reinstate stimulus-selective firing across distant sites with >90% phase coherence and <5% JEV speculation leakage, while a feedforward transformer baseline will score <60% on the same reinstatement metric. If not, the field model is falsified.

Ripple Loom