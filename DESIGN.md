# micrograd-quilt — design law (full-quilt lane, amended 2026-09-21)

Three questions micrograd cannot ask, per fleet brief. Engineering amended per
critic ref M3-01 (MiniMax-M3 hostile review, 2026-09-21 ~01:10Z):

1. WHERE DOES FLOAT BACKPROP BREAK — stochastic rational auditor (default,
   ~1/sqrt(N) node promotion to fractions.Fraction, per-path confidence
   intervals; calibrated measurement, NOT claimed equivalence). Full-twin
   `--exact` mode retained opt-in for small graphs; Demo A pins under it.
2. PROVE WHAT IT DID — 5-opcode WAL (BIND/LINK/EFFECT/VIEW/TICK + FORGET for
   GC) with fnv1a hash chain. Framing is determinism/regression guard
   (replay == live graph, bitwise), NOT an equivalence theorem. tape+replay
   target ~100-150 lines.
3. HOW DOES THE ENGINE EVOLVE — ship ONLY the genotype encoding (tape =
   genotype) + a minimal seeded 3-generation consumability demo. No in-repo
   MAP-Elites; the real negative-space GAN breeds tapes via the-tap PR #7.
4. COMB GOES FLOAT-NATIVE — default view = two backward passes under
   different topo/reduction orders, teeth shaded by disagreement; the
   rational auditor supplies exact ground-truth spot-checks on sampled paths.

Dependency-free: stdlib only (fractions, fnv1a, json, math, random). Every
constant derived or cited in a comment.

Fleet doctrine pins:
- negative-space GAN + binary viability floor: SuperInstance/the-tap
  NEGATIVE-SPACE-GAN.md @ 2c60f314, PR #7 (151/151 green at review);
  tripwire floor doctrine per PR #6.
- 5-opcode WAL kernel + fnv1a hash chain: fleet WAL doctrine (the-tap).
- commensuration comb: quilt-studio 11-window comb doctrine (threshold
  teeth = instability markers).
