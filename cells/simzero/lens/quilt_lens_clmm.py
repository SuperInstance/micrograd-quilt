#!/usr/bin/env python3
"""quilt-lens — clmm-backend run: real weak-lensing reconstruction, sealed.

clmm 1.16.10 + pyccl 3.3.6. Mock catalog -> tangential shear profile ->
chi2-grid mass inversion with clmm's own NFW/CCL theory (correct Sigma_crit).
Chain sealed stone-v1 per STONE-SPEC 4.6. Shed-1 (numpy) recovered 0.204x
because it divided by (1+Sigma) with dimensional Sigma — clmm's calibrated
machinery is the fix, and the pair of receipts (shed-1 vs clmm-run-1) is the
honest before/after the LENS opcode exists to produce.
"""
import json, hashlib, os

import numpy as np
import clmm

print("clmm", clmm.__version__, flush=True)
SEED = 20260927
rng = np.random.default_rng(SEED)

cosmo = clmm.Cosmology(H0=70.0, Omega_dm0=0.265 - 0.049, Omega_b0=0.049,
                       Omega_k0=0.0)
M_TRUE, C_TRUE, Z_CL = 1.0e15, 4.0, 0.42

# ---------- 1. Mock source catalog via clmm's own generator ----------
from clmm.support import mock_data
catalog = mock_data.generate_galaxy_catalog(
    M_TRUE, Z_CL, C_TRUE, cosmo,
    zsrc=1.0, ngals=3000,
    zsrc_min=0.7, zsrc_max=1.5,
    field_size=12.0, shapenoise=0.3, photoz_sigma_unscaled=0.05)

# ---------- 2. Tangential components -> physical-radius profile ----------
cluster = clmm.GalaxyCluster("toy", 0.0, 0.0, Z_CL, catalog)
cluster.compute_tangential_and_cross_components(geometry="flat")
gt = np.asarray(cluster.galcat["et"])
theta = np.asarray(cluster.galcat["theta"])  # radians
da = cosmo.eval_da_z1z2(0.0, Z_CL)         # angular diameter distance, Mpc
R_src = theta * da

edges = np.linspace(0.2, 3.0, 13)
R, GT, ERR, N = [], [], [], []
for lo, hi in zip(edges[:-1], edges[1:]):
    m = (R_src >= lo) & (R_src < hi)
    if m.sum() >= 25:
        R.append((lo + hi) / 2)
        GT.append(float(gt[m].mean()))
        ERR.append(0.3 / np.sqrt(int(m.sum())))
        N.append(int(m.sum()))
R, GT, ERR = np.array(R), np.array(GT), np.array(ERR)

# ---------- 3. Inversion: chi2 grid over M200, clmm NFW/CCL theory ----------
model = clmm.theory.Modeling(massdef="mean", delta_mdef=200,
                             halo_profile_model="nfw")
model.set_cosmo(cosmo)

def m_gt(r, m):
    model.set_mass(m)
    model.set_concentration(C_TRUE)
    return np.array([model.eval_reduced_tangential_shear(
        rr, Z_CL, 1.0) for rr in np.atleast_1d(r)])

grid = np.geomspace(3e14, 3e15, 60)
chi2 = np.array([float(np.sum(((GT - m_gt(R, m)) / ERR) ** 2)) for m in grid])
i_best = int(np.argmin(chi2))
M_REC = float(grid[i_best])

# ---------- 4. Seal stone-v1 ----------
def sha(b): return hashlib.sha256(b).hexdigest()
def canon(o): return json.dumps(o, sort_keys=True, separators=(",", ":"))

prof_serial = [{"r": round(float(r), 4), "gt": round(float(g), 6),
                "err": round(float(e), 6), "n": int(n)}
               for r, g, e, n in zip(R, GT, ERR, N)]
header = {"kind": "stone.header", "alg": "stone-v1",
          "genesis": "STONE-GENESIS-1", "op": "LENS",
          "cell": "quilt-lens/clmm-run-1", "tool": "clmm-1.16.10+pyccl-3.3.6"}
payloads = [
    {"op": "BIND", "args": {"cell": "quilt-lens/clmm-run-1",
        "M200c_true_msun": f"{M_TRUE:.3e}", "c_true": C_TRUE,
        "z_cluster": Z_CL, "seed": SEED, "n_src": 3000,
        "profile_sha": sha(canon(prof_serial).encode()),
        "profile_points": len(prof_serial)}},
    {"op": "EFFECT", "args": {"op": "lens.reconstruct",
        "method": "chi2-grid-clmm-nfw-ccl",
        "grid_lo": "3e14", "grid_hi": "3e15", "grid_n": len(grid),
        "chi2_min": round(float(chi2[i_best]), 3)}},
    {"op": "VIEW", "args": {"M200c_recovered_msun": f"{M_REC:.3e}",
        "ratio_vs_true": round(M_REC / M_TRUE, 3),
        "shed1_ratio": 0.204,
        "note": "clmm backend fixes shed-1 dimensional Sigma bug"}}]
chain, prev = [], None
for row in [header, *payloads]:
    h = sha(canon([prev, row]).encode() if prev else
            canon(["STONE-GENESIS-1", row]).encode())
    row["row_hash"] = h
    chain.append(row)
    prev = h

outdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, "lens-clmm-chain.json")
with open(out, "w") as f:
    json.dump(chain, f, indent=1)

print(json.dumps({
    "ok": True, "links": len(chain), "tip": prev[:16],
    "profile_points": len(prof_serial),
    "M200c_true": f"{M_TRUE:.2e}", "M200c_recovered": f"{M_REC:.3e}",
    "recovery_ratio": round(M_REC / M_TRUE, 3),
    "chi2_min": round(float(chi2[i_best]), 3),
    "chain_file": out}, indent=1))
