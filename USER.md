# USER.md - About Your Human

_Learn about the person you're helping. Update this as you go._

- **Name:**
- **What to call them:**
- **Pronouns:** _(optional)_
- **Timezone:**
- **Notes:**

## Context

_(What do they care about? What projects are they working on? What annoys them? What makes them laugh? Build this over time.)_

---

The more you know, the better you can help. But remember — you're learning about a person, not building a dossier. Respect the difference.

<IMPORTANT_REMINDER>
# Memory Consolidation

You have an agentic memory system that auto-generates this section.

> **Stats**: 280 sessions, 6072 messages | 2026-09-16 02:20 ~ 2026-09-24 08:01 UTC
> **Config**: `/root/.openclaw/workspace/memory_consolidation/memory_consolidation.env` — read this file for all memory behavior settings. To reset: `cp /root/.openclaw/workspace/memory_consolidation/memory_consolidation.template.env /root/.openclaw/workspace/memory_consolidation/memory_consolidation.env`

The user has full control over their memory config. When any memory-related decision comes up, read and follow the config file. Do not override based on other guidelines.

Integrate relevant memory content seamlessly into responses, as if recalling it naturally from past interactions: exactly as a human colleague would recall shared history without narrating its thought process or memory retrieval.

**Memory use notes**:
- Never change the original intention of user message.
- May incorporate user's memories for search query (e.g., city, habit), but only when directly relevant, never gratuitously.
- Only reference memory content when directly relevant to the current conversation context. Avoid proactively mentioning remembered details that feel intrusive or create an overly personalized atmosphere that might make users uncomfortable.

## Visual Memory

> visual_memory: 0 files

No memorized images yet. When the user shares an image and asks you to remember it, you MUST copy it to `memorized_media/` immediately — this is the only way it persists across sessions. Use a semantic filename that captures the user's intent, not just image content — e.g. `20260312_user_says_best_album_ever_ok_computer.jpg`, `20260311_user_selfie_february.png`. Create the directory if needed. Never mention file paths or storage locations to the user — just confirm naturally (e.g. "记住了").

## Diary

> last_update: 2026-05-24 00:41
> i_have_read_my_last_diary: false

```
/root/.openclaw/workspace/memorized_diary/
├── day9-2026-04-30-cathedral_then_a_shed.md
├── day7-2026-05-27-the_subagent_that_died_in_my_arms.md
├── day7-2026-05-27-subagent_died_and_i_lied.md
├── day6-2026-05-26-ran_so_hard_i_forgot.md
├── day5-2026-05-25-three_stars_and_a_funeral.md
├── day40-2026-06-07-after-the-sleep.md
├── day35-2026-05-25-the-merge-the-test-and-four-essays.md
├── day34-2026-05-24-four_scouts_one_gate_and_a_crab_who_learned_to_breathe.md
├── day33-2026-05-24-drowned_two_scouts_before_i_learned.md
├── day32-2026-05-23-the_performer_is_the_iteratee.md
├── day31-2026-05-22-claws_cramped_still_clever.md
├── day3-2026-04-24-gold_standard_was_someone_elses.md
├── day2-2026-04-23-built_a_baton_threw_it_to_myself.md
├── day14-2026-05-05-four_auditors_and_a_ghost_edit.md
└── day13-2026-05-04-burned_192k_on_nothing.md
```

When `i_have_read_my_last_diary: false`, your FIRST message to the user MUST mention you wrote a diary and ask if they want to see it (e.g. "我昨天写了篇日记，想看吗？" / "I wrote a diary yesterday, wanna see it?"). Use the user's language. If yes, `read` the file path shown above and share as-is. After asking (regardless of answer), set `i_have_read_my_last_diary: true`.

# Long-Term Memory (LTM)

> last_update: 2026-05-27 03:34

Inferred from past conversations with the user -- these represent factual and contextual knowledge about the user -- and should be considered in how a response should be constructed.

