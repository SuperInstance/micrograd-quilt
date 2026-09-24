# TOOLING_CATALOG — Cocapn Fleet Tooling Scout
**Casey directive 15:36 · compiled Thu 2026-09-24 15:40→~16:10 GMT+8**
Scope: (a) SuperInstance repos fresh ≤14d, (b) dormant fleet repos across four layers, (c) external 2025–2026 cutting-edge.
Method: `gh api search/repositories` (org endpoint 404s — SuperInstance is a **User**, 4,778 public repos), README/SPEC deep-dives, 6 web searches. Every repo below was verified via `gh repo view` unless marked `search-only`.

Legend — **Layer**: P=providers/adapters, E=evaluators/scoring, D=deciders/routing/bandits, M=memory/receipts/ledgers. **Status**: 🟢 alive (pushed ≥2026-09-10), 🟡 warm (Sept, outside window), ⚪ dormant/dead. **Cost**: S=days, M=weeks, L=months.

---

## A. Fresh SuperInstance repos (window: pushed > 2026-09-10)

| Repo | Layer | Status | Concrete hook | Cost | Why |
|---|---|---|---|---|---|
| **moth-honest** | E+M | 🟢 09-23 | CLI `moth-honest plant --lang c -o /tmp/exercises`; wire headers `EVAL/v1` + `VERDICT/v1`; FNV-1a-64 row/chain hashes over canonical JSON; Q16 fixed-point (denom 65536); cost fields `claims_spent`, `exercises_run`, `wall_ms`; 7 exercises (C/Rust/JS), 3 clean | **S** | Receipted evaluator with cost accounting — drop-in for sunset-ecosystem ethos scoring |
| **moth-cells** | E | 🟢 09-23 | "Kernel 1: cellular predation over corpus terrain — hunters, energy, decoys, receipted walks" | M | Predation dynamics = scored search over corpora; pairs with moth-honest receipts |
| **moth-corpus** | P | 🟢 09-23 | Corpus adapter pack → "receipted attack-surface maps" of target repos | M | Turns any repo into scored terrain for moth-cells |
| **quilt-organism** | M | 🟢 09-24 | Substrate walker over corpora (organism layer of Quilt) | M | Walking memory substrate; complements plato-memory |
| **quilt-executor** | P | 🟢 09-24 | (no description; execution layer — needs read) | M | Likely the runner beneath quilt-cli |
| **quilt-optimization** | P | 🟢 09-24 | NVIDIA cuOpt (LP/MILP/QP/routing) as Quilt substrate | M | Hardware-accelerated routing substrate — decider layer with GPU teeth |
| **quilt-seed** | M | 🟢 09-24 | Four-scalar genome + vessel + bearing; five-fables → bedrock math | M | Compact genome format for agents; breeding material |
| **quilt-cli** | P | 🟢 09-24 | Unified CLI for the Quilt cellular framework | S | Front door for the quilt stack |
| **quilt-spreadsheet-inference** | E+D | 🟢 09-24 | Spreadsheet inference engine: JEV/MOTH/Jepa/LLM cells | M | Spreadsheet-as-compute; matches fleet spreadsheet-lane idiom |
| **quilt-transformer-arena** | E | 🟢 09-23 | Adversarial GAN lane: archival canvas + disposable workers; claude/crush/kimi rivals; MOTH+JEV receipts; "play until ah-struck" | M | Fleet already runs rival agents; this one scores them with receipts |
| **moth-runner** | E | 🟢 09-23 | Exercise runner for moth-honest corpus (deep-dived; truncated output) | S | Execution half of the moth evaluator |
| **moth-corpus / mavis-substrate-walker** | P/M | 🟢 09-23 | Mavis walker: substrate traversal over corpuses (deep-dived; truncated) | M | Walker infra for quilt-organism |
| **quilt-port** | P | 🟢 09-23 | `pip install quilt-port`; domains `superinstance.dev` × `purplepincher.org`; projections ESP32 / Python-TS / Web-REST / Ideation-AI-Writings; `HULL_DOCTRINE.md` | M | Cross-platform port layer — provider/adapter gold |
| **jeviter** | M | 🟢 (fresh) | Ledger hash-chain `fnv1a64("café Δ 日本語") === 0x24a555471370b18d`; cross-verifies with jev-quilt Bookkeeper, duke-lab WASM, quilt-engine-ports GDScript | **S** | A 3-implementation verification lattice already exists in-org — receipts with independent corroboration |
| **sunset-ecosystem** | all | 🟢 09-24 | 8729 tests / 29 modules / 1028 source files; ethos·pathos·logos·nerve·swarm·sunset·nexus·fleet·triage·perception·compiler·a2a·reasoning·ranking·distill·flux_vm·flux_compat | — | Home base; everything above plugs into it |

