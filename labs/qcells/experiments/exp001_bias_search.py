"""exp001 — champion-seeded bias search toward |01> on 2 qubits.

Prelude probes (the reason the train/verify seed split exists, measured
not assumed), then the search, then full-ledger emit + replay proof of
the champion. Findings land in labs/qcells/FINDINGS.md by the runner.
"""
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import micromoth
from qcell.emit import emit_ledger, program_to_circuit
from qcell.replay import replay_ledger
from qcell.search import genome_circuit, p_target, run_search

LAB = Path(__file__).resolve().parent.parent
LEDGERS = LAB / "ledgers"
TELEM = LAB / "experiments" / "exp001.telemetry.jsonl"
ROOT_SEED, TRAIN, VERIFY, SHOTS = 7, 101, 202, 512

print("== prelude A: mid-circuit m does not collapse (statevector VIEW) ==")
qc_a = micromoth.QuantumCircuit(2, 2)
qc_a.h(0); qc_a.cx(0, 1)
sv_no_m = micromoth.simulate(qc_a, get="statevector")
qc_b = micromoth.QuantumCircuit(2, 2)
qc_b.h(0); qc_b.cx(0, 1); qc_b.measure(0, 0)  # mid-circuit measure
sv_mid_m = micromoth.simulate(qc_b, get="statevector")
print("identical statevector with/without mid m:", sv_no_m == sv_mid_m)

print("== prelude B: seed-variance of a fixed near-champion ==")
probe = [["x", 0], ["h", 1]]
spread = [p_target(probe, s, SHOTS) for s in range(32)]
lo, hi = min(spread), max(spread)
print(f"P(01) over 32 seeds: min={lo:.3f} max={hi:.3f} -> spread {hi - lo:.3f}")

print("== search: 8 gens x pop 16, budget 6, target |01> ==")
if TELEM.exists():
    TELEM.unlink()
res = run_search(ROOT_SEED, generations=8, pop=16, shots=SHOTS,
                 train_seed=TRAIN, verify_seed=VERIFY, telemetry_path=str(TELEM))
for row in res["curve"]:
    mark = "PROMOTE" if row["promoted"] else "stall  "
    print(f"gen {row['gen']}: train_p={row['train_p']:.3f} verify_p={row['verify_p']:.3f} {mark}")

champ = res["champion"]
print("champion genome:", json.dumps(champ.genome))
print(f"champion P(01): train={champ.train_p:.3f} verify={champ.verify_p:.3f}")

print("== emit champion ledger + replay proof ==")
ledger_path = LEDGERS / "exp001-champion.jsonl"
if ledger_path.exists():
    ledger_path.unlink()
qc = genome_circuit(champ.genome)
head = emit_ledger(qc, seed=VERIFY, shots=SHOTS, path=str(ledger_path),
                   kind="qc-exp001-champion")
print("PROOF head:", head["hash"][:16], f"({head['args']['rows']} rows)")
verdict = replay_ledger(str(ledger_path))
print("replay:", "OK" if verdict["ok"] else f"REFUSED {verdict['errors']}")

out = {
    "prelude_mid_circuit_m_no_collapse": sv_no_m == sv_mid_m,
    "prelude_seed_spread": round(hi - lo, 4),
    "curve": res["curve"],
    "champion_genome": champ.genome,
    "champion_train_p": champ.train_p,
    "champion_verify_p": champ.verify_p,
    "ledger_rows": verdict["rows"],
    "replay_ok": verdict["ok"],
    "proof_head": verdict["head"][:16],
    "seeds": {"root": ROOT_SEED, "train": TRAIN, "verify": VERIFY},
}
(LAB / "experiments" / "exp001.results.json").write_text(
    json.dumps(out, indent=2, sort_keys=True))
print("results -> experiments/exp001.results.json")
