# SPEC-PREREG — hash-bound pre-registration of expectation specs

Adoption, not rivalry. This tool ports a mechanism two sibling fleet repos
converged on independently into fleet house style. Provenance, cited:

- **SuperInstance/unspoken-resonance** `3ad67d4 -> 48dcd93` — spec sealed in an
  earlier commit, cited by `spec_sha` in the implementing commit message;
  `--check` mode recomputes in memory and byte-compares, never writes;
  breach -> verdict INDETERMINATE; missing/malformed spec refuses before
  anything runs (`WARM_RUN_REFUSED`).
- **SuperInstance/madlibs-jev** `ee7b73a -> 9baec4f` — self-modification
  compile loop; `spec_sha = sha256(canon(spec))` of the pre-registered
  `spec/invariants.json`; missing spec -> `COMPILE_REFUSED` exit 1 and nothing
  happens ("a receipt of nothing would be noise"); invariant breach ->
  receipted INDETERMINATE, child identified by `child_sha` but never
  materialized; refusal is append-only history.

Convergence signal: spec-bound pre-registration is receipts-culture instance
#7/#8 org-side (edge-watch 10/4 receipts). This repo adds instance #9 with a
mechanism shaped for generic lanes: any JSON expectation doc, any run.

## Mechanism

```
spec      = JSON expectations, sealed BEFORE the run (house law)
spec_sha  = sha256(canon(spec))          # canon: sorted object keys,
                                         # compact separators, arrays ordered
seal      = append {kind:seal, spec_sha, spec_path, spec_bytes, note, chain}
            to receipts/spec-prereg.jsonl (genesis-anchored fnv1a-64
            order-sensitive chain, doubt-ledger grammar)
check     = recompute spec_sha; GREEN only if the ledger chain is intact AND
            a seal row carries exactly this hash
```

Exit codes: `0` green / `1` breach, named / `2` REFUSED, nothing written.

```
python3 tools/spec_prereg.py seal spec.json --note "R85 prereg"
python3 tools/spec_prereg.py check spec.json     # before AND after the run
python3 tools/spec_prereg.py verify              # chain-only audit
```

## House-style deltas from the siblings (reasons, not improvements-for-free)

- **Ledger is a standalone chain** (siblings embed spec_sha inside experiment
  receipts). A lane with no other receipt surface still gets pre-registration.
- **fnv1a-64 chain + sha256 spec hash, both disclosed.** sha256 binds content;
  the fnv1a-64 chain gives order-sensitive tamper-loudness in 20 lines of
  stdlib. Different jobs, both named.
- **Duplicate seal REFUSED.** Append-only means the first seal wins; a spec
  that needs revision gets a NEW file (and a superseded note), never an
  overwrite — same law as oracle1-workspace's Active/Superseded/Retracted
  tile lifecycle (edge-watch 10/4D).

## Pins — tests/pins_spec_prereg.sh (9/9 GREEN, canary RED demonstrated)

| pin | what it proves | RED state |
|-----|----------------|-----------|
| P1  | seal -> check roundtrip green | chain-disabled tool copy |
| P2  | tampered value -> BREACH named, exit 1 | observed on refusal path |
| P3  | canon reorder-stable (keys reordered -> same seal matches) | value change |
| P4  | array order IS semantic (swap -> BREACH) | — |
| P5  | missing ledger -> REFUSED exit 2 | — |
| P6  | unparseable spec -> REFUSED, ledger untouched | — |
| P7  | chain tamper -> verify names the LINE | observed; canary below |
| P8  | duplicate seal -> REFUSED, ledger length 1 | — |
| P9  | **canary**: chain-check-disabled copy exits 0 on tampered ledger — pin expectation fails against it | demonstrated in-run |

Build history (FAIL-first culture): first run was 4/9 — a real bug. Seal-time
hash excluded the row's own `chain` field; verify-time hash included it
(parsed from disk). Chain broke on every roundtrip. Fixed by hashing the
chain-stripped body at both ends; RED -> GREEN on the record in
`tests/pins_spec_prereg.log`.

## Honest limits

1. **Integrity, not authorship.** sha256 binds content; a party who can
   rewrite the ledger can re-seal a mutated spec. The chain makes tampering
   LOUD (names the line), not impossible. Same law as doubt-ledger limit #1.
2. **Bytes, not meaning.** The hash guarantees the spec you READ is the spec
   that was SEALED. Whether "stdev >= 0.5x parent" means what it should is a
   human/verifier question — pair with frozen-clock-lab style fixed-clock
   regeneration pins for the run itself.
3. **Array order is semantic.** Deliberate, sibling-identical. Reordering
   expectations is a new spec, not a reformat.
4. **No time claim.** Seals carry no timestamp by design (order-not-time law);
   git history supplies ordering when the ledger is committed.