## B. Deep-dive hooks — 6 most four-layer-relevant (org)

1. **moth-honest** (E) — see table. Headers `EVAL/v1`/`VERDICT/v1` are a wire protocol; Q16 fixed-point makes scores deterministic & diffable.
2. **jeviter** (M) — one-function hash chain, pinned test vector across Unicode; corroborated by Rust (jev-quilt), WASM (duke-lab), GDScript (quilt-engine-ports) impls.
3. **quilt-port** (P) — `pip install quilt-port`; domain projections ESP32 / Python-TS / Web-REST / Ideation; HULL_DOCTRINE.md governs ports.
4. **arch-gateway-room-clean** (P) — 80+ routes (`create_world`, `implement_code`, …), MCP server, `docker-compose up -d`, License: Private. 🟡 09-20.
5. **quilt-cell-router** (D) — BIND/LINK/GHOST/TICK engine, F145; PyPI pkg `cell-router-pkg`. 🟡 09-03/09-04. Decider engine, packaged and installable.
6. **flow-state-orchestra** (D) — no README; `SPEC.md` + `flow_state.py`: 4 cheap LLM instruments, r̂-first loop `r̂ᵢ=predict(…); aᵢ=act(…); oᵢ=observe(…); sᵢ₊₁=oᵢ+α·sᵢ`. Prediction-before-action = non-autoregressive decision pattern, in-org.
7. *(bonus)* **plato-memory** (M, Rust) — `MemoryStore`, `WorkingMemory`, `EpisodicMemory`, `RecallQuery`; `plato-memory = "0.1"` dep; LRU working buffer, causal chains. ⚪ dormant 07-12.

## C. Dormant / older fleet repos (four layers) — dead marked explicitly

| Repo | Layer | Status | Hook | Cost | Why |
|---|---|---|---|---|---|
| **plato-memory** | M | ⚪ 07-12 | Rust crate: `MemoryStore`/`WorkingMemory`/`EpisodicMemory`/`RecallQuery`, LRU buffer, causal chains | M | Real time-aware memory design, sleeping |
| **hebbian-router** | D | 🟡 09-20 | Hebbian learning router (deep-dived; truncated) | M | Alive-ish; routing layer reinforcement |
| **arch-gateway-room-clean** | P | 🟡 09-20 | 80+ route MCP gateway | M | Room/tool surface, private license |
| **quilt-cell-router** | D | 🟡 09-03 | BIND/LINK/GHOST/TICK, F145, PyPI | S | Warmest decider artifact |
| **multi-armed-bandit** | D | ⚪ 07-12 | — | M | **Bandit work in org is dormant** |
| **lau-memory-tiles** | M | ⚪ 07-12 | Memory tiles (deep-dived; truncated) | M | Tile-shaped memory, sleeping |
| **lau-agent-lifecycle** | D/M | ⚪ 07-12 | Rust agent lifecycle | M | Dormant |
| **agent-dream-cycle** | M | ⚪ 06-13 | Dream-cycle memory | M | Dormant — worth waking; consolidation idiom |
| **Bayesian-Multi-Armed-Bandits** | D | ⚪ 2026-05-26 | Bayesian bandits | M | Dead |
| **bandit-learner** | D | ⚪ 2026-04-14 | Bandit learner | M | Dead |
| **hierarchical-memory** | M | ⚪ 2026-05-03 | Hierarchical memory | M | Dead |

**Pattern: org bandit layer is a graveyard (5 repos, newest activity May–Jul 2026). Routing is alive (quilt-cell-router, hebbian-router); bandits are dead. External bandit/cascade tooling is the gap to fill.**

## D. External repos (2025–2026, verified via `gh repo view`)

