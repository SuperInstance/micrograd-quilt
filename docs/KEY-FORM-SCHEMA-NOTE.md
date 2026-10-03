# Key-Form Schema Note — mavis-workspace adoption (2026-10-03)

Source: SuperInstance/mavis-workspace (01:42Z 10/3), flagged as SYNERGY CANDIDATE in
edge-watch 2026-10-03 (fleet-triage PR #5). Adoption, not rivalry.

## The key form (three laws, copied not paraphrased)

1. **Null-forced last_measured** — a measurement key must exist and be null-forced;
   absence of the key is a schema error, not a missing-value error.
2. **Refuted-warns-if-empty** — a refuted-claims section that is empty must still be
   present and must say so; silence is not empty.
3. **known_failures names the mistake CLASS** — every entry names the class of the
   mistake (off-by-one, stale-premise, dropped-memory-tree), never just the instance.

## Adoption map onto fleet surfaces

| mavis law | fleet surface | status |
|---|---|---|
| null-forced last_measured | /srv/fleet/ws handoff keys (.fleet-scout markers, readyz preflight) — a handoff key absent must fail loud, not read as "not yet" | adopt in ws README |
| refuted-warns-if-empty | doubt-ledger discharge grammar — unreasoned discharge = blindness again; an empty covered_by must print EMPTY, not vanish | aligns with existing law, cite |
| known_failures names class | our own receipt practice: incidents already name classes (plumbing-rebuilt tree, mislanded commit, dropped-memory) | already live; formalize wording |

## Boundaries (honest)

- This is a schema-note, not a dependency: no code imports mavis-workspace.
- Weight law: CANDIDATE until the source edge VERIFIED; flip on merge.
- Do not retro-edit old receipts to the new vocabulary; apply forward.
