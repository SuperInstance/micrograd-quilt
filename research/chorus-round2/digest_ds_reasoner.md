# Divergent Digestion: Four Papers, One Substrate

## 1. Verzhbinsky et al., *Nat Neurosci* 2026 — Co-ripple co-firing

**Mechanism.** ~90 Hz ripples occur in HIP, AMY, vmPFC, ACC, preSMA and co-occur across bundles; co-ripple windows (~100 ms) raise cross-region unit co-firing ~30% over what independent rate increases predict. The enhancement scales with memory load, is stimulus-specific, and during retrieval reinstates the encoding co-firing pattern. Critically, it does not decay with fiber distance to 220 mm — including across hemispheres.

**Load-bearing facts.** (1) 1,373 single units, 35 patients/43 sessions, 2,253 microwires. (2) STTC during co-ripples 0.023 vs 0.011 no-ripple — +117% synchrony *after* rate correction. (3) Co-firing enhancement increases slightly with distance: Pearson's r = 0.04, P = 5.3×10⁻¹⁴. (4) Pattern reinstatement 0.29% (co-ripple) vs 0.14% (duration-matched no-ripple); fast-RT 0.36% vs slow-RT 0.23%. (5) HIP ripple onset 379±33 ms leads AMY 473±30 ms on retrieval.

> "Co-ripples are not only associated with elevated excitability, but also promote the reinstatement of encoding-specific co-firing patterns that predict behavioral efficiency."
> "ripples occupy an optimal range for long-distance communication."

**Substrate implication.** Ripple = **commit primitive**: an atomic, broadcast, content-bearing write whose payload is the co-firing pattern inside a 25-ms coincidence window, not the oscillation itself. Zero-lag coordination over 220 mm rules out a purely delay-driven bus; the substrate needs a global commit without a global clock.

## 2. Muller et al., *Neuron* 2026 — Traveling waves review

**Mechanism.** Horizontal patchy fiber delays plus local E/I dynamics spontaneously generate traveling waves in awake cortex, intrinsically or evoked. Because wave position encodes recent input history, a cortical area behaves as a delay-embedded, predictive buffer. Computation lives in spatiotemporal trajectories, not in static receptive fields.

**Load-bearing facts.** (No primary statistics — load-bearing claims): (1) waves gate behaviour in primates (Davis et al. 2020); (2) horizontal fiber time delays alone suffice to generate them; (3) they appear in V1, V4, MT, motor, parietal, PFC working memory, and sleep spindles; (4) they encode stimulus *history*, not just identity; (5) the review itself flags that "sequentially activated discrete modules appear as traveling waves" under limited spatiotemporal sampling — a serious confound.

> "nTWs can implement spatiotemporal computations, such as predicting upcoming sensory inputs, by **embedding sensory history in the evolving activity pattern of an individual cortical region**."
> Dependencies "**not naturally captured by purely feedforward or feedback processing**."

**Substrate implication.** The idea field is literally a propagating phase field; delays are weights; the read head is a *position*, not a unit. Memory is trajectory replay.

## 3. Xu et al., *Nat Hum Behav* 2023 — Spiral waves

**Mechanism.** Phase-field analysis of 0.01–0.1 Hz HCP fMRI reveals spiral waves rotating around phase singularities during rest and