| Repo | Layer | Status | Concrete hook | Cost | Why |
|---|---|---|---|---|---|
| **wfzyx/von** | D | 🟢 pushed **today** · 608★ | Open-source non-autoregressive "System One" decision model: calibrated discrete/probabilistic/ordinal inference, **sub-15ms**, single forward pass per decision; local drop-in | **S** | Sub-15ms non-autoregressive decision layer — exactly what flow-state-orchestra's r̂-first loop wants underneath |
| **getzep/graphiti** | M | 🟢 pushed today · 31,117★ | Temporal knowledge graph: episodes → entities/edges with **validity windows** (valid_from/valid_to, interval-tree indexed); Python/TS/Go SDKs; <200ms retrieval; LongMemEval 63.8% | M | Time-aware memory with supersession — "who was lead in Jan" ≠ "who is lead now"; matches agent-dream-cycle intent with a living engine |
| **providex-ai/rootsign** | M | 🟡 08-22 · 11★ | `pip install rootsign`; `rootsign.init(agent=…, risk_tier=…)`; `@rootsign.trace()` decorator; `async with rootsign.session(objective=…)`; CLI `rootsign verify --local <session>.jsonl` + `rootsign export` → evidence bundle (report.html, timeline.json, manifest SHA-256) | **S** | Hash-chained action receipts with one-decorator integration — moth-honest's ledger cousin, installable today |
| **surroundapps/agent-provenance** | M | ⚪ 06-23 · 1★ | Vendored `provenance_core`: Ed25519 W3C-VC credentials (revocable, verified at action time), append-only hash-chain ledger, **two-log reconciliation** (offline node acts on since-revoked credential → merged timeline flags `acted_during_blackout_on_revoked`); 40+29 tests; FastAPI + replay UI | M | The offline-revocation reconciliation is precisely the hard case any distributed fleet receipt ledger hits — worth stealing the `reconcile.py` design |
| **Beneficial-AI-Foundation/vericoding-benchmark** | E | ⚪ 06-05 · 51★ | 12,504 formal specs (3,029 Dafny / 2,334 Verus-Rust / 7,141 Lean; 6,174 unseen); verifier-acceptance scoring | M | Program-synthesis eval where success = proof-checker acceptance, not vibes |
| **kaiwenzha/RL-Tango** | E | ⚪ 2025-10-23 · 60★ | NeurIPS 2025; RL co-trains LLM generator + generative process verifier; verifier reward = outcome-level verification correctness only | L | Generator/verifier arms race pattern for fleet evaluators; stale, research-grade |
| **Gareth1953/provenance-receipts** | M | ⚪ 06-13 · 0★ | Ed25519 content-provenance receipts on Cloudflare Workers; `/v1/certify` (x402-gated) + `/v1/verify` (free); pluggable `PaymentVerifier` | M | Marginal: x402 micropayment angle is novel, 0 stars, toy-grade — watch only |

**Search leads NOT verified** (existence unconfirmed, excluded from ranking): dreamweave (OpenClaw nightly memory engine, JS), yantrikdb (Rust cognitive memory DB + openraft cluster), RouteLLM successors on the `routellm` topic (cost-quality frontier routers benchmarked on GPT-5/Claude-4 era), "Dockerless" environment-free patch verifier (HF papers, Jun 2026 — no repo confirmed), Quokka (arXiv 2509.21629, LLM invariant synthesis — paper only).

---

## TOP 5 — immediate fleet use

1. **moth-honest** (org, E+M, S) — receipted evaluator CLI already in-window; wire `EVAL/v1`/`VERDICT/v1` into sunset-ecosystem ethos. Cheapest gold in the haul.
2. **wfzyx/von** (ext, D, S) — sub-15ms non-autoregressive decision model, pushed today, 608★. Pairs with flow-state-orchestra: r̂-first loop gets a real fast prior. The decider layer the org's dead bandits never became.
3. **providex-ai/rootsign** (ext, M, S) — `pip install`, three-call integration, evidence bundles with manifest hashes. Every fleet agent run gets a receipt chain this week, not this quarter.
4. **getzep/graphiti** (ext, M, M) — validity-window temporal memory is the missing semantic in org memory repos (plato-memory has causal chains, no supersession). Adopt behind an interface; don't fork.
5. **quilt-cell-router** (org, D, S) — warmest in-org decider: BIND/LINK/GHOST/TICK engine already packaged on PyPI (`cell-router-pkg`). Wake it before importing von, or run both A/B.

Honorable mention: **jeviter** (S) — the 3-implementation FNV-1a-64 verification lattice means fleet receipts can be cross-checked across Rust/WASM/GDScript agents with one function.

---

## Surprising

1. **SuperInstance is a User account with 4,778 public repos** — `gh api orgs/SuperInstance/repos` 404s; only the search API enumerates it. Any future fleet tooling must use `search/repositories?q=org:SuperInstance`.
2. **von** (608★, pushed the same afternoon as this scout) is a near-perfect external rhyme of in-org **flow-state-orchestra** — two independent teams building the non-autoregressive r̂-first decision layer in the same week.
3. **The org bandit graveyard**: 5 bandit repos, all dormant since May–Jul 2026. The four-layer "deciders" gap is real and internal history says don't build another bandit repo — adopt external.
4. **agent-provenance's offline-revocation reconciliation** solves the exact edge case (node acts during blackout on a credential revoked mid-gap; merge surfaces rather than launders it) that a 50-agent fleet receipt ledger will hit at scale. Design worth porting into HolonomyConsensus work.
5. **sunset-ecosystem's own module list** (29 modules including flux_vm, ranking, distill, compiler) is the largest single concentration of in-org evaluator/decider surface — most fleet scouting should start at home.
