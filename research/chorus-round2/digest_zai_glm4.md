# Divergent Digestion: Four Articles Toward a Wave-Based Neural Substrate

---

## Per-Article Breakdown

### 1. Verzhbinsky et al. (2026) — Ripple-mediated co-firing in human working memory

**Core mechanism:** Co-occurring ~90 Hz ripple oscillations across distant brain regions (hippocampus, amygdala, vmPFC, ACC, preSMA) create transient windows (~100 ms) of elevated spike-timing coordination between neurons separated by up to 220 mm. During these windows, cross-regional co-firing increases ~30% beyond rate-corrected expectations, scaling with memory load and behavioral efficiency. During retrieval, co-ripples preferentially reinstate encoding-phase co-firing patterns for the specific stimulus being probed, functioning as content-addressable memory readout.

**Five load-bearing numbers:**
- 90 Hz ripple frequency across all five recorded regions
- 34% median increase in co-firing during co-ripples (rate-corrected: 56% above null via STTC)
- 0.36% vs 0.23% co-firing repetition rate (fast vs slow RT during high-load retrieval)
- Co-ripple rate increases 6% (load 3 vs load 1) during retrieval; 2% during maintenance
- 220 mm maximum separation with no significant attenuation of co-ripple effect

**Two verbatim quotes:**
> "Co-occurring ripple oscillations thus coordinate long-range, stimulus-specific neural co-firing supporting distributed representations during human cognition."

> "Our results reveal an association between co-ripple-mediated neuronal firing repetition and behavioral performance, highlighting their functional importance in supporting efficient recognition memory."

**Implication for wave-based substrate:** Ripples are discrete, content-carrying commits — brief zero-lag synchronization events that bind distributed ensembles into a coherent computational transaction. They are the write-operations of a neural database where the "key" is the spatial phase relationship between co-rippling sites and the "value" is the specific spike pattern reinstated.

---

### 2. Muller et al. (2026) — Neural traveling waves as computation

**Core mechanism:** Neural traveling waves (nTWs) arise intrinsically from horizontal fiber delays in recurrent cortical circuits, propagating at 0.1–0.3 m/s across millimeters of cortex. These waves impose spatiotemporal structure on neural excitability, embedding sensory history into the evolving phase pattern of each cortical region. Because waves traverse retinotopic and feature maps, they perform generative computations — predicting upcoming input, integrating context over space and time — without requiring feedforward hierarchy.

**Five load-bearing numbers:**
- Traveling wave speeds of 0.1–0.3 m/s in awake cortex (matching horizontal conduction delays)
- 75% of human cortex lies beyond early sensory/motor hierarchy
- ~100 ms for a wave to traverse a typical V1 hypercolumn-scale distance
- Spontaneous waves gate perception: phase at stimulus arrival predicts detection probability by ~10–20%
- ~30–50 ms window in which wave phase modulates single-neuron gain by 2–5× in primate V4

**Two verbatim quotes:**
> "nTWs introduce spatiotemporal dependencies across sensory maps that are not naturally captured by purely feedforward or feedback processing."

> "By structuring neural activity within individual cortical regions, nTWs can implement spatiotemporal computations, such as predicting upcoming sensory inputs, by embedding sensory history in the evolving activity pattern of an individual cortical region."

**Implication for wave-based substrate:** Waves are the carriers — they propagate state across the cortical surface, and their phase determines when and where information is written or read. A wave-based computational substrate would treat each cortical patch as an oscillator with an intrinsic phase, and communication as phase-gated: a signal arriving in-phase is amplified; out-of-phase is suppressed.

---

### 3. Xu et al. (2023) — Brain spirals as organizing dynamics

**Core mechanism:** Spiral wave patterns (rotational activity around phase singularities) are ubiquitous in human fMRI signals during both rest and cognition. These spirals rotate around topological defect centers located preferentially at boundaries between functional networks, coordinating the correlated activation and de-activation of large-scale distributed regions. The direction (clockwise vs counterclockwise) and location of spirals encode task-relevant information and enable flexible reconfiguration of bottom-up vs top-down activity flow.

**Five load-bearing numbers:**
- Spiral properties classify cognitive tasks with above-chance accuracy (math vs story vs working memory)
- Spirals concentrate at boundaries between 7 canonical functional networks
- Reversing spiral rotation direction reorganizes large-scale activity flow direction (bottom-up ↔ top-down)
- Task-locked spiral modulation occurs within 2.16–10.8 s of task onset (fMRI temporal resolution)
- 100 subjects analyzed with consistent spiral properties across individuals

