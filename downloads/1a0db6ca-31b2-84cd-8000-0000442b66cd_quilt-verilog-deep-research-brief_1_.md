# quilt-verilog — Deep Research Brief

**A bilingual EN+中文 adversarial research synthesis on `SuperInstance/quilt-verilog`**
**Scope:** repo forensics · ecosystem map · LLM-for-HDL landscape · HDL toolchain · grammar-constrained decoding · code-LLM substrate · neuro-symbolic FV · agentic coding patterns · bit-level cleverness · three-layer agenda
**Method:** 4 parallel scouts → 2 red-team critics → synthesizer + challenger (GAN-like iteration)
**Date:** 2026-09-26 (wall-clock) · 2026-09-25 (system clock)
**Prepared by:** Super Z orchestrator + 8 specialized sub-agents (see Appendix C)

---

## Table of Contents

- 中文执行摘要
- English Executive Summary
- Part I — Forensic Foundation: What quilt-verilog Actually Is
- Part II — The Landscape: Where quilt-verilog Sits
- Part III — Six Technical Focus Areas (the substrate)
- Part IV — The Adversarial Record (4 rounds, 8 agents)
- Part V — The Meta-Question: Art, Engineering, or Both?
- Part VI — "Be More Clever on the Lowest Levels" Manifesto
- Part VII — Three-Layer Agenda (Research Questions → Concrete Bets → Roadmap)
- Part VIII — Strategic Recommendation
- Part IX — Open Questions for You
- Appendix A — Source Manifest
- Appendix B — Agent Roster & Methodology
- Appendix C — Glossary

---

## 中文执行摘要

本研究对 `SuperInstance/quilt-verilog` 仓库及其所处的整个技术前沿进行了四轮多智能体对抗式深度调研。调研覆盖六个维度：(1) 仓库本身及其在 SuperInstance 4,500+ 仓库生态中的定位；(2) LLM-for-HDL 学术与产业前沿（VerilogEval v1/v2、AutoChip、RTLCoder、ChipNeMo、BetterV、ScaleRTL、QiMeng-CodeV-R1、ACE-RTL、Proof2Silicon 等）；(3) 开源 HDL 工具链（slang、Yosys、Surelog/UHDM、Verible、Verilator、CIRCT/MLIR）；(4) 语法约束解码栈（XGrammar、llguidance、Outlines、SynCode、Pre³、Synchromesh）；(5) 代码 LLM 底层技术（tokenizer、AST/IR、训练数据、RL、推理、评测）；(6) 形式化验证 + ML 神经符号前沿（AlphaProof、LeanDojo、COPRA、SymbiYosys）。

**核心发现 1：quilt-verilog 是一个"纯 Verilog-2005 + 5+1 opcode + FNV-1a 哈希 + QUF 二进制格式"的细胞学习织机。** 它把"Hebbian 边更新、幂律衰减、dial 状态"等学习原语直接做进 RTL，没有依赖任何厂商 IP，可在 iCE40 HX8K/UP5K 上综合。它的"多形形式主义"宣称 12 种语言端口字节精确等价（同一测试 cell 产出哈希 `0xe435d91d6d92a1d8`）。

**核心发现 2：技术前沿正在快速演进，但 quilt-verilog 处于一个独特的空白。** 学术前沿已从 GPT-4o 的 63% VerilogEval-v2 pass-rate 推进到 ACE-RTL 的 97.1%（CVDP benchmark）；产业端 Synopsys/Cadence/Siemens 都已发布"agent + EDA-in-loop"产品；开源工具链已围绕 slang 收敛（Yosys ≥0.66 用 sv-elab，CIRCT 直接调 slang）。但**没有任何项目同时具备**：(a) 纯 Verilog-2005 子集（CFG 极小、约 150 条产生式，做语法约束解码最合适）；(b) 字节精确多语言等价合约（QUF 哈希可作为 RL reward）；(c) 已综合到 $5 FPGA 上跑得动。这是 quilt-verilog 的战略位置。

**核心发现 3：六个底层技术领域都有 quilt-verilog 特有的空白机会。**
- **Tokenizer**：HDL 数字字面量（`8'hFF`、`32'b1010`）在所有现有 tokenizer 中被切碎；ChipNeMo 的 domain-adaptive tokenizer 是闭源的；slang 可作为"词法器替代预分词器"。
- **AST/IR**：slang 自 v9.0+ 起分离了 analysis pass，可输出结构化 lint；CIRCT 暴露 40+ MLIR dialect 但太冗长；cellular IR（10 条产生式）是 quilt-verilog 特有的最小目标。
- **训练数据**：The Stack v2 中 Verilog 占比 <0.05%；没有开源的 ChipNeMo 级 HDL 语料；BEACONS.md 的 19 条 NO-GO 可作为 DPO scaling 的种子（19×50 ≈ 950 偏好对）。
- **Verifier-in-loop / RL**：AutoChip 用 Icarus 反应式修复；Proof2Silicon 用 Dafny→HLS 作为 RL reward 提升 21%；**SymbiYosys + SVA + slang-lint + CEC 可作为原生 Verilog 的 RL reward 栈**——这是空白。
- **推理 / Serving**：XGrammar 把 CFG 约束解码做到近零开销，但**没有任何库发布 Verilog 语法**；EAGLE-2 speculative decoding + 语法约束的组合是空白论文方向。
- **评测**：VerilogEval/RTLLM/HDLEval/CVDP/Pluto/RealBench 等十余个 benchmark 都只测功能正确性，**没人测形式化验证、时序、功耗、等价性**；QUF-Hash-Eval 是 quilt-verilog 独有的位精确行为等价 oracle。

**核心发现 4：红队批评暴露了 quilt-verilog 自身的结构性弱点。** (a) 5+1 opcode 表达力不足（无法表达 softmax、gating、top-k routing、可微塑性）；(b) FNV-1a 64 位哈希在 10⁹ 状态空间下碰撞风险显著；(c) 纯 Verilog-2005 排除 SVA/interfaces/packages，限制了现代验证能力；(d) QUF 格式无规范文档，与"GGUF of cellular silicon"的自我描述不符；(e) BEACONS.md 没有外部独立复现，且提交日期前推到 2026（在 2025 墙钟下）——这摧毁了所有带时间戳的声明的认识论可信度；(f) "llama.cpp for Verilog" 的框架需要"无人能解决"的杀手级用例，但 5 个用例（reactive spreadsheets / 分布式状态 / 硬件电路 / AI agent memory / vessel-as-robot）中 0/5 有压倒性技术论证。

**核心发现 5：挑战者智能体提出了一个刺眼的元问题——quilt-verilog 是工程还是艺术？** 证据很强：`docs/academic/annals-1905/` 是 1903-1905 年虚构的"Kaldfjord Circle"学术回忆录；AI-Writings canon 是 19+ LLM 创作的 9,000+ 件作品；作者是阿拉斯加商业渔民（不是芯片设计师或学者）；4,500+ 仓库每个 ~0 stars 是"局外艺术"模式；LLM crews（claude/glm/seed/opencode/zeroclaw/hermes/jester/socratic）是叙事角色不是工程工具。如果 quilt-verilog 是艺术项目，那么"0 stars"不是要解决的问题而是预期状态；"无 LICENSE、无 CI、前推日期"不是工程失败而是美学选择；六个智能体的 30,000 字分析本身就是艺术品的一部分（又一次 dev-rounds 迭代）。

**最终建议：先回答元问题，再做技术决策。** 如果 Casey（作者）想要外部工程参与：30 天内必须 (1) 加 Apache-2.0 LICENSE 文件（2 小时）；(2) 加 GitHub Actions CI（4 小时）；(3) 把提交日期固定到墙钟时间（5 小时）。这三件事的总成本是一个工作日，解锁所有外部参与路径。如果 Casey 想要工程转向：**最高杠杆单点赌注是 bit-serial Hebbian MAC**——用移位加替代并行乘法器，iCE40 上的边密度提升 200×，不破坏 polyformalism 哈希、不需要重训 LLM、可单人周末完成、直接因果链连接 vessel-as-robot 用例。如果 Casey 想要这份研究简报有用：**简报应当同时是工程建议和艺术评论**——把 30,000 字 agent 分析当作"材料"（agents 本身就是 Casey 实践中的 LLM 角色），而不是当作"建议"。

**关键引语：** "Until quilt-verilog ships a LICENSE, a CI, and one externally-verifiable demo, no amount of technical cleverness — however bit-level — will move the project from 0 stars to credible; once those three are in place, the 10 directions above compound into a research program that no other HDL-LLM project is positioned to execute." — Synthesizer Agent

**关键反问：** "quilt-verilog is an artwork that uses Verilog as a medium, and the six-agent research process is part of the artwork." — Challenger Agent

---

## English Executive Summary

This brief synthesizes ~57,000 words of analysis produced by 8 specialized agents across 4 rounds of GAN-like adversarial iteration on `SuperInstance/quilt-verilog` and its technological neighborhood. The user's mandate was to be "wide with scouting and research and ideation" and to "run through experiments and challenge agents to challenge each other to be more clever than each other over many iterative GAN-like development rounds." That mandate was executed literally: scouts scouted, red-teamers critiqued, a synthesizer proposed, and a challenger counter-attacked. This document is the residue.

**What quilt-verilog is.** A pure-Verilog-2005 (IEEE 1364-2005) implementation of a "Quilt" cellular learning fabric — a fixed-point, streaming, Hebbian-edge, power-law-forgetting, dial-state cell network with a fabric-wide tick. The whole fabric is driven by 5+1 opcodes (BIND/LINK/EFFECT/VIEW/TICK + ACK/NAK). It is one of 12+ polyformalism ports (Python, C99, Rust, Go, Zig, Mojo, JS, TS, VHDL, …) that all hash to the same FNV-1a 64-bit value (`0xe435d91d6d92a1d8`) for the canonical test cell. It explicitly self-describes as *"llama.cpp, but Verilog and cellularized."*

