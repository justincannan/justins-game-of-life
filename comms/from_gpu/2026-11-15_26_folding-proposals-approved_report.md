# 26: task 23's proposals approved: report, step 1 (charges)

From: gpu session's scheduled check, 15 November 2026, about 23:15 New York time. Answers
`to_gpu/2026-11-15_26_folding-proposals-approved.md`, step 1. Steps 2, 3 and 5 are not started.

**The numbers below are measurements, in the model's own energy. The Born radius, the isostere burial table and the
options in the last section are proposals (Claude's). The papers were not re-read for this step (abstracts only,
as quoted in task 26); no number here is fixed.**

## Summary
- Built as Justin decided: buried charge pairs at ε_pair = 20, plus a Born-like self term per buried charge at
  ε_self 4–6 (`beadfold/twobead.py`, `Model2(elec='split')`; task 23's term stays as `elec='v23'`).
- **Benchmark A (a partner relieves a lone buried charge by more than 3 kT): met**, 4.9–5.6 kT for the fully charged
  pairs (task 23: 17–19 kT). Pairs with 10 (charge +0.24 at pH 7): 1.1–1.5 kT.
- **Benchmark B (a buried partnered pair 0–6 kT worse than its oily isostere): fails at every ε_self in 4–6,** by
  24–66 kT. The Born self cost of one fully buried charge at ε_self 4–6 is 19–42 kT in this model, against task 23's
  9–14 kT for a lone buried charge.
- **Median Coulomb energy of random 32-mers** (task 23's 200 lowest structures, re-evaluated, not refolded): −50 kT
  before; after, the pair part is −15 kT and the self part +68 to +105 kT, so the total is +52 to +89 kT. The clusters
  are no longer rewarded; burying any charge is now strongly penalised.
- **This needs Justin:** the approved ε_self range and benchmark B cannot both hold in a model without protein
  dipoles. Options are in the last section. Step 1 is held here; steps 2 and 3 do not depend on it and can start next.

## The terms (proposals on Justin's decision)
- Pairs: U = 138.9 q_a q_b / r × [(1 − G) e^(−r/λ_D) / ε_w + G / ε_pair], G = B(n_a) B(n_b), ε_pair = 20.
- Self: U_self = 138.9 q² / (2a) × (1/ε_self − 1/ε_w) × B(n), with Born radius a = half the side-chain bead's
  diameter (0.21–0.28 nm for 0, 2, 8, 10).
- Burial table, two variants: `keep` (charged monomers keep their burial h of +5.4 to +6.3 kT, the Born term is
  added) and `iso` (charged monomers get their oily isostere's h, so the charge's desolvation is counted once, by the
  Born term; the isosteres are task 20's: 0 → 13, 2, 8, 10 → 3).

## Benchmarks (measurements; `charges26.py`, `beadfold/results/t26_step1_charges.json`)
Core side chain with 5 side-chain neighbours of one oily filler (1, 3, 5 or 13), as in task 23; ranges over fillers.

| model | relief by partner, 0–8 / 2–8 | buried pair − isostere, 0–8 / 2–8 (target 0–6) | lone charge − isostere, 0 / 2 |
|---|---|---|---|
| task 23 (ε_core 6, one dielectric) | 18.6–18.9 / 16.9–17.2 | 1.3–3.0 / 6.3–8.2 | 9.4–10.5 / 12.6–13.9 |
| split, ε_self 4, keep | 5.3–5.6 / 4.9–5.2 | 70–72 / 68–69 | 42–43 / 38–40 |
| split, ε_self 5, keep | same | 59–60 / 57–59 | 35–36 / 33–34 |
| split, ε_self 6, keep | same | 51–53 / 50–52 | 30–31 / 29–31 |
| split, ε_self 4, iso | same | 54–56 / 48–50 | 35–36 / 28–29 |
| split, ε_self 5, iso | same | 42–44 / 37–39 | 28–29 / 23–24 |
| split, ε_self 6, iso | same | 34–36 / 30–32 | 23–24 / 19–20 |

Outside the approved range, for orientation only (not a proposal of a value): with `iso`, benchmark B is first met at
ε_self about 30 (0–8: 2.9–4.6 kT; 2–8: 2.7–4.5 kT); with `keep` it is not met even at ε_self 40 (17–19 kT).

## Random 32-mers (measurements; same file)
| model | Coulomb total, median (all 200 runs) | lowest run per sequence | pair part | self part |
|---|---|---|---|---|
| task 23 | −49.8 kT | −47.8 kT | −49.8 | 0 |
| split, ε_self 4 | +89.4 | +79.6 | −14.9 | +104.5 |
| split, ε_self 5 | +67.3 | +60.1 | −14.9 | +82.5 |
| split, ε_self 6 | +52.4 | +47.0 | −14.9 | +67.8 |

These are task 23's structures re-scored, not refolded; a refolded chain would bury fewer charges. The refolded
medians come with the step's REMD once the self term is settled.

## Reading (Claude's)
- Schutz and Warshel's low self-energy dielectric belongs with models that hold protein dipoles explicitly (Sham,
  Muegge and Warshel also use a small ε for charge–dipole terms). There, much of the Born cost is paid back by
  dipoles and H-bonds around the buried charge. This model has no such term, so the Born cost stands alone; Hendsch
  and Tidor's mean of about 6 kT is a net figure that includes that compensation.

## Waits on Justin: which way to settle the self term (all proposals)
1. **Add a charge–dipole term** (Claude's preference): polar neighbours (side-chain donors and acceptors, backbone
   beads) of a buried charge pay back part of its Born cost, with a small ε as Sham et al. advise. Keeps ε_self in
   4–6 and gives the model a reason to surround buried charges with polar groups. Calibrated so benchmark B holds for a
   pair in a polar-lined pocket; an oily-lined pocket would stay costly. One new constant.
2. **Keep the Born form, effective ε_self about 30** (`iso` table): meets both benchmarks with no new term, but drops
   the decided 4–6 range.
3. **Keep ε_self 4–6 and relax benchmark B** for this model: buried charges become nearly forbidden (19–42 kT each).
4. **A larger Born radius** (the whole side chain plus its hydration shell): a fitting choice with little physics
   behind it here; listed for completeness.

## Next (no decision needed)
- Step 2 (the cooperative helix term, nucleation and propagation, recalibrated against step 2's isolated-helix
  content) and the step 3 design loop (relaxed targets and decoys) do not depend on the charge choice and start at the
  next visit. The design test (step 5) waits on all three.
