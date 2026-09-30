# Divergent Digestion: Four Papers on Oscillatory Coordination

## Article 1: Verzhbinsky et al. (2026), *Nature Neuroscience* — Cross-region co-firing via ripples

**Core mechanism.** High-frequency (~90 Hz) ripple oscillations co-occur across distant limbic and frontal regions (up to 220 mm, including across hemispheres) during a Sternberg working-memory task, and these "co-ripples" transiently elevate cross-region neuronal co-firing by ~30% beyond what independent rate increases predict. The enhancement is load-dependent, scales with memory demand during maintenance and retrieval, and during retrieval reinstates stimulus-specific co-firing patterns first observed at encoding—especially on fast trials. This positions co-ripples as a content-bearing, distance-invariant binding mechanism rather than a local hippocampal consolidation signature.

**Five load-bearing facts.**
1. 1,373 single units across 1,927 microwire channels in 35 patients; co-firing enhancement median +34% (IQR −2% to 163%) during co-ripples vs. no-ripple periods.
2. Co-ripple rates barely decline with distance: ~5% within-hemisphere interbundle vs. essentially identical cross-hemisphere, despite fiber tracts of 35–223 mm.
3. STTC (rate-corrected synchrony) was 117% greater during co-ripples (0.023 vs. 0.011, P = 1.7×10⁻⁵³), proving the effect isn't just excitability.
4. Load modulation was strongest in the ripple band (CNR = 12.42 retrieval) versus low-γ (6.21) and very-high-γ (10.13).
5. Stimulus-specific encoding→retrieval co-firing repetition: 0.29% during co-ripples vs. 0.14% during no-ripples; 0.36% fast vs. 0.23% slow RT (P = 3.3×10⁻¹⁴).

**Verbatim quotes worth building on.**
> "Co-ripples mark brief windows where increased firing within and between cortical and limbic locations could enable spike transmission between distant regions with sufficient temporal precision to drive plasticity."

> "These findings suggest that the phenomena reported here result from activation of an interactive network rather than sequential directed transmission."

**Implication for a wave-based substrate.** Ripples look like **commit events** in a distributed field: brief (~100 ms), zero-lag across distant sites, carrying stimulus-specific spiking content. For a wave-based computer, this is the natural "write" primitive—a synchronized phase-lock across many sites that binds a pattern into a retrievable address. Replay is literally what retrieval does here: encoding patterns are re-instantiated during retrieval under co-ripple windows. A substrate that stores memories as phase-relationships across oscillators could reproduce this exactly.

---

## Article 2: Muller et al. (2026), *Neuron* — Neural traveling waves review

**Core mechanism.** Neural traveling waves (nTWs) are spatially propagating patterns of activity that arise from horizontal/patchy connectivity with conduction delays and can be triggered by stimuli or emerge intrinsically. They structure activity within a region by embedding sensory history into the evolving spatial pattern, potentially implementing predictive and generative computations. The review argues nTWs are a canonical cortical computation, not an epiphenomenon.

**Five load-bearing facts.**
1. nTWs arise in awake animals and influence excitability and behavior—not just anesthesia artifacts.
2. Horizontal fiber delays plus patchy connectivity are sufficient to generate nTWs intrinsically.
3. Waves can implement short-term prediction of upcoming sensory input (Benigno et al., Nat Commun 2023).
4. They appear across visual, motor, prefrontal, hippocampal, and thalamic systems.
5. Spontaneous waves gate perception in behaving primates (Davis et al., Nature 2020).

**Verbatim quotes.**
> "By structuring neural activity within individual cortical regions, nTWs introduce spatiotemporal dependencies across sensory maps that are not naturally captured by purely feedforward or feedback processing."

> "nTWs can implement spatiotemporal computations, such as predicting upcoming sensory inputs, by embedding sensory history in the evolving activity pattern."

**Implication for a wave-based substrate.** Waves are the **continuous carrier** — the ongoing computational field. Ripples (Art. 1) are punctuated commits on top of this carrier. A wave-based computer would use nTWs as the substrate's "operating system clock + spatial addressing," with ripple-like events as transactional writes.

---

## Article 3: Xu et al. (2023), *Nature Human Behaviour* — Interacting spiral waves

**Core mechanism.** Human cortical fMRI slow fluctuations contain spiral-like rotational wave patterns whose phase-singularity centers organize correlated activations and deactivations across distributed functional networks. Spiral rotational directions and locations are task-relevant, classify cognitive tasks, and multiple interacting spirals reconfigure activity flow between bottom-up and top-down directions during cognition.

