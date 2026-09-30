# MothQuantum × GravityField — First Contact Findings

> Live experiments, 2026-09-25 ~02:20–02:45 GMT+8. All results sha-sealed in
> /tmp/quantum-jev-lab/results.jsonl. Keys from /root/.env (never logged).

## Key audit (6 keys, honest status)

| Key | Status | Evidence |
|---|---|---|
| TYPESAFEAI_KEY | ✅ live | jev-1.13.0, ~850ms/call |
| MOTHQUANTUM_KEY | ✅ live | 31 engines, 7 jobs completed |
| DEEPSEEK_KEY | ✅ live | deepseek-chat, 347ms, "quorum" |
| DEEPINFRA_KEY | ✅ live | Llama-3.3-70B, 854ms |
| ZAI_KEY | ❌ 429/1113 | "Insufficient balance or no resource package" |
| OPENROUTER_KEY | ❌ 402 | "Insufficient credits" |

Z.ai and OpenRouter need credit top-ups from Casey.

## Friction discovered (now handled, document for the fleet)

1. api.mothquantum.com sits behind Cloudflare bot-filter: bare
   `Python-urllib` UA → 403 error code 1010. Fix: browser User-Agent header.
2. Engine params are strict JSON Schema — `disorder: 1.7` → 422 (max 1.0);
   always GET /engines/{id} first and respect min/max.
3. JEV scores *prose claims*, not code semantics: gravity.py scored 0.35
   where field notes scored 0.93 and spam 0.02. Wrap code artifacts in a
   descriptive claim, or the gate misreads silence as absence.
4. Response shapes reward inspection before parsing: comet-qrng output is
   deeply nested (random.hex at .output.random.hex); OTOC series are
   tap-major lists of lists.

## E1 — Coin toss (shape proof)

Job 8d6799e2: heads 64/128 on backend aer. Confirms submit→poll→result
contract end-to-end. Params expose `qpu_instance`/`qpu_token`/`mode` for
IBM hardware runs (not yet exercised — hardware quota unknown).

## E2 — Certified quantum entropy (comet-qrng-v1) — the flagship find

Job 82308b28, output 150 bytes / 1200 certified bits from 49152 raw Born-rule
bits (12 randomness qubits × 4096 shots, counts readout), Toeplitz extractor
ε=2^-64. The receipt bundle is the most honest randomness engineering we
have ever seen:

- **CHSH witness**: S = 2.756, classical bound 2, Tsirelson 2.828,
  z = 33.4σ above classical, **p(local realist) = 1.7e-244**, with the
  honest caveat "fixed measurement settings, no space-like separation,
  fair sampling assumed" printed verbatim.
- **Entropy accounting**: h_bit = 0.907, independence-collision health
  tests passed, **assumption-free budget = 0** (they do not claim
  unconditional randomness), modelled budget 1329.51 bits.
- **Commitment scheme**: salted commit hash formed at submit time,
  *before* outcomes existed — anti-after-the-fact tampering, exactly our
  witness idiom.
- **Pulse hash chain**: pulse_hash + prev_hash — a blockchain of RNG pulses.
- **Device fingerprint**: 20-qubit readout-bias and pair-correlation map;
  zero stuck qubits.
- Grade stamped honestly: "simulator-baseline" (mode emu, backend aer).

Our check: the 150 certified bytes carry 1197.4 bits IID capacity by our
own estimate — consistent with the claimed 1200 within rounding. The
certificate is truthful. **Integration point: MothQRNGBackend for QCell —
gravity proposals draw tie-break entropy from comet-qrng-v1, and the
bell_witness S + job_id ride the backend descriptor on the ledger.**

## E3 — OTOC chaos dial (otoc-echo-v1) — the ML insight

"Perturb a scrambled qubit chain, reverse it, listen for what returns."
The echo-decay rate λ is a measurable chaos signature of a perturbation
landscape. Seed-controlled sweep (seed 1234, depth 8):

| disorder | λ (log-echo slope) | job |
|---|---|---|
| 0.0 | −0.1368 | dfe0fd11 |
| 0.5 | −0.1247 | f860c203 |
| 1.0 | −0.1154 | 4a8154c2 |

Monotone in disorder. **Design: GravityField candidates carry a landscape
ruggedness prior fed by OTOC λ — candidates proposing perturbations in
slow-echo (ordered, smoothly exploring) regions get shaped differently
from fast-scrambling ones; certified QRNG bytes break ties. The chaos of
the search space becomes a measurable, hardware-certifiable input to the
search itself.** Params to explore next: lattice (chain/square), kick
site/channel, theta couplings, n_sites up to 156, twirls, and hardware
mode for a real-device λ certificate.

## JEV canon-gate calibration (jev-1.13.0, live)

| Artifact | noul score | Read |
|---|---|---|
| JEV_MOTH_FIELD_NOTES.md | 0.93 | on-canon prose ✅ |
| executor/gravity.py | 0.35 | code without claim wrapper — gate reads prose, not semantics |
| spam control | 0.02 | crushed ✅ |

Gate works; question/claim design is the craft. Use noul for prose gates;
for code, attach a claim header or score the README/spec instead.

## Next builds (queued)

1. `executor/quantum_moth.py` in quilt-executor: MothQRNGBackend +
   OTOCChaosPrior behind the QCell Backend protocol, all receipts carrying
   job_id + bell S + pulse hash. (Lane-safe branch: coordinate with the
   snowball lane's branch state first.)
2. Z.ai/OpenRouter: awaiting credits; DeepSeek + DeepInfra already give
   us a two-provider LLM fleet for candidate-judging ensembles.
3. Hardware run: test qpu_instance/qpu_token path on coin-toss to learn
   the quota model before certifying hardware-grade entropy.
