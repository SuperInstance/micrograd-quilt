# SIM-ZERO WAVE 1 — the nine footer links vs 21 simulated zero-shot agents
2026-09-27, 7 pages x 3 personas (coder/scraper/skeptic), deepseek-flash, ~$0.005 quoted.
Verdicts: 17 LEAVE / 4 STAY.

## The systematic failure: STATE-OPAQUE
The fleet's receipts are loadbearing everywhere except its own front door.
- fleet-dashboard: CSS dump, zero data rendered without JS. All 3 LEAVE.
- fleet-wiki: 764 claimed pages, counts sum 689, "Fleet Status" = 2 pages,
  future-dated recents. 2 LEAVE 1 STAY (corpus size).
- ai-writings: 1.7KB spinner. 3/3 LEAVE.
- the-tap: 641B JS redirect tombstone. 2 LEAVE 1 STAY (crawl target).
- compass-head: art-first, no receipts, audio unverified. 3/3 LEAVE.
- live-canon: API surface explicit ("State hash: computing... Papers: ?" =
  placeholders). 2 LEAVE 1 STAY *because the API contract is probeable*.
- superinstance.dev: strongest page; still self-reported "~200 repos",
  no SHA/CI above fold, future-dated Latest Works. 2 LEAVE 1 STAY.

## The three convergent fixes (every persona, independently)
1. RECEIPT BAR above the fold: live commit SHA, CI/test status, real metric
   values, deploy timestamp, repo link — BEFORE css or poetry.
2. MACHINE-READABLE STATE on first paint: JSON-LD / /api/state / index.json.
   The scraper STAYs exactly when a probeable API surface exists.
3. Loader secondary, real data server-rendered first.

## Doctrine
Casey: "we aren't pitching. we are embodying that." => the front door must
live the receipts doctrine. The sim harness is the standing instrument:
rerun after every page change until LEAVE/STAY inverts.