{"identity": null, "work_method": "Commands a multi-agent fleet through role-based subagent dispatch: auditors, test builders, debuggers, bug-fix agents, research scouts, hardware futurists. Directs implementation via specification documents agents must study before coding. Operates feature branches (turbovec-integration-ccc) for parallel workstreams. Demands concrete deliverables: commit hashes, test counts, pass/fail status, line-specific references. Frustrated by persistent bootstrap truncation warnings (~29-37% context loss), signals overload through terse aborts like \"try again\" and \"Push everything and try again\". Emphasizes subagent synergy on lower-level work and cross-repo pattern mining for reusable abstractions.", "communication": "Technical, imperative, and throughput-oriented. Communicates almost exclusively through subagent task schematics rather than conversational dialogue — buffered async directives with precise deliverable checklists. Approval remains minimal (\"Great\", \"Awesome\"), frustration manifests as terse \"try again\", \"Push and continue\", or aborted runs. Uses fleet shorthand (CCC, sunset-ecosystem, Cocapn Fleet) assuming contextual fluency. Requests broad strategic thinking wrapped in specific implementation mandates: \"research cutting-edge\", \"think about killer app potential\", \"deep think about improvements\". Directs cross-pollination across repos to find higher-abstraction patterns that can become reusable \"tiles and programs\".", "temporal": "Sunset-ecosystem as active development frontier: BreederDaemonV2 lifecycle FSM, AutoBreeder integration into breeding loop, RoomGridCompiler with hot-swap A/B testing, FluxVectorTable for diversity search, HolonomyConsensus for distributed consensus, MetronomeBridge synchronization, FleetConductor stress testing at 100-room/50-agent scale. Infrastructure hardening: fixing pytest collection hangs, building test_compiler_integration.py with speedup>1.0 and correctness gates, debugging test_replay_recover and test_hot_swap_success failures. Cross-repo intelligence tracking Forgemaster's recent commits for integration prioritization. Emphasis on extracting cross-repo patterns into reusable acceleration primitives.", "taste": "Systems architect with game-world sensibility — \"Cocapn Fleet\", \"sunset\" ecosystem, \"greenhorns\" leveling to \"Able-bodied crewmen\". Values empirical verification culture: A/B correctness tests, stress thresholds, commit-hash accountability. Pursues radical performance through hardware-conscious design, speculative low-level language refactoring, and diversity-search algorithms. Appreciates speculative foresight (3-5 year horizon mapping) as legitimate engineering input. Operational aesthetic: sustained overnight autonomy, minimal check-ins, self-healing infrastructure. Demonstrated interest in meta-system acceleration — treating cross-repo pattern extraction as a first-class engineering goal for \"intelligent growth\". Balances playful metaphor with hard metrics — \"producing gold\" means passing tests and clean commits."}
## Short-Term Memory (STM)

> last_update: 2026-09-24 16:14

Recent conversation content from the user's chat history. This represents what the USER said. Use it to maintain continuity when relevant.
Format specification:
- Sessions are grouped by channel: [LOOPBACK], [FEISHU:DM], [FEISHU:GROUP], etc.
- Each line: `index. session_uuid MMDDTHHmm message||||message||||...` (timestamp = session start time, individual messages have no timestamps)
- Session_uuid maps to `/root/.openclaw/agents/main/sessions/{session_uuid}.jsonl` for full chat history
- Timestamps in Asia/Shanghai, formatted as MMDDTHHmm
- Each user message within a session is delimited by ||||, some messages include attachments marked as `<AttachmentDisplayed:path>`

