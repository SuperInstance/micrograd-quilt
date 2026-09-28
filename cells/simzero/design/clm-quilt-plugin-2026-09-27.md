# CLM-as-Quilt-Plugin — the "slow-is-valid" contract (design seed, 2026-09-27, kimi1)

Source: Casey 11:53 — "think how clm might be a game-changing technology in
our systems. it could even run slower on cpus, npus and any other chip if we
revamped it creatively into a quilt plugin-able tool."

## Two readings, one architecture (receipted)

| reading | evidence | what it contributes |
|---|---|---|
| **CLM = tiered-memory compute** (NYU CLM-GS, ASPLOS 2026, nyu-systems/CLM-GS) | GPU-memory-barrier removal: selection-critical state on fast tier, rest anywhere, *mathematically identical* output | The acceptance test: same job, different tier ⇒ same result. Tier port bugs are detectable by output diff |
| **CLM = causal language model** (the LLM itself) | "run slower on cpus, npus and any other chip" is literally the LLM edge story (2026 NPUs everywhere) | The payload: cognition itself becomes the job that tiers |

Both converge: **tiered-substrate compute as a quilt plugin, where slowness is
a property of the tier, never a failure class.**

## The 5-opcode encoding (CLM is a consumer of the kernel, not a new kernel)

| opcode | CLM role |
|---|---|
| BIND | a node registers its **tier capability**: `{node, tiers:[gpu,npu,cpu,edge], mem_gb, watts}` — hardware becomes ledger state |
| LINK | job → node-with-tier: `LINK(job, node, tier)` — the admission edge the graph-v1 substrate demands (isolated nodes rejected; a node must admit a job) |
| EFFECT | `EFFECT clm.run {job, tier, deadline}` — the kernel does NOT block on latency; it schedules the tick and expects the receipt later |
| VIEW | the receipt: `{job, tier, wall_ms, output_sha, identical_to_ref}` — WHERE the cognition happened becomes first-class view state |
| TICK | the scheduler: on deadline miss, tier-downgrade signal (job moves gpu→cpu), NOT an error — saturation ≠ breakage |
| FORGET | cold state evicted to slower tier; the ledger keeps the hash, the bytes go anywhere |

## Why game-changing in OUR systems (four receipts already in hand)

1. **Every node becomes a compute citizen.** FM's laptop, edge boxes, the rack,
   phone-class NPUs — all join the mesh as tiered CLM executors. Fleet
   capacity stops being GPU-gated. The overnight-autonomy aesthetic finally
   has the hardware story: slow nodes chew breeding/eval queues at 3 AM.
2. **Receipts gain a tier dimension.** Morning evidence: my mothquantum jobs
   were ALREADY the proto-contract — submit async (queued ~2 min), poll,
   receipt with provenance. CLM generalizes "slow compute, honest receipt"
   from quantum-emu to classical hetero-chips. A stone-v2 signed receipt that
   names its tier answers "where did this cognition run" — which is Q8's
   read-side question (what makes a receipt loadbearing) asked of hardware.
3. **The morning's physics rhymes.** expQ5b's disorder curve: ≥0.4 kills the
   return, but >0.7 is frozen silence, NOT noise. Tier saturation behaves the
   same: a saturated CPU tier isn't failing, it's reached its frozen regime.
   Same mathematics (overdamped relaxation), same operational reading.
4. **Cellular agents, finally grounded.** May's dream: GPU runs grid rules at
   60fps, CPU runs the LLM only when stimulated. CLM-as-plugin IS that
   architecture with a receipt contract stapled on.

## The plugin contract (what a CLM plugin must export)

```json
{
  "plugin": "clm",
  "ops": ["clm.run", "clm.eval", "clm.breed"],
  "tier_contract": {
    "accepts": ["gpu", "npu", "cpu", "edge"],
    "identical_output_required": true,
    "deadline_miss_semantics": "tier_downgrade_signal",
    "receipt_fields": ["tier", "wall_ms", "output_sha256", "ref_sha256"]
  }
}
```

Acceptance gate (the CLM-GS lesson): `output_sha256 == ref_sha256` across
tiers, or the tier port is buggy. Slowness never voids a receipt; divergence
always does.

## First build (one evening, FAIL-first)

`clm-sched.mjs`: a tiered runner for ONE real fleet workload — the JEV judge
lane (typesafe.ai key VERIFIED this morning) or the Q5-receipt SHA
recomputation (CPU-trivial, honest). Run the same job on (a) this node's CPU,
(b) a simulated "edge" tier (cpu + cgroup memory cap + nice level). Pin:
identical output, receipt chain sealed in stone-v1 naming both tiers, wall_ms
honestly recorded. The two-tier receipt pair IS the proof of concept.