**Five load-bearing facts.**
1. Brain spirals appear in both resting and task states, across 100 HCP subjects.
2. Spiral rotational direction/location classifies cognitive tasks.
3. Multiple spirals interact—annihilation between opposite-chirality spirals, repulsion between same-chirality.
4. Spiral rotation coordinates DMN deactivation/activation during math tasks.
5. Phenomenological coupled-oscillator models reproduce spiral interactions and activity-flow reorganization.

**Verbatim quotes.**
> "Multiple, interacting brain spirals are involved in coordinating the correlated activations and de-activations of distributed functional regions."

> "This mechanism enables flexible reconfiguration of task-driven activity flow between bottom-up and top-down directions."

**Implication for a wave-based substrate.** Spiral phase-singularities are natural **operators**: topological defects that route information flow. Their chirality is a binary state; their position is an address; their interactions (annihilation, repulsion) are computational primitives. A wave-based computer could use spiral defects as the fundamental logic elements — like anyons in topological quantum computing, but classical and cortical.

---

## Article 4: Vishne et al. (2023), *Cell Reports* — Sustained vs. transient representation

**Core mechanism.** Using ECoG in 10 patients viewing images of variable duration (300–1500 ms), the authors show that ventral temporal cortex maintains a **sustained, time-invariant** distributed representation of both category and exemplar content, tracking stimulus duration. In contrast, prefrontal and parietal cortex show only **transient onset representations** that do not track duration. This dissociates a "sensory experience subspace" from a "perceptual updating" signal.

**Five load-bearing facts.**
1. Category decoding in VT: 99.6% AUC, sustained 100–900 ms; PFC: 84.1% but transient.
2. Single-electrode selectivity decays 77% by 800–900 ms, yet multivariate decoding stays near-perfect—representation lives in the population geometry, not individual units.
3. Temporal generalization matrices show rectangular (time-invariant) structure in VT, not PFC.
4. Exemplar-level RSA reliability sustained after partialling out category structure in VT.
5. Reducing VT electrodes to match PFC count did not abolish sustained decoding—coverage isn't the explanation.

**Verbatim quotes.**
> "To the extent perception is sustained, it may rely on sensory representations; and to the extent perception is discrete, centered on perceptual updating, it may rely on frontoparietal representations."

> "The same classifier could discriminate categories from the onset response to the end of the presentation time... an embedded subspace within the vast space of possible neural responses."

**Implication for a wave-based substrate.** Two distinct memory registers: a **stable geometric subspace** (VT-like) that holds content as a fixed point in phase-space, and a **transient ignition register** (PFC-like) that fires on updates. A wave-based architecture could implement both: standing-wave patterns as the stable subspace, and traveling-wave bursts as the update signal.

---

## Cross-cutting: 8 surprising connections

1. **Ripples and spirals are both zero-lag, distance-invariant** (Art. 1, 3). The brain seems to have a "no-delay" communication mode that defies axonal conduction times—consistent with coupled-oscillator synchronization, not transmission.
2. **Time-invariance lives in population geometry, not units** (Art. 4) — same logic as ripple co-firing (Art. 1): the *pattern*, not the spike rate, carries content.
3. **Ripples commit; waves carry; spirals route** — three temporal scales (100 ms, ~1 s, ~10 s) forming a stack.
4. **Spiral chirality ≈ ripple co-occurrence direction** — both are binary topological states that classify task context (Art. 3 task classification; Art. 1 load modulation).
5. **Replay is retrieval** (Art. 1) and **sustained representation is standing-wave** (Art. 4): both are geometric, not sequential.
6. **Horizontal connections generate waves (Art. 2) and co-ripples propagate without decrement (Art. 1)** — same anatomical substrate, two dynamical regimes.
7. **PFC transience (Art. 4) matches PFC's role in co-ripple load scaling (Art. 1)** — PFC is an updater, not a holder.
8. **All four papers invoke interactive networks over sequential transmission** — a convergent paradigm shift.

---

## Six wild-but-grounded build directions

**1. Spiral-defect logic gates.** *Exists:* Xu et al. show spirals annihilate (opposite chirality) and repel (same chirality). *Missing:* treating this as boolean logic. *First experiment:* build a 2D oscillator field (Kuramoto with phase-dependent coupling); inject two spirals of controlled chirality at chosen coordinates; measure whether annihilation (XOR-like) vs. repulsion (AND-like) can be gated by a third spiral injected at the midpoint.

**2. Ripple-as-commit in a neuromorphic chip.** *Exists:* Loihi 2 and SpiNNaker 2 support burst events; ripple-like 90