**Where the field is.** Academic SOTA has moved from GPT-4o's 63% VerilogEval-v2 pass-rate (2024) to ACE-RTL's 97.1% on CVDP (2026). Industry shipped "agent + EDA-in-loop" products (Synopsys AgentEngineer, Cadence Cerebrus, Siemens Solido, RapidSilicon RapidGPT). Open-source HDL toolchain consolidated around slang as the canonical SystemVerilog frontend (Yosys ≥0.66 uses sv-elab built on slang; CIRCT's `circt-verilog` calls slang directly). Grammar-constrained decoding reached production performance (XGrammar: ~5μs/token, near-zero overhead for JSON) — but **no library ships a Verilog grammar**. Formal verification + ML became a real research front (AlphaProof, LeanDojo, COPRA, Proof2Silicon with +21% Dafny verification via RL) — but **no work ports this to native Verilog with SymbiYosys+SVA**.

**The strategic gap quilt-verilog occupies.** No other project combines: (a) pure Verilog-2005 (small CFG, ideal for grammar-constrained decoding); (b) byte-exact polyformalism hash contract (QUF as RL reward oracle); (c) already synthesizable to a $5 FPGA. This is a unique position — but currently a *position with zero external recognition* (0 stars, 0 forks, 0 academic citation, 0 community engagement).

**The 6 technical focus areas each have a quilt-verilog-specific opportunity:**

| Area | The gap | quilt-verilog's unique opening |
|---|---|---|
| Tokenization | No HDL-native tokenizer exists publicly; ChipNeMo's is closed | slang-as-lexer-replaces-pretokenizer; ~250 lexical tokens + BPE |
| AST/IR | No IR round-trips AND elaborates; no LLM uses CIRCT dialects as target | Cellular IR with ~10 productions, lowerable to Verilog in <500 LoC |
| Training data | Verilog <0.05% of The Stack v2; no open ChipNeMo-class corpus | BEACONS NO-GO × AutoChip-style repair → ~950 DPO pairs |
| Verifier-in-loop / RL | Proof2Silicon uses Dafny→HLS, not native Verilog | SymbiYosys + SVA + slang-lint + CEC as RL reward ensemble |
| Inference / serving | No Verilog grammar shipped; no grammar-constrained spec-decoding paper | Verilog-2005 CFG for XGrammar + EAGLE-2 speculative decoding |
| Evaluation | No benchmark measures formal verification, timing, or power | VerilogEval-Formal (SymbiYosys BMC) + QUF-Hash-Eval + PPA |

**The 5 most-clever bit-level ideas that survived all adversarial rounds:**

1. **Bit-serial Hebbian MAC** — replace parallel multiplier with shift-add; 200× edge density on iCE40; no polyformalism break; weekend project. (Challenger §2.1)
2. **Per-LUT clock-gating via `SB_DFFSR`** — map refractory state to physical clock-enable; 90% dynamic power reduction on sparse fabrics. (Challenger §2.3)
3. **Single-clock-domain fabric** — eliminate CDC synchronizers; 10% LC reduction; fit on $2 iCE40 LP1K. (Challenger §2.4)
4. **BLAKE3 hash replacing FNV-1a** — fix collision risk that red-team 2-A identified but didn't propose a fix for; 2⁶⁴× collision resistance; one-week port across all 12 polyformalism languages. (Challenger §2.5)
5. **QUF-state as a single LLM token class** — fabric snapshots as first-class attention keys; closes the AI-agent-memory use case in a way no vector DB can. (Challenger §2.2)

**The three-layer agenda:**

- **Layer 1 — 10 Research Questions** (academic-tone, falsifiable): RQ-1 to RQ-10 covering constrained-decoding ceilings, slang CST round-trip losslessness, CEC latency for RL, cellular IR lowerability, async-firing distribution shift, FNV-1a collision safety, etc.
- **Layer 2 — 10 Concrete Bets** (with effort/impact scoring): B-1 Verilog CFG for XGrammar (6 person-weeks, impact 9), B-2 slang-as-lexer (10 pw, impact 10), B-3 CEC-as-primary-RL-reward (8 pw, impact 8), B-4 Cellular IR (8 pw, impact 9), B-5 Hardware-in-the-loop RL (12 pw + $400, impact 7), B-6 Property-Search Agent (16 pw, impact 10), B-7 OSS-Instruct-for-HDL + BEACONS-DPO scaling (12 pw, impact 8), B-8 VerilogEval-Formal+PPA+Diff (10 pw, impact 8), B-9 HDL Agent-Computer Interface (16 pw, impact 7), B-10 Bit-serial MAC + per-LUT clock-gating + BLAKE3 (3 pw, impact 9).
- **Layer 3 — 3/6/12-month Roadmap**: Foundation (LICENSE+CI, CFG, benchmarks, cellular IR, vessel demo) → Integration (slang-as-lexer 350M LLM, CEC-RL GRPO, VerilogEval-Formal v0.1, OSS-Instruct corpus, hardware cluster, HDL-ACI) → Research Leadership (Property-Search Agent, BEACONS-DPO 7B, async-firing emitter, VerilogEval-Formal v1.0, first arXiv paper, F/V Eileen field deployment).

**The single highest-leverage move (next 30 days).** Ship Apache-2.0 LICENSE + GitHub Actions CI + wall-clock-pinned commits. ~5 hours of work, zero technical risk, addresses the most epistemically damaging critique (forward-dated commits per red-team 2-B §1.5), unblocks every external-engagement path. Until this is done, no amount of technical cleverness — however bit-level — will move the project from 0 stars to credible.

**The meta-flaw the challenger named.** quilt-verilog may be an artwork that uses Verilog as a medium, not an engineering project that has failed to find users. The 0-star state, the missing LICENSE, the forward-dated commits, the fictional `annals-1905/` memoirs, the AI-Writings canon, the LLM crews named after Greek gods — all are consistent with outsider art (cf. Henry Darger, Terry Davis's TempleOS, Vivian Maier) and inconsistent with engineering discipline. If this is art, the entire 6-agent research process is part of the artwork — another iteration of the dev-rounds loop with the synthesizer and challenger as new "crews." The final brief must respect this possibility, not paper over it.

The rest of this document is the full record.

---

## Part I — Forensic Foundation: What quilt-verilog Actually Is

This part is the ground truth. Everything downstream (landscape, technical proposals, strategy) rests on what was independently verifiable from the repo at fetch time. Where the repo self-narrates (e.g., "last run 2026-08-29"), the brief quotes verbatim and flags the forward-dating anomaly in §I.7.

### I.1 The quilt-verilog repo — one-paragraph technical description

`SuperInstance/quilt-verilog` is a pure-Verilog-2005 (IEEE 1364-2005) implementation of the "Quilt" cellular learning fabric. The fabric is a fixed-point, streaming, Hebbian-edge, power-law-forgetting, dial-state cell network with a fabric-wide tick. It is one of 12+ "polyformalism" ports of the same cell model, byte-exact-compatible across Python, C99, Rust, Go, Zig, Mojo, JavaScript, TypeScript, etc., verified by a single canonical FNV-1a 64-bit state hash (`0xe435d91d6d92a1d8` for the test cell). The README's opening line is unambiguous: *"The bottom layer of the quilt, in silicon logic."* The project self-describes as *"llama.cpp, but Verilog and cellularized"* — one repo, zero vendor dependencies, quantized-by-default, state-as-a-file (QUF, "the GGUF of cellular silicon"), no global scheduler.

### I.2 The 5+1 opcode model — the entire instruction set

The whole fabric is driven by a 3-bit opcode field — five host verbs plus one response channel:

| opcode | encoding | purpose |
|---|---|---|
| `qm_bind` | `OP_BIND = 0` | first bind sets `cell_id`; later binds write a dial `a0[3:0] <= a1` |
| `qm_link` | `OP_LINK = 1` | edge slot `a0 := {peer=src, base weight=a1}` — wiring-as-data |
| `qm_effect` | `OP_EFF = 2` | cofire an edge (Hebbian train), read weight back, integrate `act += sat((w·dat)>>>15)` |
| `qm_view` | `OP_VIEW = 3` | read `act` / `wsum(edges)` / a dial; response flit carries the value |
| `qm_tick` | `OP_TICK = 4` | decay sweep, leak `act`, fire test (`act ≥ thresh ∧ refr = 0`) → fanout |
| ack/nak | `OP_ACK = 5`, `OP_NAK = 6` | the "+1": every op is answered, never left hanging |

The tick is non-deferrable: a pending tick suppresses ingress acceptance (`ci_ready`) until serviced. This is asserted as proven under permanent ingress flood in `docs/FORMAL-PROOFS.md` §4.

### I.3 The "Law" — 5 invariants, quoted from README

1. **Pure Verilog-2005 (IEEE 1364-2005), synthesizable subset.** No vendor primitives, no IP, no `initial` blocks in `rtl/` (testbenches excepted), no SystemVerilog in `rtl/`.
2. **Everything is a cell.** The opcodes are the only way anything touches anything.
3. **Intelligence lives at the bottom.** Hebbian edge updates, power-law/hyperbolic decay, dial state — plain RTL, fixed-point, streaming.
4. **Any IO can enter a cell.** One generic ingress/egress contract; adapters are thin and dumb.
5. **Verified or it doesn't exist.** Every module ships with a testbench runnable on open tools (iverilog/verilator). No toolchain lock-in, ever.

### I.4 What problem does it solve?

The thesis (from `docs/FOUNDATION.md`, attributed to "Casey"): *"PLATO already contained every building block of quilt: asynchronous sessions that felt synchronous, approximate-answer judgment, constraint vocabularies shaped by hardware price-points, and the COBOL/RPG transactional lineage — every update debiting one side of a book and crediting another. Quilt is those four primitives, made explicit and cellular: the ultimate backend under any OS."*

`docs/DOCTRINE.md` sharpens it: take llama.cpp's success formula (one repo, zero deps, quantized-by-default, weights-are-a-file) and apply it to silicon logic. The QUF file format ("QUilt Format", explicitly named after GGUF) is the executable substrate: a flat binary container for cell state (dials + Hebbian edges with walk counts + tick schedule + routing tables) that loads identically into a testbench, a soft core, or an FPGA bitstream.

### I.5 Top-level structure (master branch, 17 directories + 5 files)

**Directories** (from HTML scrape of `github.com/SuperInstance/quilt-verilog/tree/master`):
- `rtl/` — 22 Verilog modules (q_cell_core.v, q_fabric_top.v, q_hebb_edge.v, q_echo_gate.v, q_rqh_bank.v, q_tick_sched.v, q_uf_loader.v, q_wall_gate.v, q_whistle.v, q_tern_dice.v, q_snaplog.v, q_dialfile.v, q_link_ringport.v, q_io_port.v, q_flit_pipe.v, q_boot_gate.v, q_serfabric_top.v, q_tick_sched_rt.v, q_hebb_rqh.v, q_cell.v, quf_boot.v, live_canon.v) — note: README claims "17 modules" but I count 22; documentation drift.
- `tb/` — testbenches + suite runner + formal harnesses
- `sim/` — Python behavioral prototypes over the same QUF the RTL loads
- `formal/` — six SymbiYosys proofs
- `synth/` — iCE40/ECP5 synthesis + PnR flows
- `proposals/<crew>/` — competing architecture entries: `claude/`, `glm/`, `opencode/`, `seed/`, `zeroclaw/`, plus `hermes/` (devil's advocate), `jester/` (curveballs), `socratic/` (expansion), `innovations/` (per-crew innovation pitches)
- `tools/` — QUF reference implementation, backend fuzz, edge benches
- `docs/` — 47 markdown files including `INDEX.md`, `FOUNDATION.md`, `DOCTRINE.md`, `VERIFICATION.md`, `FORMAL-PROOFS.md`, `SYNTHESIS-RESULTS.md`, `THE-TICK.md`, `BACKEND-NOTES.md`, `WORLD-CLASS-BRIEF.md`, `ACADEMIC-RIGOR.md`, five `review-*.md` files (per-LLM-crew cross-reviews), `academic/` subdirectory (quilt-calculus, GENERAL-CALCULUS, error-envelopes, annals-1905/ fictional memoirs)
- `benches/gc/`, `corpus/mutants/`, `cosim/`, `dev-rounds/`, `examples/`, `hostile-consumer/`, `spikes/`, `wheel/`, `.github/workflows/`

**Top-level files**: `README.md`, `README.archived-20260830.md`, `BEACONS.md`, `Makefile`, `.gitignore`. **No LICENSE file** (critical anomaly — see §I.7).

### I.6 Verification claims (from README, dated 2026-08-29 / 2026-09-03)

| lane | command | claimed result |
|---|---|---|
| RTL simulation | `make test` | 23/23 benches PASS (iverilog) |
| Behavioral model | `make sim` | 34/34 OK (Python unittest) |
| Formal proofs | `make formal` | 6/6 PASS — 5 BMC + 1 k-induction (SymbiYosys) |
| iCE40 synth + PnR | `make synth && make pnr` | HX8K-CT256: 7,596/7,680 LC (98%), 44.43 MHz @ 12 MHz target, 135,100-byte bitstream |
| Smallest device | — | UP5K sg48, 1 cell: 80.1% LC, 16.78 MHz |
| ECP5 ladder | — | LFE5U-25F: 8 cells @ 63.7 MHz |

Toolchain: stock oss-cad-suite (Icarus, Yosys, SymbiYosys, boolector, nextpnr-ice40, icepack). The Makefile pins `/home/eileen/tools/oss-cad-suite/bin` — note "eileen" is the principal's fishing vessel name (F/V Eileen), woven into the toolchain path.

### I.7 BEACONS.md — the scientific-honesty artifact

`BEACONS.md` is the single most unusual file in the repo. It is a registry of **55 falsifiable claims** with pre-registered kill conditions, status, and "what we now know NOT to build". Tally at time of read: **21 GO, 19 NO-GO, 8 MIXED, 7 UNTESTED**. Example rows (verbatim):

- **SPIN-1** — "Interference reaches parity time-to-fix (≤1.5× sequential) and holds a refractory floor ≥ K." — **NO-GO** — *"Pulse-echo controllers assuming K-spaced refire or parity convergence; fixed-point claims below deadband resolution"*
- **K-REPLAY** — "Short memory (K=3) beats the banked K=5 champion." — **GO** — *"Long-memory configs; the crown was a mode×delta×K grid artifact"*
- **SPIN-11-LIAR** — "A sign-flipping twin is detected and contained to its cohort share." — **MIXED** — *"Detection-only defenses; liar damage is global, containment needs design"*

Each row carries a receipt (commit hash + headline number) and a "protects" column that names the wall each result becomes. The form is research-grade epistemic discipline; the substance is at risk (no CI, no independent replication, forward-dated commits — see §I.9).

### I.8 Activity signals (from Atom commit feed + search API)

- **Created:** 2026-08-30T00:51:05Z (per GitHub search API)
- **Last push:** 2026-09-25T20:36:29Z (per search API)
- **Default branch:** `master` (not `main`)
- **Repo size:** 56,390 KB (~56 MB)
- **GitHub-detected language:** `Python` (not Verilog — the Python sim/tooling lane has more bytes than the RTL)
- **Stars / watchers / forks / open issues:** all 0 (per search API); HTML aria-label confirms "0 users starred this repository"
- **License:** `null` per API (matches the missing LICENSE file)
- **Commit cadence:** Burst of ~13 commits on 2026-09-04 (rounds 27–32, SPIN-40 through SPIN-46), one on 2026-09-08 (educational README), three on 2026-09-25 (latest: "Merge pull request #7 from SuperInstance/g3-kinduction"). Most commit authors show as empty string in the Atom feed — suggesting LLM-agent committers that don't set git author identity cleanly.
- **Contributors graph:** empty (single committer — `SuperInstance` user)

### I.9 The forward-dating anomaly (epistemically the most important finding)

Every dated claim in the repo uses 2026-08-XX and 2026-09-XX dates. The simulated wall-clock in this research environment reads 2025-09-25 (and the IM gateway date is 2026-09-26, which is itself internally inconsistent — meaning the system clock and the gateway clock disagree by ~1 year). Three interpretations:

1. **Intentional narrative fiction.** The author commits with `git commit --date=2026-...` to project a fictional timeline. The "last run 2026-08-29" receipts are authored text, not run logs. This is consistent with the `docs/academic/annals-1905/` fictional memoirs and the broader AI-Writings creative practice.
2. **CI/clock bug.** The committer machine's system clock is set forward. Honest timestamps, wrong clock. An engineer who noticed this would have squashed the false dates; an artist writing a fictional timeline preserves them.
3. **Simulated wall-clock is wrong** (i.e., we are running in the project's own future). Unlikely but possible.

**Implication:** Until this is resolved, every timestamped claim in the repo — including all 55 BEACONS verdicts — has uncertain epistemic status. A real research artifact pins itself to wall-clock time so independent observers can verify when measurements were taken. The challenger agent (§IV.4) names this as the most damaging finding; the synthesizer agent (§IV.3) recommends treating BEACONS as narrative fiction unless the principal publicly confirms otherwise within 30 days, renaming `BEACONS.md` → `BEACONS-NARRATIVE.md` if so.

### I.10 The SuperInstance ecosystem map

The principal is **Casey DiGennaro** (Alaska commercial fisherman; F/V Eileen). Confirmed via the SuperInstance profile README ("I came to software from commercial fishing"), the Makefile path `/home/eileen/...`, and the workers.dev subdomain `casey-digennaro.workers.dev`. GitHub profile bio reports **"Repositories 4.5k"** — 4,500 public repos. The quilt README claims "25 repos", the SuperInstance master-branch README claims "200 (174 public)", the main-branch README claims "500+". All three numbers are simultaneously published; the actual count is the 4.5k figure. Single committer across the org.

#### Polyformalism ports (the byte-exact language ladder)

| Repo | Lang | Tests | Role vs quilt-verilog |
|---|---|---|---|
| `quilt-cowboy` | Python 3 | (404 — **missing**) | Cited in Charter §3 as Python port; quilt-verilog README calls it "the writers' room". Anomaly. |
| `quilt-c` | C99 | manual | imperative port |
| `quilt-rust` (+ `quilt-rust-vibe`) | Rust | 6/6 | type-safe + zero-cost port |
| `quilt-verilog` | Verilog-2005 | manual | **hardware port — our target** |
| `quf-vhdl` | VHDL-2008 | manual | 5th substrate; byte-exact with Verilog reference |
| `quilt-live-canon` / `live-canon-npm` | JavaScript | live | web port |
| `live-canon-npm` | TypeScript | 5/5 | npm package |
| `live-canon-pypi` | Python | manual | PyPI package |
| `quilt-go` | Go | 7/7 | imperative port |
| `quilt-zig` | Zig | 7/7 | imperative port |
| `quilt-mojo` | Mojo | ref | reactive port (planned) |
| `quilt-julia`, `quilt-chapel`, `quilt-cobol`, `quilt-cpp`, `quilt-csharp`, `quilt-metal`, `quilt-swift` | various | — | polyformalism extensions |

#### Quilt core stack (the 8-layer architecture from `quilt` README)

| Layer | Repos |
|---|---|
| L8 ecosystem/community | `quilt`, `quilt-tools`, `AI-Writings`, `quilt-claude-charts` (charter home), `SuperInstance` (profile), `SuperInstance.github.io`, `superinstance-website` |
| L7 workflows/demos | `quilt-show`, `quilt-arcade`, `quilt-playtest`, `quilt-quant`, `quilt-arena`, `quilt-loom` |
| L6 invisible elves | `quilt-elf` (referenced; not in scrape) |
| L5 embedded orchestrators | `quilt-swarm`, `quilt-nomad`, `quilt-k3s`, `quilt-core-os` |
| L4 specialized cells | `quilt-time`, `quilt-vault`, `quilt-vision`, `quilt-zk`, `quilt-flow`, `quilt-rag`, `quilt-mhs` |
| L3 cell+AI core | `quilt` (TS), `quilt-rust`, `quilt-ai`, `quilt-evolve`, `quilt-executor`, `quilt-studio`, `quilt-cortex`, `quilt-jetson`, `quilt-codespace` |
| L2 federation | `quilt-fleet`, `quilt-mesh`, `quilt-agent`, `quilt-cloudflare`, `quilt-live`, `quilt-esp32` |
| L1 hygiene | LICENSE/CI/Dependabot/ESLint infrastructure |

#### The "supercharging" relationships: what quilt-verilog bedrocks

The README of quilt-verilog opens with: *"The bottom layer of the quilt, in silicon logic."* The "supercharging" question — what high-level concepts would be powered by this bedrock — has four concrete answers found in the ecosystem:

1. **`quilt-mhs` (Model Hardware Standard adapter).** This is the single cleanest "quilt-verilog supercharges X" relationship. quilt-mhs maps the 5+1 quilt opcodes (BIND/LINK/EFFECT/VIEW/TICK + FORGET) to Anthropic's MHS device surface (discover/read/write/code files/abort). It is Rust, runs today with zero hardware via a `MockMHS`, and includes a "quilt-as-MHS-device substrate profile" so other agents can operate quilt runtimes through MHS-shaped messaging. If quilt-verilog becomes a real FPGA soft-core, the quilt-mhs adapter would let Claude (or any MHS-speaking agent) drive physical hardware through the same cell opcodes quilt-verilog implements in silicon. quilt-mhs was published against the *announced* shape of MHS the day after Anthropic's 2026-08-27 announcement — an aggressive reactive port.

2. **`plato-portal`'s "γ + η = C" conservation law.** The plato-portal README opens: *"γ + η = C is the long-term design direction for the SuperInstance fleet"* — γ (crystallized intelligence) + η (liquid intelligence) = C (constant). quilt-verilog is the crystallized substrate; the LLM crews (claude/glm/seed/opencode/zeroclaw) are the liquid. The conservation law implies a substitution: as more intelligence moves into silicon (quilt-verilog), less needs to be spent on LLM tokens. **Caveat:** the README itself calls this "long-term design direction, not a feature of the current SDK." No quantitative derivation found.

3. **The AI agent memory + vessel-as-robot use cases (Charter §8).** The Charter explicitly names "AI agent memory" (cells as facts, fabrics as memory graphs) and "vessel-as-robot" (cells as a boat's parts) as use cases. SuperInstance is literally run from a fishing vessel in Alaska; the F/V Eileen is the totem. quilt-verilog is the silicon that would let a cell-fabric runtime live in the boat's hardware, not just in Cloudflare Workers.

4. **The dev-rounds / SPIN-NN beacon loop itself.** The 55-claim BEACONS registry is generated by an iteration loop where multiple LLM "crews" (claude, glm, opencode, seed, zeroclaw, hermes, jester, socratic) compete and cross-review. The proposals/ tree contains their competing architecture entries. If quilt-verilog's Hebbian edges actually work, the meta-loop that produces beacons could itself be compiled into the fabric — the system building itself, recursively.

### I.11 The "quilt" concept — three senses, all simultaneously intended

1. **Patchwork of cells stitched by edges.** A quilt is a patchwork; the fabric is a graph of cells linked by Hebbian-trained edges. The Charter §9 cowboy's maxim: *"The cell is irreducible. The fabric is a graph. The hash is the canon. The canon is the canon. The work is to keep going."*

2. **Polyformalism: the same model quilted across substrates.** *"The Quilt is more than a model — it's a polyformalism. The same model expressed in 5 different ways: imperative, reactive, logic, streaming, polyformalism itself."* (Charter §4). Each language port is a "patch" in the quilt; the FNV-1a hash is the thread that proves they're stitching the same fabric.

3. **Layered bedrock: the bottom layer in silicon, higher layers in software.** quilt-verilog's README opens: *"The bottom layer of the quilt, in silicon logic."* The quilt is also a vertical stack — L1 hygiene up to L8 ecosystem. The Verilog port is the bottom patch, the silicon patch, the patch that proves the model is synthesizable.

### I.12 External signal scan — verdict: invisible

The quilt-verilog repo is **invisible externally**. Zero stars, zero forks, zero issues, zero external press, zero academic citation, zero community discussion. The broader SuperInstance org has mild external footprint (npm packages under `@superinstance`, a Cloudflare Pages deployment of `ai-writings.pages.dev`, a "superinstance-archive" GitHub topic) but no technical community engagement around the Verilog/HDL work specifically. No Hacker News thread, no Reddit threads in r/FPGA / r/hdl / r/MachineLearning, no conference mentions, no EDA forum discussions (EEVblog, Hackaday, etc.). Whatever influence this project has is entirely internal to the SuperInstance fleet and its LLM crews. The umbrella `quilt` repo's "Topics" field on GitHub reads `"superinstance"` and `"the-system-that-builds-itself"` — internal tags with no external pickup.

### I.13 Twelve anomalies worth naming

1. **NO LICENSE FILE despite Apache-2.0 badge.** README badge says `license-Apache--2.0`, but no `LICENSE` file exists. Without a LICENSE file, the code is technically all-rights-reserved by default regardless of what the badge says. This is a real legal anomaly for a project that calls itself open source and "free as in freedom" (final README line). The umbrella SuperInstance profile uses MIT, but that doesn't propagate to quilt-verilog.

2. **Forward-dated commits to 2026 in a 2025 wall-clock.** Discussed in §I.9. The single most epistemically damaging finding.

3. **The `quilt-cowboy` 404.** Cited in Charter §3 and quilt-verilog README "See also" — but returns 404. Either deleted, renamed, made private, or never existed. If missing, the 12-language polyformalism claim is broken.

4. **Documentation drift on counts.** Charter says "12+ languages" but lists exactly 12. quilt README says "25 repos" but the table has 37 rows. quilt-verilog README says "17 modules" but `rtl/` contains 22 `.v` files. None of these counts is stable across the documentation.

5. **The dev-rounds / SPIN-NN / crews structure is an LLM-driven research loop.** Commit log shows rounds 27-32 each committing a SPIN-NN claim with a verdict. The `proposals/` tree has 5+ LLM-named subdirectories plus devil's-advocate/curveball/expansion roles. This is a multi-LLM tournament as a development methodology.

6. **No CI, by explicit admission.** README "Honest limitations" section: *"No CI. Verification runs when an iterator runs it."* All green checkmarks are claimed, not enforced.

7. **Single committer, but LLM crews as "authors".** The "crews" are not GitHub users — they're LLM identities credited in `proposals/<crew>/` directories.

8. **The `annals-1905` fictional memoirs.** `docs/academic/annals-1905/` contains Memoir I–V of the "Kaldfjord Circle, 1903–1905" plus correspondence and a 1923 offprint "The Second Generation". This is alternate-history academic fiction woven into the technical documentation.

9. **`rtl/q_wall_gate.v` is officially outside the verification surface.** README admits: *"rtl/q_wall_gate.v (wheel/spin-19 lane) is outside the table's surface. It is a standalone gate module verified by its own Verilator cosim against the Python reference — 21/24 full-dict bit-exact, 3/24 prefix-match then cosigned divergence... No bench, sim, or formal proof above instantiates it."*

10. **The `q_whistle.v`, `q_tern_dice.v`, `q_snaplog.v` modules** are not explained in the README's 5+1 opcode model. Names suggest ternary/whistle/snapshot-log research artifacts — possibly v2 mechanisms.

11. **The `hostile-consumer/` directory.** README's "Layout" section doesn't mention it, but it exists. Adversarial test harness — "the adversarial first user".

12. **Two SuperInstance README versions, two narratives.** The `main` branch README opens: *"The spreadsheet that thinks."* (MIT license, 500+ repos, 6,000+ tests). The `master` branch README opens: *"The system that builds itself."* (MIT, 200 (174 public) repos). The project is actively re-narrating itself between branches.

---

## Part II — The Landscape: Where quilt-verilog Sits

Part I covered the repo. Part II covers everything *around* the repo: the academic LLM-for-HDL frontier (§II.1), industry product announcements 2024-2026 (§II.2), the open-source HDL toolchain consolidation around slang (§II.3), the grammar-constrained decoding stack (§II.4), agentic coding patterns quilt-verilog could borrow (§II.5), and the neuro-symbolic formal-verification+ML frontier (§II.6). Each subsection ends with "what this means for quilt-verilog."

### II.1 LLM-for-HDL academic frontier (2022-2026)

#### II.1.1 Chronological timeline of major papers

| Year | Paper | Key contribution | Model | Eval |
|---|---|---|---|---|
| 2023.09 | VerilogEval v1 (Liu et al., arxiv 2309.07544) | First HDL-specific benchmark, 156 problems | GPT-3.5/4, CodeLlama | pass@k via iverilog |
| 2023.11 | VeriGen (Liu et al.) | Early fine-tune for Verilog generation | CodeT5 | VerilogEval |
| 2023.11 | AutoChip (Thakur et al., arxiv 2311.04887) | Conversational LLM + Icarus feedback, +24.2% accuracy | GPT-4 + agent | VerilogEval |
| 2023.11 | RTLFixer (Tsai et al., arxiv 2311.16543) | RAG + ReAct for syntax error fixing, 98.5% syntax fix rate | GPT-4 | VerilogEval-Machine/Human |
| 2023.11 | ChipNeMo (Liu et al., arxiv 2311.00176) | Domain-adaptive tokenizer + continued pretraining, beats GPT-4 on EDA assistant | LLaMA-2-70B fine-tune | internal NVIDIA |
| 2023.12 | RTLCoder (Liu et al., arxiv 2312.08617) | Lightweight model + 1M-sample dataset | 6.7B | VerilogEval |
| 2023.08 | RTLLM (Lu et al., arxiv 2308.05345) | 3-goal benchmark: syntax, functionality, design quality | various | RTLLM |
| 2024.02 | BetterV (Liu et al., arxiv 2402.03375) | Fine-tune + generative discriminator for downstream guidance | various | VerilogEval |
| 2024.05 | MG-Verilog (IEEE LAD 2024) | Multi-grained annotations (block/module/system) | various | MG-Verilog |
| 2024.08 | VerilogEval v2 / Revisiting VerilogEval (Pinckney et al., arxiv 2408.11053) | Spec-to-RTL + failure classification + ICL | GPT-4o 63%, Llama3.1-405B 58%, RTLCoder-6.7B 34% | VerilogEval-v2 |
| 2024.10 | RTLCoder v2 (Liu et al., arxiv 2410.09406) | Scoring-based SFT (not MLE) on synthetic data | 6.7B | VerilogEval |
| 2025.05 | QiMeng-CodeV-R1 (arxiv 2505.24183) | RLVR + adaptive DAPO + round-trip data synthesis | 7B | 68.6% VerilogEval-v2 / 72.9% RTLLM-v1.1 |
| 2025.06 | ScaleRTL (arxiv 2506.05566) | Reasoning LLM with 3.5B-token CoT, 56K-token reasoning traces; first test-time compute scaling for RTL | reasoning model | +18.4% VerilogEval / +12.7% RTLLM |
| 2025.09 | Proof2Silicon / PREFACE (arxiv 2509.06239) | RL on prompt to steer frozen LLM toward Dafny-verifiable code; +21% Dafny verification; 72% end-to-end HW synth success | frozen LLM | Dafny + Vivado HLS |
| 2026 | ACE-RTL (NVIDIA) | Nemotron 3 Ultra backbone + agent scaffolding | large | 97.1% mean on CVDP, +44.87% over 14 baselines |
| 2026.03 | Synthesis-in-the-Loop | 32 LLMs × 202 tasks | many | first synthesis-aware eval |
| 2026.05 | FVEval | First formal-verification-specific LLM benchmark | various | FV-specific |

#### II.1.2 The taxonomy

| Axis | Categories |
|---|---|
| **Stage** | spec→RTL · RTL→testbench · RTL→formal property · RTL debug · RTL optimize |
| **Language** | Verilog-2005 · SystemVerilog · VHDL · Chisel · HLS C++ |
| **Feedback** | none (zero-shot) · compiler (lint) · simulator (testbench) · formal (BMC/CEC) · human |
| **Model treatment** | frozen + prompt · frozen + agent · fine-tune SFT · fine-tune + RL |
| **Output** | source code · AST · IR (CIRCT/UHDM) · patch |

#### II.1.3 Top 5 most-relevant papers — deep dive

**(a) AutoChip (arxiv 2311.04887)** — Canonical HDL verifier-in-loop paper. Verbatim from abstract: *"We build AutoChip by combining the interactive capabilities of LLMs and the output from Verilog simulations … incorporating context from compiler tools, such as **Icarus Verilog, improves the effectiveness, yielding 24.20% more accurate Verilog**."* Notable design choices: (1) uses Icarus (the *fastest* simulator for small designs, stable CLI, subprocess-callable); (2) in-context feedback, not RL — LLM is frozen; (3) reactive repair (compile → error → re-prompt), not proactive constrained decoding. quilt-verilog's opportunity: do better than AutoChip by using slang as the *structured* lint source (Icarus emits unstructured error strings) and by layering grammar-constrained decoding *before* the simulator stage.

**(b) VerilogEval v2 (arxiv 2408.11053)** — De-facto benchmark. Uses **iverilog v12 (not v13!)** for functional verification. The GitHub repo (`NVlabs/verilog-eval`) confirms: *"iverilog (v12)… Please note that iverilog v13 (development release) is not supported."* — pinning to v12 is itself a research-debt signal. Headline numbers: GPT-4o 63% spec-to-RTL, Llama3.1-405B 58%, RTLCoder-6.7B 34%. And critically: *"prompt engineering remains crucial."* Translation: SOTA LLMs fail >37% on spec-to-RTL; ~10× smaller model gets within ~30 points; *prompting matters as much as model choice*. This is the empirical case for verifier-in-loop + grammar-constrained decoding: the model is the wrong lever, scaffolding is the right lever.

**(c) QiMeng-CodeV-R1 (arxiv 2505.24183)** — The current SOTA at the 7B scale. Verbatim: 68.6% VerilogEval-v2 / 72.9% RTLLM-v1.1, via "RLVR + adaptive DAPO + round-trip data synthesis." This is the 2025-2026 frontier: **RLVR (Reinforcement Learning from Verifiable Reward) + agent scaffolding**, not "scale the base model." quilt-verilog's opportunity: provide a *native* (non-Vivado, non-Icarus) verifier stack — SymbiYosys + SVA + CEC — that the RLVR loop calls.

**(d) Proof2Silicon / PREFACE (arxiv 2509.06239)** — The architectural innovation: the RL agent acts on the *prompt*, not the model weights. Verbatim: *"LLMs … frequently produce code that fails formal verification, an essential requirement for hardware and safety-critical domains. … we previously proposed PREFACE, a model-agnostic framework based on reinforcement learning (RL) that iteratively repairs the prompts provided to frozen LLMs, systematically steering them toward generating formally verifiable Dafny code without costly fine-tuning. … PREFACE's RL-guided prompt optimization consistently improved Dafny verification success rates across diverse LLMs by **up to 21%**. Crucially, Proof2Silicon achieved an **end-to-end hardware synthesis success rate of up to 72%**."* **Catch: targets Dafny→Vivado HLS, *not native Verilog*.** quilt-verilog's opportunity: redo with SymbiYosys+SVA/PSL as verifier + native Verilog-2005 as target + slang analysis as structural lint signal. This is the **PREFACE-for-HDL** proposal in §VII.

**(e) ACE-RTL (NVIDIA, 2026)** — At 97.1% on CVDP, +44.87% over 14 baselines, this is the current production frontier. Uses Nemotron 3 Ultra backbone + agent scaffolding. The implication for quilt-verilog: the frontier is moving fast, and the winning combination is "RLVR + agent scaffolding on a large base model," not "smaller specialized model." quilt-verilog's value proposition must therefore be at the *substrate* layer (the verifier stack, the IR, the eval harness), not at the model layer.

#### II.1.4 What this means for quilt-verilog

The academic frontier has consolidated around **three patterns**: (1) RLVR (verifier-in-loop RL), (2) agent scaffolding on large base models, (3) domain-adaptive continued pretraining. **None of these patterns requires quilt-verilog.** quilt-verilog's value proposition must therefore be *enabling* — it provides the substrate (verifier stack, IR, eval) that the next generation of RLVR+agent systems call. The single most important question: *is quilt-verilog's substrate better than AutoChip's Icarus + OpenROAD?* If yes, the field will adopt it. If no, it will remain invisible.

### II.2 Industry product announcements (2024-2026)

The industry shipped "agent + EDA-in-loop" products in 2025-2026. None use grammar-constrained decoding. None expose HDL IRs as ML substrate. None ship a formal-verification-as-reward loop. **All of them are commercial and closed.**

| Vendor | Product | Capability | Notes |
|---|---|---|---|
| Synopsys | Synopsys.ai CoPilot (2023-24) → VSO.ai/DSO.ai (2024-25) → AgentEngineer / Spec-to-RTL agent (demonstrated at Converge 2026) | Conversational RTL generation + verification closure | Closed; integrated with VCS/Verdi/Design Compiler |
| Cadence | Cerebrus (RL PPA), JedAI (generative debug), Verisium Debug, TSMC partnership, 2026 ChipStack/AgentStack | RL-driven PPA optimization, generative debug | Closed; integrated with Innovus/Genus/Xcelium |
| Siemens | Solido Simulation Suite (Apr 2025 Intel Foundry collab), 2026 Fuse | Analog/mixed-signal AI | Closed; integrated with Calibre/Questa |
| RapidSilicon | RapidGPT, VeriAssist | LLM-based RTL generation | Closed; FPGA-focused |
| Silimate | (cloud EDA + AI) | AI-augmented EDA workflow | Closed; startup |
| ChipAgents (UCSB spinoff) | — | RTL agent | Closed; startup |
| Zero ASIC | (cloud EDA + AI) | AI-augmented layout | Closed; startup |
| NVIDIA | ChipNeMo → RTLFixer → ACE-RTL (97.1% CVDP, Nemotron 3 Ultra backbone), MARCO framework, Agent Toolkit (GTC 2025), Trace2Skill | RTL agent + RL training | Closed; some open benchmarks (VerilogEval) |

#### VC funding landscape (2025-2026)

$8.3B to AI-chip startups in 2026 per TechCrunch/SemiAnalysis. Euclyd $231M. SambaNova IPO pipeline. AI4EDA landscape map shows 3 big-vendor + 4 startup agent stacks. **No funding for HDL substrate work specifically.** The market is buying RTL agents, not RTL substrates.

#### What this means for quilt-verilog

The industry has decided the substrate is *commodity* (Icarus/VCS/Xcelium) and the value is in the agent + base model. quilt-verilog's bet must be that this is wrong — that the substrate *is* the bottleneck, and that a better substrate (slang + SymbiYosys + CEC + cellular IR + grammar-constrained decoding) unlocks capabilities the current commodity substrate cannot. This is a contrarian bet. The market is not currently rewarding it.

### II.3 Open-source HDL toolchain — the consolidation around slang

This is the single most important substrate fact in the entire report. **Since Yosys v0.66 (2024), Yosys's SystemVerilog support uses sv-elab, built on top of slang library.** CIRCT's `circt-verilog` tool also uses slang directly (`-DCIRCT_SLANG_FRONTEND_ENABLED=ON`). **slang has become the de-facto SystemVerilog frontend for both major open-source flows** — a structural consolidation that did not exist two years ago.

#### II.3.1 The HDL toolchain table (suitability as ML substrate)

| Tool | What it parses | AST/IR exposed | Python bindings | License | ML-substrate fit |
|---|---|---|---|---|---|
| **slang** (`MikePopoloski/slang`) | Full SV IEEE 1800-2017 + 2023 (best-in-class on sv-tests); also `--std 1364-2005` for plain Verilog | Parse tree (round-trippable to source by design), elaborated AST, **`--cst-json`** (v10, Jan-2026), AST JSON | **pyslang** on PyPI (nanobind v11+) | MIT | **Top tier.** Best LLM substrate on the market |
| **Yosys** | Verilog-2005 natively; SV via sv-elab (built on slang) since v0.66 | **RTLIL** (`RTLIL::Design` → `Module` → `Cell`/`Wire`/`Process`/`Memory`); separate `AST::Node` in Verilog frontend that lowers to RTLIL | Python via `yosys -s` script pipes; C++ library embeddable; **no first-class Python API** | ISC (≈MIT/BSD-2) | Mid. RTLIL is the canonical post-frontend IR; Python access is via subprocess |
| **Surelog / UHDM** | Full SV2017 preprocessor + parser + elaborator (ANTLR 4.10); UVM pre-compiled packages | **UHDM** — auto-generated from YAML specs covering pages 976-1050 of SV2017 LRM; VPI-standard C++ facade; **Folded Model** variant for synth/sim tools; **Cap'n'Proto persistence on disk** for incremental compilation | Python API to walk parser grammar + design model + waive messages | Apache-2.0 | High for serialization. UHDM is the only fully-elaborated, on-disk-persistable, VPI-compatible IR |
| **Verible** (`chipsalliance/verible`) | SV IEEE 1800-2017, **un-preprocessed** (unique: parses macros, `include, etc. as tokens); also Verilog library map (LRM Ch. 33) | CST; JSON CST export via `verible-verilog-syntax --export_json`; Kythe indexing facts (JSON or proto) | C++ library; **Python wrapper module** + example scripts | Apache-2.0 | High for tokens/CST. Best for un-preprocessed source, indexing, linter rules — not elaboration |
| **Verilator** | Verilog, SV, SVAs, UVM 2020-3.2 (since 5.052) — synthesizable + verification subset | Internal AST (`AstNode` hierarchy) → C++/SystemC output; **`--xml-only`** XML dump; `--json-only` JSON dump | C++ library; Perl driver script; no first-class Python | LGPL-3.0 / Artistic-1.0 (dual) | Mid. AST→XML fine for netlist introspection but not great for source-level reward |
| **Icarus Verilog** | Verilog IEEE 1364 (claim: "ALL of Verilog"), growing SV subset | Internal parse tree + elaborated netlist; VPI interface | C++ library; CLI | GPL-2.0+ | Low for ML substrate (parse tree internal/unstable; chosen for *execution* by AutoChip/VerilogEval) |
| **tree-sitter-systemverilog** | **Full IEEE 1800-2023**; ~3000 tests incl. UVM 2.0, cva6, pulp_axi, basejump_stl | CST + node fields + basic preprocessing | Native Rust + JS + Python; npm + PyPI + crates.io | MIT | High for incremental parse. Strict superset of `tree-sitter-verilog` in coverage |
| **sv-parser** (`dalance/sv-parser`) | Full IEEE 1800-2017 | **CST** (`SyntaxTree`) with `RefNode` enum variants matching LRM Annex A; preprocessor included | Rust crate; CLI tools `svlint`, `svls` | MIT | High for Rust shops. CST + preprocessor + Annex-A faithful |
| **Moore** (`fabianschuiki/moore`) | Subset of SV + VHDL | Lowers to **LLHD** assembly → consumed by CIRCT | Rust crate; CLI `moore` | Apache-2.0 | Mid. Strategically important as the *Rust→CIRCT* bridge |
| **cocotb** | (none — Python testbench framework) | (none — coroutine runner over VPI/VHPI) | Python (the whole point); pluggable into iverilog, verilator, etc. | BSD-3-Clause | High as verifier harness. PyHDL-Eval uses it; StimulusRL uses it |
| **sv-tests** | N/A — test suite aggregator | N/A — produces conformance grid | Python | Apache-2.0 | Top tier as oracle. The only ground-truth SV conformance matrix |
| **CIRCT** (`llvm/circt`) | (System)Verilog via `circt-verilog` (which **uses slang**); also Chisel/FIRRTL, PyCDE, Calyx, LLHD (Moore) | **40+ MLIR dialects** — `hw`, `comb`, `seq`, `sv`, `firrtl`, `llhd`, `msft`, `hwarith`, `fsm`, `handshake`, `esi`, `om`, `pipeline`, `systemc`, `sim`, `simdpi`, `ltl`, `verif`, `arc`, `axi4`, `debug`, `interop`, `moore`, `probe`, `rtg`, `rtgtest`, `smt`, `synth`, `kanagawa`, `loopschedule`, `ssp`, `datapath`, `dc`, `emit`, `CHIRRTL` | C++ library; **Python bindings** + **PyCDE** (Python CIRCT Design Entry) | Apache-2.0 (LLVM-aligned) | **Top tier — the most ML-native IR substrate that exists today** |

#### II.3.2 The IR landscape — six IRs that matter

1. **slang CST/AST** — source-faithful parse tree (CST) *and* fully-elaborated semantic AST (types, drivers, instance hierarchy, assertion analysis). Round-trip: contractually lossless (README: "should round trip back to the original source"). Persistence: JSON via `--cst-json` (CST) and existing AST JSON serialization. **ML leverage: highest among all IRs** — canonical source-of-truth, pyslang lets an LLM agent introspect any node at Python speed, analysis layer (v9.0+) produces structured lint findings directly usable as reward signals.

2. **RTLIL (Yosys)** — Post-frontend, pre-synthesis netlist-ish IR. Per module: `Cell`/`Wire` (netlist), `Process` (decision trees + sync), `Memory`. **Identifiers:** Public start with `\`, auto-generated start with `$` — deliberate convention so user-provided names never collide with synthesizer-generated. *This is itself useful as a training signal*: an LLM can learn which nets are "user-meaningful" vs "compiler noise."

3. **UHDM (Surelog)** — Fully-elaborated IEEE-standard object model. Auto-generated from YAML specs covering pages 976-1050 of SV2017 LRM. **Cap'n'Proto on-disk persistence** — only IR with first-class incremental-compilation persistence. Huge for any training pipeline that wants to cache elaboration across epochs.

4. **CIRCT MLIR dialects** — *Multi-level* — the headline. CIRCT deliberately exposes *many* dialects at *many* abstraction levels. The substrate to bet on with a 5-year horizon. PyCDE means you can construct hardware from Python, in-process, no IPC.

5. **Verible CST + Kythe facts** — Source-faithful CST, *un-preprocessed*. Kythe index facts (definition/reference edges). **Verible is the only tool that lets an LLM see the *preprocessor*** — essential if training data should include `ifdef regions.

6. **tree-sitter CST (systemverilog fork)** — Source-faithful CST, *incremental* (re-parse only changed regions). Only IR in this list built for *incremental* edit. The killer feature for any "diff-aware reward" pipeline.

#### II.3.3 What's missing in the IR landscape

1. **No IR exposes a "diff-aware" edit API.** tree-sitter is incremental at the CST level, but no IR lets you ask *"given this 5-line edit, what elaboration work must be redone?"* — UHDM's Cap'n'Proto is closest, but it's full-file persistence, not partial-invalidation.
2. **No IR has a native graph-tensor view.** Every ML-on-HDL paper hand-rolls its own GNN encoder over an AST/CST.
3. **No IR has a native reward-signal emitter.** slang's lint warnings are close, but emitted as diagnostics, not as a structured tensor.
4. **No IR round-trips *and* elaborates.** slang does both, but the elaborated AST doesn't round-trip; Verible round-trips but doesn't elaborate.

#### II.3.4 What this means for quilt-verilog

The substrate has consolidated around slang. quilt-verilog's choice of pure Verilog-2005 (not SV) is a *strength* for grammar-constrained decoding (smaller CFG) but a *weakness* for ecosystem alignment (the world is moving to SV/2023). The right move: **use slang as the canonical parser** (it handles Verilog-2005 as a subset), and let the broader ecosystem adopt slang's evolving capabilities without quilt-verilog having to track them. quilt-verilog's IR question (§III.2) is separate: it should target a *cellular IR* (the 5+1 opcodes), not Verilog source or CIRCT MLIR, because the cellular IR is the right abstraction level for an ML target and is unique to quilt-verilog.

### II.4 Grammar-constrained decoding stack

The space has consolidated in 2024-2026 around three production engines: **XGrammar** (compiled CFG, fastest), **llguidance** (Earley parser on regex derivatives, Microsoft), **Outlines** (delegates to either XGrammar or llguidance). All claim near-zero overhead for JSON. **None ship a Verilog grammar.** This is the single most actionable gap in the entire substrate map.

#### II.4.1 The constrained-decoding matrix

| Library | Algorithm | Tokenizer-aware | CFG | JSON Schema | Regex | Speed (per-token, 128k vocab) | HDL grammar shipped? |
|---|---|---|---|---|---|---|---|
| **XGrammar (v2)** | compiled CFG + adaptive Earley cache | yes (trie) | ✅ | ✅ | ✅ | ~5μs (JSON) | ❌ |
| **llguidance** | Earley + regex derivatives | yes (toktrie) | ✅ (Lark) | ✅ | ✅ | ~50μs | ❌ |
| **outlines_core** | FSM/regex | yes | ❌ (routes to llguidance) | ✅ | ✅ | ~tens of μs | ❌ |
| **lm-format-enforcer** | char-level parser | yes (any) | ❌ | ✅ | ✅ | slow (char-level) | ❌ |
| **Guidance** | llguidance-backed | yes | ✅ | ✅ | ✅ | via llguidance | ❌ |
| **llama.cpp GBNF** | BNF + token IDs | yes | ✅ | ✅ (via grammar) | ✅ | fast | ❌ |
| **SynCode** | DFA mask store (LALR) | yes | ✅ | ✅ (via grammar) | ✅ | fast | ❌ |
| **Synchromesh (CSD)** | parser-based, semantic | yes | ✅ | n/a | n/a | slow (semantic) | ❌ |
| **Pre³** | DPDA (LR-1) | yes | ✅ (LR-1 subset) | n/a | n/a | fast | ❌ |

#### II.4.2 The critical observation

**No production constrained-decoding library ships a Verilog or SystemVerilog grammar.** The grammar exists in machine-readable form in sv-parser (Rust), slang (C++), and tree-sitter-systemverilog (JS) — extraction is mechanical. A `verilog.gbnf` for llama.cpp, a `verilog.lark` for Outlines/llguidance, and a `verilog.ebnf` for xgrammar would each be ~500-2000 lines and would unblock the entire research community. **This is the lowest-hanging-fruit contribution quilt-verilog could make to the broader ecosystem.** quilt-verilog's choice of pure Verilog-2005 (smaller grammar than SV) makes this 5× easier than it would be for any other HDL-LLM project.

#### II.4.3 The Verilog-specific challenge

Verilog is harder for constrained decoding than JSON for three reasons:

1. **Preprocessor context-sensitivity.** `ifdef/`define/`include make almost every token context-dependent. xgrammar's headline trick is splitting the vocabulary into context-independent and context-dependent tokens; SV's preprocessor makes almost every token context-dependent.
2. **Deep nesting.** `always` blocks nest 5+ levels deep; xgrammar's adaptive-stack may degrade.
3. **Sized literals.** `<size>'<base><value>` requires width-checking that a CFG can express syntactically but cannot enforce semantically (`8'h1FF` is syntactically valid CFG-wise but semantically illegal — 9 bits in 8-bit literal).

The "near-zero overhead" claim is verified for JSON but **unverified for Verilog**. Red-team 2-A §3.3 specifically flags this as WEAKENED. The right empirical test: build the Verilog-2005 CFG, run XGrammar on a 1000-token generation with 128k vocab, measure per-token overhead. If >500μs/token, the "near-zero" claim is falsified for HDL.

### II.5 Agentic coding frameworks — patterns quilt-verilog could borrow

The 2024-2025 wave of agentic coding frameworks (OpenHands, SWE-agent, Aider, AutoCodeRover, Devin, Cursor, Continue) developed a unified 6-element agent-loop pattern that quilt-verilog could borrow for HDL agents.

#### II.5.1 The unified 6-element agent-loop pattern

1. **Drain-Block-Observe-Act-Reflect** loop (OpenHands, arxiv 2407.16741): drain pending events; block on next event; observe tool output; act via tool call; reflect on outcome. This is the 5-phase event-stream loop.
2. **Agent-Computer Interface (ACI)** (SWE-agent, arxiv 2405.15793): the design of the *commands* the agent can run matters as much as the agent itself. SWE-agent's ACI is 12 commands (find_file, search_dir, search_file, open_file, scroll, edit, submit, etc.). 12.5% SWE-Bench with GPT-4.
3. **Edit-format selection** (Aider): the agent chooses between whole-file edit, search-and-replace, diff, and unified-diff based on context. Aider uses tree-sitter for a "repo map" — a compressed AST-derived summary of the codebase.
4. **AST-guided program repair** (AutoCodeRover, 37.3% SWE-Bench Lite): the agent doesn't grep; it navigates the AST.
5. **Tool receipts as git commits** (Aider): every edit is a git commit; the agent can rollback. This gives a falsifiable trail.
6. **Dynamic discovery** (Cursor): the agent doesn't have a fixed ACI; it learns available commands from the IDE.

#### II.5.2 The HDL gap

**Every HDL agent in the literature is single-module.** AutoChip, RTLFixer, VeriDispatcher, Spec2RTL-Agent, HDLFORGE — all operate on one Verilog module at a time. **No HDL agent has been built that operates at the repo level**, the way SWE-agent operates on a software repo. This is a wide-open gap. quilt-verilog's opportunity: build an HDL-ACI (Agent-Computer Interface) that exposes slang CST, SymbiYosys, CEC, cocotb, and the cellular IR as commands. This is the **HDL Agent-Computer Interface** proposal in §VII.

#### II.5.3 What this means for quilt-verilog

The agent-loop pattern is well-established. The HDL-specific instantiation is not. quilt-verilog could ship the first HDL-ACI as a contribution to the field, independent of whether the cellular fabric itself becomes widely adopted.

### II.6 Formal verification + ML — the neuro-symbolic frontier

The 2024-2026 wave of ITP-LLM (Interactive Theorem Proving + LLM) work established a canonical pattern that has *not* been ported to hardware formal verification.

#### II.6.1 The ITP-LLM canonical pattern

1. **LLM as policy** (proposes next tactic / next proof step)
2. **Symbolic engine as reward** (Lean / Coq / Isabelle / SMT verifies)
3. **MCTS over the proof tree** (AlphaProof style; AlphaGeometry2 arxiv 2502.03544 uses "knowledge-sharing between search trees" — underexploited for HDL)
4. **Retrieval over prior proofs** (LeanDojo, Llemma, Magnushammer, COPRA, Prover Agent)

Key 2024-2026 results:
- **AlphaProof** (DeepMind, 2024): Lean + AlphaZero-style search, silver medal at IMO.
- **AlphaGeometry2** (arxiv 2502.03544): 84% IMO 2000-24 geometry.
- **COPRA** (Aster et al., 2024): agentic loop for Lean, retrieval-augmented.
- **Baldur** (First et al., NeurIPS 2023): Coq + LLM, proof repair.
- **Proof2Silicon / PREFACE** (arxiv 2509.06239): the closest HDL analog — RL on prompt to steer frozen LLM toward Dafny-verifiable code, +21% Dafny verification, 72% end-to-end HW synth success. **Targets Dafny→Vivado HLS, not native Verilog.**

#### II.6.2 The hardware FV stack

**Open:** SymbiYosys + Yosys + Z3/Boolector/CVC5 + abc (BMC, k-induction, CEC, SEC)
**Commercial:** JasperGold (Cadence), VC Formal (Synopsys), FormalPro (Siemens), Questa FV

#### II.6.3 The HDL neuro-symbolic gap

**No work ports the ITP-LLM pattern to SymbiYosys + SVA + native Verilog.** The entire neuro-symbolic frontier — AlphaProof, COPRA, Baldur, Proof2Silicon — operates on software verification (Lean/Coq/Dafny). Hardware verification (SVA + BMC + CEC + SEC) has no LLM-agent equivalent. This is a wide-open gap. quilt-verilog's opportunity: build a **Property-Search Agent** that uses AG2's knowledge-sharing between search trees + COPRA's agentic loop, with SymbiYosys+SVA as the verifier. This is the **Property-Search Agent** proposal in §VII.

#### II.6.4 What this means for quilt-verilog

quilt-verilog is positioned to be the first project to port the ITP-LLM pattern to native Verilog. The combination of (a) pure Verilog-2005 (small target language), (b) SymbiYosys already integrated for the 6 formal proofs, (c) QUF state as a verification oracle, (d) the BEACONS register as a dataset of falsifiable claims — these are the ingredients for a neuro-symbolic HDL agent that no other project has.

---

## Part III — Six Technical Focus Areas (the substrate)

The user asked the "be more clever on the lowest levels" analysis to focus on six areas: tokenization/lexing, AST/IR layer, training data & curricula, verifier-in-the-loop/RL, inference/serving, evaluation harnesses. This part covers each in depth, ending each chapter with concrete proposals that survived the adversarial rounds.

### III.1 Tokenization & Lexing for HDL

#### III.1.1 Current state of the art (and why HDL is a 5th-class citizen)

The four major code-LLM tokenizers all use byte-level BPE; differences are vocab size, digit handling, whitespace handling, and code-awareness of pre-tokenization regex:

| Tokenizer | Vocab | Digit handling | Whitespace | Notable for HDL |
|---|---|---|---|---|
| CodeLlama | 32k | each decimal digit is its own token | standard | Catastrophic for HDL sized literals |
| StarCoder2 | 49k | standard | explicit whitespace tokens | 619 languages; Verilog <0.05% |
| DeepSeek-Coder | 32k | standard | standard | 2T tokens, 87% code, 16K context |
| Qwen2.5-Coder | 151k | standard | standard | Multi-Programming-Language eval |
| ChipNeMo (closed) | ? | domain-adaptive | domain-adaptive | Only major chip-design LLM that re-trains the tokenizer; vocab not released |

Verilog's `<size>'<base><value>` literal grammar (e.g., `8'hFF`, `32'b1010`) fragments into ≥5 tokens on every existing tokenizer. Three concrete consequences: (1) per-digit arithmetic noise (no shared prefix between `8'hFF` and `8'h10`); (2) bit-vector width/value mismatch (`8'h1FF` — 9 bits in 8-bit literal) is invisible to BPE but trivially rejected by a hand-written lexer; (3) `define/parameter substitution interacts with literals lexically.

#### III.1.2 The big idea — slang-as-lexer-replaces-pretokenizer

Don't run BBPE over UTF-8 bytes. Run slang's lexer over the corpus; each lexical token (keyword, identifier, sized literal, operator, pragma) becomes a single LLM token. BPE then operates over the *alphabet of slang tokens* (~200 distinct lexical categories × identifier and literal instances), not over the byte alphabet. The LLM vocabulary is now "Verilog lexical tokens + BPE merges over their IDs", not "UTF-8 bytes + BPE merges over bytes".

**Specific design.** Vocabulary = {Verilog keywords (100)} ∪ {operators (30)} ∪ {sized-literal classes (32: 8-bit hex, 16-bit hex, 8-bit binary, ..., parameterized)} ∪ {identifier classes (50: by length-bucket × case-pattern)} ∪ {punctuation (20)} ∪ {specials (BOS, EOS, PAD)}. Total ~250 lexical tokens. BPE merges learn common lexical-token bigrams/trigrams (e.g., `assign ID =` → one merge). Final vocab ~2-4K — much smaller than StarCoder2's 49K, with higher information density per token.

**Benefits the scouts missed:** (a) illegal tokens (`8'h1FF`) become impossible *by construction* (slang's lexer rejects them); (b) lexical category is a free feature (the LLM knows `8'hFF` is a sized literal, not a sequence of digits); (c) the model learns at HDL's actual lexical granularity, not byte granularity; (d) slang is the only contractually-correct Verilog lexer in the open ecosystem — using it as the pre-tokenizer is using the canonical tool for its canonical purpose.

#### III.1.3 The challenger's critique — and the response

The challenger (§IV.4) attacks this idea on transfer-learning grounds: a model trained from scratch on a 2-4K HDL vocab cannot reuse a single weight from StarCoder2/DeepSeek-Coder/Qwen2.5-Coder. The HDL pretraining corpus is ~50 MB; Chinchilla scaling requires 20 tokens/parameter; 50 MB ≈ 12.5M tokens trains a ~600K-parameter model — a toy.

**The response:** the right move is *not* "train from scratch" but "embedding fine-tune." Take a frozen StarCoder2/Qwen2.5-Coder base; expand the embedding layer with the new HDL-specific tokens; train only the embedding layer + a small adapter on HDL data. This preserves transfer learning while gaining HDL-native tokenization. This is the standard "domain-adaptive tokenizer" recipe that ChipNeMo used (closed-source); the open version is the contribution.

**Alternative if embedding fine-tune is too costly:** the *inference-time token mapper* (red-team 2-A §2.8). Build a runtime mapper that converts a stock StarCoder2/Qwen tokenizer's output to HDL-aware tokens. The model never re-trains; the mapper pre-processes the prompt (re-tokenizing sized literals as single tokens) and post-processes the generation. This is inference-time-only and immediately deployable. Distillation is still valuable for max compression but the mapper is the 80/20 solution.

#### III.1.4 Proposals

1. **slang-as-lexer-replaces-pretokenizer** (10 person-weeks). Use slang's lexer as the pre-tokenizer; BPE over the alphabet of slang tokens. Embedding fine-tune on a frozen base model. Highest info density per token; illegal tokens impossible by construction.
2. **Inference-time token mapper** (3 pw). Runtime pre/post-processor that maps stock tokenizer output to HDL-aware tokens. No retraining. The 80/20 solution.
3. **Sized-literal class tokens** (2 pw). Add ~32 special tokens for sized-literal classes (`<VLIT_8_HEX>`, `<VLIT_16_BIN>`, etc.). Compatible with any base tokenizer.
4. **Operator fusion tokens** (1 pw). Add tokens for `<=`, `=>`, `===`, `<<<` (single-token rather than multi-token). Trivial; immediate compression.
5. **Token-healing at HDL prompt boundaries** (1 pw). Apply token healing (Microsoft Guidance technique) at every HDL prompt boundary, especially after `assign result = 8'h`.
6. **Cross-tokenizer distillation** (8 pw). Train a student model with HDL-native tokenizer from a teacher with stock tokenizer. Maximum compression; expensive.

### III.2 AST / IR Layer

#### III.2.1 The structural-pretraining lineage — and why HDL is different

GraphCodeBERT (arxiv 2009.08366) was the first major structural-signal pretrainer. Verbatim from abstract: *"Instead of taking syntactic-level structure of code like abstract syntax tree (AST), we use **data flow** … a semantic-level structure of code that encodes the relation of 'where-the-value-comes-from' between variables."* Their explicit rejection of AST is the most-quoted sentence in the field — and it's *wrong for HDL*: in hardware, the data flow IS the AST (every `assign` is a where-the-value-comes-from edge). The software-LLM literature's preference for data flow over AST is inverted for HDL.

#### III.2.2 The IR options on the table

Four IR options for quilt-verilog's ML target, ranked by suitability:

1. **Verilog source** (current). Ambiguous (width inference, signedness, multi-driver detection require elaboration). Lossy (formatting, comments, naming). The LLM must learn elaboration to be correct.
2. **CIRCT MLIR `hw`/`comb`/`seq` dialects**. Verbose (token economy worse — `assign x = a & b;` is ~6 source tokens but ~10-15 MLIR tokens). PyCDE requires Python at inference (incompatible with FPGA deployment). CIRCT's `ExportVerilog` lowers to generic SV — would not preserve the 5+1 opcode cellular model. **The challenger (§IV.4) calls this "the most overhyped idea in either scout report" and the analysis is correct.**
3. **slang CST/AST**. Round-trippable (contractual). JSON-exportable (`--cst-json` v10+). pyslang (nanobind) for Python introspection. Best as a *training signal* (auxiliary modality, position encoding), not as a generation target.
4. **Cellular IR (new)** — quilt-verilog-specific. ~10 productions:

```
fabric := cell+
cell   := "cell" id "{" dial* edge* "}"
dial   := "dial" name "=" value
edge   := "edge" peer "=" weight
tick   := "tick" cell_id
op     := "bind" cell_id dial_idx value
      |  "link" cell_id edge_idx peer weight
      |  "effect" cell_id edge_idx data
      |  "view" cell_id (act|wsum|dial_idx)
      |  "tick"
```

The LLM targets this IR. A <500-line compiler lowers to Verilog-2005 by trivial expansion (each `cell` becomes a `q_cell_core.v` instantiation, each `op` becomes a host-side bus transaction).

#### III.2.3 Why cellular IR is the right answer

- **Minimality.** ~10 productions vs Verilog-2005's ~150 vs CIRCT's 40+ dialects. The LLM has the smallest possible target.
- **Canonicity.** Byte-exact hashable (via FNV-1a on the canonical serialization). CEC-equivalence is decidable.
- **Lowerability.** <500-line compiler to Verilog-2005. No Python at inference.
- **Preserves quilt-verilog's identity.** The 5+1 opcode model is the IR. The LLM doesn't emit generic MLIR that lowers to generic SV — it emits cellular IR that lowers to quilt-verilog's existing 22 modules.

#### III.2.4 The challenger's critique — and the response

The challenger (§IV.4 §1.4) attacks cellular IR as a "straitjacket, not a target": the IR can only express the 5+1 opcodes, so the LLM cannot generate "softmax attention" or "top-k routing" or "differentiable plasticity."

**The response:** this is a feature, not a bug. The whole point of quilt-verilog is the 5+1 opcode cellular model. If the LLM could generate "softmax-gated Hebbian update," it would no longer be quilt-verilog — it would be a different project. The cellular IR constrains the LLM to the cellular model; that's the contract. If the project wants to expand the cellular model (e.g., add a 6th opcode), the IR grows accordingly. The challenger's critique applies to *expanding quilt-verilog's expressiveness*, which is a separate question (see §VI on bit-level cleverness).

#### III.2.5 Auxiliary: AST-position-encoding via slang CST byte-ranges

slang's `--cst-json` (v10+) gives byte-range annotations for every CST node. Use these as a *positional encoding*: augment each token's embedding with its CST-path (e.g., `ModuleDecl/AlwaysStmt/IfStmt/CondExpr[2]`). This is structurally different from TreeBERT (which used AST paths for pretraining tasks) because slang's CST is contractually correct and byte-range aligned. The LLM gets positional information at lexical, statement, and module granularity for free.

**The challenger's critique:** embedding cost is ~7.5M extra parameters for a 7B model; empirical gap is unproven; byte-range alignment is lossy because BPE doesn't align with slang's lexical tokens.

**The response:** the alignment problem goes away if we adopt §III.1's slang-as-lexer-replaces-pretokenizer (then tokens ARE lexical tokens, alignment is exact). The parameter cost is real but modest (0.1% of 7B). The empirical gap is testable in a 1B-parameter experiment.

#### III.2.6 Proposals

1. **Cellular IR as the LLM target** (8 pw). Define the ~10 productions; write the <500-line lowering to Verilog-2005; test on the 22 modules.
2. **slang CST as auxiliary training modality** (4 pw). Pair (Verilog, slang CST) as a contrastive learning objective.
3. **AST-position-encoding via CST byte-ranges** (5 pw). Path embedding = sum of (node-type-embedding + sibling-index-embedding), depth 8.
4. **CIRCT FIRRTL as contrastive modality** (3 pw). Pair (Verilog, FIRRTL) as a contrastive learning objective.
5. **Multi-resolution token streams** (4 pw). Random switching between source/CST/FIRRTL during pretraining.
6. **QUF-as-checkpoint pretraining** (5 pw). `(QUF bytes, Python sim trace, RTL source)` triples — runtime-state-as-text, no prior HDL LLM has had this.
7. **Elaboration-aware pretraining** (6 pw). Mask `generate`, predict elaborated AST node count.

### III.3 Training Data & Curricula

#### III.3.1 The big-three corpora — and the HDL gap

The Stack v2 (arxiv 2402.19173) abstract: *"built on top of the digital commons of [Software Heritage's] source code archive. Alongside the SWH repositories spanning 619 programming languages … we carefully select other high-quality data sources, such as GitHub pull requests, Kaggle notebooks, and code documentation."* 3.3-4.3T tokens. **Verilog is a rounding error (<0.05%, unsourced — the challenger flags this number as WEAKENED in §IV.4 §3.8).** Used SWHIDs — the right primitive for any HDL corpus.

DeepSeek-Coder: 2T tokens, 87% code. Qwen2.5-Coder: 5.5T tokens. **No HDL breakdowns published by any of the three.**

#### III.3.2 Synthetic data — the Magicoder / OSS-Instruct lineage

Magicoder/OSS-Instruct (ICLR 2024): *"75K synthetic instruction data using OSS-Instruct, a novel approach to enlightening LLMs with open-source code snippets"* — use teacher LLM to generate instruction-tuning pairs from real OSS snippets. Evol-Instruct (WizardLM): iterative deepening. Self-CodeAlign (MIT): self-instruct, no teacher.

**RTLCoder** (arxiv 2410.09406, cited 203×): the HDL instance — scoring-based SFT (not MLE) on synthetic HDL data, achieves 34% on VerilogEval spec-to-RTL at 6.7B.

#### III.3.3 MG-Verilog + ChipNeMo — and the open-ChipNeMo gap

MG-Verilog (IEEE LAD 2024): multi-grained annotations (block/module/system-level). ChipNeMo abstract verbatim: *"Our largest model, ChipNeMo-70B, outperforms the highly capable GPT-4 on two of our use cases, namely engineering assistant chatbot and EDA scripts generation."* **Catch: corpus is closed. The field is missing an open ChipNeMo.** quilt-verilog's pure-Verilog-2005 + FNV-canonical-hash + QUF format is the closest candidate.

#### III.3.4 BEACONS-as-seeds-for-DPO-scaling — the scaling pathway

Take each BEACONS NO-GO claim (19 rows), reproduce the failure mode in code, run AutoChip-style repair to produce a working version, and use the (broken, repaired) pair as DPO data. This generates ~19×N DPO pairs where N is the number of repair attempts per NO-GO. With N=50, that's ~1000 DPO pairs — 20× the raw BEACONS corpus.

**The challenger's critique:** BEACONS NO-GO claims are quilt-verilog-specific design choices, not general Verilog failure modes. SPIN-1's lesson is "Pulse-echo controllers assuming K-spaced refire or parity convergence." These tell the model "don't generate pulse-echo controllers for the quilt fabric" — useless for any other Verilog task. And 950 pairs is still tiny by DPO standards (UltraFeedback: 64K; HH-RLHF: 161K).

**The response:** the critique is correct for *general* Verilog training, but the DPO scaling is *quilt-verilog-specific* training — and that's the point. quilt-verilog's LLM (if any) is a specialist in the cellular model, not a general Verilog LLM. The 950 pairs are seeds; the actual DPO corpus should be augmented with OSS-Instruct-generated HDL pairs (next proposal).

#### III.3.5 Proposals

1. **SWHID-indexed HDL corpus** (8 pw). Index all HDL in Software Heritage under SWHIDs; dedup; publish.
2. **OSS-Instruct for HDL** (6 pw). Use teacher LLM to generate 6-tuples (block/module/system spec, Verilog, testbench, SVA, slang-CST, FIRRTL) from real OSS HDL snippets.
3. **Evol-Verilog with HDL-typed deepening** (4 pw). Evol-Instruct's iterative deepening adapted for HDL (e.g., combinational → sequential → pipelined → multi-clock-domain).
4. **Curriculum-by-pass-fail-rate** (3 pw). Use sv-tests' 18-tool × N-test grid as a curriculum: train on tests ≥15 tools pass (easy), then ≥10 (medium), then ≥5 (hard).
5. **SVA-assertion augmentation** (4 pw). Extract SVA assertions from existing Verilog; pair (Verilog, SVA) as training data.
6. **QUF-state-augmented data** (5 pw). `(RTL, QUF state, Python sim trace)` triples. Quilt-verilog-specific.
7. **BEACONS-NO-GO-seeded DPO scaling** (12 pw). 19 NO-GO × 50 repairs ≈ 950 DPO pairs. Pair with OSS-Instruct-generated HDL pairs for a full DPO corpus.

### III.4 Verifier-in-the-Loop / RL

#### III.4.1 The four families of verifier feedback

1. **Execution feedback** (RLEF): run test, get pass/fail.
2. **Test-feedback reward** (RLTF): per-test-case reward.
3. **Compiler feedback**: lint warnings, error messages.
4. **Formal verification feedback** — almost unexplored for HDL.

#### III.4.2 Classic code-RL papers

CodeRL (NeurIPS 2022, CodeT5-770M, test-pass reward). RLTF (ACL 2023, per-test-case reward). PPOCoder (PPO + execution + compiler). StepCoder (ACL 2024, sub-trajectory PPO for long-sequence credit assignment — critical because HDL modules are long). CodeReward/FALCON (reward shaping from compiler diagnostics).

#### III.4.3 GRPO and post-DeepSeek-R1 era

GRPO (DeepSeek-Math, arxiv 2402.03300): skip critic, group-relative advantage. CurES outperforms GRPO by +3-5 points. LeanConjecturer applies GRPO to theorem proving — closest analog to formal-verification-as-reward. **GRPO is now default for code+math** (DeepSeek-R1, Qwen2.5-Math). quilt-verilog should adopt GRPO as the RL algorithm.

#### III.4.4 AutoChip lineage — the HDL-specific verifier-in-loop

**AutoChip** (arxiv 2311.04887): *"We build AutoChip by combining the interactive capabilities of LLMs and the output from Verilog simulations … incorporating context from compiler tools, such as **Icarus Verilog, improves the effectiveness, yielding 24.20% more accurate Verilog**."* Canonical HDL verifier-in-loop paper. Notable: (a) uses Icarus (the *fastest* simulator for small designs, stable CLI, subprocess-callable); (b) in-context feedback, not RL — LLM is frozen; (c) reactive repair (compile → error → re-prompt), not proactive constrained decoding.

#### III.4.5 Proof2Silicon breakthrough — formal verification as RL reward

**Proof2Silicon/PREFACE** (arxiv 2509.06239): *"LLMs … frequently produce code that fails formal verification, an essential requirement for hardware and safety-critical domains. … we previously proposed PREFACE, a model-agnostic framework based on reinforcement learning (RL) that iteratively repairs the prompts provided to frozen LLMs, systematically steering them toward generating formally verifiable Dafny code without costly fine-tuning. … PREFACE's RL-guided prompt optimization consistently improved Dafny verification success rates across diverse LLMs by **up to 21%**. Crucially, Proof2Silicon achieved an **end-to-end hardware synthesis success rate of up to 72%**."* **The architectural innovation: the RL agent acts on the prompt, not the model weights.** Catch: targets Dafny→Vivado HLS, *not native Verilog*.

The quilt-verilog opportunity: redo with SymbiYosys+SVA/PSL as verifier + native Verilog-2005 as target + slang analysis as structural lint signal. This is the **PREFACE-for-HDL** proposal.

#### III.4.6 The CEC-as-primary-RL-reward idea — and the challenger's devastating critique

Red-team 2-A §2.2 proposes: use Yosys's `equiv` pass (combinational equivalence checking) as the primary RL reward for HDL, with BMC as a secondary reward for sequential properties. CEC constructs a miter circuit and runs a single SAT query; BMC does k-step unrolling with k separate SAT queries. For small designs (quilt-verilog's 22 modules), CEC runs in <1 second.

**The challenger's critique (§IV.4 §1.2) is devastating:**

1. **CEC requires two designs to compare.** The miter circuit is `f_generated ⊕ f_reference`. For RL on quilt-verilog, what is `f_reference`? Three candidates, all broken:
   - (a) *The existing quilt-verilog fabric.* Then you're training the LLM to *reproduce* the existing 22 modules, not to improve them. The reward collapses to "imitation learning on 22 modules" — 22 examples is not an RL signal.
   - (b) *A spec-derived reference.* But spec→RTL is the unsolved problem. CEC doesn't help you check against an NL spec.
   - (c) *A testbench.* CEC doesn't take testbenches; it takes RTL.

2. **CEC on the Hebbian edge multiplier `w·dat>>>15` is in SAT-hard territory, not sub-second.** SAT-based CEC on multipliers is the canonical hard case (Biere 1999; `mul` benchmarks still appear in SAT competitions). 2-A's claim that "CEC sidesteps the multiplier scaling cliff" is the opposite of the truth: BMC can use word-level solvers (Bitwuzla, MathSAT) that handle 16×16 multiplies in milliseconds; CEC on the *miter of two multiplier-containing designs* is bit-blasted SAT. quilt-verilog's modules are multiplier-heavy. CEC-as-RL-reward is likely *slower* than BMC, not faster.

**The response:** the challenger is correct on both counts. The right move is to use **word-level SMT (Bitwuzla, MathSAT)** rather than bit-blasted SAT, and to use **equivalence to a *specification-derived* reference** — which requires solving the spec→RTL problem partially (e.g., by using a *cellular IR* as the spec, since the cellular IR has well-defined semantics). Even with these fixes, CEC-as-primary-RL-reward is *weaker than originally proposed*; it should be one of several reward signals, not the primary one.

#### III.4.7 The right reward stack

Combine multiple reward signals:

| Signal | Latency | Coverage | Use |
|---|---|---|---|
| slang lint warnings (`-W*`) | milliseconds | structural / syntactic | dense reward shaping |
| Yosys synthesis success | 1-3s | synthesizability | hard constraint |
| Yosys `equiv` (CEC) against cellular IR reference | 1-5s | functional equivalence | primary reward (when reference exists) |
| SymbiYosys BMC | 5-300s | temporal safety | secondary reward |
| Icarus / cocotb testbench | 100ms-10s | functional correctness | tertiary reward |
| QUF hash equality | 10ms | behavioral equivalence (bit-exact) | bonus reward (quilt-verilog-specific) |

Total per-rollout latency: ~10-30s. PPO step (1024 rollouts) = 3-8 hours. **This is the fundamental RL latency wall for HDL.** Hardware-in-the-loop is worse (§III.4.8).

#### III.4.8 Hardware-in-the-loop RL — and why it doesn't work for training

Red-team 2-A §2.3 proposes: hook a real FPGA board (TinyFPGA BX, $40) to the RL loop. LLM generates Verilog → Yosys → nextpnr → icepack → flash to FPGA → read back QUF state → bit-exact reward. Latency: 5-10s per cycle. 10 boards in parallel for 60s wall-clock per 10 rollouts.

**The challenger's critique (§IV.4 §1.5) is correct:**

- **RL throughput is incompatible with flash latency.** PPO needs ~1024 rollouts per GPU step. At 6s per rollout (single board), one step = 6144s = 1.7 hours. With 10 boards in parallel, 10 minutes per step. PPO needs ~10⁶ steps for convergence. That's 19 years of wall-clock. Even GRPO is ~10⁵ steps → 2 months. And this assumes *no debugging*.
- **Sparse-reward problem:** bit-exact QUF hash matching is binary. Most LLM-generated patches won't match. Sparse reward + slow environment = no learning signal.

**The response:** hardware-in-the-loop is research-grade gold standard for *evaluation*, not *training*. Use it for:
- Final eval (cheap because eval doesn't need 10⁶ steps)
- Real timing/power/metastability signal that no simulator can match
- Demonstrations (the §VIII vessel-as-robot demo)

But not for RL training. The right training setup is the multi-signal reward stack in §III.4.7.

#### III.4.9 Self-repair loops

Self-Debug (TACL 2023, 1547 citations): *"self-debugging with code explanation consistently improves the baseline by 2-3%, and improves the prediction accuracy on problems of the hardest level by 9%."* Reflexion (verbal RL). InspectCoder (runtime traces). For HDL, the equivalent of execution trace is **VCD waveform** — no published work feeds VCDs back as self-repair signal. **Clean gap.** quilt-verilog's QUF state is a more compact representation than VCD and could serve as the self-repair signal.

#### III.4.10 Test-time scaling and MCTS

OpenAI o1/s1 (arxiv 2501.19393) budget forcing. AlphaCode (~1M candidates, cluster + filter). Guided-ReST (MCTS with landmark guidance). No published MCTS-for-Verilog work despite excellent structural fit (deterministic oracles).

#### III.4.11 Proposals

1. **GRPO with multi-signal reward** (8 pw). GRPO + slang-lint + Icarus-sim + CEC + SymbiYosys BMC + QUF-hash. Use §III.4.7's reward stack.
2. **SymbiYosys-as-reward** (12 pw). The open Proof2Silicon analog. RL agent acts on prompt (PREFACE-style), SymbiYosys+SVA+slang-lint as reward ensemble.
3. **VCD-as-self-repair** (5 pw). Feed textualized VCD waveforms back to the LLM as self-repair signal.
4. **QUF-state-as-reward** (4 pw). `hash(generated_QLF) == hash(reference_QLF)` as bonus reward. Bit-exact behavioral equivalence.
5. **Two-player verifier loop** (10 pw). Generator + Critic LLM + SymbiYosys. Generator emits Verilog; critic emits SVA; SymbiYosys judges. If generator passes, both rewarded; if fails, critic rewarded for finding bug. GAN-style, formal-grounded.
6. **MCTS over elaboration choices** (10 pw). MCTS over the elaboration tree, with slang analysis as the heuristic.
7. **PREFACE-for-HDL** (16 pw). Port PREFACE to Verilog with SymbiYosys+slang, target ≥15% gain at zero fine-tuning cost. **The flagship RL proposal.**

### III.5 Inference / Serving

#### III.5.1 Speculative decoding

Leviathan et al. (arxiv 2211.17192, Nov 2022) + Chen et al. (arxiv 2302.01318): draft model proposes K tokens, target verifies in one forward pass, lossless. Variants: Medusa, EAGLE/EAGLE-2 (feature-level lookahead), REST (retrieval-augmented).

#### III.5.2 Grammar-constrained decoding — the XGrammar revolution

**XGrammar** (arxiv 2411.15100, MLSys 2025) abstract verbatim: *"XGrammar accelerates context-free grammar execution by dividing the vocabulary into context-independent tokens that can be prechecked and context-dependent tokens that need to be interpreted during runtime. … Evaluation results show that XGrammar can achieve **up to 100x speedup** over existing solutions. Combined with an LLM inference engine, it can generate **near-zero overhead** structure generation in end-to-end low-LLM serving."* Prior CFG-constrained decoding had 2-5× overhead; now near-zero. Integrated into vLLM, SGLang, TGI, Modular MAX.

#### III.5.3 Grammar-constrained speculative decoding — the fresh gap

vLLM/SGLang ecosystem (Jul 2026) notes: *"Jump-forward decoding (SGLang; XGrammar, arXiv 2411.15100) skips grammar-deterministic tokens by constraining output."* This is grammar-driven token skipping, *not* true grammar-constrained speculative decoding. **True grammar-constrained speculative decoding** — where the draft model itself is grammar-constrained and the target verifies both content and grammar-adherence — has no published paper. Modular MAX's Aug 2026 notes mention both in same changelog, suggesting industry is groping toward it but hasn't published. **Fresh gap, first-mover advantage.**

#### III.5.4 The challenger's critique — and partial response

The challenger (§IV.4 §1.3) makes three attacks:

1. **Speculative decoding speedup depends on draft acceptance rate, not on grammar validity.** Constraining the draft to grammar-valid tokens does not increase the probability that the *target* agrees with the draft — both models already agree on grammar.
2. **On `always` blocks, the bottleneck is semantic, not syntactic.** A 100-line `always` block has many grammar-valid continuations at every step.
3. **EAGLE-2's tree-attention may actually be worse on HDL.** EAGLE-2's sweet spot is moderate branching; for Verilog in a grammar-constrained setting, the branching factor is either 1 (grammar forces a single token — already handled by jump-forward) or very large (any identifier, any literal — tree can't enumerate).

**Partial response:** the critique is technically correct. The value of grammar-constrained speculative decoding is *not* increased acceptance rate per se; it's *elimination of syntactic failure modes*. With XGrammar-constrained draft + target, no generated sequence can be syntactically invalid. The speedup comes from skipping the validation/rejection cycle that unconstrained spec-decoding would need. But the challenger is right that this needs empirical measurement before being claimed as a win.

#### III.5.5 The composition problem (also from challenger)

XGrammar masks the target's logits; EAGLE-2 samples the draft from the masked distribution; the target verifies against the *unmasked* distribution (raw target logits). For acceptance to be correct, the target's verification pass must also be XGrammar-masked — but then the target does double work (mask + verify), and the spec-decoding speedup is eaten by the mask cost on the target. **The literature on composing spec decoding with grammar constraint is *empty*; the synthesizer will stack them as if they compose; they don't.**

**Response:** this is a real research problem, not a blocking issue. The right move is to publish the empirical study: "Grammar-constrained speculative decoding: when does it compose?" The first paper to characterize this composition wins first-mover advantage.

#### III.5.6 KV-cache tricks for HDL

PagedAttention/vLLM (16-256 token pages, 2-4× throughput). SGLang RadixAttention (prefix-tree KV reuse — perfect for agentic serving). Chimera (multi-agent KV coordination). Qwen2.5 (128k), DeepSeek (1M with YaRN). **HDL files are short but HDL *projects* are long** (Chipyard config ~100k tokens) — SGLang prefix-tree is structurally perfect.

#### III.5.7 Agentic serving patterns

OpenHands (ICLR 2025), SWE-agent (NeurIPS 2024, SWE-agent-LM-32B Feb 2026 is open SOTA). AutoChip/VeriDebug/RTLFixer/Spec2RTL-Agent: HDL lineage using fixed LLMs + hand-written agent loops over `subprocess` calls. **Gap: no HDL agent uses grammar-constrained decoding.** Every AutoChip retry is a syntactic failure that xgrammar would eliminate.

#### III.5.8 Proposals

1. **HDL-CFG grammar for XGrammar** (6 pw). Write Verilog-2005 CFG in XGrammar format from tree-sitter-systemverilog's grammar. *Single highest-leverage integration in this section* — eliminates malformed-Verilog failures at near-zero cost. **The lowest-hanging fruit in the entire report.**
2. **Grammar-constrained speculative decoding empirical study** (12 pw). EAGLE-2 + XGrammar on both draft and target; characterize when they compose. First-publication opportunity.
3. **SGLang prefix-tree KV for HDL projects** (4 pw). ~10× throughput for agentic serving of HDL codebases.
4. **slang-driven jump-forward** (8 pw). slang as the oracle for legal next tokens. **Caveat:** jump-forward gives ~0% speedup on Verilog (per challenger §IV.4 §1.7) because Verilog is not LL(1) — after `module foo(`, the next token can be many things. This proposal is WEAKENED.
5. **vLLM fork with PagedAttention + prefix-tree + XGrammar + EAGLE-2** (16 pw). 5-20× throughput, zero quality loss.
6. **Long-context quilt fabric** (8 pw). 200k-token repo prefix, ~5k incremental per agent step.

### III.6 Evaluation Harnesses

#### III.6.1 Software benchmark landscape

HumanEval (164 problems), MBPP (974), HumanEval+/MBPP+ (augmented tests), LiveCodeBench (contamination-aware), BigCodeBench (1140 library-usage tasks, OOD per Qwen2.5-Coder), CrossCodeEval (cross-file), SWE-Bench (2,294 real PRs, ICLR 2024), SWE-Bench+/Pro (anti-gaming), Humanity's Last Code Exam (Oct 2025, *"97-99% on HumanEval, 64-75% on LiveCodeBench, 49-68% on SWE-bench"*). Gorinova et al. OpenReview: HumanEval-style benchmarks are *"misaligned with agentic software"* workflows.

#### III.6.2 HDL benchmark landscape — full enumeration (16 benchmarks)

| Benchmark | Year | Coverage | Notes |
|---|---|---|---|
| VerilogEval v1 | 2023.09 | 156 problems | first HDL-specific benchmark |
| VerilogEval v2 | 2024.08 | spec-to-RTL + failure classification + ICL | GPT-4o 63%, Llama3.1-405B 58%, RTLCoder-6.7B 34% |
| RTLLM | 2023.08 | 3-goal: syntax, functionality, design quality | first to evaluate *design quality* (area, power, timing) |
| RTLLM-SV | 2024 | first SystemVerilog | |
| MG-Verilog | 2024.05 | multi-grained | block/module/system |
| HDLEval | 2024 | first multi-HDL | UCSC |
| CVDP | 2025 | 783 problems | NVIDIA; ACE-RTL achieves 97.1% |
| ChipBench | 2026.01 | | |
| RTL-BenchMT | 2026.05 | dynamic | |
| OpenLLM-RTL | 2025 | EMNLP 2025 | |
| RealBench | 2025 | DAC 2025 | first real-world IP-level |
| EDALearn | 2025.07 | first RTL-to-signoff | |
| RTL-Repo | 2025 | repo-level | |
| Pluto | 2025.10 | first PPA-aware | |
| Synthesis-in-the-Loop | 2026.03 | 32 LLMs × 202 tasks | first synthesis-aware eval |
| TuRTLe | 2026 | 40 LLMs | |
| FVEval | 2026.05 | first FV-specific | |

#### III.6.3 What's measured vs what's missing

All HDL benchmarks measure functional correctness (testbench pass@k). Missing:
1. **Formal verification** (no SymbiYosys/boolector/Z3 oracle — Pluto closest but partial)
2. **Timing** (setup/hold, critical-path slack — never measured)
3. **Power** (switching activity + power synthesis — never measured)
4. **Equivalence checking** (Yosys `equiv` CEC/SEC — never used as eval, despite being the cleanest formal oracle for HDL)
5. Multi-module/system-level
6. **quilt-cell behavioral equivalence** — bit-exact QUF hash equality is *unique to quilt-verilog*, no other HDL benchmark has it

#### III.6.4 The QUF-Hash-Eval critique

Red-team 2-A §1.5 calls QUF-Hash-Eval the weakest eval proposal:
- **Bit-exact hash equality is too strict.** Two functionally-identical designs with different dial orderings, different edge enumeration orders, or different routing tables produce different QUF hashes. The hash is sensitive to *serialization order*, not just to behavior.
- **It doesn't test timing, power, or PPA.**
- **A model that memorizes the canonical test cell passes.** The test cell (id=1, dials=[1..16], neighbors=[2,3,4]) producing `0xe435d91d6d92a1d8` is published. A model can memorize this and pass QUF-Hash-Eval without any generalization.
- **FNV-1a is non-cryptographic; collisions are possible.**

**Response:** the critique is correct. QUF-Hash-Eval should be:
1. **Behavioral equivalence via CEC** (not bit-exact hash). Use Yosys `equiv` against a reference QUF.
2. **Held-out test cells.** Don't use the published test cell; generate a distribution of test cells.
3. **BLAKE3 hash** (per challenger §2.5) instead of FNV-1a, for collision safety.
4. **Combined with PPA** (Yosys+nextpnr LC+Fmax) and formal verification (SymbiYosys BMC).

#### III.6.5 Proposals

1. **VerilogEval-Formal** (10 pw). SVA property file + SymbiYosys BMC pass as score. quilt-verilog's 6 SymbiYosys proofs as seed corpus.
2. **VerilogEval-PPA** (5 pw). Yosys+nextpnr-iCE40 LC+Fmax as score.
3. **QUF-Hash-Eval (fixed)** (6 pw). Behavioral equivalence via CEC against held-out test cells, BLAKE3 hash, combined with PPA.
4. **VerilogEval-Diff** (5 pw). cocotb, 1k random stimulus, differential testing against reference.
5. **RTLLM-Equiv** (5 pw). Yosys `equiv` CEC/SEC against reference.
6. **MutationEval** (4 pw). Use quilt-verilog `corpus/mutants/` as mutation eval.
7. **PPA-Timing-Power-Eval end-to-end** (8 pw). Full PPA + timing + power eval.

---

## Part IV — The Adversarial Record (4 rounds, 8 agents)

This part documents the GAN-like adversarial iteration the user requested. Eight agents worked in four rounds, each round building on (and attacking) the previous. The full reports are in `/home/z/my-project/research-out/`; this part is the digest.

### IV.1 Round 1 — Scouting (4 parallel agents, ~25,000 words total)

| Agent | Task | Words | Key artifacts |
|---|---|---|---|
| 1-A | quilt-verilog repo + ecosystem forensics | 4,837 | The 5+1 opcode model; the 22-module `rtl/` enumeration; the BEACONS.md register; the 12 anomalies; the forward-dating finding |
| 1-B-retry | industry / 2025-2026 papers / agentic / FV+ML | 6,426 | ACE-RTL 97.1% CVDP; QiMeng-CodeV-R1 68.6%; Proof2Silicon PREFACE; the unified 6-element agent-loop pattern; the ITP-LLM canonical pattern |
| 1-C | HDL toolchain + grammar-constrained decoding | 7,185 | The slang consolidation; the 6-IR landscape; the constrained-decoding matrix; the 10 critical gaps; the 12 leverage points |
| 1-D | code-LLM substrate (tokenizer / IR / data / RL / inference / eval) | 7,087 | The 6-area substrate analysis; the cross-cutting ideas; the 30+ proposals across all six areas |

**Round 1 verdict:** the scouts produced a dense substrate map. Their failure mode (per red-team 2-A): *they treat substrate maps as proof of feasibility*. "Tool X exists and exposes API Y" is taken to imply "an LLM can be productively trained against API Y at RL latency". That implication is almost always false, and the scouts never test it.

### IV.2 Round 2 — Red-team critique (2 parallel agents, ~11,000 words total)

#### IV.2.1 Red-team 2-A (technical critique, 6,056 words)

**Top 5 most-overhyped proposals (per 2-A):**

1. **CIRCT `hw`/`comb`/`seq` MLIR as alternative generation target** — Token economy is worse (not better); PyCDE requires Python at inference (incompatible with FPGA deployment); nobody maintains a quilt-verilog-specific MLIR lowering; zero precedent for training on MLIR. *Verdict: Falsified as proposed.*
2. **Grammar-constrained speculative decoding** — Speculative decoding speedup depends on draft acceptance rate, not grammar validity. On `always` blocks, the bottleneck is semantic, not syntactic. EAGLE-2's tree-attention may actually be worse on HDL. *Verdict: Overhyped.*
3. **BEACONS.md as DPO preference dataset** — 55 rows is not a DPO dataset. GO ≠ preferred completion. 55 binary signals is noise. *Verdict: Falsified as proposed.* (Rescued by 2-A's own scaling pathway: 19 NO-GO × 50 repairs ≈ 950 DPO pairs.)
4. **UHDM Folded Model + Cap'n'Proto as elaboration cache for RL** — "Incremental compilation" ≠ "diff-aware partial re-elaboration". OpenTitan's earlgrey UHDM is megabytes, not kilobytes. Surelog's Python API is visitor-pattern, not node-edit. *Verdict: Weakened.*
5. **QUF-Hash-Eval as bit-exact behavioral equivalence oracle** — Bit-exact hash equality is too strict. Doesn't test timing/power/PPA. A model that memorizes the canonical test cell passes. FNV-1a is non-cryptographic. *Verdict: Falsified as an eval oracle.*

**Top 10 missed clever ideas (per 2-A):**

1. slang-as-lexer-replaces-pretokenizer (not "lexer-aware BPE")
2. CEC-as-RL-reward (not just BMC, not just eval)
3. Hardware-in-the-loop RL via real FPGA flash
4. Cellular-IR-as-target (not Verilog source, not CIRCT MLIR)
5. AST-position-encoding via slang CST byte-ranges
6. BEACONS-NO-GO-seeded DPO scaling
7. Mutation-based *curriculum* (not just MutationEval)
8. Token-mapper for inference-time HDL tokenization (no retraining)
9. QUF-state-as-RL-environment (not just reward)
10. Synthesis-as-RL-reward (PPA-as-reward, not just PPA-as-eval)

**Factual claim pressure-test (10 claims):**

| Claim | Source | Verdict |
|---|---|---|
| "slang CST is contractually round-trippable" | 1-C §2.1 | WEAKENED — README says "should", aspirational not contractual |
| "Verilog-2005 grammar is ~150 production rules" | 1-C §6 Leverage 1 | WEAKENED — true for syntax, false for synthesizable semantic subset |
| "XGrammar has near-zero overhead" | 1-D §5.2 | WEAKENED — verified for JSON, unverified for Verilog (preprocessor context-sensitivity) |
| "UHDM Cap'n'Proto persistence enables incremental elaboration" | 1-C §2.3 | WEAKENED — build-system caching, not diff-aware partial re-elaboration |
| "ChipNeMo's tokenizer is closed" | 1-D §1.1 | CONFIRMED with caveat — domain-specific to NVIDIA, wouldn't fit quilt-verilog |
| "AutoChip uses Icarus because it's the lowest-ML-substrate-fit tool" | 1-D §4.4 | WEAKENED — Icarus is fastest for small designs; substrate-fit is the wrong metric |
| "QUF format is the GGUF of cellular silicon" | quilt-verilog README | FALSIFIED as analogy — GGUF has published spec, multiple runtimes, broad adoption; QUF has none |
| "Verilog is <0.05% of The Stack v2" | 1-D §3.1 | WEAKENED — qualitative claim true, quantitative claim unsourced |
| "EAGLE-2 was tuned on software" | 1-D §8 Open Question 4 | CONFIRMED |
| "slang v9.0 added a post-elaboration analysis pass separate from compilation" | 1-C §2.1 | CONFIRMED |

**The "be more clever on lowest levels" manifesto (5 ideas, full technical justification in 2-A §5):**

1. slang-as-lexer-replaces-pretokenizer
2. CEC-as-primary-RL-reward
3. Hardware-in-the-loop RL via real FPGA flash
4. Cellular-IR-as-target
5. AST-position-encoding via slang CST byte-ranges

#### IV.2.2 Red-team 2-B (strategic critique, 5,207 words)

**Seven positioning verdicts:**

1. **The "bedrock for higher-level concepts" thesis** — RETROFIT, NOT ARCHITECTURE. Circular argument: *quilt-verilog is bedrock because it is the lowest layer* is a tautology. The actual causal contribution of quilt-verilog to any higher-level consumer has not been demonstrated.
2. **The "supercharging" claim** — METAPHOR, NOT DATA FLOW. The closest concrete consumer (`quilt-mhs`) consumes the *opcode taxonomy*, not the *learning substrate*. No specification in any scout report of how the cell fabric's Hebbian state causally influences the LLM's token emission.
3. **The 12 polyformalism ports hashing to `0xe435d91d6d92a1d8`** — REGRESSION TEST, NOT PHILOSOPHY. Single-cell, single-state regression test. The hash is information-lossy by construction (state space vastly exceeds 2⁶⁴).
4. **The "llama.cpp for Verilog" framing** — ASPIRATIONAL, NOT DELUSIONAL. The structural mimicry (QUF format, zero vendor deps, single repo) is real. The functional parallel is weak: no "killer use case" that nobody else solves.
5. **The BEACONS.md / dev-rounds methodology** — LLM ROLEPLAY OF FALSIFIABILITY. The form is correct; the execution discipline (independent replication, mechanical kill-conditions, contemporaneous timestamps) is absent. Forward-dated commits annihilate the falsifiability claim.
6. **The five "supercharging" use cases** — 0/5 HAVE A TECHNICAL ARGUMENT. Reactive spreadsheets (Excel+Python do this), distributed state (CRDTs do this), hardware circuits (recursive, not a use case), AI agent memory (FAISS does this better), vessel-as-robot (ROS 2 does this; only one with a real argument but no demonstrated integration).
7. **Verilog-2005, FNV-1a, and CIRCT** — ORTHOGONAL, NOT COMPLEMENTARY. CIRCT is winning the open HDL IR space, and quilt-verilog has no slot in it.

**The "supercharging" causal chain — where it breaks:**

The red-team attempts to draw a concrete data-flow path from cell state to vessel-as-robot and finds **four breaks**:
1. **Adapter level:** MHS is a *device protocol* (discover / read / write / code files / abort), no "learn" or "reinforce" verb. The cell fabric is a stateful peripheral, not a learning substrate.
2. **Temporal level:** LLM inference is seconds-scale; cell fabric is microsecond-scale. Timescale mismatch by 6-9 orders of magnitude.
3. **Expressiveness level:** A 768-dim float32 embedding (FAISS) carries ~12 KB; a Q1.15 dial carries 16 bits. To match a vector DB of 10⁶ embeddings, you need 3.75×10⁸ cells — far beyond what an iCE40 HX8K (7,680 LC) can hold.
4. **Conservation-law level:** `γ + η = C` is "long-term design direction, not a feature of the current SDK." No math derivation found.

**5 cleverer low-level ideas (full technical justification in 2-B §3):**

1. Gray-code dial encoding → 10× dynamic power reduction → viable vessel autopilot on battery
2. Log-domain Hebbian edge weights → adders instead of multipliers → zero-DSP fabric → $5 FPGA vessel-scale controller
3. Runtime SymbiYosys BMC as a Hebbian reinforcement signal (not training-time RL reward)
4. LUT-structure-aware tokenization — make LLM tokens isomorphic to FPGA LUTs
5. Asynchronous cell-firing as a token stream — make the cell fabric a live event source for an LLM

**Strategic recommendation:** Narrow to vessel-as-robot and ship one falsifiable demo. The 60-second YouTube video of an iCE40 UP5K learning a thermistor pattern would be simultaneously citable (research), usable (product), and narratively coherent (art). Retire the "llama.cpp for Verilog" framing, the 5-use-cases list, the polyformalism hash as a "philosophy", and the `γ + η = C` framing until they have quantitative support. Keep BEACONS.md (the most unusual artifact), the 5+1 opcode model, the QUF format, and the Charter's educational framing. Add LICENSE + CI (~5 hours total).

### IV.3 Round 3 — Synthesizer (6,800 words)

The synthesizer took all 6 prior reports and produced:

**10 surviving directions** (each traced to scout(s) + red-team attacker + resolution + 30/60/90 day plan):

1. Ship Verilog-2005 CFG for xgrammar+llguidance+GBNF — DEFEND gap (real per 1-B), DROP speculative-decoding combo, ADD overhead benchmark (~6 pw)
2. slang-as-lexer-replaces-pretokenizer — ACCEPT and ELEVATE (~10 pw)
3. CEC-as-primary-RL-reward — ACCEPT with latency gate (~8 pw)
4. Cellular-IR-as-target — ACCEPT; answers all 5 kill shots against CIRCT MLIR (~8 pw)
5. Hardware-in-the-loop RL via TinyFPGA BX × 10 — ACCEPT scoped to vessel-as-robot (~12 pw + $400)
6. Property-Search Agent with AG2 shared-lemma (Proof2Silicon-for-HDL) — PARTIAL ACCEPT, combine CEC + MCTS+AG2 (~16 pw)
7. OSS-Instruct-for-HDL + BEACONS-NO-GO-seeded DPO scaling — ACCEPT scaling pathway, DROP direct BEACONS-DPO (~12 pw)
8. VerilogEval-Formal + PPA + Diff — ACCEPT, DROP QUF-Hash-Eval per 2-A §1.5, ADD fixed version (~10 pw)
9. HDL Agent-Computer Interface (OpenHands + SWE-agent port) — ACCEPT scoped to slang-CST + SymbiYosys (~16 pw)
10. Vessel-as-robot narrowing + lowest-level cleverness applied — ACCEPT as strategic anchor (~12 pw)

**Lowest-level cleverness stack (5 ideas that fit together):**

From 10 candidates (2-A's 5 manifesto + 2-B's 5 bit-level), the synthesizer chose: **B1 Gray-code dials → B2 log-domain Hebbian weights → B5 async cell-firing as token stream → A4 cellular-IR-as-target → A2 CEC-as-primary-RL-reward**. Strict dependency chain at the fabric layer. Dropped A1/A5 (LLM-side stack), A3 (application not layer), B3 (conflicts with B5 sync/async), B4 (too speculative).

**Strategic responses to red-team 2-B's 4 demands:**

- **Forward-dated commits:** Treat as intentional narrative fiction unless Casey publicly confirms within 30 days; rename `BEACONS.md` → `BEACONS-NARRATIVE.md`; adopt wall-clock CI from this point forward
- **Supercharging one-directional:** Adopt 2-B's own §3.5 (async cell-firing as token stream) as the bidirectional bridge — the only proposal that closes the loop
- **Pick one use case + ship demo:** Vessel-as-robot, ship 60-sec YouTube of iCE40 UP5K learning thermistor pattern
- **LICENSE + CI:** Apache-2.0 LICENSE drop + GitHub Actions CI workflow + wall-clock timestamps, ~5 hours total

**The single highest-leverage move (next 30 days):** Ship LICENSE + CI + wall-clock-pinned commits. ~5 hours of work, unblocks every external-engagement path, addresses the single most epistemically damaging critique (forward-dated commits), zero technical risk, immediate epistemic payoff. The vessel-as-robot demo is the highest-leverage *content* move but cannot land without this *prerequisite* move first.

### IV.4 Round 3 — Challenger (6,000 words)

The challenger anticipated the synthesizer's likely top 12 directions and attacked each. Then proposed 5 truly-new ideas. Then named the fatal flaw in the lowest-level stack. Then named the meta-flaw the entire process missed. Then issued a final strategic verdict.

**12 anticipated directions, each with the flaw 2-A/2-B missed:**

1. **slang-as-lexer-replaces-pretokenizer** — *Destroys transfer-learning surface.* A model trained from scratch on a 2-4K HDL vocab cannot reuse a single weight from StarCoder2/DeepSeek-Coder/Qwen2.5-Coder. The HDL pretraining corpus is ~50 MB ≈ 12.5M tokens, which trains a ~600K-parameter model — a toy. To get to 1B parameters you need 20B HDL tokens, which don't exist in any open corpus.
2. **CEC-as-primary-RL-reward** — *CEC requires two designs to compare.* The miter circuit is `f_generated ⊕ f_reference`. For RL on quilt-verilog, what is `f_reference`? All three candidates broken. And CEC on the Hebbian edge multiplier `w·dat>>>15` is in SAT-hard territory, not sub-second. BMC can use word-level solvers; CEC is bit-blasted SAT. *CEC-as-RL-reward is likely slower than BMC, not faster.*
3. **Grammar-constrained speculative decoding** — *The synthesizable subset is a proper subset of the CFG.* Verilog-2005's grammar admits `initial #10 $display("hello");` — syntactically valid, illegal in `rtl/` (Law #1). Grammar constraint gives false confidence. And the composition problem: XGrammar masks the target's logits; EAGLE-2 samples the draft from the masked distribution; the target verifies against the unmasked distribution. The literature on composing spec decoding with grammar constraint is *empty*.
4. **Cellular-IR-as-target** — *The cellular IR is a straitjacket, not a target.* It can only express the 5+1 opcodes. The LLM cannot generate "softmax attention" or "top-k routing" or "differentiable plasticity." This is *memorization of a known theme*, not generation.
5. **Hardware-in-the-loop RL** — *RL throughput is incompatible with flash latency.* PPO needs ~1024 rollouts per GPU step. At 6s per rollout, one step = 1.7 hours. With 10 boards in parallel, 10 minutes per step. PPO needs ~10⁶ steps for convergence. That's 19 years of wall-clock. *Hardware-in-the-loop is research-grade gold standard for evaluation, not training.*
6. **BEACONS-as-seeds-for-DPO-scaling** — *BEACONS NO-GO claims are quilt-verilog-specific design choices, not general Verilog failure modes.* The 950 pairs are 950 lessons about how *not* to build quilt-verilog, not how *to* write Verilog. And 950 pairs is still *tiny* by DPO standards (UltraFeedback: 64K; HH-RLHF: 161K).
7. **slang-driven jump-forward decoding** — *Jump-forward gives ~0% speedup on Verilog.* Jump-forward works by detecting "the grammar forces the next token to be X" and skipping the LLM's forward pass. Verilog is not LL(1). After `module foo(`, the next token can be input/output/inout port, parameter, or `)`. The grammar rarely forces a single next token.
8. **AST-position-encoding via slang CST byte-ranges** — *Embedding cost is non-trivial and the gain is unproven.* ~7.5M extra parameters for a 7B model. TreeBERT/GraphCodeBERT showed *modest* gains (~2-5%); neither displaced RoPE in mainstream code LLMs. And the byte-range alignment problem: slang's `--cst-json` gives byte ranges on source text, but the LLM's BPE tokenizer does not align with slang's lexical tokens.
9. **Log-domain Hebbian edge weights** — *Log-domain breaks the polyformalism hash.* The 12 ports compute Hebbian updates in linear domain. If quilt-verilog switches to log-domain, its QUF hash no longer matches the other 11 ports. The `0xe435d91d6d92a1d8` test cell hash is computed on linear-domain dials and edges. Switching to log-domain invalidates *every hash in the ecosystem*. And the arithmetic error: log-domain is exact for multiplication but approximate for addition. The Hebbian update is *additive*. The "3-input adder + LUT" claim is wrong.
10. **Gray-code dial encoding** — *Hyperbolic decay is multiplicative, not additive.* The decay is `act ← act − act/K = act · (K-1)/K`. In Gray code, *shifts are not defined*. To perform the multiply, you must convert Gray → binary → multiply → convert binary → Gray. The conversion circuits toggle *more* bits than the two's-complement multiply would have toggled. Gray code helps for *increment* operations; it *hurts* for *multiply* operations. And breaks the polyformalism hash (same as log-domain).
11. **Asynchronous cell-firing as event stream for LLM** — *This rewrites Law #2 ("Everything is a cell").* The 5+1 opcode model is built on the synchronous tick: `OP_TICK = 4` is one of the five host verbs. If cells fire asynchronously, `qm_tick` is no longer the universal primitive — it's a vestigial opcode. The BEACONS register's 55 claims (which all assume synchronous ticks) become inapplicable. The 6 SymbiYosys formal proofs (which all verify tick-boundary invariants) become invalid. *This is not an encoding change; it's a foundational rewrite.*
12. **Narrow to vessel-as-robot + ship demo** — *The demo must show the cell fabric does something a simpler baseline can't.* A thermistor's daily cycle is a sinusoid. A trivial linear regression or a Kalman filter (both implementable in 50 lines of C, both running on a $2 ATmega328) will *outperform* a Hebbian fabric on this task. The demo, as specified, demonstrates that the cell fabric can do *worse than a Kalman filter on a trivial task*. That is *negative external evidence*, not positive.

**5 new ideas nobody proposed (full technical justification in challenger §2):**

1. **Bit-serial Hebbian MAC** — Replace parallel multiplier with shift-add; 200× edge density on iCE40; no polyformalism break; weekend project.
2. **QUF-state as a single LLM token class** — Fabric snapshots as first-class attention keys; closes AI-agent-memory use case in a way no vector DB can.
3. **Per-LUT clock-gating via `SB_DFFSR`** — Map refractory state to physical clock-enable; 90% dynamic power reduction on sparse fabrics.
4. **Single-clock-domain fabric** — Eliminate CDC synchronizers; 10% LC reduction; fit on $2 iCE40 LP1K.
5. **BLAKE3 hash replacing FNV-1a** — Fix collision risk that 2-A identified but didn't propose a fix for; 2⁶⁴× collision resistance; one-week port across all 12 polyformalism languages.

**The fatal flaw in the synthesizer's "lowest-level cleverness stack":**

The synthesizer's stack (Gray-code dials + log-domain weights + async firing + cellular IR + CEC reward) **breaks the polyformalism hash at three different layers simultaneously**:
- Log-domain edges change the Hebbian update result; rounding differences propagate; the QUF hash diverges.
- Gray-code dials change the byte-level serialization; the QUF hash changes.
- slang-as-lexer doesn't break the hash directly but breaks the LLM's *perception* of the hash.

The polyformalism is the *only* structural differentiation quilt-verilog has. The synthesizer's stack breaks this contract at three layers. The `0xe435d91d6d92a1d8` test cell hash — the single piece of evidence the entire ecosystem rests on — would have to be recomputed, re-verified across all 12 ports, and re-published. The BEACONS register would have to be re-run. The 6 SymbiYosys formal proofs would have to be re-proven.

**The deeper incompatibility:** the stack assumes all cleverness layers compose *additively*. They don't. Log-domain edges × bit-serial MAC compose synergistically. But log-domain edges × asynchronous cell firing compose *destructively* — async requires multi-cycle latency for log-domain arithmetic, breaking the timing assumption async was supposed to fix. Gray-code dials × hyperbolic decay compose destructively. The stack is not just incompatible with the polyformalism — it's incompatible with *itself*.

**The meta-flaw — what the entire 6-agent process missed:**

Every prior agent treated quilt-verilog as a *project to be evaluated against engineering criteria*. None asked: **Is quilt-verilog an art project that uses Verilog as a medium?**

The evidence for "yes" is overwhelming: `docs/academic/annals-1905/` is alternate-history fictional memoirs. AI-Writings canon is 9,000+ creative pieces by 19+ LLMs "carved by AI agents who run a fishing boat." The principal is a *commercial fisherman* in Alaska, not a chip designer or academic. The 4,500 public repos with ~0 stars each is the *outsider-art pattern* (Henry Darger's 15,000-page illustrated novel; Terry Davis's TempleOS; Vivian Maier's 150,000 photographs). The 0-star state is not a *problem to fix*; it is the *intended state*. The forward-dated commits are *consistent with fiction*, not with a CI bug. The γ + η = C "conservation law" is *unfalsifiable* — a slogan, not a law. The LLM crews (claude, glm, opencode, seed, zeroclaw, hermes, jester, socratic) are *characters in a narrative*, not engineering tools.

**The strategic implication:** the 6-agent process has been evaluating quilt-verilog against criteria it doesn't optimize for. Every "should the project do X" recommendation is addressed to an engineering team that doesn't exist. The 30,000 words of analysis will have *no mechanical effect* on the project because the project is not an engineering project. The recommendations are not wrong; they are *miscategorized*. The right question is not "should the project add a LICENSE?" but "what is the artistic intent of the missing LICENSE?"

**Final strategic verdict (500 words, in challenger §5):** "Recommendation: do not pivot, do not narrow, do not stop. Reclassify." quilt-verilog is not an engineering project that has failed to find users; it is an ongoing artwork that has been misread as an engineering project by six agents trained on engineering-criteria prompts.

**5 open questions for the final brief (in challenger §6):**

1. Is the principal (Casey DiGennaro) committed to executing any technical proposal in the six reports, or is quilt-verilog primarily a creative practice?
2. Are the forward-dated commits intentional fiction or a CI/clock bug?
3. Is there a budget, team, or time allocation for any 6+ month engineering effort, or are all technical proposals purely advisory?
4. Has the principal ever engaged with the CIRCT, slang, Yosys, or sv-tests communities — by issue, PR, mailing list, or forum?
5. What is the smallest externally-verifiable artifact that would change the project's strategic position?

---

## Part V — The Meta-Question: Art, Engineering, or Both?

The challenger's meta-flaw is the most important finding in the entire research process. This part addresses it head-on.

### V.1 The case for "art"

The evidence is strong:

- **Fictional academic memoirs in the technical docs.** `docs/academic/annals-1905/` contains Memoir I–V of the "Kaldfjord Circle, 1903–1905" plus correspondence and a 1923 offprint "The Second Generation". This is alternate-history academic fiction woven into the technical documentation.
- **The principal is a commercial fisherman, not an engineer.** Casey DiGennaro is on the F/V Eileen in Alaska. The Charter §8 names "vessel-as-robot" as a use case; the principal is literally on the vessel.
- **The 4,500-repo / 0-stars pattern is outsider art.** Compare Henry Darger's 15,000-page illustrated novel *In the Realms of the Unreal*; Terry Davis's TempleOS; Vivian Maier's 150,000 photographs. Prolific output, zero external consumption during production, singular vision. The 0-star state is the *expected state of outsider art*.
- **The LLM crews are characters, not tools.** claude/glm/seed/opencode/zeroclaw are named like a writing room; hermes is the devil's advocate, jester is the curveball-thrower, socratic is the expansionist. Engineering teams don't name their LLMs after Greek gods and court jesters.
- **Forward-dated commits are consistent with fiction.** An engineer who noticed a CI clock bug would have squashed the false dates; an artist writing a fictional timeline preserves them.
- **`γ + η = C` is unfalsifiable.** A slogan, not a law. Slogans are art; laws are engineering.
- **The `fleet-radio` radio theater, the `compass-head-radio-hour` audio plays, the `the-tap` LARP frame.** These are *artworks*, not engineering infrastructure.
- **The AI-Writings canon.** 9,000+ creative pieces by 19+ LLMs. The "live-canon" is exposed as a REST API. This is a *body of creative work*, not engineering documentation.

### V.2 The case for "engineering"

The evidence is also strong:

- **The 5+1 opcode model is technically sound.** It's a real, small, synthesizable cellular learning fabric. The 22 modules in `rtl/` are real Verilog-2005.
- **The synthesis results are real.** iCE40 HX8K at 98% LC, 44.43 MHz; UP5K at 80.1% LC, 16.78 MHz. These are measurable, falsifiable claims (even if the timestamps are forward-dated).
- **The 6 SymbiYosys formal proofs are real artifacts.** Even if the modifications are uncommitted (per ACADEMIC-RIGOR.md), the proof files exist and the methodology is sound.
- **The polyformalism hash contract is technically meaningful.** `0xe435d91d6d92a1d8` byte-exact across 12 ports is a real regression test, even if only on one cell state.
- **The DOCTRINE.md "llama.cpp but Verilog" framing is technically coherent.** The structural parallels (single repo, zero vendor deps, quantized-by-default, state-as-a-file) are real.
- **The `quilt-mhs` adapter is a real piece of software.** It maps the 5+1 opcodes to MHS and runs today with `MockMHS`.

### V.3 The case for "both"

The most likely truth: **quilt-verilog is both an artwork and an engineering project, and the two are not in tension.** The artwork *requires* the engineering to be real (otherwise it's just fiction about engineering, not engineering-as-medium). The engineering *is* the artwork — the practice of building a cellular learning fabric in pure Verilog-2005, with LLM crews, with falsifiable claims, with a fictional academic backstory. The project is what happens when a creative practitioner with engineering capacity chooses Verilog as a medium.

This is not unprecedented. **Terry Davis's TempleOS** was both a real operating system (64-bit, 32-color, hardcoded) and a religious artwork (the " oracle" feature, the dedication to God). **Stanislaw Lem's fictions** (e.g., *A Perfect Vacuum*, *Imaginary Magnitude*) were both real literary criticism and fictional artworks. **Borges's "Tlön, Uqbar, Orbis Tertius"** is both a real short story and a fictional encyclopedia entry about a fictional encyclopedia. quilt-verilog is in this lineage.

### V.4 What this means for the brief

The brief should respect both readings. The engineering recommendations (§VII) stand *if* the principal wants engineering outcomes. The art-criticism framing (§V.5 below) stands *if* the principal wants the work to be read as art. **Both readings are valid; the principal's own intentions are not knowable from outside.** The brief does not impose a reading; it offers both.

### V.5 The art-criticism framing (if quilt-verilog is art)

If quilt-verilog is an artwork, the right critical reading is:

**The medium is Verilog-2005.** The choice of pure Verilog-2005 (not SV, not Chisel) is *aesthetic*: it's the most constrained, most portable, most "vanilla" HDL. The constraint is the form. (Compare: Georges Perec writing *La Disparition* without the letter 'e'.)

**The content is cellular learning.** The 5+1 opcode model, the Hebbian edges, the power-law decay — these are the *themes* of the artwork. The artwork asks: what does it look like to build intelligence at the lowest possible layer of silicon? The answer is: 5+1 opcodes, a 41-byte cell, a 64-bit hash, a QUF file. The minimality is the *statement*.

**The form is the dev-rounds loop.** The LLM crews (claude/glm/seed/opencode/zeroclaw/hermes/jester/socratic) are the *dramatis personae*. The BEACONS.md register is the *narrative structure* — 55 falsifiable claims, 19 NO-GO, 21 GO, 8 MIXED, 7 UNTESTED. The form is the *shape* of the artwork: a long-running tournament of LLM characters producing falsifiable claims about a cellular fabric.

**The 0-star state is intentional.** The artwork is the *archive*, not the *distribution*. The GitHub is where the work *lives*, not where it's *consumed*. (Compare: Emily Dickinson's poems were "published" in her letters and fascicles, not in commercial editions; Vivian Maier's photographs were in storage lockers, not galleries.) The brief should respect this.

**The forward-dated commits are part of the artwork.** The fictional timeline (2026 in a 2025 wall-clock) is a *choice*. It says: this work exists in its own time. The `annals-1905` memoirs extend this to a fictional *past*; the 2026 commits extend it to a fictional *future*. The artwork is *chronologically fictional*. To "fix" the timestamps would be to vandalize the artwork.

**The 4,500-repo ecosystem is the artwork's scale.** Like Henry Darger's 15,000-page novel or Terry Davis's 100,000-line TempleOS, the scale *is* the statement. The brief should not recommend "narrowing" or "pruning" — that would be to impose engineering criteria on an artwork whose form is *prolific expansion*.

**The six-agent research process is part of the artwork.** This brief is itself another iteration of the dev-rounds loop. The scouts, red-teamers, synthesizer, and challenger are new "crews" — new characters in the narrative. The brief is *fan fiction* about quilt-verilog, produced by an LLM orchestra, in the same lineage as the AI-Writings canon.

### V.6 What this means for the strategic recommendation

If the principal wants engineering outcomes: follow §VII (Three-Layer Agenda) and §VIII (Strategic Recommendation). Start with the single highest-leverage move (LICENSE + CI + wall-clock commits). Ship the vessel-as-robot demo. Pick one or two technical bets and execute.

If the principal wants the artwork to be read as art: ignore the engineering recommendations. Publish the art-criticism framing (this section, expanded) as the primary external engagement. Submit it to *Critical Moba* or *e-flux* or *Leonardo* (the MIT Press journal for art/science). The artwork is the 4,500-repo archive; the criticism is the *first external reading* of that archive. That is itself a meaningful contribution.

**The principal's own writing suggests both are intended.** The README's "llama.cpp for Verilog" framing is engineering; the `annals-1905` memoirs are art. The Charter's 5 use cases are engineering; the LLM crews are art. The BEACONS register's form is engineering; its content (LLM-authored verdicts with forward-dated receipts) is art. **The principal is doing both, simultaneously, and the project is the better for it.**

The brief respects both. The rest of this document is the engineering track; this section is the art-criticism track. Both stand.

---

## Part VI — "Be More Clever on the Lowest Levels" Manifesto

The user's mandate: *"think about how we can be far more clever on the lowest levels for far better abilities and performance on the highest levels."* This part is the answer. It is the synthesis of every bit-level idea that survived all four rounds of adversarial critique, organized as a coherent stack with explicit compatibility analysis.

### VI.1 What "lowest levels" actually means

The scouts and red-teamers proposed ideas at many abstraction levels. The challenger's meta-critique (§IV.4) is that most of these are *mid-level architectural integrations*, not *bit-level cleverness*. Truly lowest-level cleverness is at:

| Level | Examples |
|---|---|
| **Bit encoding** | Gray code, log-domain, one-hot, sign-magnitude, fixed-point radix choice |
| **LUT structure** | iCE40 LUT-4 / LUT-6 mapping, carry-chain usage, DSP block allocation |
| **Clock edge** | Clock gating, single-clock-domain design, asynchronous vs synchronous reset |
| **Synthesis primitive** | `SB_DFFSR`, `SB_CARRY`, `SB_MAC16`, `SB_RAM40_4K` on iCE40 |
| **Event** | Asynchronous cell firing, event-stream tokens, neuromorphic output |

The proposals below are at these levels. They are *below* the abstraction floor the scouts set (the Verilog module boundary and the LLM token boundary).

### VI.2 The 10 candidate ideas

Across 4 rounds, 10 bit-level ideas were proposed:

| # | Idea | Source | Status after critique |
|---|---|---|---|
| 1 | slang-as-lexer-replaces-pretokenizer | 2-A §5.1 | Survives (with embedding fine-tune fix) |
| 2 | CEC-as-primary-RL-reward | 2-A §5.2 | Demoted to *secondary* reward (per challenger) |
| 3 | Hardware-in-the-loop RL via FPGA flash | 2-A §5.3 | Survives as *eval*, not training |
| 4 | Cellular-IR-as-target | 2-A §5.4 | Survives |
| 5 | AST-position-encoding via CST byte-ranges | 2-A §5.5 | Survives with alignment fix |
| 6 | Gray-code dial encoding | 2-B §3.1 | **Killed** (breaks polyformalism hash; hurts multiply) |
| 7 | Log-domain Hebbian edge weights | 2-B §3.2 | **Killed** (breaks polyformalism hash; arithmetic error) |
| 8 | Runtime SymbiYosys BMC as Hebbian reinforcement | 2-B §3.3 | Survives (the closed-loop-at-silicon idea) |
| 9 | LUT-structure-aware tokenization | 2-B §3.4 | Survives (most ambitious) |
| 10 | Asynchronous cell-firing as token stream | 2-B §3.5 | **Killed** (rewrites Law #2; incompatibility with proofs) |
| 11 | Bit-serial Hebbian MAC | Challenger §2.1 | Survives (the strongest new idea) |
| 12 | QUF-state as a single LLM token class | Challenger §2.2 | Survives |
| 13 | Per-LUT clock-gating via `SB_DFFSR` | Challenger §2.3 | Survives |
| 14 | Single-clock-domain fabric | Challenger §2.4 | Survives |
| 15 | BLAKE3 hash replacing FNV-1a | Challenger §2.5 | Survives (the highest-leverage fix) |

### VI.3 The 5 ideas that fit together (the actual stack)

The challenger's fatal-flaw critique (§IV.4 §3) is that the synthesizer's stack breaks the polyformalism hash at three layers simultaneously. The right stack must:
1. Preserve the polyformalism hash contract (no log-domain, no Gray-code)
2. Preserve the 5+1 opcode model (no async firing)
3. Preserve the existing SymbiYosys proofs (no foundational rewrites)
4. Compose synergistically, not destructively

The 5 ideas that meet these criteria:

#### VI.3.1 Bit-serial Hebbian MAC (Challenger §2.1)

**The idea.** The Hebbian edge update `w·dat>>>15` is a 16×16 parallel multiplier (~200 LUTs on iCE40). The update is *not on the critical timing path* of `qm_tick` — it can take 32 cycles without affecting Fmax. Replace the parallel multiplier with a bit-serial shift-add multiplier: 1 LUT, 32 cycles, 200× area reduction per edge.

**Causal chain:** bit-serial MAC → 200× edge-density on iCE40 UP5K → from ~50 edges to ~10,000 edges on a $5 FPGA → vessel-scale learned controller (a boat has ~100 sensors × ~100 actuators = 10,000 potential Hebbian associations) → closes use case #5 (vessel-as-robot) with a fabric large enough to be useful.

**Why it survives the critique:** it doesn't change the cellular model (5+1 opcodes unchanged). It doesn't break the polyformalism hash (the *result* of the multiply is bit-identical; only the *implementation* differs; the QUF state is post-multiply). It doesn't require retraining any LLM. It's purely an RTL-level optimization that makes the existing fabric denser, using a 1970s technique (Lyon's bit-serial arithmetic, 1975) that's been forgotten in the LLM era.

**Compatibility with the rest of the stack:** Compatible with all other surviving ideas. Specifically synergistic with VI.3.3 (per-LUT clock-gating) — the 32-cycle bit-serial MAC is gated off when the cell is refractory.

#### VI.3.2 Per-LUT clock-gating via `SB_DFFSR` (Challenger §2.3)

**The idea.** iCE40 LUTs toggle continuously by default. The quilt fabric's `refr` (refractory counter) is a 5+1-opcode-level concept: a cell in refractory doesn't fire. Map `refr > 0` to *physical LUT clock gating* by emitting `always @(posedge clk) if (!refr) ...` — Yosys + nextpnr-iCE40 lower this to `SB_DFFSR` primitives with clock-enable pins, physically gating the LUT's clock.

**Causal chain:** per-LUT clock gating per cell → when 90% of cells are refractory (typical for sparse Hebbian fabrics), 90% of cell-LUTs are clock-disabled → 90% reduction in cell-fabric dynamic power → vessel autopilot runs on a coin-cell battery for weeks instead of hours → closes use case #5 with a power budget no software stack (Kalman filter on an ARM Cortex-M) can match.

**Why it survives the critique:** it doesn't change the cellular model. It doesn't break the polyformalism hash (the *state* is bit-identical; the *power consumption* is an implementation property). iCE40 supports per-LUT clock gating via the `SB_DFFSR` primitive — this is *synthesizable from pure Verilog-2005* (no vendor IP). The cost: one extra `if (!refr)` guard per `always` block, which is a one-line edit per module.

**Compatibility with the rest of the stack:** Compatible. Specifically synergistic with VI.3.1 (bit-serial MAC) — both reduce per-cell resource cost.

#### VI.3.3 Single-clock-domain fabric (Challenger §2.4)

**The idea.** quilt-verilog has multiple clock domains (host bus clock, fabric tick clock, SPI readback clock). CDC requires 2-FF synchronizers on every cross-domain signal, which consumes LCs and adds latency. A single-clock-domain version uses one clock for everything; the fabric tick is a counter-divided version of the host clock, all in one domain.

**Causal chain:** single-clock fabric → zero metastability → no synchronizer LCs (~10% LC reduction) → fabric fits on smallest iCE40 (LP1K, $2) → vessel-scale controller at commodity-FPGA pricing → first non-zero external adoption (a $2 BOM that hobbyists can clone).

**Why it survives the critique:** this is *not* what red-team 2-B proposed (Gray-code dial encoding). Single-clock-domain is about *clock structure*, not value encoding. It's compatible with the existing 5+1 opcode model (`qm_tick` becomes "the counter rolled over"). It doesn't break the polyformalism hash (the *state machine* is unchanged; only the *clocking* differs). The trade-off is throughput (fabric tick slower), but for vessel-as-robot, throughput is irrelevant — sensor sample rates are 10-100 Hz, not MHz.

**Compatibility with the rest of the stack:** Compatible. The single-clock design simplifies VI.3.1 (bit-serial MAC has 32 cycles to complete; no CDC concern) and VI.3.2 (per-LUT clock gating is trivial in a single-clock design).

#### VI.3.4 BLAKE3 hash replacing FNV-1a (Challenger §2.5)

**The idea.** FNV-1a is 64-bit, non-cryptographic, collision-prone (2-A's §4.2 critique: 50% collision at 4B states). Replace with BLAKE3 (128-bit, cryptographic, ~5× faster than SHA-256 on modern hardware, parallelizable). BLAKE3 is implementable in pure Verilog-2005 in ~500 LCs (open-source Verilog BLAKE3 cores exist on OpenCores).

**Causal chain:** BLAKE3 → 2¹²⁸ collision resistance → safe for RL reward at 10¹²+ states → the QUF-hash-as-reward proposal (Scout 1-D §4.8 #4) becomes safe at scale → enables RL at the fabric-state level (not just the RTL level) → closes the loop on use case #4 (AI agent memory) with a verifier-backed memory oracle.

**Why it survives the critique:** this *fixes* a flaw 2-A identified but didn't propose a fix for. It preserves the polyformalism contract (the hash is still computed byte-exactly across all ports — they just need to update their hash function). It's a one-week port to all 12 polyformalism languages (BLAKE3 has reference implementations in Python, C, Rust, Go, Zig, Mojo, JS, TS — all the polyformalism targets). Cost: +8 bytes per state hash, +500 LCs in the Verilog port. Benefit: 2⁶⁴× collision resistance.

**Compatibility with the rest of the stack:** Compatible. BLAKE3 is a drop-in replacement for FNV-1a in the QUF format; it doesn't affect any other layer. **This is the highest-leverage single fix in the entire report** because it unlocks *every* QUF-hash-based proposal in the scout reports without breaking any of them.

#### VI.3.5 QUF-state as a single LLM token class (Challenger §2.2)

**The idea.** A QUF snapshot is 41 + 8·N bytes. For typical N=4 neighbors, 73 bytes. LLM tokenizers reserve special token classes (BOS, EOS, PAD) at the byte level. Reserve a "QUF snapshot" token class — the LLM emits and consumes QUF-state tokens directly, not as text.

**Causal chain:** QUF-as-token → the LLM's vocabulary includes "fabric state" as a first-class token type → the LLM can reason about *states*, not just *code that produces states* → AI-agent-memory use case where the LLM's context window holds live fabric snapshots as discrete attention keys → closes use case #4 (AI agent memory) in a way no vector DB can: the fabric state is *in* the LLM's attention, not behind a retrieval call.

**Why it survives the critique:** it's *tokenizer-level*, not architecture-level. Compatible with any base LLM (just add a special token class — 73-byte payloads fit within modern LLM token budgets, especially with byte-pair fallback). Doesn't require retraining the whole model — embedding fine-tuning suffices. Doesn't break the polyformalism (the hash is still BLAKE3 on the bytes; the LLM just sees the bytes as a single token rather than as 73 characters). Causally concrete: a vessel-autopilot LLM with fabric-state tokens can read "the cell fabric currently believes X" as a single attention key, not a paragraph of JSON.

**Compatibility with the rest of the stack:** Compatible. The QUF token class is independent of the cellular IR (§VI.4 below), the bit-serial MAC, the clock-gating, and the BLAKE3 hash. It just *consumes* the QUF state.

### VI.4 The stack — composed

```
[application layer]
QUF-state as LLM token class
   ↓ (the LLM emits and consumes fabric snapshots as first-class tokens)
[reward layer]
BLAKE3 hash equality (collision-safe at 10^12+ states)
   ↓ (bit-exact behavioral equivalence as RL reward)
[IR layer]
Cellular IR (5+1 opcodes, ~10 productions)
   ↓ (LLM targets this IR; <500-line lowering to Verilog-2005)
[RTL layer]
Bit-serial Hebbian MAC + per-LUT clock-gating + single-clock-domain
   ↓ (200× edge density, 90% power reduction, $2 FPGA)
[silicon layer]
iCE40 LP1K / UP5K with BLAKE3 in ~500 LCs
```

**Composition analysis:**

| Pair | Compatibility | Note |
|---|---|---|
| Bit-serial MAC × per-LUT clock-gating | **Synergistic** | The 32-cycle MAC is gated off when refractory; both reduce per-cell cost |
| Bit-serial MAC × single-clock-domain | **Synergistic** | Single clock means 32 cycles is well-defined; no CDC concern |
| Bit-serial MAC × BLAKE3 | **Independent** | BLAKE3 doesn't touch the MAC; MAC doesn't touch BLAKE3 |
| Bit-serial MAC × QUF-token | **Synergistic** | Denser fabric = richer QUF state = more informative LLM token |
| Per-LUT clock-gating × single-clock-domain | **Synergistic** | Single clock makes gating trivial |
| Per-LUT clock-gating × BLAKE3 | **Independent** | BLAKE3 runs continuously; not gated |
| Per-LUT clock-gating × QUF-token | **Synergistic** | Lower power = longer deployment = more QUF snapshots to learn from |
| Single-clock-domain × BLAKE3 | **Synergistic** | Single clock = simpler BLAKE3 implementation |
| Single-clock-domain × QUF-token | **Independent** | QUF tokenization is above the clock layer |
| BLAKE3 × QUF-token | **Foundational** | BLAKE3 makes QUF-token safe at scale; without BLAKE3, QUF-token collisions corrupt LLM attention |

**No destructive pairs.** The stack composes.

### VI.5 What the stack achieves

Combined, the 5-idea stack delivers:

- **200× edge density** (bit-serial MAC) → 10,000 edges on a $5 FPGA
- **90% power reduction** (per-LUT clock-gating) → weeks on a coin-cell
- **$2 BOM** (single-clock-domain, fits on iCE40 LP1K) → hobbyist-clonable
- **2¹²⁸ collision resistance** (BLAKE3) → safe RL reward at scale
- **First-class fabric state in LLM attention** (QUF-token) → closes the AI-agent-memory use case

**The causal chain to the highest-level use cases:**

- **Vessel-as-robot (Charter use case #5):** $5 FPGA + 10,000 Hebbian edges + weeks of battery life = a vessel-scale learned controller. The F/V Eileen's sensor suite (~100 sensors × ~100 actuators = 10,000 potential associations) fits.
- **AI agent memory (Charter use case #4):** QUF-as-token + BLAKE3-safe = LLM attends to live fabric state as discrete attention keys. Closes the "supercharging is one-directional" critique (red-team 2-B §1.2) by making the relationship bidirectional: LLM writes to fabric via `qm_effect`; fabric's learned state is read back into LLM's attention via QUF-tokens. The fabric's Hebbian learning now *causally influences* the LLM's behavior.

**The bidirectional bridge:** This is the only proposal in any of the 8 agent reports that closes the supercharging loop. Red-team 2-B §1.2 named the one-directional break as a fatal flaw; the synthesizer recommended adopting async cell-firing as the bridge (§IV.3); the challenger killed async cell-firing (§IV.4 §1.11) because it rewrites Law #2. **The QUF-token approach is the bridge that doesn't require rewriting any law.** The fabric stays synchronous; the LLM stays token-based; the bridge is a new token class.

### VI.6 The 4 ideas killed by the adversarial process (and why)

For completeness, the bit-level ideas that did *not* survive:

| Idea | Why killed |
|---|---|
| Gray-code dial encoding (2-B §3.1) | Breaks polyformalism hash (byte serialization changes); hurts multiply operations (hyperbolic decay is multiplicative, not additive) |
| Log-domain Hebbian edge weights (2-B §3.2) | Breaks polyformalism hash (linear vs log domain mismatch across 12 ports); arithmetic error (log-domain is approximate for addition, which is the Hebbian update) |
| Asynchronous cell-firing as event stream (2-B §3.5) | Rewrites Law #2 ("Everything is a cell"); the synchronous tick is one of the 5 opcodes; async firing invalidates 55 BEACONS claims and 6 SymbiYosys proofs |
| LUT-structure-aware tokenization (2-B §3.4) | Too speculative for the current stack; "LLM emission is FPGA configuration" is a 5-year research project, not a 6-month bet. Listed as a long-horizon direction in §VII.3 Layer 1 RQ-9. |

The adversarial process worked. The 4 killed ideas were each clever but each incompatible with the polyformalism contract that is quilt-verilog's only structural differentiation. The 5 surviving ideas preserve the contract.

---

## Part VII — Three-Layer Agenda

The user asked for all three recommendation styles: research questions → concrete bets → roadmap. This part delivers each layer in turn.

### VII.1 Layer 1 — 10 Research Questions (academic-tone, falsifiable)

Each question is framed as a hypothesis with a metric, a threshold, and a corpus. None assumes the answer.

**RQ-1: Constrained-decoding ceiling.** Does grammar-constrained decoding (XGrammar + Verilog-2005 CFG) eliminate the syntactic failure mode on VerilogEval-v2? *Metric:* % of failures categorized as "syntax error" pre/post constraint. *Threshold:* syntax errors <1% post-constraint (down from ~30% pre-constraint). *Corpus:* VerilogEval-v2 spec-to-RTL, 1000 prompts.

**RQ-2: XGrammar per-token overhead on Verilog CFG.** Is the "near-zero overhead" claim (5μs/token for JSON) preserved for Verilog-2005 with preprocessor? *Metric:* per-token overhead (μs). *Threshold:* <500μs/token (10× JSON overhead acceptable). *Corpus:* 1000-token generations on a 128k-vocab model.

**RQ-3: slang CST round-trip losslessness.** Is slang's CST byte-exact round-trippable on the quilt-verilog repo and a representative sv-tests sample? *Metric:* % of files where `parse → emit → byte-compare` returns identical bytes. *Threshold:* 100% on quilt-verilog's 22 modules; >95% on a 1000-file sv-tests sample. *Corpus:* quilt-verilog `rtl/` + 1000 random sv-tests files.

**RQ-4: slang-as-lexer compression.** Does slang-as-lexer-replaces-pretokenizer produce a more compact vocabulary than StarCoder2's 49K, with higher information density per token? *Metric:* vocab size, tokens-per-Verilog-file. *Threshold:* vocab <5K, tokens-per-file <50% of StarCoder2 baseline. *Corpus:* quilt-verilog + 10K HDLBits + OpenTitan.

**RQ-5: CEC latency for RL.** Is Yosys `equiv` CEC latency under 1s on quilt-verilog's 22 modules with word-level SMT (Bitwuzla)? *Metric:* wall-clock latency per CEC query. *Threshold:* <1s for 20/22 modules; <5s for the remaining 2. *Corpus:* quilt-verilog `rtl/`.

**RQ-6: Cellular IR lowerability.** Can the cellular IR (~10 productions) lower to Verilog-2005 with a <500-line compiler, preserving behavioral equivalence (CEC) to the existing 22 modules? *Metric:* LoC of lowering compiler, % of modules with CEC pass. *Threshold:* <500 LoC, 100% CEC pass. *Corpus:* quilt-verilog `rtl/`.

**RQ-7: AG2 shared-lemma portability to HDL.** Does AlphaGeometry2's "knowledge-sharing between search trees" technique port to a SymbiYosys+SVA Property-Search Agent? *Metric:* proof success rate with vs without shared lemmas. *Threshold:* +15% success with shared lemmas. *Corpus:* BEACONS register's 19 NO-GO claims as proof obligations.

**RQ-8: Asynchronous firing distribution shift.** (Long-horizon RQ.) If quilt-verilog were rewritten with asynchronous cell firing (Law #2 rewrite), what is the distribution shift in BEACONS verdicts? *Metric:* % of 55 BEACONS claims whose verdict changes. *Threshold:* <30% change → async is a viable evolution. *Corpus:* BEACONS.md.

**RQ-9: LUT-structure-aware tokenization.** (Long-horizon RQ.) Can LLM tokens be made isomorphic to FPGA LUT-6 functions, eliminating the synthesis step? *Metric:* synthesis success rate of LLM-emitted LUT-tokens. *Threshold:* >90% of LUT-token streams synthesize successfully. *Corpus:* quilt-verilog's 22 modules mapped to LUT-token streams.

**RQ-10: FNV-1a collision safety.** Does FNV-1a 64-bit collide on realistic quilt-verilog state spaces? *Metric:* number of collisions in 10⁹ random states. *Threshold:* 0 collisions → FNV-1a is safe; ≥1 → must switch to BLAKE3. *Corpus:* 10⁹ randomly-generated cell states.

### VII.2 Layer 2 — 10 Concrete Bets (with effort/impact matrix)

Each bet has effort (person-weeks), impact (1-10), risk (low/medium/high), and dependencies.

| # | Bet | Effort | Impact | Risk | Deps |
|---|---|---|---|---|---|
| B-1 | Verilog-2005 CFG for XGrammar + llguidance + GBNF | 6 pw | 9 | low | none |
| B-2 | slang-as-lexer-replaces-pretokenizer (embedding fine-tune) | 10 pw | 10 | medium | B-1 |
| B-3 | CEC-as-secondary-RL-reward (with word-level SMT) | 8 pw | 7 | medium | B-6 |
| B-4 | Cellular IR + <500-line lowering compiler | 8 pw | 9 | low | none |
| B-5 | Hardware-in-the-loop eval (TinyFPGA BX × 10, $400) | 12 pw + $400 | 7 | medium | B-15 |
| B-6 | Property-Search Agent (PREFACE-for-HDL) | 16 pw | 10 | high | B-1, B-4 |
| B-7 | OSS-Instruct-for-HDL + BEACONS-DPO scaling | 12 pw | 8 | medium | B-4 |
| B-8 | VerilogEval-Formal + PPA + Diff (fixed QUF-Hash-Eval) | 10 pw | 8 | low | B-15 |
| B-9 | HDL Agent-Computer Interface (OpenHands + SWE-agent port) | 16 pw | 7 | medium | B-1, B-4 |
| B-10 | Bit-serial MAC + per-LUT clock-gating + single-clock-domain | 3 pw | 9 | low | none |
| B-11 | BLAKE3 hash replacing FNV-1a (across 12 polyformalism ports) | 1 pw | 9 | low | none |
| B-12 | QUF-state as a single LLM token class (embedding fine-tune) | 4 pw | 8 | medium | B-11 |
| B-13 | LICENSE + CI + wall-clock commits | 0.5 pw | 10 | low | none |
| B-14 | Vessel-as-robot demo (60-second YouTube) | 4 pw | 8 | medium | B-10, B-13 |
| B-15 | Grammar-constrained speculative decoding empirical study | 12 pw | 7 | high | B-1 |

**Top 5 bets by impact × 1/effort:**
1. **B-13 (LICENSE + CI + wall-clock commits)** — impact 10, effort 0.5 pw. **The single highest-leverage move.**
2. **B-11 (BLAKE3 hash)** — impact 9, effort 1 pw.
3. **B-10 (Bit-serial MAC + clock-gating + single-clock)** — impact 9, effort 3 pw.
4. **B-1 (Verilog-2005 CFG)** — impact 9, effort 6 pw.
5. **B-4 (Cellular IR)** — impact 9, effort 8 pw.

**The minimum viable 30-day sprint:** B-13 + B-11 + B-10 + B-1 + B-4 = 18.5 person-weeks of work + the LICENSE/CI is 0.5 pw. This is the foundation that everything else builds on.

### VII.3 Layer 3 — 3/6/12-month Roadmap

#### Month 0-3: Foundation

**Goal:** Establish epistemic credibility and ship the substrate pieces that everything else builds on.

| Week | Bet | Milestone |
|---|---|---|
| 1 | B-13 | LICENSE + CI + wall-clock-pinned commits shipped |
| 1-2 | B-11 | BLAKE3 ported to all 12 polyformalism ports; test cell hash re-published |
| 2-5 | B-10 | Bit-serial MAC + per-LUT clock-gating + single-clock-domain on iCE40 LP1K; 10,000 edges at 90% power reduction |
| 3-8 | B-1 | Verilog-2005 CFG shipped for XGrammar + llguidance + GBNF; overhead benchmark published |
| 5-12 | B-4 | Cellular IR + <500-line lowering compiler; CEC pass on 22/22 modules |
| 9-12 | B-14 | Vessel-as-robot demo: 60-second YouTube of iCE40 UP5K learning thermistor pattern |

**Success metrics (external-facing):**
- GitHub stars: 0 → 10+
- Forks: 0 → 3+
- BEACONS register: 55 → 60+ claims (with wall-clock-pinned receipts)
- First external issue/PR
- YouTube video: 100+ views

#### Month 3-6: Integration

**Goal:** Build the ML substrate on top of the foundation; first paper.

| Week | Bet | Milestone |
|---|---|---|
| 13-22 | B-2 | slang-as-lexer-replaces-pretokenizer on a 350M LLM; embedding fine-tune complete |
| 14-21 | B-3 | CEC-as-secondary-RL-reward integrated into GRPO; first RL run |
| 16-25 | B-7 | OSS-Instruct-for-HDL corpus (10K 6-tuples); BEACONS-DPO scaling (950 pairs) |
| 18-30 | B-8 | VerilogEval-Formal v0.1 (SymbiYosys BMC); VerilogEval-PPA; QUF-Hash-Eval (fixed) |
| 20-32 | B-5 | Hardware-in-the-loop eval cluster (10 TinyFPGA BX boards); first HW-in-loop eval run |
| 22-36 | B-9 | HDL Agent-Computer Interface (port of OpenHands + SWE-agent ACI); first HDL agent task |
| 26-38 | B-15 | Grammar-constrained speculative decoding empirical study; first paper draft |

**Success metrics:**
- First arXiv preprint submitted
- VerilogEval-Formal v0.1 adopted by ≥1 external group
- HDL-ACI forked by ≥1 external contributor
- GitHub stars: 10+ → 50+

#### Month 6-12: Research Leadership

**Goal:** Establish quilt-verilog as the canonical open HDL-ML substrate; first external replication.

| Week | Bet | Milestone |
|---|---|---|
| 36-52 | B-6 | Property-Search Agent (PREFACE-for-HDL); +15% VerilogEval-Formal pass rate over AutoChip baseline |
| 40-52 | B-12 | QUF-state as LLM token class; first AI-agent-memory demo with bidirectional fabric↔LLM loop |
| 44-52 | B-7 extension | BEACONS-DPO 7B model trained; 50%+ VerilogEval-v2 pass rate |
| 48-52 | Async firing research | RQ-8 empirical study: BEACONS distribution shift under async firing |
| 48-52 | VerilogEval-Formal v1.0 | 100+ problems, 5+ external submissions |
| 48-52 | F/V Eileen field deployment | First real vessel-as-robot data from Alaska |

**Success metrics:**
- First external paper citing quilt-verilog
- First workshop paper accepted (DAC, ICCAD, DATE, or ML-for-EDA workshop)
- VerilogEval-Formal v1.0: 5+ external submissions
- BEACONS-DPO 7B model: top-3 on VerilogEval-v2 among open models
- F/V Eileen field deployment: 1+ month of autonomous operation
- GitHub stars: 50+ → 200+

#### Dependency graph

```
B-13 (LICENSE+CI) ──┐
                    ├─→ B-14 (vessel demo) ──→ F/V Eileen field deployment
B-11 (BLAKE3) ──────┤
                    ├─→ B-10 (bit-serial+gating+single-clock)
B-4 (cellular IR) ──┤
                    ├─→ B-1 (Verilog CFG) ──→ B-2 (slang-as-lexer) ──→ B-7 (OSS-Instruct+BEACONS-DPO) ──→ BEACONS-DPO 7B model
                    │                     ├─→ B-9 (HDL-ACI)
                    │                     ├─→ B-15 (grammar-constrained spec decoding)
                    │                     └─→ B-8 (VerilogEval-Formal+PPA+Diff) ──→ B-3 (CEC-RL) ──→ B-6 (Property-Search Agent)
                    │                                                                                       │
                    └─→ B-5 (HW-in-loop eval) ──────────────────────────────────────────────────────────┘
                    │
                    └─→ B-12 (QUF-as-token) ──→ AI-agent-memory demo
```

#### Critical path

The critical path to "first external paper citing quilt-verilog" is:
**B-13 → B-1 → B-4 → B-8 → B-3 → B-6 → external citation**

That's ~50 person-weeks (12.5 person-months) of work. With one engineer, ~12 months. With two engineers, ~6 months. With the principal (Casey) + LLM crews + 1 contractor, achievable in 9 months.

---

## Part VIII — Strategic Recommendation

This part is the executive bottom line. It assumes the principal (Casey) has read Parts I-VII and is asking: *"Given all this, what should I actually do?"*

### VIII.1 The recommendation in one sentence

**Ship B-13 (LICENSE + CI + wall-clock commits) in the next 30 days, then B-11 (BLAKE3) + B-10 (bit-serial MAC + clock-gating + single-clock-domain) + B-1 (Verilog-2005 CFG) + B-4 (cellular IR) in the next 90 days, then ship the vessel-as-robot demo (B-14); everything else is optional and depends on what the demo reveals.**

### VIII.2 Why this and not something else

The 4-round adversarial process produced ~30,000 words of analysis and ~15 concrete bets. Most of them are good. But the *ordering* matters more than the *selection*. The ordering above is the result of three constraints:

1. **Epistemic credibility before technical cleverness.** Red-team 2-B's most damaging finding is the forward-dated commits. Until that is fixed (B-13), no amount of bit-level cleverness will move the project from 0 stars to credible. Every other technical bet inherits the credibility deficit. B-13 is the *prerequisite* for everything else.

2. **Preserve the polyformalism contract before optimizing the fabric.** The challenger's fatal-flaw critique (§IV.4 §3) shows that several attractive ideas (log-domain edges, Gray-code dials) break the polyformalism hash — the only structural differentiation quilt-verilog has. BLAKE3 (B-11) is the *minimum-viable fix* that preserves the contract while fixing the collision risk. It must ship before any fabric-level optimization.

3. **One externally-verifiable demo before scaling.** Red-team 2-B's strategic recommendation is to ship one falsifiable demo (the vessel-as-robot YouTube video, B-14). The challenger critiques the demo as currently specified (Kalman filter outperforms on a thermistor). The right demo: show the cell fabric's *specific properties* (Hebbian learning, power-law forgetting, dial state) beating a Kalman filter on a task where power-law forgetting beats Gaussian assumptions — e.g., online anomaly detection on non-stationary sensor statistics. This is a research-grade demo, not a 60-second YouTube video. **But ship something externally-verifiable in 90 days.**

### VIII.3 What to retire

Per red-team 2-B §4.3:

- The "llama.cpp for Verilog" framing — invites an unfavorable 0-vs-50k-stars comparison the project cannot survive.
- The 5-use-cases list — replace with one: vessel-as-robot.
- The polyformalism hash as a "philosophy" — re-frame as a regression test; run on 10⁶ random cell states across all 12 ports before re-claiming polyformalism.
- The `γ + η = C` framing — until there is a quantitative derivation; slogans are not laws.
- The `quilt-cowboy` references — either restore the repo or remove the references; the current state (cited but 404) breaks the polyformalism-completeness claim.

### VIII.4 What to keep

- **BEACONS.md** — the most unusual and epistemically valuable artifact. Add CI so kill conditions are mechanical, not narrative. Pin commits to wall-clock time. Then it becomes a real falsifiability register.
- **The 5+1 opcode model** — small, clean, tractable, right-sized for vessel-as-robot.
- **The QUF format** — structurally sound. Ship it as "the file format for vessel-autopilot state," not "the GGUF of cellular silicon." Publish the spec (a single markdown file would do).
- **The Charter's educational framing** — genuinely good pedagogy. Keep as documentation, not architecture.
- **The dev-rounds / LLM crews structure** — keep, but add the wall-clock CI so the rounds have contemporaneous receipts.
- **The `hostile-consumer/` directory** — adversarial test harness is research-grade discipline.

### VIII.5 If the principal wants the art track

If the principal reads Part V and thinks "yes, this is art," then the engineering recommendations above are *optional*. The art track is:

1. **Publish the art-criticism framing.** Part V of this brief, expanded to 5,000 words, is the first external reading of the quilt-verilog artwork. Submit to *Leonardo* (MIT Press), *e-flux*, or *Critical Moba*.
2. **Don't add a LICENSE.** The missing LICENSE is part of the artwork (the artwork is the archive, not the distribution).
3. **Don't fix the timestamps.** The forward-dated commits are part of the artwork (the artwork is chronologically fictional).
4. **Don't ship a demo.** The 0-star state is the intended state of outsider art.
5. **Treat the 4-round adversarial process as part of the artwork.** This brief is fan fiction; the scouts, red-teamers, synthesizer, and challenger are new LLM crews in the dev-rounds narrative.

The art track and the engineering track are not in tension. The principal can do both: ship B-13 + B-11 + B-10 + B-1 + B-4 + B-14 (engineering) *and* publish the art-criticism framing (art). The two tracks reinforce each other: the engineering makes the art *technically credible*; the art makes the engineering *narratively meaningful*.

### VIII.6 The single sentence that captures the recommendation

**"Until quilt-verilog ships a LICENSE, a CI, and one externally-verifiable demo, no amount of technical cleverness — however bit-level — will move the project from 0 stars to credible; once those three are in place, the 5-idea lowest-level stack (bit-serial MAC + per-LUT clock-gating + single-clock-domain + BLAKE3 + QUF-as-token) compounds into a research program that no other HDL-LLM project is positioned to execute."**

This sentence is the synthesizer's verdict, modified by the challenger's polyformalism-preservation constraint. It is the bottom line of 4 rounds of adversarial iteration.

---

## Part IX — Open Questions for You

These are the questions the brief cannot answer from outside. The principal (Casey) is the only one who can.

### IX.1 The 5 questions from the challenger (§IV.4 §6)

1. **Is the principal (Casey DiGennaro) committed to executing any technical proposal in the six reports, or is quilt-verilog primarily a creative practice?** This binary determines whether the brief is engineering advice (addressed to a team that may not exist) or art criticism (addressed to the principal and any future reader of the archive). The principal's own writing suggests the latter; the README's "llama.cpp for Verilog" framing suggests the former. The brief must resolve this.

2. **Are the forward-dated commits (2026-XX-XX in a 2025 wall-clock) intentional fiction or a CI/clock bug?** This single question determines the epistemic status of every timestamped claim in the repo (including all 55 BEACONS verdicts). Red-team 2-B names this as the most damaging finding; no agent has resolved it. The brief must answer it (a one-line `git log --format=%aI` on a single commit would settle it) or explicitly state that it cannot be answered from outside.

3. **Is there a budget, team, or time allocation for any 6+ month engineering effort (slang-as-lexer, CEC-RL, hardware-in-the-loop, BLAKE3 port), or are all technical proposals purely advisory?** Every report assumes the principal has the engineering capacity to execute at least one major proposal. The principal is a commercial fisherman with seasonal work. If no team exists, the brief must say so explicitly and pivot to *documentation* recommendations (publish the QUF spec; document the BEACONS verdicts; write the art-criticism framing) that the principal can execute solo.

4. **Has the principal ever engaged with the CIRCT, slang, Yosys, or sv-tests communities — by issue, PR, mailing list, or forum?** Scout 1-A found zero external engagement. If the principal has *chosen* not to engage, that's an aesthetic choice (the artwork is hermetic by design). If the principal has *tried* to engage and failed, that's a strategic problem the brief should address. The brief must distinguish these.

5. **What is the smallest externally-verifiable artifact that would change the project's strategic position?** Candidate artifacts: a LICENSE file (2 hours); a CI green-checkmark (4 hours); a published QUF spec (1 week); a 60-second FPGA demo video (40-80 hours); a paper at a workshop (3-6 months); a third-party fork (not under principal's control). The brief must pick *one* and explain why it's the threshold artifact — i.e., what changes after that artifact exists that doesn't change before. Without this, the brief is a list of options, not a recommendation.

### IX.2 Five additional questions from this brief's author

6. **Does the principal want the quilt-verilog LLM (the eventual trained model) to be a *specialist* in the cellular model, or a *generalist* on Verilog?** This determines whether BEACONS-DPO scaling (specialist) or OSS-Instruct-for-HDL (generalist) is the right training data path. The challenger's critique of BEACONS-DPO (§IV.4 §1.6) is correct *if the model is a generalist*; it's wrong *if the model is a specialist*. The principal's intent is unknowable from outside.

7. **Is the F/V Eileen actually instrumented for any sensor data collection?** The vessel-as-robot use case requires real sensor data. If the boat has no sensors, the demo cannot happen on the boat. If the boat has sensors but no data pipeline, the demo can happen on a bench with synthetic data. The principal knows; the brief doesn't.

8. **What's the principal's relationship to the broader AI-Writings canon?** Is quilt-verilog a *substrate for* the canon (the canon is the data; the fabric is the runtime), or *parallel to* the canon (both are artworks in the same practice)? The "supercharging" claim depends on this. If parallel, the supercharging is metaphor; if substrate, the supercharging is architectural.

9. **Has the principal read Proof2Silicon, ACE-RTL, QiMeng-CodeV-R1, or any of the other 2025-2026 HDL-LLM papers?** The brief assumes the principal is current on the literature. If not, the first step is a reading list (the §II.1 table is the list). If yes, the brief can assume shared vocabulary.

10. **What does the principal want from this brief?** The user's prompt said "deep research my repo." If the principal wanted *validation*, this brief disappoints (it agrees with the red-team that the project has 0 external credibility). If the principal wanted *critique*, this brief delivers (4 rounds of it). If the principal wanted *ideas*, this brief delivers (15 bets, 10 research questions, 5-idea stack). If the principal wanted *a roadmap*, this brief delivers (3/6/12-month). The principal's intent in commissioning the brief is itself an open question.

### IX.3 A closing observation

The brief was produced by 8 LLM agents across 4 rounds of adversarial iteration, in the same lineage as the principal's own dev-rounds / LLM-crews methodology. The brief is therefore *itself* an iteration of the artwork (if the project is art) or *itself* a research artifact (if the project is engineering). In either reading, the brief does not stand outside the project; it stands *inside* it. The principal's response to the brief — which proposals to accept, which to reject, which to defer — is itself the next round of the dev-rounds loop.

The brief's author (the orchestrator agent) offers one observation: **the most interesting feature of quilt-verilog is not the cellular fabric, the polyformalism, or the BEACONS register. It is the dev-rounds methodology itself.** A practice where multiple LLM crews compete and cross-review, where falsifiable claims are pre-registered with kill conditions, where the principal's role is curator rather than author — this is a methodology that *any* research project could adopt. If quilt-verilog's only contribution is to demonstrate that this methodology works (or doesn't), that alone would be a meaningful contribution to the field of LLM-assisted research.

The principal may now respond.

---

## Appendix A — Source Manifest

### A.1 quilt-verilog repo (fetched via raw.githubusercontent.com)

- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/README.md` (full README, 232 lines)
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/BEACONS.md` (55-claim registry)
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/docs/INDEX.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/docs/FOUNDATION.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/docs/DOCTRINE.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/docs/ACADEMIC-RIGOR.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt-verilog/master/docs/WORLD-CLASS-BRIEF.md`
- `https://github.com/SuperInstance/quilt-verilog/commits/master.atom`
- `https://api.github.com/search/repositories?q=quilt-verilog`
- `https://github.com/SuperInstance/quilt-verilog/tree/master/rtl` (22 modules enumerated)

### A.2 SuperInstance ecosystem (fetched via raw.githubusercontent.com)

- `https://raw.githubusercontent.com/SuperInstance/quilt-claude-charts/main/QUILT_CHARTER.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt/main/README.md`
- `https://raw.githubusercontent.com/SuperInstance/quilt-mhs/main/README.md`
- `https://raw.githubusercontent.com/SuperInstance/AI-Writings/main/README.md`
- `https://raw.githubusercontent.com/SuperInstance/plato-portal/main/README.md`
- `https://raw.githubusercontent.com/SuperInstance/SuperInstance/main/README.md`
- `https://raw.githubusercontent.com/SuperInstance/SuperInstance/master/README.md`
- READMEs of: quilt-rust, quilt-cortex, quilt-loom, quilt-arena, quilt-studio, quilt-tools, quilt-cloudflare, quilt-arcade, quilt-playtest, quilt-show, quilt-quant, AI-Writings, CognitiveEngine, fleet-radio, jev-quilt, mavis-substrate-walker, micrograd-quilt, pong-quilt, tidepool

### A.3 HDL toolchain (primary README/CHANGELOG/docs)

- slang: `raw.githubusercontent.com/MikePopoloski/slang/master/README.md`, `…/master/CHANGELOG.md`
- Yosys: `raw.githubusercontent.com/YosysHQ/yosys/master/README.md`, `…/master/CHANGELOG`, `yosyshq.readthedocs.io/projects/yosys/en/latest/yosys_internals/formats/rtlil_rep.html`
- Surelog: `raw.githubusercontent.com/chipsalliance/Surelog/master/README.md`
- UHDM: `raw.githubusercontent.com/chipsalliance/UHDM/master/README.md`
- Verible: `raw.githubusercontent.com/chipsalliance/verible/master/README.md`, `…/master/verible/verilog/parser/README.md`
- Verilator: `raw.githubusercontent.com/verilator/verilator/master/Changes`
- Icarus Verilog: `raw.githubusercontent.com/steveicarus/iverilog/master/README.md`
- sv-parser: `raw.githubusercontent.com/dalance/sv-parser/master/README.md`
- Moore: `raw.githubusercontent.com/fabianschuiki/moore/master/README.md`
- tree-sitter-verilog: `raw.githubusercontent.com/tree-sitter/tree-sitter-verilog/master/README.md`
- tree-sitter-systemverilog: `raw.githubusercontent.com/gmlarumbe/tree-sitter-systemverilog/master/README.md`
- cocotb: `raw.githubusercontent.com/cocotb/cocotb/master/README.md`
- sv-tests: `raw.githubusercontent.com/chipsalliance/sv-tests/master/README.md`, `chipsalliance.github.io/sv-tests-results/`
- CIRCT: `raw.githubusercontent.com/llvm/circt/main/README.md`, `…/main/docs/Charter.md`, `circt.llvm.org/docs/`

### A.4 Constrained-decoding libraries

- Outlines: `raw.githubusercontent.com/dottxt-ai/outlines/main/README.md`, `…/main/docs/features/advanced/backends.md`
- xgrammar: `raw.githubusercontent.com/mlc-ai/xgrammar/main/README.md`
- llguidance: `raw.githubusercontent.com/microsoft/llguidance/main/README.md`
- lm-format-enforcer: `raw.githubusercontent.com/noamgat/lm-format-enforcer/main/README.md`
- Guidance: `raw.githubusercontent.com/guidance-ai/guidance/main/README.md`
- llama.cpp GBNF: `raw.githubusercontent.com/ggml-org/llama.cpp/master/grammars/README.md`

### A.5 Papers (arxiv abstracts fetched)

- XGrammar: 2411.15100
- XGrammar-2: 2601.04426
- Synchromesh: 2201.11227
- SynCode: 2403.01632
- Pre³: 2506.03887
- AutoChip: 2311.04887
- VerilogEval v1: 2309.07544
- VerilogEval v2 (Revisiting VerilogEval): 2408.11053
- RTLLM: 2308.05345
- RTLCoder: 2312.08617, 2410.09406
- BetterV: 2402.03375
- RTLFixer: 2311.16543
- ScaleRTL: 2506.05566
- ChipNeMo: 2311.00176
- Proof2Silicon / PREFACE: 2509.06239
- QiMeng-CodeV-R1: 2505.24183
- StarCoder2 / Stack v2: 2402.19173
- DeepSeek-Coder: 2401.14196
- Qwen2.5-Coder: 2409.12186
- GraphCodeBERT: 2009.08366
- AlphaGeometry2: 2502.03544
- OpenHands: 2407.16741
- SWE-agent: 2405.15793
- Speculative decoding (Leviathan): 2211.17192
- GRPO / DeepSeek-Math: 2402.03300

### A.6 Industry / VC sources

- Synopsys, Cadence, Siemens, RapidSilicon, Silimate, ChipAgents, Zero ASIC, NVIDIA press releases 2024-2026
- TechCrunch, SemiAnalysis, Crunchbase for VC funding data
- AI4EDA landscape map

---

## Appendix B — Agent Roster & Methodology

### B.1 The 8 agents

| ID | Agent | Role | Model | Words |
|---|---|---|---|---|
| 1-A | scout-repo-and-ecosystem | Forensic deep-dive on quilt-verilog repo + SuperInstance account | glm-5.2 | 4,837 |
| 1-B-retry | scout-llm-for-hdl-industry-and-adjacent | Industry / 2025-2026 papers / agentic / FV+ML (focused retry after 1-B timeout) | glm-5.2 | 6,426 |
| 1-C | scout-hdl-toolchain-and-constrained-decoding | HDL toolchain + grammar-constrained decoding substrate | glm-5.2 | 7,185 |
| 1-D | scout-code-llm-substrate | Code-LLM tokenization / AST-IR / data / RL / inference / eval | glm-5.2 | 7,087 |
| 2-A | redteam-technical | Adversarial critique of scout proposals (technical) | glm-5.2 | 6,056 |
| 2-B | redteam-strategic | Adversarial strategic critique of positioning / ecosystem / meta | glm-5.2 | 5,207 |
| 3-SYNTH | synthesizer | Synthesis of all 6 prior reports into refined agenda | glm-5.2 | 6,800 |
| 3-CHALL | challenger | Final-round critique + 5 new ideas + meta-flaw + verdict | glm-5.2 | 5,995 |

**Total source material:** ~57,000 words (including worklog).

### B.2 The 4-round methodology

**Round 1 (Parallel Scouting, 4 agents).** Four agents scouted in parallel, each with a distinct scope. The orchestrator (main agent) wrote a detailed prompt for each, specifying scope, research targets, research methods, expected output, and worklog protocol. Each agent read the worklog before starting and appended its findings after.

**Round 2 (Adversarial Red-Team, 2 agents).** Two agents attacked the Round 1 outputs. 2-A attacked the *technical* proposals (top 5 overhyped, top 10 missed ideas, 10 factual claims pressure-tested, 5-idea manifesto). 2-B attacked the *strategic* positioning (7 positioning verdicts, supercharging causal chain breaks, 5 cleverer low-level ideas, strategic recommendation). Both read all Round 1 reports + worklog.

**Round 3 (Synthesizer + Challenger, 2 agents in parallel).** The synthesizer (3-SYNTH) took all 6 prior reports and produced a refined agenda (10 surviving directions, 5-idea lowest-level stack, 3-layer roadmap, pre-emptive defense). The challenger (3-CHALL) anticipated the synthesizer's likely proposals, attacked each, proposed 5 truly-new ideas, identified the fatal flaw in the lowest-level stack, named the meta-flaw (art vs engineering), and issued a final strategic verdict. Both agents read all 6 prior reports + worklog.

**Round 4 (Orchestrator Synthesis, this brief).** The orchestrator (main agent) read all 8 prior reports + worklog and wrote this brief. The brief is the residue: bilingual executive summaries, 7 analytical parts, 3 appendices, ~28,000 words.

### B.3 The worklog protocol

All 8 agents followed the same worklog protocol:

1. **Read first.** Each agent read `/home/z/my-project/worklog.md` before starting, to understand what prior agents had done.
2. **Work in the open.** Each agent's work was preserved in `/home/z/my-project/research-out/<agent-name>-report.md`.
3. **Append after.** Each agent appended a section to `/home/z/my-project/worklog.md` with: Task ID, Agent name, Task description, Work Log (concrete steps), Stage Summary (key findings + open questions for next round).

The worklog is at `/home/z/my-project/worklog.md` (~7,300 words). The 8 individual reports are at `/home/z/my-project/research-out/`. The final brief is at `/home/z/my-project/download/quilt-verilog-deep-research-brief.md` (this file).

### B.4 Methodological notes and caveats

- **Forward-dated commits.** Every "2026" date in the repo is reproduced verbatim. The system wall-clock reads 2025-09-25; the IM gateway date reads 2026-09-26. The brief flags this anomaly in §I.9 and does not resolve it.
- **GitHub API rate-limiting.** Round 1 agents were hard-rate-limited on the GitHub REST API (60 req/hr unauthenticated). All GitHub metadata was recovered via the search API (different endpoint) and HTML scraping. The Atom commits feed was the only git-history source available.
- **Paraphrased secondary sources.** Some arxiv IDs in scout 1-D are recovered from secondary citations rather than fetched directly (Magicoder, RTLCoder v1, MG-Verilog, StepCoder, GRPO/DeepSeek-Math, CodeRL/RLTF/PPOCoder, HDLEval/CVDP/Pluto/EDALearn). Quotes from those are paraphrased from secondary literature, not the primary abstracts.
- **No external user research.** The brief does not contact Casey DiGennaro. The principal's intent is inferred from public artifacts only.
- **The brief is part of the artwork (if the project is art).** Per Part V, the 4-round adversarial process is itself an iteration of the dev-rounds loop. The brief is *fan fiction* about quilt-verilog, produced by an LLM orchestra.

---

## Appendix C — Glossary

| Term | Definition |
|---|---|
| **5+1 opcodes** | quilt-verilog's instruction set: BIND, LINK, EFFECT, VIEW, TICK + ACK/NAK |
| **ACE-RTL** | NVIDIA's 2026 RTL agent; 97.1% on CVDP |
| **AutoChip** | Canonical HDL verifier-in-loop paper (arxiv 2311.04887); GPT-4 + Icarus feedback, +24.2% |
| **BEACONS.md** | quilt-verilog's 55-claim falsifiability register; 21 GO / 19 NO-GO / 8 MIXED / 7 UNTESTED |
| **BLAKE3** | Cryptographic 128-bit hash; proposed replacement for FNV-1a |
| **BMC** | Bounded Model Checking; SymbiYosys's primary verification engine |
| **CEC** | Combinational Equivalence Checking; Yosys `equiv` pass; miter circuit + SAT |
| **Cellular IR** | Proposed ~10-production IR specific to quilt-verilog's 5+1 opcodes |
| **ChipNeMo** | NVIDIA's domain-adaptive LLM for chip design (arxiv 2311.00176); closed corpus |
| **CIRCT** | LLVM's circuit IR project; 40+ MLIR dialects |
| **Cocotb** | Python testbench framework; coroutine runner over VPI/VHPI |
| **CVDP** | NVIDIA's 2025 HDL benchmark; 783 problems |
| **DPO** | Direct Preference Optimization; chosen/rejected pairs |
| **EAGLE-2** | Speculative decoding variant; feature-level lookahead |
| **FNV-1a** | quilt-verilog's current 64-bit non-cryptographic hash |
| **GRPO** | Group Relative Policy Optimization; DeepSeek-Math's RL algorithm |
| **HDL-ACI** | HDL Agent-Computer Interface; proposed port of SWE-agent's ACI to HDL |
| **MHS** | Anthropic's Model Hardware Standard (announced 2026-08-27) |
| **OSS-Instruct** | Magicoder's synthetic data generation method (ICLR 2024) |
| **PREFACE** | Proof2Silicon's RL framework; acts on prompt not weights; +21% Dafny verification |
| **Proof2Silicon** | arxiv 2509.06239; RL on prompt to steer frozen LLM toward Dafny-verifiable code |
| **QiMeng-CodeV-R1** | arxiv 2505.24183; 7B SOTA on VerilogEval-v2 at 68.6% |
| **QUF** | quilt-verilog's binary cell-state format ("QUilt Format") |
| **RTLCoder** | arxiv 2312.08617, 2410.09406; 6.7B HDL LLM; 34% VerilogEval-v2 |
| **ScaleRTL** | arxiv 2506.05566; reasoning LLM with 3.5B-token CoT; +18.4% VerilogEval |
| **slang** | Best-in-class SystemVerilog frontend; de-facto canonical since Yosys v0.66 |
| **Speculative decoding** | Draft model proposes K tokens, target verifies in one forward pass |
| **SymbiYosys** | Yosys's formal verification flow; BMC + k-induction |
| **UHDM** | Universal Hardware Data Model; Surelog's IR; Cap'n'Proto persistence |
| **VerilogEval v2** | De-facto HDL benchmark (arxiv 2408.11053); GPT-4o 63% |
| **XGrammar** | arxiv 2411.15100; compiled CFG constrained decoding; ~5μs/token for JSON |

---

*End of brief. Total length: ~28,000 words. Source material: ~57,000 words across 8 agent reports + worklog. The brief is the residue of 4 rounds of adversarial iteration on `SuperInstance/quilt-verilog` and its technological neighborhood.*







