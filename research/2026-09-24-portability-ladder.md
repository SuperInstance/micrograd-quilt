# The Portability Ladder — quilt-executor as tiles
**Casey 16:34 — "a tool for scaling abstractions as a first-class citizen; embedding tiles as easy as spreadsheet porting"**

## Thesis
Every artifact in the executor stack is a **tile**: `{opcode ∈ BIND/LINK/EFFECT/VIEW/TICK(+FORGET),
payload, parent_hash}`. Porting a tile must be like copying a spreadsheet cell: **select → copy →
paste into another substrate**; the recipe (opcode + payload) travels, the substrate re-evaluates.
The hash chain is the clipboard format — it already IS the before/after agreement (Casey's 15:38
doctrine), so a ported tile carries its own provenance.

quilt-port already projects domains (ESP32 / Python-TS / Web-REST / Ideation-AI-Writings). Our
executor is the reference Python substrate. The ladder, bottom-up:

## Rung 1 — Library (`pip install quilt-executor`)
Stdlib-first core (zero hard deps; laya/cuopt are extras). Public API:
`Ledger, bind_ledger, TaskRequest, TaskResult, QualityScore, Evaluator, FleetRouter/dispatch,
ThompsonBandit, book_effect`. Semver from 0.3.0. Receipts protocol versioned (`RECEIPTS_V1`).
Artifact: `pyproject.toml`.

## Rung 2 — Plugin
- **OpenClaw tool surface** (`executor/tools.py`): `tick()`, `dispatch(task)`, `score(result)`,
  `verify()`, `rows(since)` — any fleet agent imports and receipts without knowing the ledger.
- **Arena bridge** (typed absence rows → MOTH REFUSAL payloads) per `research/2026-09-24-arena-wire.md`.
- Optional pytest hook: per-run EFFECT row with pass/fail counts (receipts for the test suite itself).

## Rung 3 — Web (`python -m executor.web`, stdlib-only)
Zero-dependency `http.server` app: `GET /ledger/rows?since=n`, `GET /ledger/verify`,
`POST /tick`, `POST /dispatch`, `POST /score`, `GET /stream` (newline-delimited receipts = the
SSE idiom without the dependency). FastAPI variant later as `[web]` extra. This is the
application face: any cell, any node, any browser — same receipt language.

## Rung 4 — Embedded (`ports/embedded/`)
MicroPython manifest: 5 opcodes + FNV-1a-64 + the café Δ 日本语 pin (`0x24a555471370b18d`)
as the conformance vector. `ledger_micro.py` = rows + chain + verify subset (no dataclasses,
no asyncio). An ESP32 cell can book EFFECT rows into the same family chain; verify() cross-checks
with the Python substrate (jeviter lattice doctrine: three cells, one recipe).

## Rung 5 — Spreadsheet (`executor/cells.py`)
Tile↔cell isomorphism: **a ledger row is a cell record** `{coord, opcode, payload_hash, value_view}`;
a chain segment is a column range. `to_sheet(ledger)` → grid; `from_sheet(grid)` → replay.
**Porting = copying a column of hashes between workbooks** — the spreadsheet idiom made native.
This is the rung that makes Casey right: tiles embed as easily as cells, because they ARE cells.

## Cross-rung invariants (pinned)
1. The café-pin vector verifies on every rung (one recipe, all substrates).
2. A row booked on any rung verifies on every other rung (chain is the portable format).
3. Every rung books EFFECT rows for its own operations (self-receipting ladder).
4. Fallbacks are visible: a rung that can't do something books REFUSED with the reason.
