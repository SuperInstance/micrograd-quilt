"""Demo C — 3-generation breeding run over tape genotypes (seeded).

Per design law 3 (amended): this proves the genotype encoding is CONSUMABLE
(decode -> rebuild -> evaluate -> binary viability floor -> empty-cell
novelty). The real negative-space GAN breeds these tapes from the-tap PR #7
via the composition seam; nothing here is MAP-Elites.

Run from repo root: python3 -m demos.demo_c
"""

from quilt import breeder


def main():
    print("Demo C — tape-as-genotype, 3 generations, seeded")
    print(breeder.demo(seed=0, generations=3, pop=6))
    print()
    print("Demo C done — encoding consumable; floor binary; honest nulls "
          "reported as they occur.")


if __name__ == "__main__":
    main()