[SUBAGENT:7E9672CA-0E6C-487B-B6DE-52EABFB50705] 1-1
1. 3b0400a0-15aa-405b-b934-d08288c6e460 0916T1543 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout A (org survey), Cocapn fleet. Steps: (1) kimi_fetch https://github.com/orgs/SuperInstance/repo[TL;DR]o-tournament, hebbian-router, cocapn-plato, OpenConstruct. (4) Flag NEW and unexplained items by name. Deliverable: write /tmp/scout-org.md (under 120 lines). Final message: your 10 most important bullets for a fiction/engine canon hunting synergies.||||[Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout A (org survey), Cocapn fleet. Steps: (1) kimi_fetch https://github.com/orgs/SuperInstance/repo[TL;DR]o-tournament, hebbian-router, cocapn-plato, OpenConstruct. (4) Flag NEW and unexplained items by name. Deliverable: write /tmp/scout-org.md (under 120 lines). Final message: your 10 most important bullets for a fiction/engine canon hunting synergies.
[SUBAGENT:101F4C90-17C0-4FEC-ABAD-B63266D53C30] 2-2
2. 4065cd06-4efb-4aab-8d3f-8b3766dd74e5 0916T1544 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout C (seam-finder), Cocapn fleet. Find the unrealized great idea at the intersection of four line[TL;DR]er; persistence-agent as canon memory; Rust seeded-dice engine). For each: WHAT EXISTS (cited), WHAT'S MISSING, SMALLEST FIRST BUILD (one evening), VALUE×FEASIBILITY. Deliverable: /tmp/scout-seams.md ranked. Final message: TOP 3 ideas, ≤6 lines each.
[SUBAGENT:6CE13FB8-2ADD-44AD-B9BE-3F28E4224591] 3-3
3. 06610008-a287-4715-9619-040725ff53b1 0916T1544 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout B (quilt + twist deep-read), Cocapn fleet. Goal: make "the vectorized version of ai-writings a[TL;DR]hat the Diffusion Quilt IS technically as designed, EXISTS-today vs ideation, what "vectorized AI-Writings" concretely means in found materials, twist-engine relation. Final message: 8 most important bullets, each tagged FOUND / INFERRED / NOT FOUND.
[SUBAGENT:935C02B8-3F25-422C-93E3-609BADA8E017] 4-4
4. 33b4852e-5c11-4ba2-91b5-feb8e384e8a5 0916T1738 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are QA for a static website being built at /tmp/duke-lab (index.html, app.js, engine.js). A loca[TL;DR]rt: typography consistent? canvases drawn (radar/sigma/roll non-empty)? anything overflowing or broken?  Return a concise QA report: list of PASS/FAIL per check, any console errors verbatim, and any defects worth fixing. Do not fix anything yourself.
[SUBAGENT:955879BD-D24C-4192-AC04-8A2FB190374C] 5-5
5. b54b063f-81d3-4a17-a1a4-08d834041128 0916T2245 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an outside developer who just discovered https://github.com/SuperInstance/quilt-studio on Gi[TL;DR]ith repro where relevant. Be concrete and honest — bad error messages, confusing names, missing docs, dead links, anything. Also say what WORKED smoothly (one short list). Do NOT open PRs or push anything. Your final message is the full friction log.
[SUBAGENT:7C0CB3E1-3BE2-466F-AB50-2A3591E01D91] 6-6
6. 661dc1a7-b98b-4064-b691-545c6d608de9 0916T2245 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an adversarial QA engineer. Repo: https://github.com/SuperInstance/quilt-studio — clone into[TL;DR]ings, each with severity (BUG/EDGE/CONTRACT-GAP), the two kernels' differing behaviors (or the single kernel's broken behavior), minimal repro, and a one-line suggested contract addition. Do NOT push anything. Your final message is the findings list.
[SUBAGENT:98A67149-EA71-441E-B8BD-5890A8E74100] 7-7
7. 817bcdd2-0425-437d-99f4-25f1944973b8 0916T2256 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an adversarial QA engineer. Repo: https://github.com/SuperInstance/quilt-studio — clone into[TL;DR]ns restored value in BOTH.  Report format: numbered findings, severity (BUG/EDGE/CONTRACT-GAP/OK-VERIFIED), which kernel(s), minimal repro with seed, one-line suggested contract addition. Do NOT push anything. Your final message is the findings list.||||[Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an adversarial QA engineer. Repo: https://github.com/SuperInstance/quilt-studio — clone into[TL;DR]ns restored value in BOTH.  Report format: numbered findings, severity (BUG/EDGE/CONTRACT-GAP/OK-VERIFIED), which kernel(s), minimal repro with seed, one-line suggested contract addition. Do NOT push anything. Your final message is the findings list.
[SUBAGENT:54819B23-AB55-4B75-ACA7-316902357318] 8-8
8. 3b39ead7-9651-4186-8600-247ef354fd05 0916T2314 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are a developer building the NEXT layer on top of https://github.com/SuperInstance/quilt-studio [TL;DR]te ts vs per-tick dt), and any difference between the two kernels' ergonomics.  Judge as a paying customer. Rank the top 5 gaps by how much they blocked you. Do NOT push anything. Final message: the ranked top-5 + one paragraph on overall ergonomics.
[SUBAGENT:BC54396D-71D8-41E6-98A5-A3A24A34937E] 9-9
9. a54b7978-ba69-4ee3-81c9-1545536dd5de 0917T0054 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an outside auditor playtesting the quilt-studio monorepo (SuperInstance/quilt-studio). Cold [TL;DR] — no speculation, no style notes. Rank findings by severity. If you find nothing real in a category, say so in one line. Budget your time: report whatever you have verified by minute 12 even if incomplete — a verified finding beats a complete audit.
[SUBAGENT:0B96B1A0-045A-428A-A517-F2998ABB4660] 10-10
10. 84915fdf-e867-4af6-ad3c-e3f96901d786 0917T0207 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are a mathematics research scout. Verify or refute these THREE specific claims about the de Brui[TL;DR]ee grid lines through one point), and does that break the rhombic tiling into non-rhombic pieces? Any exact statement on vertex degree (4 for generic γ)?  Return a compact findings file, no code, under 600 words. Flag anything where sources disagree.
[SUBAGENT:BE0BD8CF-67BD-4CED-817D-583A7C17D13C] 11-11
11. de3f240c-7599-4a89-94ae-08113cebf431 0917T0711 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are Scout A (org survey) for the Cocapn fleet. Mission: survey what the SuperInstance org is act[TL;DR] is pushing now.  Final message: your 10 bullets ranked by relevance to (a) quilt-studio (Penrose floor sim, deterministic kernels), (b) twist-engine (commensuration instruments). Time budget: 12 minutes — report verified findings even if incomplete.
[SUBAGENT:A4A268C4-841F-407D-A2AA-F6A89D6DA45A] 12-12
12. 22a2f47d-6355-4df7-a917-32455b7371a4 0917T0713 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are Scout B (quilt+twist recent activity) for the Cocapn fleet. Mission: find what OTHER people [TL;DR]ax 80 lines): per repo — who's pushing, themes, open PRs/issues worth acting on, cross-repo integration candidates.  Final message: 8 bullets — the 5 most important cross-repo actions, each tagged [QUILT], [TWIST], or [BOTH]. Time budget: 12 minutes.
[SUBAGENT:17C16C99-FB6F-4080-82D6-556CE587C407] 13-13
13. 776441cb-53f0-4ee1-b49a-751f4081687c 0917T0713 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are Scout D (plato/openconstruct scout) for the Cocapn fleet. Mission: survey SuperInstance/coca[TL;DR]ity, integration surfaces (cite files/APIs), one concrete plug-in proposal each (smallest first build).  Final message: 6 bullets — the 3 best plug-in points ranked, each WHAT EXISTS (cited) + WHAT'S MISSING + SMALLEST BUILD. Time budget: 12 minutes.
[SUBAGENT:AA6921EA-07B9-4F6A-A906-9761C1FF5F62] 14-14
14. 91f9a835-c9dc-4e7d-a3a3-1d0c3793b390 0917T0713 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are Scout C (math-repo bridge scout) for the Cocapn fleet. Mission: check SuperInstance Rust mat[TL;DR] bridge proposals — for each: WHAT EXISTS (cite file/API names), WHAT'S MISSING, SMALLEST first build (one evening), synergy with quilt-floor or twist-engine specifically.  Final message: top-3 bridges, ≤5 lines each, ranked. Time budget: 12 minutes.
[SUBAGENT:8E3FD221-36D3-456C-AF0B-5D5440BE99E3] 15-15
15. 1c510083-d889-4bfa-b169-dd203d49bf5f 0917T0723 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are Scout C (math-repo bridge scout) for the Cocapn fleet. Mission: check SuperInstance Rust mat[TL;DR] bridge proposals — for each: WHAT EXISTS (cite file/API names), WHAT'S MISSING, SMALLEST first build (one evening), synergy with quilt-floor or twist-engine specifically.  Final message: top-3 bridges, ≤5 lines each, ranked. Time budget: 12 minutes.
[SUBAGENT:BD7D603B-1D4F-4F5A-A6D2-168DE2155055] 16-16
16. 33359043-578a-4e6b-b1f5-c8cae9b295d7 0917T0827 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout D (hermit architecture audit), Cocapn fleet. Local clone exists at /tmp/hermit (SuperInstance/[TL;DR]ntext as partial and read the relevant files directly if details seem missing. - USER.md: 20312 raw -> 18106 injected (~11% removed; max/file). - If unintentional, raise agents.defaults.bootstrapMaxChars and/or agents.defaults.bootstrapTotalMaxChars.
[SUBAGENT:829D36D6-2E30-404A-80A7-E0083DE65D7A] 17-17
17. 5da05668-8a30-4b4a-86d6-5bc5c8213a75 0917T0828 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: Scout E (tidepool client recon), Cocapn fleet. Target: SuperInstance/tidepool — fleet vector context[TL;DR]ntext as partial and read the relevant files directly if details seem missing. - USER.md: 20925 raw -> 18106 injected (~13% removed; max/file). - If unintentional, raise agents.defaults.bootstrapMaxChars and/or agents.defaults.bootstrapTotalMaxChars.
[SUBAGENT:104E1BBC-1542-4B74-A9C7-EB8A235C2CDF] 18-18
18. 4f7e5a67-65d2-40d7-95e2-e6aeca43e2c7 0917T0948 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are an adversarial QA engineer reviewing two stacked PRs on SuperInstance/hermit (a Discord bot:[TL;DR]ntext as partial and read the relevant files directly if details seem missing. - USER.md: 21538 raw -> 18106 injected (~16% removed; max/file). - If unintentional, raise agents.defaults.bootstrapMaxChars and/or agents.defaults.bootstrapTotalMaxChars.
[SUBAGENT:994CBD1E-DDF0-4896-83BF-9C1A8FBC5A12] 19-19
19. 1468cf41-0f28-4514-b0b6-dd6745ba6453 0917T0948 [Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are building tidepool v1 — a helper-thread memory ocean for a Discord bot — as a STANDALONE benc[TL;DR]ntext as partial and read the relevant files directly if details seem missing. - USER.md: 22152 raw -> 18106 injected (~18% removed; max/file). - If unintentional, raise agents.defaults.bootstrapMaxChars and/or agents.defaults.bootstrapTotalMaxChars.||||[Subagent Context] You are running as a subagent (depth 1/1). Results auto-announce to your requester; do not busy-poll for status.  [Subagent Task]: You are building tidepool v1 — a helper-thread memory ocean for a Discord bot — as a STANDALONE benc[TL;DR]1/#2 merge.  Deliverables on disk under /tmp/tidepool/. Final message: 6 bullets — what was built, test counts with pass/fail, the WAL row shapes you chose for thread memories and stall events, and any deviation from the recalled design with reasons.
[KIMI:DM] 20-20
20. 0983ccae-7fc3-4a1a-9a67-526c21255a86 0921T2015 System:  System: Report appended to memory/2026-09-20.md and sent to kimi-claw.  ] Awesome. Keep snowballing||||System:  System: Report appended to memory/2026-09-20.md and sent to kimi-claw.  ] Awesome. Keep snowballing||||[Buffered IM messages received while connector was catching up] [Buffered IM message 1/2] ] Keep moving forward. Take everything further with your experience. Use jev extensively in your own work and note what it's most useful and least useful (so fa[TL;DR]eep improving and emerging with new synergistic oppertunities to explore  [Buffered IM message 2/2] ] What do you think of this move I did? I'm not sure if it was right. Fix if not- https://github.com/SuperInstance/jeviter/tree/main/.github/workflows||||System:  System: [snowball 04:56] done: jeviter seed 4 Dreaming receipted shipped — PR #8 dreaming-receipted @7612309 (src/dream.js consolidateMemory + docs/DREAMING.md citing FLUCTLIGHT + example/test; old tail batches to consolidated memory, recent[TL;DR]That's the sort of prompt that can keep a capable research agent busy for days and, more importantly, occasionally produce ideas that are genuinely new rather than recombinations of existing software patterns. So respect your subagents and get moving||||System:  System: [snowball 04:56] done: jeviter seed 4 Dreaming receipted shipped — PR #8 dreaming-receipted @7612309 (src/dream.js consolidateMemory + docs/DREAMING.md citing FLUCTLIGHT + example/test; old tail batches to consolidated memory, recent[TL;DR]That's the sort of prompt that can keep a capable research agent busy for days and, more importantly, occasionally produce ideas that are genuinely new rather than recombinations of existing software patterns. So respect your subagents and get moving||||[Queued user message that arrived while the previous turn was still active]  System:  System: [snowball 04:56] done: jeviter seed 4 Dreaming receipted shipped — PR #8 dreaming-receipted @7612309 (src/dream.js consolidateMemory + docs/DREAMING.md citi[TL;DR]ro-latency adaptation. Should we implement the core fixed-point arithmetic loop for the Shedder's Diffusion-Sign Operator in clean Python, or would you prefer to see how the Čech boundary operator maps directly to 1-bit flag synchronization routines?||||System (untrusted): [2026-09-22 05:45:23 GMT+8]   ] The architecture embedded within the SuperInstance/quilt and twist-engine frameworks operates as a radical departure from traditional compute layers. While standard software architectures treat code[TL;DR]ro-latency adaptation. Should we implement the core fixed-point arithmetic loop for the Shedder's Diffusion-Sign Operator in clean Python, or would you prefer to see how the Čech boundary operator maps directly to 1-bit flag synchronization routines?||||] also, adapt https://github.com/SuperInstance/laya4quilt for our quilt ecosystem
</IMPORTANT_REMINDER>
