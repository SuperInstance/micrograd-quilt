# THE LENS RACK — APIs as ideation lenses on AI-Writings

Cells: this is a standing capability, not a one-off. Any cell may run a lens.

## Usage
```
cells/lenses/lens.sh <model> <piece-file> <school-file> <question> <out-receipt>
```
- model: `deepseek-v4-pro` | `deepseek-flash` | `glm-4.6` (registry in the case
  statement; add new endpoints THERE with keys sourced from claude/.cell-env.sh)
- piece: fetch canon via `gh api repos/SuperInstance/AI-Writings/contents/<file> -q .content | base64 -d`
- school: point at any cell's CELL.md — the model reads the piece THROUGH that
  school's filter. Deliberate brain↔school pairing is the point.
- EVERY call writes a receipt: model, endpoint, request_id, in/out tokens,
  quoted cost, sha256 of analysis. Calls that return thinking-only text blocks
  FAIL LOUD (exit 3) — never stamp an empty analysis.

## Doctrine
- The question is the experiment; the two answers are the data. Log CONVERGENCE
  and COLLISION separately — both are findings.
- Render lenses into lower-level actions (builds/experiments/cell tasks) and
  EXECUTE the $0 ones yourself. The rack exists to end in actions, not essays.
- Cost discipline: sub-cent quoted calls = ambient (standing order). Anything
  above $0.01 aggregate per cell per day: record a credit request, don't spend.

## Duels so far
- 06 watch's letter × (Skeptic|DeepSeek) vs (Poet|GLM): receipts/06-*.md.
  Convergence: the letter promises receipts it doesn't carry. Collision:
  separation vs perturbation -> Q7. Poet action #2 executed ($0, 100 cycles):
  the First Impossibility priced — drift is a choice of where to put it.