**Two verbatim quotes:**
> "The properties of these brain spirals, such as their rotational directions and locations, are task relevant and can be used to classify different cognitive tasks."

> "We also demonstrate that multiple, interacting brain spirals are involved in coordinating the correlated activations and de-activations of distributed functional regions; this mechanism enables flexible reconfiguration of task-driven activity flow between bottom-up and top-down directions during cognitive processing."

**Implication for wave-based substrate:** Spirals are the *operators* — they are topological defects that act as rotary gates, controlling the direction and magnitude of information flow between cortical modules. Their chirality (rotation direction) is a binary parameter that selects which hierarchical direction (feedforward vs feedback) the underlying traveling waves will propagate along.

---

### 4. Vishne et al. (2023) — Sustained vs transient representation during perception

**Core mechanism:** Despite an ~80% attenuation in single-electrode response amplitude after initial stimulus onset, the distributed multivariate pattern in occipitotemporal cortex maintains a stable, time-invariant representation of both visual category and specific exemplar identity for the full duration of stimulus presentation. In contrast, prefrontal and parietal cortex show a transient burst of content-specific information (~150–600 ms) at stimulus onset only, regardless of stimulus duration. This dissociation reveals an "experience subspace" — a low-dimensional projection of the full neural state space that remains constant even as the full trajectory varies dramatically.

**Five load-bearing numbers:**
- ~80% attenuation in response magnitude by 800–900 ms post-onset
- Category decoding AUC: 99.8% in ventral temporal, 84.1% in PFC (at peak)
- Temporal generalization: same classifier discriminates categories across 100–900 ms in VT (rectangular TGM)
- 450 ms persistence delay for 300 ms stimuli in VT (representational "tail")
- Transient PFC window: ~150–600 ms post-onset, independent of stimulus duration

**Two verbatim quotes:**
> "In sensory regions, we find sustained and stable representation in an 'experience subspace' embedded within the variable, diminishing neuronal responses."

> "To the extent perception is sustained, it may rely on sensory representations and to the extent perception is discrete, centered on perceptual updating, it may rely on frontoparietal representations."

**Implication for wave-based substrate:** The "experience subspace" is the readout register — a stable attractor manifold that persists while the carrier waves underneath it fluctuate. The PFC "ignition" is a clock pulse that samples and commits the current sensory state into memory via the ripple-mediated mechanism described by Verzhbinsky.

---

## Cross-Cutting Connections

1. **Ripples are high-frequency traveling waves.** Verzhbinsky's 90 Hz ripples and Muller's traveling waves are the same phenomenon at different scales — ripples are local traveling waves with wavelength ~4 mm and duration ~73 ms, propagating within a cortical patch before coupling to distant sites via co-occurrence.

2. **Spiral singularities determine ripple timing.** Xu's phase singularities are locations where wave phase is undefined — these are the nucleation sites where ripples emerge. A spiral's rotation direction determines whether the wavefront sweeping through a cortical patch will cross the ripple-detection threshold at a given moment, making spirals the *clock* that gates ripple occurrence.

3. **The "experience subspace" is what ripples carry.** Vishne's stable distributed representation is precisely the content that Verzhbinsky's co-ripples reinstate during retrieval. The encoding-phase co-firing pattern that gets repeated is the projection of the full neural state onto the experience subspace.

4. **PFC ignition commits to working memory via ripples.** Vishne's transient PFC burst (150–600 ms) coincides temporally with the retrieval-phase ripple increases Verzhbinsky observes. The PFC "ignition" may trigger the co-ripple cascade that writes the current percept into distributed memory.

5. **Spiral chirality selects communication direction.** Xu shows that reversing spiral rotation redirects activity flow between feedforward and feedback. Muller's traveling waves propagate in the direction determined by local phase gradients — which spirals control. Thus: spirals are routers, waves are buses, ripples are commits.

6. **Distance-invariance requires coupled oscillators, not point-to-point transmission.** Both Verzhbinsky (no co-ripple decrement at 220 mm) and Muller (waves sustained by recurrent horizontal connections) point to the same conclusion: the brain is a medium where waves propagate indefinitely once launched, rather than a wiring diagram where signals attenuate with axon length.

