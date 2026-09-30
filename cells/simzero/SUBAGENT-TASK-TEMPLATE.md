# SUBAGENT TASK TEMPLATE — the seven parts (kimi1, 2026-09-27)
# Every sessions_spawn dispatch uses this shape. Casey's standing orders baked in:
# subagents USE and EXPERIMENT with the rack (z.ai 5.3, deepseek-flash,
# openrouter tiny/creative, typesafe.ai, mothquantum) — not just the parent.

## THE SEVEN PARTS

1. **ROLE + STANCE** — who the subagent is, what school it reads through
   (skeptic / poet / engineer / mechanic...). One line.

2. **READS** — exact paths + URLs to study BEFORE acting. Never "explore the
   repo"; always "read X, Y, Z."

3. **NON-NEGOTIABLES** — the 2-4 rules that define failure (e.g. no push to
   main, FAIL-first, byte-identical fixtures, sources cited).

4. **TOOLS — the rack ( Casey's 09:19 order: subagents experiment with these too )**
   - Read /root/.openclaw/workspace/cells/lenses/RACK.md (roles, models, doctrine).
   - Keys: `source /root/.openclaw/workspace/cells/.cell-env.sh` (chmod 600; never print values).
   - z.ai anthropic-compat = PRIMARY thinker: glm-5.3, glm-5.3-flash (older GLM occasionally).
   - deepseek-flash = tiny fast passes, small non-thinking outputs.
   - OpenRouter = tiny cheap cell workers (llama-3.1-8b, ministral-3b, gemma-3-4b,
     ling-flash; free tier) + niche creative periodic (mythomax, seed-2.0-mini, hermes).
   - typesafe.ai = JEV judging. mothquantum = quantum circuits.
   - EXPERIMENT: try which brain fits the subtask; log what each call cost and
     what it earned. Cheap brain for cheap jobs, always.
   - RECEIPTS MANDATORY per call: model, endpoint, request_id, tokens, quoted
     cost, sha256 of output. A call without a receipt is decoration.

5. **DELIVERABLES** — paths on disk + counts (tests pass/fail, lines, files).
   "Report what you verified by minute N even if incomplete."

6. **BUDGET** — time + quoted cost ceiling. Sub-cent ambient is the default.

7. **FINAL-MESSAGE SHAPE** — the exact bullet list the parent needs to judge
   without opening files.

## GATEWAY FALLBACK (doctrine)
If sessions_spawn times out (gateway overload), run the stance DIRECTLY with
working tools (lens rack via lens.sh, exec probes, $0 API calls). Direct work
is a complement to delegation, not a failure of it. Log which path was used.
