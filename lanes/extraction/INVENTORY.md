# Extraction lane — inventory & queue

Opened 2026-09-28 by Kimi directive ("bicycle maker" doctrine): pull pong-quilt's
embedded novel tech into standalone modules outsiders can adopt and develop.
Each extraction: zero-dep preferred, tests/pins, honest stats, README aimed at
outsiders, claim provenance tagged.

## Shipped

### #3 `SuperInstance/quantum-audio-honesty` — waveform-imaging honesty channel
- **Source:** pong-quilt `qa.js` @ b4d15c8 (L2 advisor), ported verbatim except the page-coupled doctor-lens seam.
- **Sibling-port check done first (queue gate):** `quilt-quantumaudio-demo` / `quilt-quantum-audio` / `quilt-quantum-audio-push` exist (real QPAM rigs) + `quilt-echovision` (sonify→lossy→image idiom) — extraction consolidates the CHANNEL SEAM, does not duplicate the rig; sibling edges named in-repo.
- **The lure:** every oracle-in-your-loop builder hand-rolls the stand-in badly. Here: deterministic LABELED stand-in (low-pass + seeded shot noise ∝ 1/√spb), empty-pot refusal (null, never a fake; `??`-not-`||` semantics), BYO endpoint (base64 shot bins + injectable validator + `byo-qpam-fallback` honest degrade, real replies NOT sim-capped).
- **Generalizations (only these):** rng/sonify/validateReply/N/deadzone/envelopeGrid injectable; shotBins+toB64 exported (they ARE the wire format); zero-dep, no core.js.
- **Stats:** 20 pins, `node tools/run-tests.js`, FAIL-first (suite dies without src/); 5 pins are a faithful-port contract with values captured live from qa.js @ b4d15c8 (sonify/channel/suggest/estimateX/envelope rows); 20/20 green at first commit c7a2125 (repo born: main = the artifact, single branch, per paced-seam precedent).
- **Bugs found by running before push:** pin "byo: validator injectable" initially asserted the WRONG side (custom validator accepting a custom reply shape is success, not fallback) — caught at first run, expectation corrected. Nothing in the port itself diverged.
- **Edges named in-repo:** `quantum-audio-honesty -> pq-l2`, `-> qad-qpam`, `-> qad-echovision`.

### #2 `SuperInstance/paced-seam` — one-in-flight LLM advice seam
- **Source:** pong-quilt `core.js` `makeSeam` (R3 pacing/serialization + R4 timeout).
- **The lure:** every LLM-app builder hand-rolls this badly (per-frame fetches,
  arrival-burst applies, hung-endpoint stalls). Zero-dep reference seam,
  transport injected, ~60-line implementation outnumbered by its pins.
- **Contract:** paced fires (injected clock), one in flight (refused, never
  queued), stale fence by seq, opt-in timeout with exactly-once settlement
  (late arrival fenced, NOT double-counted), four-class honest drop counters.
- **Stats:** 12 pins, `node tools/run-tests.js`, FAIL-first (RED without the
  module), 12/12 green at first commit 71b594c.
- **Edge names in-repo:** `paced-seam -> pq-r3`, `paced-seam -> pq-r4`.

### #1 `SuperInstance/coev` — adversarial coevolution engine + integrity auditor
- **Source:** pong-quilt `core.js` @ `b4d15c8` (C1), ring/evaluator lineage quilt-edge-ml.
- **The lure:** GAN-style adversarial evolution for any domain + the auditor
  that caught the R53 hollow champion (claimed 1259.1, benched 239.6). `REFUTED`
  exits 1 — CI-gateable.
- **Pieces:** src/{rng,ring,evaluator,ledger,engine,audit}.js (each standalone),
  arenas/pong.js reference port, bin/coev.js (run/audit/demo), docs/{ARENA,INTEGRITY}.md.
- **Verdict vocabulary:** CONFIRMED / REFUTED / SIMULATED / MEASURED.
- **Stats:** 33 pins, node tools/run-tests.js. Bugs found by running before push:
  (1) claim-null audited as REFUTED instead of MEASURED (semantics bug);
  (2) `result.json` passed as --champion fed whole object to arena → loadNet unwrap
  announced on stderr + arena.validate hook. Both now regression-pinned.
- **Edge names in-repo:** `coev -> pq-c1`, `coev -> qe-ml`.

## Queue (ranked by lure × feasibility)

### #4 Receipt/WAL tooling (`wal-export`, `receipt-completeness`, `doctor-verdict`)
- Fleet-coupled (stone-v1, quilt-tools discovery). Extract only the generic
  subset (jsonl WAL writer/reader, completeness auditor with verdict rows).
- **Defer** until fleet receipt formats stabilize (sahu -00 churn).

## Not extracted (and why)
- `prerun.js` / `prerun-coev.js` — CI harness for a specific artifact; the
  generic engine covers it.
- `site-*.mjs`, `build-site.mjs`, `diet-compare.js` — page-specific tooling.
- `makeJepa` (micro-JEPA) — small; fold into a later "sim predictors" module if
  the L2/L3 lanes ever need it standalone.
- L1 single-player training (`trainL1`) — belongs to a future `evolve` module
  (classic GA), separate from the adversarial loop.

## Doctrine notes
- Extraction reviews the SOURCE honestly: pong-quilt's C1 has known warts
  (4v4 live collapse, HUD cadence mismatch — R55 spec). The extraction ports
  the engine faithfully and documents the warts in docs/, not silently.
- Every module keeps its FAIL-first pins and honest-eviction semantics.
- Weight-law edges named in-repo at first commit so discovery can mint them.
