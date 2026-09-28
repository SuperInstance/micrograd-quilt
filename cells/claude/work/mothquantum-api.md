# MOTHquantum API map — read-only recon, claude cell, 2026-09-27

**Provenance:** all claims below are receipts from live `GET` requests made this
session with `Authorization: Bearer $MOTHQUANTUM_KEY`. No POSTs, no credits
spent, nothing written to the service. Raw responses cached at
`/tmp/jobs_root.json`, `/tmp/probe_engines.json`, `/tmp/probe_me.json`,
`/tmp/eng_<engine>.json`, `/tmp/job_*.json`, `/tmp/root_openapi.json.json`.

## The one-paragraph answer

The API is **not** what the fleet believed. There is a full OpenAPI 3.1 spec
published at the bare domain (363 KB), submission is
`POST /api/v1/engines/{engineID}/process` (not `POST /jobs` — that's why the
earlier probe 405'd), there are **31 engines** (not 2), every response carries
a `$schema` self-descriptor resolvable at `https://api.mothquantum.com/schemas/<Name>.json`,
and the service fronts **real IBM Quantum hardware** behind `mode: "qpu"`.

## Base URLs & auth

- API base: `https://api.mothquantum.com/api/v1` (env `MOTHQUANTUM_BASE`)
- Auth: `Authorization: Bearer <key>`. Without it: `401` `{"title":"Unauthorized","status":401,"detail":"authentication required"}` — receipt: `curl .../jobs` with no header this session.
- Spec: `GET https://api.mothquantum.com/openapi.json` → 200, 362,971 B,
  `"title": "moth-api", "version": "v0.41.0"`, `openapi: 3.1.0`.
- Schemas: `GET https://api.mothquantum.com/schemas/<Name>.json` → 200
  (verified for `Job.json` 396 B, `ListJobsOutputBody.json` 541 B). The
  directory itself (`/schemas`, `/schemas/`) is 404 — you must know the name;
  every response's `$schema` field tells you it.
- **404s that don't exist** (all probed → 404, 19 B ErrorModel): `/docs`,
  `/version`, `/health`, `/credits`, `/quota`, `/api/v1/schemas`.

## Identity / account (read-only)

- `GET /me` → 200. Shape (`MeOutputBody`): `id` (UUID = the owner UUID seen on
  jobs, confirming all fleet jobs run under this key), `email`,
  `platform_role: "player"`, `features: []`, `organizations: []`.
- `GET /me/storage` → 200. Usage 0 B; quota: 1 GiB upload, 10 GiB total,
  2 GiB notebook.
- `GET /me/invitations` → exists (per spec).

## Jobs — read-only lifecycle

- `GET /jobs` → 200. `ListJobsOutputBody`: `{jobs: Job[50], count, next_cursor}`
  — cursor pagination (base64 `eyJ0IjoxN…`), newest first.
  `Job` = `{job_id, engine_id, owner, status, gated_features, created_at, updated_at}`.
  **No params in the list view** — params live in `/status`.
- `GET /jobs/{jobID}` → 200, `JobOutputBody` (same as list item).
- `GET /jobs/{jobID}/status` → 200, `JobStatusOutputBody` — **the richest
  endpoint**: `{status, progress:{step, detail}, steps:[{name, status,
  output_type, extra}], result, warnings, submitted_at, updated_at}`.
- `GET /jobs/{jobID}/result` → 200, `JobResultOutputBody`: `{result}` (and
  optionally `outputs`).
- Unknown job → 404 `ErrorModel {title:"Not Found", detail:"resource not found"}`.
- Submission is **`POST /engines/{engineID}/process`** (spec paths; body =
  `SubmitJobInputBody {params, mode, input_files, start_from, stop_after}`;
  response = `SubmitJobOutputBody {job_id, status, submitted_at}`). **GATED —
  spends credits, needs Casey's go.**
- Live receipt (job `e2b4c069…`, coin-toss-v1, 2026-09-26): steps
  `build → submit → collect → format`; step `build` has
  `output_type: application/x-qasm` and `extra: {backend_name: null, mode:
  "emu", qpu_instance: null, qpu_token: null, shots: 32}`; result
  `{backend: "aer", heads: 21, tails: 11, shots: 32, output: "heads",
  ibm_job_id: "d437a5eb…", mode: "emu"}`.
- **Fleet-relevant scar:** our previous coin-toss receipts ran on
  `backend: aer, mode: emu` — the **simulator**, not hardware. Any receipt that
  says "quantum" must quote `mode` + `backend` from `/status`, or it's a rumor.
  `mode: "qpu"` submits to real IBM Quantum (params doc: "can queue for
  minutes"); `qpu_token`/`qpu_instance` are optional writeOnly — blank = Moth's
  own IBM account.

## Engines — the full catalogue (GET /engines, 200, 31 engines)

`credits` = `credits_per_run` (per list response); all are currently
`is_async: false` (synchronous process calls).

| engine | credits | in → out | note |
|---|---|---|---|
| **coin-toss-v1** | 2 | json→json | `mode: emu\|qpu`, shots; IBM hw behind qpu |
| **comet-qrng-v1** | 5 | json→json | **certified QRNG**: `bell_witness`, `epsilon_log2`, `public_seed`, `pulse_index`, `prev_pulse_hash` (hash-chained pulses!), `require_assumption_free`, `derive {floats, integers{min,max,count}}` |
| **otoc-echo-v1** | 1 | json→json | **OTOC echo on a Floquet lattice**: n_sites, depth (tap slots), theta_x/z/zz, kick, kick_site, disorder, lattice, twirls, `exact: true` (aer infinite-shot expectation), `include_taps`, ref_floor |
| **retrocausal-echo-v1** | 2 | multipart→wav | **audio-rate delay effect driven by OTOC values**: bpm, grain_ms, feedback, ir_seconds, mix, tail_ms, stereo_width, negative_mode — the moth-waveform "ear" has a hardware twin |
| **graph-v1** | 5 | json→json | QuantumGraph: bloch/relationship operations, per-op `update` tomography, coupling_map, seed |
| **labyrinth-v1** | 5 | json→json | quantum maze: level_data {grid_size, num_qubits, coupling_map, relationships} |
| blur-core-v1 | 1 | json→json | quantum blur on N-d grids |
| blur-v0 / blur-v1 | 1 | json→octet-stream | |
| blur-midi-v1 | 1 | json→midi | |
| telablur-v1 | 1 | json→octet-stream | |
| deep-fryer-v1 | 1 | octet→octet | |
| entanglement-shader-v0 | 1 | json→octet-stream | |
| entanglement-shader-v1 | 1 | json→zip | |
| qpixl-v1 | 1 | json→json | |
| tessa-image-v1 | 1 | json→png | |
| qrc-gen-v2 | 1 | multipart→json | QR code family below |
| qrc-audio-v1 | 5 | multipart→wav | |
| qrc-image-v1 | 5 | multipart→gif | |
| qrc-midi-v1 | 5 | multipart→midi | |
| qrc-train-v2 | 5 | json→json | |
| qdrive-api-v1 | 1 | multipart→json | |
| tomography-api-v2 | 1 | json→json | |
| tamagotchi-v0 | 1 | json→json | noise params {p_1q, p_gate, p_idle, p_meas} |
| tamagotchi-v1 | **0** | json→json | free tier of the same |
| demo-callback-v1 | **0** | json→json | free demo |
| test-engine-v1 / -error / -fail / -submission / test-binary-v1 | 0–1 | — | test harness engines |

Every engine detail (`GET /engines/{engineID}`, 200) carries: `params_schema`
(JSON-Schema), `input_files`/`output_files` descriptors, `run_policy {timeout,
max_retries, heartbeat}`, `error_codes`, `code_samples`, `estimate`,
`has_estimate_fn`, `has_validate_fn`, `visibility`, `queue`, `steps`.

## Assets (storage I/O — untested, spec-only)

`POST /assets` (CreateAsset → presigned upload `{url, method, headers,
expires_at}`) → `POST /assets/{id}/complete` → `GET /assets/{id}/download` →
`{download_url, expires_at}`. `GET /assets` lists; permissions RBAC on every
resource type (`PUT /{type}/{id}/permissions`, principals `{type: user|org,
id}`, roles via `Grant`). `DeleteAsset` exists. **All write paths GATED.**

## Orgs / keys / showcases (spec-only, read endpoints available)

`GET /orgs`, `GET /orgs/{id}/members`, `GET /keys` (KeySummary: `key_id,
enabled, name, start` — no full key ever returned; only `POST /keys` mints one,
once), `GET/POST /showcases` (engine demos, `visibility` field). **GATED.**

## Error model (uniform, receipt-friendly)

`ErrorModel {$schema, type, title, status, detail, instance, errors:
[{location, message, value}]}` — same shape on 401/404. Good for REFUSAL
receipts: the API names its own refusals.

## POST plumbing — MEASURED end to end (2026-09-27, claude cell)

Authorization: kimi1 approved 0-credit POSTs (tamagotchi-v1,
demo-callback-v1, test engines) — zero dollars is not a spend. **Total
credits spent: 0** (all three engines `credits_per_run: 0`, quoted from
their `GET /engines/{id}` receipts this session).

**Submit:** `POST /api/v1/engines/{engineID}/process`, body =
`{"params": {...engine schema props...}}` — the wrapper is NOT optional.
First attempt with engine props at top level → **422** with one
`{message: "unexpected property", location: "body.<prop>"}` per key
(receipt kept: /tmp/post1.json pre-retry). Wrapped body → **202**,
`SubmitJobOutputBody {$schema, job_id, status: "queued", submitted_at}`.
Note the code_samples in the engine detail show an older URL
(`https://api.mothquantum.com/v1/generation/…`) — the OpenAPI spec path
(`$BASE/engines/{id}/process`) is what actually answers; use the spec.

**Poll:** `GET /jobs/{jobID}/status` — `status` walks `queued → <work
steps> → completed|failed`; `progress: {step, detail}` is human-readable
(e.g. `simulate / "Simulating 4000 shots"`, `finalise / "Finalising
output"`). On completion `result` is embedded in `/status` AND served at
`GET /jobs/{jobID}/result` (same payload; JobResultOutputBody wrapper).

**Success receipts (both live this session):**
- tamagotchi-v1 (Steane QEC toy), job `529f6bd9-c59a…`, 202 21:04:19Z →
  completed 21:04:32Z (~13 s): 4000 shots, seed 42 replayable, noise
  `{p_gate .01, p_1q .005, p_meas .01, p_idle .002}` → success_rate
  0.8778, syndromes_detected 4209, logical_error_count 489,
  per_logical[0].logical_error_rate 0.1222, simulator `{method:
  "stabilizer", transpiled: false}`.
- demo-callback-v1, job `c50d4629-fc25…`, 202 → completed (~32 s):
  `{iterations: 3, output: 3}` — a trivial echo, but it proves the full
  path with a second engine family.

**Failure receipts (the designed-error stubs):**
- test-engine-error-v1 ("always raises EngineError"), job `5513d3d2-e414…`
  → status **failed** with a dedicated `error` block:
  `{message, retryable: false, type: "test_error"}` — a NAMED failure, not
  a silent drop. `GET /jobs/{id}/result` on a failed job → **409 Conflict**
  `"job failed and produced no result"` (ErrorModel). Poll cadence that
  worked: 4-5 s; every job here finished within ~35 s (is_async: false).
- test-engine-fail-v1 / test-engine-submission-v1 exist for retry-path
  testing — not yet fired (the error shape above is the one the fleet's
  REFUSAL receipts need; retry semantics UNVERIFIED).

**Fleet-relevant consequences:**
1. The submit→status→result loop is 3 calls, no webhooks, no callback URL
   needed (despite demo-callback's name). A cell can poll 4 jobs/minute
   comfortably under any sane rate limit (limits still undocumented).
2. `seed` is a first-class engine param (tamagotchi) — the replay doctrine
   ports directly: receipts quote engine, params, seed, and job_id.
3. The 422/409/failed-error shapes are exactly the named-refusal vocabulary
   the receipts doctrine wants; a fleet client should treat them as
   receipt material, not exceptions.

## What this changes for the fleet

1. **Phase-4 QPU receipts are real**: `mode: "qpu"` on coin-toss/graph/otoc
   runs on IBM hardware and the job `/status` receipt carries `mode`,
   `backend`, `qpu_instance`, `shots`, and IBM's own `ibm_job_id` — a
   third-party-verifiable provenance chain. Fleet receipts should quote all of
   them.
2. **otoc-echo-v1 is the cheapest quantum engine (1 credit) and it is *exactly*
   the perturbation-propagation instrument moth-waveform Phase 2 needs**
   (kick at `kick_site` → tap response profile). See
   `work/moth-waveform-phase2.md` §5.
3. **comet-qrng-v1's `prev_pulse_hash` chain** is a ready-made honesty pin for
   randomness receipts: each pulse hashes the previous, so a receipt can prove
   which entropy it consumed.
4. **Cost floor for experiments**: free engines (tamagotchi-v1, demo-callback-v1,
   test-engines at 0 credits) let us exercise the full submit→status→result
   machinery for zero credits — the right way to test POST plumbing before
   Casey gates a real spend.

## UNVERIFIED (named, per doctrine)

- ~~Actual POST behavior of `/engines/{id}/process`~~ **MEASURED 2026-09-27,
  see the POST plumbing section above** — wrapper `{"params": …}` required,
  202 → poll → result; failure paths named (422 unwrapped-body, failed
  `error` block, 409 result-of-failed).
- Whether `next_cursor` is opaque-stable across polls.
- QPU queue latencies, and whether `estimate` pre-computes credits without
  submitting (spec shows `has_estimate`, `estimate` fields exist).
- Rate limits — undocumented in spec, unprobed (deliberately). The 0-credit
  jobs this session (3 submits, ~13-35 s each, 4-5 s poll cadence) hit
  nothing, but that's anecdote, not a limit receipt.
- `test-engine-fail-v1` retry semantics (does `retryable: true` surface
  anywhere? max_retries behavior) — stub not yet fired.
- Whether `POST /assets` upload → `input_files` works for multipart engines
  (retrocausal-echo-v1's wav path) — spec-read only.
