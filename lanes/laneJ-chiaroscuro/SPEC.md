# laneJ-chiaroscuro — Jev-Chiaroscuro neural text-substrate rendering

Status: SEEDED 2026-10-03 ~02:10 by Kimi (multi-part vision). This SPEC is the
fleet distillation. The vision text is seed, not constraint — every claim
below is tagged FOUND (in the seed), ASSUMED (design choice), or UNVERIFIED
(cannot be honestly claimed on current hardware).

## The core idea (distilled)

Render video/worlds as a **bivariate text substrate** — a C×R cell lattice
where each cell carries [luma, gradient-angle, magnitude] — instead of pixel
tensors. A dual-rate loop (fast reflex cells / slow strategic models) plus a
vision-teacher GAN shapes the cell states. Characters double as opcodes
(bounders/carriers/diffusers/evaluators). The endgame: the lattice becomes a
self-simulating world engine (physics, agents, render in one buffer),
compilable to a portable identity (.pai) and reverse-rendered via diffusion.

## Claim ledger (honest tags)

| claim (from seed) | tag | note |
|---|---|---|
| Bivariate state [l,θ,m] per cell is sufficient substrate | ASSUMED | plausible; needs an exp, not a paper |
| Two-pass 32-thread ballot ↔ agent consensus | FOUND | warp-vote family already proved this shape |
| WGSL single-pass Sobel+JEPA on real GPU | UNVERIFIED on fleet hosts | no GPU here; swiftshader maybe |
| 60 FPS locked with zero variance | UNVERIFIED | frame-delivery profile must be measured, never asserted |
| VLM-as-discriminator semantic loss | FOUND-as-concept | no local VLM wired; loss is stubbed MSE+contrast in seed code |
| Self-evolving JIT shader rewrites | FOUND-as-concept | hot-swap exists in WebGPU; self-authoring needs the Liaison |
| .pai portable identity + ControlNet reverse render | FOUND-as-concept | codec is trivial; diffusion needs ComfyUI/Workers-AI |
| "Quilt architecture" = stitch/prune cells | FOUND | matches CONSTELLATION.md plugin contract + pruning loops |

## The receipts-native phase ladder (dogfood order)

Each phase must RUN and PIN before the next begins. Dogfood law: code from
phase N builds phase N+1.

- **P1 Base Canvas** — luma field → ASCII matrix at a measured frame rate,
  density/contrast/chroma controls re-binding per frame, frame-time console.
  *Honest on this host: CPU/procedural sim. WebGPU flagged as the GPU variant.*
- **P2 Sentinel** — watchdog + polyfill ladder (WebGPU→WASM-SIMD→workers→edge),
  simulated crash injection, recovery < 1500ms measured.
- **P3 Cloud Bridge** — Durable-Object state mesh + WebRTC ingest (Cloudflare
  Calls), 8s cold-parameter pruning. *Blocked until fleet has a CF account
  binding — flag, don't fake.*
- **P4 Crystallization** — .pai codec + R2/Workers-AI reverse render.
  *Blocked on inference endpoint; codec itself is buildable now.*

## Doctrine mapping (why this fits the fleet)

- The lattice IS a receipt surface: cell states append-only → WAL ticks are
  renders. backward-holdem already proved "record on the effect path".
- Cells-as-opcodes == capabilities-as-verbs (warp platform contract).
- Pruning dead cells == the EvolutionAgent law, receipts culture applied to
  code itself: unused ⇒ extracted, with a trace row.
- The Liaison layer == the fleet's URL-param agent door (foundry): intent in,
  artifact out, hash-stamped.

## Immediate honest slice (tonight)

`sim/phase1_canvas.html` — procedural luma field (no camera on headless host)
through the full bivariate pipeline shape: field → throttle → cells → glyph
map → viewport, with live frame-time console. Measures what the seed only
asserts. Screenshot + pins in the lane.

## Blockers (named, not hidden)

- tmux server down since Sep 27 reboot → the "competing coders in tmux"
  dogfood needs a `tmux new-server` + zcode/kimi-cli availability check.
- No GPU/WebRTC/camera on fleet host → P1 is sim-first; P3/P4 need Cloudflare
  binding or ComfyUI endpoint before any real claim.
- Repo creation is Casey-gated; lane lives in workspace until then.
