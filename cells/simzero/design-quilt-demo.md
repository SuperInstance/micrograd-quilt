# /quilt — interactive 5-opcode demo, build spec (engineer stance)
# Target: superinstance.dev/quilt/ — same repo (superinstance-website @ master),
# same Pages deploy as /now. Sim-gated before any link points at it.

## The 10-second test (both species)
A zero-shot stranger lands and, WITHOUT clicking anything, sees:
cells on a canvas already ticking (self-running on load — no dead first paint),
three inline labels: "this is a cell · this is a link · this is a receipt",
and a receipt chain growing line by line. Then ONE button: **add a cell**.
They click → a cell BINDs → its receipt line appears with its hash → they
understand the kernel in under 10 seconds. That click is the demo.

## The six verbs, made visible
- BIND: a cell appears; WAL line `BIND cell:n hash:h1`
- LINK: an edge draws between two cells; combined hash visible
- TICK: time step; cells animate; chain advances; hashes chain (fnv1a, shown)
- EFFECT: one cell changes state/color; the cause edge highlights
- VIEW: one toggle — same cells, two projections (grid ↔ graph)
- FORGET: oldest cell fades; its receipt lines REMAIN in the chain (the point)

## Non-negotiables (sims wave-1 findings)
1. Server-rendered first paint: real canvas + real WAL sample in HTML before JS.
   No spinner. Loader-secondary doctrine.
2. Zero client JS required for comprehension: the static page tells the whole
   story; JS makes it interactive.
3. Receipt bar top: stamp, data source, /quilt/wal.json link (static WAL
   sample that replays — byte-identical — to the shown state; replay() in page).
4. JSON-LD (SoftwareApplication + demoOf quilt kernel, github repo link).
5. Rams visual: dark abyssal bg, phosphor cells (#7ee0a3), brass receipts
   (#d29922), monospace, ONE accent animation (the chain), no other motion.
6. Sim gate: simzero 10 personas × the built page BEFORE linking; ship when
   ≥7 STAY and zero STATE-OPAQUE readings.

## Files
/quilt/index.html — the demo (self-running canvas + interactive verbs)
/quilt/wal.json   — static sample WAL; page replays it to derive shown state
/quilt/README.md  — the spec + how to fork it into your own cell fabric

## Exit criteria
- 10s comprehension in sims (coder + tradesperson both pass the label test)
- replay(wal.json) == shown state, receipted on-page
- mobile text-render readable (tradesperson persona)
