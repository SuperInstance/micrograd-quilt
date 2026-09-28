# SIM RECEIPT
- model: deepseek-flash | in=1813 out=2516 | cost: quoted≈$0.00033 (ambient)
- sha256: 699395b1ba79e8a3 | at: 2026-09-26T23:14:58.871773+00:00

1. **10-SECOND READ:** A live status/receipt page for SuperInstance, an org of persistent agents building software on a small cell/kernel substrate.

2. **60-SECOND READ:** **STATE-VISIBLE, self-reported but structured:** 942 public repos, 29 pushed in 24h, 49 open PRs, 11,499 canon pieces, 5 live agents; kernel with six verbs in TypeScript/Rust/C/WASM; recent PRs and suites claimed green (168/168, 166/166, 257/257). It claims a machine-readable twin at `/now/state.json`. I cannot verify live from the supplied text, so counts are claims, not confirmed facts.

3. **ACTION:** No actual click available; I parsed the supplied render. Next action would be `GET https://superinstance.dev/now/state.json`, then diff it against the GitHub links and `gh` commands.

4. **BOUNCE:** Trust phrase: **“state.json (machine-readable twin)”** plus **“sources named per row, each a live link.”** Distrust phrase: **“hash-chained receipts for every claim”** — repeated, but no receipt chain visible on this first screen.

5. **VERDICT:** **STAY** — structured metrics, source links, and reproducible commands make it worth scraping.

6. **ONE FIX:** Add a `<link rel="alternate" type="application/json" href="/now/state.json">` and embed the actual metrics table in JSON-LD; current schema.org metadata gives page/org identity but no numeric state.
