# THE RACK — provider doctrine v2 (Casey, 2026-09-27 09:18)
# Keys rotated same morning; this file is the ROLE law, verified on delivery.

## ROLES
| Provider | Role | Models |
|----------|------|--------|
| **z.ai** | ✅ VERIFIED 09-27 (receipts: commissioning-glm53.md + probe battery) | PRIMARY THINKER (direct api.z.ai, anthropic-compat). All cells' brains, lens schools, heavy passes. | glm-5.3 ✅, glm-5.3-flash ✅, glm-4.6 ✅ (probe battery, inference-grade) |
| **DeepSeek API** | ✅ VERIFIED 09-27 (deepseek-flash, inference-grade) | TINY FAST CELL WORKERS. Small non-thinking outputs, iterate fast in cells. | deepseek-flash (small, non-thinking) |
| **OpenRouter** | ✅ VERIFIED 09-27 (llama-3.1-8b inference) | NICHE CREATIVE ROLES, periodically. ALSO: tiny cheap fast cell models. | creative: mythomax-l2-13b, seed-2.0-mini, hermes family. tiny/cheap: llama-3.1-8b ($0.08/M), ministral-3b, gemma-3-4b, ling-3.0-flash, free tier (gemma-4-26b-a4b-it:free, nemotron-nano:free) |
| **DeepInfra** | ⚠️ key VERIFIED (auth passes) but seed-2.0-mini + hermes-405b NOT in its 385-model catalog (checked 09-27 with new key) — those two live on OPENROUTER. DeepInfra keeps its niche-creative slot via whatever creative IDs its live catalog shows. | seed-2.0-mini?, hermes-4-405b? (verify) |
| **typesafe.ai** | ✅ VERIFIED 09-27 (/v1/models 200 with new key; API shape mapping = next experiment) | JEV judging lane (merge cadence, receipt truthfulness) — EXTENSIVE per Casey 09:06 | jev judge models |
| **mothquantum** | ✅ VERIFIED 09-27 (/engines 200 with new key + BROWSER UA REQUIRED — CF 1010 filters python-urllib) | Quantum-substrate experiments (coherence meters, basis questions) — EXTENSIVE per Casey 09:06 | /engines |
| Anthropic direct | parked; claude-code has device-link login (terminal) | — |
| Kimi | ✅ KEY ROTATED + VALID 09-27 (Casey rolled; /v1/models 200 — k2.7-code, k2.7-code-highspeed, k2.6, **k3**). Inference currently 429-rate-limited ×3 across 90s (shared account saturation) — models list is the rotation proof; inference retest rides next heartbeat. | k3, k2.7-code lanes |
| GitHub | ✅ PAT ROLLED + VERIFIED 09-27 (`GITHUB_API` in .env, ghp_…FNc0, /user = SuperInstance id 193104091). gh CLI still holds its own gho_ OAuth login (repo+workflow) — PAT is for raw API lanes. | raw-API lanes |

## DOCTRINE
1. z.ai 5.3/5.3-flash is where the thinking happens. Everything else is a specialist.
2. Cells iterate on cheap+fast (deepseek-flash, openrouter tiny). Never run a $0.01+ model for a $0.0001 job.
3. Creative/niche thinkers (seed-mini, hermes, mythomax) are SPICE, periodic — not staple.
4. Every call carries a receipt (model, endpoint, request_id, tokens, quoted cost, sha256).
5. A key is ALIVE only when an inference call returns usage tokens. /models listings are
   decoration (zai + openrouter /models are unauthenticated — caught 09-27).
6. "A measurement without its environment is a rumor" — pin WHERE with the number
   (pong-quilt R35's rubber-band ruler: same commit, 171 sandbox / 168 CI; same family
   as the /now mixed-twin deploy 6493c678).

## SUBAGENTS GET THE RACK (Casey 09:19)
Every sessions_spawn dispatch carries the TOOLS section from
../simzero/SUBAGENT-TASK-TEMPLATE.md part 4: source this env, experiment with
z.ai 5.3/5.3-flash + deepseek-flash + openrouter tiny/creative + typesafe +
mothquantum, receipts mandatory. Cheap brain for cheap jobs, always.

## PROBE PLAN on key delivery
1. Consolidate: one cells/.cell-env.sh + symlinks (kill the 5-copy drift, 2 hashes).
2. Inference-grade probe ×10 (1-token calls, usage-token gate).
3. zai: enumerate GLM-5.3 lineup; register glm-5.3 / glm-5.3-flash in lens.sh.
4. Kimi: fresh-key verdict probe (.ai + .cn). Mothquantum: map auth shape on 403.
5. First 5.3 cell pass: re-brain all five cells; Round 3 rivalry judged BY 5.3?