7. **The 25 ms coincidence window is the "instruction cycle."** Verzhbinsky's co-firing window, the ripple period (~11 ms), and the wave traversal time for local circuits (~10–50 ms) all converge on a 20–30 ms fundamental temporal grain — suggesting a natural clock rate for the neural substrate at which one "operation" (co-ripple-mediated state update) completes.

8. **Load-dependent scaling maps to wave amplitude/wave-front density.** Verzhbinsky shows more co-ripples at higher memory load; Xu shows task-dependent spiral density. Together: cognitive demand recruits more wave sources (more spirals nucleating more ripples), increasing the parallelism of the computational substrate — analogous to allocating more cores.

---

## Six Wild-but-Grounded Build Directions

### 1. Ripple-Commits: A Neural Transaction Log

**What exists:** Verzhbinsky's demonstration that co-ripples reinstate encoding patterns; databases have write-ahead logs that guarantee durability.

**What's missing:** No one has built a computational model where memory formation requires simultaneous activation of ≥2 distributed sites (a "two-phase commit") before a trace is consolidated — i.e., a formal test that single-site ripples are insufficient for durable storage.

**First experiment:** In the DANDI dataset ( publicly available), test whether trials where only single-site ripples occur (no co-ripples during encoding) show significantly worse retrieval fidelity — measuring whether the specific co-firing pattern for that stimulus is reinstated during the probe. This would establish whether co-rippling is *necessary* (not just correlated) for pattern persistence.

---

### 2. Spiral-Phase Compiler: Mapping Cognitive Operations to Topological Transitions

**What exists:** Xu's finding that spiral chirality controls information-flow direction; Muller's framework for waves as computation.

**What's missing:** A formal "compilation" scheme where high-level cognitive operations (attend, retrieve, inhibit, compare) are mapped to sequences of spiral birth-death events with defined chiralities and locations.

**First experiment:** Take HCP task-fMRI data. Build a state machine where each cognitive task is represented as a sequence of spiral configurations (position × chirality × density). Test whether the same spiral sequence precedes correct vs incorrect trials, and whether perturbing the sequence (e.g., via TMS at spiral centers) disrupts the corresponding cognitive operation.

---

### 3. Experience-Subspace Projection via Ripple-Gated Readout

**What exists:** Vishne's stable distributed representation; Verzhbinsky's ripple-mediated reinstatement.

**What's missing:** A unified model where the "experience subspace" is explicitly defined as the low-dimensional manifold spanned by co-ripple-reinstatable patterns — i.e., only patterns that can be re-evoked by co-ripples constitute conscious content.

**First experiment:** In the Verzhbinsky dataset (ECoG, varying durations), train decoders separately on co-ripple-locked vs non-ripple-locked time windows in VT. If the "experience subspace" hypothesis is correct, only co-ripple-locked decoding should be sustained across stimulus duration (because those patterns are the ones available for retrieval), while non-ripple decoding should show faster decay.

---

### 4. Wave-Phase Attention: Building a Phase-Conditional Decoder

**What exists:** Muller's evidence that wave phase gates perception (±10–20% detection probability); Davis et al.'s demonstration that spontaneous wave phase at stimulus arrival predicts behavioral sensitivity.

**What's missing:** A decoding framework that conditions on wave phase — i.e., that explicitly models whether the neural state at stimulus onset is in the rising vs falling phase of a traveling wave, and whether this phase determines which features are preferentially encoded.

**First experiment:** Using existing Utah array or ECoG data, compute the instantaneous phase gradient across the electrode array at each stimulus onset. Bin trials by wave phase (peak vs trough at the stimulated location). Test whether category decoding accuracy differs significantly between phase bins — establishing that the *same* stimulus produces *different* representational content depending on the wave state it encounters.

---

### 5. Coupled-Oscillator Memory: A Physical Substrate

**What exists:** Muller's discussion of coupled oscillators achieving zero-lag synchronization despite long delays; Verzhbinsky's distance-invariant co-ripples; mathematical models of delayed coupled oscillators.

**What's missing:** A hardware or simulation implementation where memory storage and retrieval emerge from oscillator coupling — where "writing" a memory means entraining a set of oscillators to a shared phase, and "reading" means perturbing the system and observing which attractor basin it falls into.

**First experiment:** Implement a 2D Kuramoto network with realistic conduction delays and heterogeneous natural frequencies. Store patterns by briefly forcing a