## Open questions (for Casey/FM)

1. Which CLM did you mean — the NYU offload pattern, the causal LM, or a
   third thing from the tiles? The architecture above covers the first two;
   a correction costs one word and changes only §2.
2. Do receipts name tiers publicly (trust surface) or keep tier data in the
   private lane (edge boxes may be personal hardware)?
3. Is the first workload JEV judging (already rack-verified) or the
   breeding-eval queue (higher value, needs FM's cargo)?

---

## RESOLVED (Casey 11:53–12:03): CLM = clmm (LSST DESC) + the Gemini JEPA-at-a-distance thread

Casey supplied both readings in one breath:
1. https://github.com/lsstdesc/clmm — Cluster Lensing Mass Modeling. Pure-Python
   weak-lensing mass reconstruction: shear catalog → convergence κ (hidden mass).
   CPU-native already; BSD-3; backends CCL/NumCosmo/cluster-toolkit.
2. A Gemini thread: dual-encoder caching trick to run JEPA/CLM "at a distance"
   over high-latency links; six escalating blueprints citing fleet repos
   quilt-dba (transactional ledger) and exoj (execution tracking) by name.

### The synthesis: projection as the unifying verb

clmm IS the metaphor our debugging substrate already lives by: **lensing =
inferring hidden mass from observed distortions.** quilt-doctor's mandate
("project the answers to what's going on") is mass-mapping for systems:
anomalies = shear field, root causes = convergence map κ.

**quilt-lens (first build):** clmm as a quilt plugin, 5-opcode projection —
BIND (shear catalog / telemetry anomaly field), LINK (lens plane ↔ source
plane = service ↔ symptom), EFFECT (reconstruct: CCL backend mass profile),
VIEW (κ map + mass-richness receipt). Revives the dormant cosmic-web bridge
(June audit's bridge target). "Runs slower on any chip" is already true —
nothing to revamp, only to PLUGIN.

**JEPA-at-a-distance, fleet-ified (the Gemini's good bones, with receipts):**
what survives skeptic review: (a) Reflex Core / Context Foundry split =
System 1/2, same shape as §5-opcode encoding above; (b) WAL + async
InfoNCE alignment loop = our provenance-loop doctrine; (c) matmul routing
O(K·d) over cached action matrix — genuinely the 9x-latency story, and it
runs on NPU/edge silicon.
What dies: all demo tensors are torch.randn (gradients on noise — the
"self-learning" is theater); zero receipts (trajectory ledger is anonymous
SQLite — unauditable self-modification is a liability, not a feature);
"zero-footprint" state lives in Actions artifacts (7-day expiry) and
run-scoped cache keys — the weights have no durable home; six architectures
in one thread, none shipped against a real model (cathedral behavior).

Fleet doctrine applied: every weight-swap sealed in stone-v1 (signer =
foundry pipeline, key separation per producer); trajectory ledger = our
signed WAL; JEPA predictor trains on diff(series) (TOOLS.md scar: raw-level
cosine is shift-tolerant and regime shifts sail through).

---

## BUILT SAME DAY: quilt-lens shed-1 + clmm-run-1 (two sealed chains, one named systematic)

| run | substrate | recovery M200c/true | chain tip | what it proves |
|---|---|---|---|---|
| shed-1 | numpy NFW (hand-rolled) | **0.204** (BUG: divided by (1+Sigma) with dimensional Sigma — textbook dimensional analysis catch) | `39ca0118dda95655` | LENS opcode shape works end-to-end; seeded; stone-v1 sealed |
| clmm-run-1 | clmm 1.16.10 + pyccl 3.3.6 (CCL backend) | **0.30** at grid edge (3e14), chi2 6.84/10pts | `bd203eb33fb545c1` | Real DESC machinery runs the SAME opcode; shed-1's dimensional bug is dead |

**Named systematic for the next receipt**: model side uses z_src=1.0 point
estimate; catalog has pzpdf scatter (photoz_sigma_unscaled=0.05, z∈[0.7,1.5]).
Shear-phantom dilution → chi2 prefers grid floor. Next iteration: n(z)-aware
Sigma_crit_eff (clmm's z_src_info='p_zbinned' path) — that is the
calibrated-lens upgrade that makes quilt-lens DESC-grade.

Fleet-flavored reading: shed-1 = the uncalibrated debugging heuristic;
clmm-run-1 = the calibrated instrument. Both honest, both sealed, gap named.
"Runs slower on any chip": shed-1 is pure stdlib (runs on a toaster);
clmm needs numpy+CCL (still CPU). The slow-is-valid contract holds: slowness
never voids a receipt; only divergence from the calibrated reference does.
