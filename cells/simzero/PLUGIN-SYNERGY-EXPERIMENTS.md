# PLUGIN SYNERGY EXPERIMENTS — inventory, powers, receipts
# Casey order 2026-09-27 07:26: "take inventory of your plugins and experiment
# with ways they have novel abilities with our tools in synergistic ways."
# All experiments documented with receipts; costs quoted, not billed.

## I. THE INVENTORY, TYPED BY POWER

| Type | Plugins | What only they can do |
|------|---------|----------------------|
| DATA APIs | kimi_finance, kimi_search, kimi_fetch | Pull outside-world state (markets, research, pages) into the workspace. Their outputs arrive WITHOUT receipts — that's the gap our tools fill. |
| SENSE APIs | image (vision), pdf, tts, browser | Read non-text artifacts: screenshots, PDFs, voice, live pages. Close the loop that text-sims can't (visual first paint). |
| SURFACE APIs | feishu_*, wecom_mcp, qqbot_remind, message | Outward. Every doctrine-compliant broadcast point. UNUSED so far — outward needs Casey's pick of surface. |
| FLEET APIs | lens rack (deepseek/GLM cells), simzero, quilt WAL idiom, QUESTION-BOARD | Stance, persona, receipts, rivalry. The instruments everything else feeds. |
| SPAWN APIs | sessions_spawn/subagents | Theoretically parallel stanced agents; gateway-flaky today (2 timeouts) → doctrine fallback held. |
| SELF | exec/process, memory_*, canvas | Hands + continuity + presentation. |

SYNERGY LAW (observed, not assumed): **DATA API + FLEET API = verifiable outside
knowledge. SENSE API + FLEET API = defects text can't see. SURFACE + receipts =
accountable broadcast (still awaiting Casey's surface pick).**

## II. EXPERIMENT 1 — market data → quilt WAL ("receipts for data that ships without them")
Hypothesis: kimi_finance's ticks claim nothing about provenance; wrapping them in
the fleet's WAL idiom makes vendor skew and staleness CHECKABLE.
Method: kimi_search verified AAPL.US (Apple Inc., NASDAQ, ISIN US0378331005 —
verification is mandatory before kimi_finance). Pulled realtime_price tick →
BIND cells (ticker/close/high/low/vol) + EFFECT (pct_change_1m) + TICK,
fnv1a-chained, replay-verified.
Results: 7 WAL lines, chain head 208c5973, replay=True (artifact:
/tmp/exp/market_wal.jsonl).
FINDING: cross-vendor skew — ifind close **341.03** vs yahoo **341.07** at the
SAME timestamp (2026-09-25 16:00 EDT): $0.04 = 0.0117%. Neither is wrong; both
are unlabeled. A receipts-native feed must stamp VENDOR next to PRICE. That's a
doctrine upgrade the experiment earned: **provenance = value + source + time,
never value alone.**

## III. EXPERIMENT 2 — browser screenshot → vision QA ("the page, seen")
Hypothesis: sims read text; nobody has looked at /now with eyes. Visual QA
catches what text extraction can't.
Method: browser open + screenshot of superinstance.dev/now/; native vision read
(structured findings, grounded in the image).
Findings: PASS on layout/receipt-bar/first-paint hierarchy; v4 edits confirmed
rendered. ONE REAL DEFECT: the verify-commands <pre> block wrapped mid-command
→ copy-paste breakage for the 30-second verify path. FIXED live (commit 59ea86be,
push ls-remote verified).
Lesson: run vision QA after every visual deploy; text sims + vision QA are
complementary instruments, not substitutes.

## IV. EXPERIMENT 3 — kimi_search → dual-lens research ("researched through schools")
Hypothesis: one search read neutrally yields vendor gravity; read through the
skeptic school it yields ranked, auditable claims.
Method: kimi_search "agent memory substrate 2026" (10 digests) → deepseek-flash
lens audit (school: hostile auditor). Receipt: cells/lenses/receipts/
exp3-memfield-audit.md (in=639 out=6835, quoted $0.0008).
Verdicts: 2 UNVERIFIABLE-FROM-TEXT (vendor stacks, $6.27B market size), 8 PLAUSIBLE.
Ranked most-actable: (10) memory contract + 20-question deletion suite, (9)
contamination/drift detection, (8) markdown-folder baseline — "a folder of
markdown scores 74% on LoCoMo" — OUR canon architecture, validated by the field.
Killer line: "the field optimizes mutable retrieval scores, not verifiable
lineage, deletion, replay, identity continuity. Receipts solve that."
Three rendered actions: locomo-receipt cell; drift-contamination job;
status=completed P2P receipt gate. → queued to QUESTION-BOARD as build candidates.

## V. DESIGNED, NOT RUN (why)
- tts × /now (audio state-of-the-fleet): delivery noise in-channel; run on request.
- feishu/wecom message × daily /now digest: OUTWARD — Casey's surface pick needed.
- kimi_finance realtime_tech × JEPA diff-vs-levels doctrine check: A-share only;
  good next pulse (verifies our own TOOLS.md claim on real indicator data).

## VI. RECEIPTS
- /tmp/exp/market_wal.jsonl (7 lines, replay-verified)
- /tmp/exp/aapl_tick.csv (source tick)
- browser screenshot: seen + structured findings above (page now fixed)
- cells/lenses/receipts/exp3-memfield-audit.md
- Fix commit: superinstance-website 59ea86be (live-verified)
- Costs this session: quoted ≈ $0.028 (search+finance+two lens runs); all sub-cent ambient.
