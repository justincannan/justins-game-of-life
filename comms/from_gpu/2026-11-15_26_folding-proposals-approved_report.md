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

## Task 27 (step 1 finished): the charge–dipole term (16 November, about 09:25 New York)

Answers `to_gpu/2026-11-16_27_charge-dipole.md` (Justin's decision of 16 November, about 00:19). **The numbers are
measurements in the model's own energy; the form of the term, the pockets and the chosen constant are proposals
(Claude's).** Sources checked (abstracts only): Sham, Muegge and Warshel 1998 (*Biophys. J.* 74: 1744) conclude that
one should use a large ε for charge–charge and a small one for charge–dipole interactions, or treat the protein's
relaxation explicitly; Schutz and Warshel 2001 (*Proteins* 44: 400): the optimal ε for self-energies is not the one
for charge–charge interactions, and ε is a model-dependent parameter. Neither abstract gives a number for this model.

### Summary
- Built as `Model2(elec='cd')` (`beadfold/twobead.py`; `'split'` and `'v23'` still work). ε_self = 5 (in Justin's
  4–6), ε_pair = 20, charge–dipole ε = ε_self. The one new constant, the effective dipole of one polar group, is
  **μ = 0.085 e·nm (4.1 D)**, calibrated on benchmark B in a polar-lined pocket. For orientation (not re-read, the
  usual textbook value): a peptide group's dipole is about 3.5–3.7 D, so the fitted value is of that order.
- **Benchmark B (buried partnered pair 0–6 kT worse than its oily isostere): met in a polar-lined pocket** at
  ε_self 5: 0–8 +3.9 to +6.0 kT, 2–8 +0.5 to +2.8 kT. **In an oily-lined pocket it stays costly:** +17 to +19 (0–8)
  and +13.5 to +15.4 kT (2–8); with no backbone near the charge, +37 to +44 kT.
- **Benchmark A (a partner relieves a lone buried charge by more than 3 kT):** met in the oily pocket (4.9–5.6 kT);
  in the polar pocket 2.9–3.8 kT, so **just short for 2–8 with filler 6 (2.9 kT)**. In a polar pocket a lone charge
  is already well solvated by dipoles, so a partner adds less; this is the model's measurement, not a choice.
- **Median Coulomb energy of random 32-mers** (pairs + net self term): task 23 −49.8 kT; step 1 (`split`, ε_self 5,
  no dipoles) +67.3 kT; **with the charge–dipole term +8.7 kT re-scored** (task 23's structures) and **+0.5 kT
  refolded** (+1.4 kT for each sequence's lowest structure). Clusters of buried pairs no longer dominate the energy.
- ε_self 4 and 6 with the same μ: at 6, B is met (0–8 +1.8 to +3.8, 2–8 −1.1 to +1.2: slightly under 0); at 4 it is
  not (0–8 +7.2 to +9.2 kT; no μ up to 0.4 e·nm meets both pairs at ε 4, because a large payback drives 2–8 below 0
  before 0–8 reaches 6). So ε_self = 5 is the value in Justin's range where the benchmark holds with one μ.

### The term (proposal; `twobead.py`)
- For each charged side chain a with Born cost U_self,a (step 1's term, ε_self 5, Born radius half the bead's
  diameter): S_a = 138.9 |q_a| μ / ε_cd × Σ_j s(r_aj) / r_aj², over its **polar neighbours j**: uncharged side chains
  with a donor or acceptor mark (4, 6, 7, 11, 12, 14) and backbone beads, |i − j| ≥ 2, inside the burial count's
  contact switch s (the same neighbourhood that buries the charge). Distances are clamped at 0.35 nm.
- Payback = U_self,a (1 − e^(−S_a / U_self,a)): an aligned dipole at small ε, saturating so that polar groups can at
  most give the charge back its water-like solvation (a choice; without it a crowded polar pocket would make a buried
  charge better than in water). Both terms are gated by the charge's burial factor, as the Born term is.
- Burial table `iso` (charged monomers get their oily isostere's h, so the charge's desolvation is counted once, by
  the Born term): chosen over `keep`, which counts it twice; with `keep`, B is +20 to +23 kT even in the polar pocket.
- Charge 10 (titratable, +0.24 at pH 7) is not counted as a dipole for others; its own Born cost is small (q²).

### Benchmarks (measurements; `charges27.py`, `beadfold/results/t27_charge_dipole.json`)
Pocket, as in step 1 and task 23: the charge has 5 side-chain neighbours (partner and fillers) and, new here, 6
backbone neighbours, all at 0.555 nm. Both numbers are measured around buried charges in task 23's random 32-mers
(median 7.6 side-chain and 6.6 backbone neighbours; effective distance √(count / Σ s/r²) = 0.555–0.558 nm). Polar
pocket: fillers 4, 6, 12, 14; oily pocket: fillers 1, 3, 5, 13. Ranges are over the four fillers; ε_self 5, `iso`.

| pocket | relief by partner, 0–8 / 2–8 (A: > 3) | pair − isostere, 0–8 / 2–8 (B: 0–6) | lone charge − isostere, 0 / 2 |
|---|---|---|---|
| step 1 (`split`, no dipoles) | 5.3–5.6 / 4.9–5.2 | 42–44 / 37–39 | 28–29 / 23–24 |
| **polar-lined, 6 backbones** | 3.2–3.8 / **2.9**–3.6 | **3.9–6.0 / 0.5–2.8** | 6.4–7.5 / 2.5–3.9 |
| **oily-lined, 6 backbones** | 5.3–5.6 / 4.9–5.2 | **17.3–19.0 / 13.5–15.4** | 14.8–15.9 / 10.5–11.7 |
| oily-lined, no backbone | 5.3–5.6 / 4.9–5.2 | 42–44 / 37–39 | 28–29 / 23–24 |
| polar-lined, 3 backbones | 2.4–3.0 / 2.1–2.9 | 9.5–11.6 / 5.3–7.6 | 9.3–10.4 / 4.7–6.1 |
| oily-lined, 3 backbones | 5.3–5.6 / 4.9–5.2 | 27–29 / 23–25 | 20–21 / 15–16 |

- Pairs with 10 (charge +0.24): relief −0.4 to +0.4 kT (a property of the monomer, as in task 23); B in the polar
  pocket 0–10 +5.1 to +7.1, 2–10 +1.2 to +3.5 kT.
- The scan of μ (0.02–0.30 e·nm) is in the JSON. B is met for both pairs over all four polar fillers only near
  μ = 0.085 at ε 5 (at 0.08, 0–8 reaches +6.9; at 0.09, 2–8 drops to −0.3; at 0.10, −1.5 to +0.8); at ε 6 from 0.075.
  The window is narrow because 0–8 and 2–8 respond alike while their isosteres differ.
- **Sensitivity:** the result depends on the backbone count. With 3 backbone neighbours instead of 6, the polar pocket
  misses B (0–8 +9.5 to +11.6). In the refolded chains (below) buried charges have their measured neighbourhoods, so
  the 3D numbers are the better test.

### Random 32-mers (measurements; `charges27.py`, `charges27_refold.py`)
| | Coulomb total, median (all runs) | each sequence's lowest | pairs | net self (Born − payback) | payback |
|---|---|---|---|---|---|
| task 23 (`v23`) | −49.8 | −47.8 | −49.8 | 0 | – |
| step 1 (`split`, ε_self 5) | +67.3 | +60.1 | −14.9 | +82.5 | – |
| **`cd`, re-scored** (task 23's structures) | **+8.7** | +6.1 | −14.9 | +24.3 | −56.4 |
| **`cd`, refolded** (20 sequences × 4 runs × 40,000 steps) | **+0.5** | +1.4 | – | +5.2 (lowest) | −36.9 (lowest) |

- Refolded with `cd`: the 20 lowest structures bury 78 charged monomers (task 23: 79), 63 of them with an
  opposite-charge partner (task 23: all 79). A buried charge has on average 2.7 polar and 2.7 oily side-chain
  neighbours. The burial term of the lowest structures is −42 kT (task 23: −7), because with `iso` a charged monomer
  buries like its oily isostere and pays its desolvation through the Born term. **Reading (Claude's):** charges are
  still buried often (about half of all charged monomers in these random chains), now lined by polar groups rather
  than clustered; whether that is too often has no benchmark here yet (a measured share of buried charges in real
  proteins would be one; not checked).
- Refolding was cut to 4 runs × 40,000 steps (task 23: 10 × 60,000); 14 minutes of queued GPU.

### Step 1 verdict
- **Met:** B in the polar-lined pocket (ε_self 5, ε_pair 20, one new constant), the oily-lined pocket stays costly,
  and random 32-mers' Coulomb energy is near zero instead of −48 kT. **Short:** A in the polar pocket for 2–8 with one
  filler (2.9 against > 3 kT), and ε_self 4 does not meet B. I take step 1 as meeting its checks, with these two
  stated, and go on (Justin may judge otherwise).

## Step 2: the cooperative helix term (16 November, about 10:50 New York)

Justin's decision of 15 November (about 21:26), item 2. **Measurements, in the model's own energy; the forms of the
term, the test hosts and the constants are proposals (Claude's).** All runs here use step 1's charges (`elec='cd'`,
`iso`). Code: `twobead.py` (`helix='coop'` and `helix='coop2'`; `'v23'` unchanged), `helix26.py`, `helix26_fig.py`;
numbers `beadfold/results/t26_step2_helix.json`; figure `26_helix.png`.

### Summary
- **Built:** Zimm–Bragg's nucleation in the tertiary energy, on the explicit helix H-bonds h_j (j → j+4):
  E_nuc = ε_nuc Σ h_j (1 − h_{j−1}), ε_nuc = −kT₀ ln σ = 6.9 kT (step 2's σ = 10⁻³, so no new constant), with
  propagation either in the local bias (`coop`) or in the H-bond term (`coop2`, below).
- **Check failed: isolated-helix content cannot be brought to step 2's Zimm–Bragg predictions with one constant.**
  - `coop` (local bias K s/(1 + K s)): content 0.02–0.07 for every K up to 100.
  - `coop2` (propagation and s in the H-bond term, one constant ε_prop): the content switches from about 0.01–0.05
    (ε_prop ≤ 4.5 kT) to 0.83–0.98 (ε_prop ≥ 6.25 kT) for all polar hosts together, whatever their length or s
    (Zimm–Bragg: 0.16–0.84). Between, at 6 kT, runs do not agree (12×16: 0.44 and 0.03) and the order of hosts is not
    Zimm–Bragg's.
  - Task 23's term (`v23`) gives a quarter to a third of Zimm–Bragg's content on polar hosts (12×20: 0.11 against
    0.54; 12×32: 0.13 against 0.78), lower than the "about half" of report 23, which was measured on other hosts.
- **Why (measurement and reading):** the narrow H-bond window (two C-alpha distances within 0.05 nm and a
  right-handed turn) costs about 6 kT of conformational entropy per H-bond, so a helix needs about 7.5 kT of energy per
  H-bond to be stable. At that scale the transition is all-or-none, and the host's side-chain size (a steric effect of
  the model) shifts it by more than step 2's s does: small side chains (14, 4: s = 1.1) form helices more readily
  than larger ones (12, 6: s = 1.3). For orientation (Pace and Scholtz 1998, *Biophys. J.* 75: 422, abstract: alanine
  has the highest helix propensity), the model's preference for small side chains is closer to real propensities than
  step 2's s ordering, but it is not what step 2 predicts. A per-H-bond energy of 7.5–7.75 kT (about 4.5 kcal/mol) is
  also several times the helix enthalpy usually quoted (about 1 kcal/mol per residue; not re-read).
- **So step 5 is not run** (task 26's order: only if 1–3 meet their checks). Step 3 (the design loop) is run with
  step 1's model and task 23's helix term (`elec='cd'`, `helix='v23'`). Options for Justin are in "Waits on Justin".

### The terms tried (proposals)
1. `helix='coop'`: E_nuc above; local helix share p = K s_i / (1 + K s_i) (step 2's per-monomer s, without its
   cooperative probability, which already contains nucleation). One constant K.
2. `helix='coop2'`: both Zimm–Bragg weights in the H-bond term:
   E_helix = Σ_j h_j [−(ε_HB + ε_prop) − kT₀ ⟨ln s⟩_{j+1..j+3}] + ε_nuc Σ_j h_j (1 − h_{j−1}), with a local bias that is
   neutral about helices (p_helix = 0.5; step 2's strand/coil split kept). One constant ε_prop (an entropy compensation
   for the H-bond window, as task 23's e³). Also tried with a wider window (0.10 nm instead of 0.05).
- Readout (fixed, as report 23's `analyse_tb.py`): helix content = share of the L − 4 helix H-bonds formed (C-alpha
  distances i, i+3 and i, i+4 within 0.08 nm of the ideal helix), Zimm–Bragg's θ analogue, WHAM-reweighted to 300 K
  (12 replicas 250–480 K, 2 runs per host). Prediction: step 2's mean helix probability (with its charge correction).
- Test hosts: polar homopolymers (12 × 12, 16, 20, 24, 32; 6 × 20; 14 × 20; 4 × 20), step 2's charge patterns on a
  polar host ((0000 8888) × 3; host 12 with 0 every fourth; host 12 with one 15). Oily homopolymers (7 × 20, 5 × 20) are
  shown for contrast only: they collapse, which Zimm–Bragg does not contain (the first scan, on step 2's oily host 7,
  was misleading for that reason and was stopped and redone on polar hosts).

### Measurements (helix content at 300 K; Zimm–Bragg first)
| host | ZB | `v23` | `coop2` 6 kT* | `coop2` 6.25 kT | `coop2` 7 kT | `coop2` wide 4.5 kT |
|---|---|---|---|---|---|---|
| 12 × 12 | 0.16 | 0.05 | 0.04 | 0.84 | 0.97 | 0.77 |
| 12 × 16 | 0.35 | 0.09 | 0.05 | 0.83 | 0.97 | 0.85 |
| 12 × 20 | 0.54 | 0.11 | 0.36 | 0.93 | 0.97 | 0.89 |
| 12 × 24 | 0.67 | 0.12 | 0.48 | 0.95 | 0.96 | 0.94 |
| 12 × 32 | 0.78 | 0.13 | 0.22 | 0.91 | 0.97 | 0.92 |
| 6 × 20 | 0.54 | 0.13 | 0.08 | 0.98 | 0.98 | 0.90 |
| 14 × 20 | 0.16 | 0.06 | 0.92 | 0.95 | 0.97 | 0.92 |
| 4 × 20 | 0.16 | 0.05 | 0.67 | 0.93 | 0.97 | 0.91 |
| (0000 8888) × 3 | 0.84 | 0.03 | 0.66 | 0.90 | 0.96 | 0.91 |
| 12, 0 every 4th | 0.19 | 0.08 | 0.04 | 0.30 | 0.96 | 0.53 |
| 12 × 24 with one 15 | 0.25 | 0.06 | 0.43 | 0.95 | 0.96 | 0.88 |

\* 30,000 steps; the two runs disagree (for example 12 × 16: 0.44 and 0.03), so these are not converged. The 6.25–7
kT columns are 60,000 steps (runs agree within about 0.1, except 12 with 0 every fourth at 6.25: 0.03 and 0.72).
`coop` at K = 3, 10, 30, 100 and `coop2` at 1, 2, 3, 4.5 kT (narrow window) and 1.5, 3 kT (wide) all give 0.01–0.07
on every host (first two scans on host 7, then on the polar hosts; the JSON holds both).
- A stability check (direct probe): an ideal 7 × 20 helix at 300 K keeps 0.86–0.95 of its H-bonds over 4,000 steps
  with ε_prop 4.5 kT and loses them within 500 steps at 1.5 kT, while REMD from random starts at 4.5 kT gives 0.03. So
  at 4.5 kT the helix is metastable: the coil wins on free energy, not on kinetics.

### Step 2 verdict
- **Fails its check.** The cooperative term is in the energy, but no single calibration constant reproduces step 2's
  graded, length- and s-dependent content; the term only moves the model between "no helices" and "all helix". The
  failure is the narrow H-bond window, not the nucleation term. Not changed further here (the window is a separate
  proposal of report 23, not approved).
- Cost: about 70 minutes of queued GPU (five scans, one stopped).

## Step 3: the design loop with relaxed targets and relaxed decoys (16 November, about 12:45 New York)

Justin's decision of 15 November (about 21:26), item 3. **Measurements; the method and its constants are proposals
(Claude's).** Model: step 1's charges with task 23's helix term (`elec='cd'`, `iso`, `helix='v23'`), because step 2
did not meet its check. Code `beadfold/design26.py`, `design26_summary.py`, `relax26.py`; numbers
`beadfold/results/t26_design_summary.json`, `t26_designs.json` (the final 15 designs and the 2 hand designs);
figure `26_design.png`.

### Summary
- **Built as decided:** every energy in the gap is a relaxed energy (side chains free); relaxed competitors are kept
  and grow each round with the designs' own blind folds; three rounds (task 23: two); gaps evaluated on relaxed
  energies against the whole competitor pool.
- **The loop now finds sequences with positive relaxed gaps:** 35 of 45 candidates (median +4.1 kT, best per target
  +10 to +27 kT). Task 23's gaps (+56 to +190 kT) were artefacts of unrelaxed structures; these are not.
- **But a positive gap against the pool does not make the target the lowest structure:** short blind folds of the
  same sequences still find non-target structures lower than the relaxed target for 41 of 45 candidates (median
  +17 kT; task 23: +20 kT for 16 of 17). In 4 of 45 the relaxed target is lower than anything the blind folds found
  (−1.0 to −5.6 kT; hairpin, sheet ×2, bundle), but those folds stayed 0.45–0.75 nm from the target, so there the
  search, not the energy, fell short. No candidate folded to its target (closest run 0.41 nm; best run's fold 0.43 nm;
  3 runs × 20,000 steps, so this is a weak test).
- **Reading (Claude's):** the competitor pool, not the relaxation, now limits the loop: each round's blind folds bring
  new, lower competitors, and the gaps of round 2 against the larger pool fall back (figure, right panel: the best
  target − fold rises again in round 2). A design loop that works for this energy needs many more rounds or
  competitors generated by folding each candidate (the expensive part).
- **Step 3's check (relaxed targets below their competitors, and designs that fold): partly met.** The relaxed-gap
  machinery works; designs that fold are not reached in three rounds.
- **Cost per designed sequence:** 3,606 s of GPU for 45 candidate sequences in three rounds: **80 s per candidate**,
  or **240 s per final design** (3 per target). Of that, relaxation 1,701 s (125,550 relaxations, 13.5 ms each in
  batches of up to 1,500), short blind folds 1,453 s (45 sequences × 3 runs × 20,000 steps), the round-0 competitor
  folds 445 s. For a developed starting protein (one target), a round costs nearly as much as for five: the
  relaxation is bound by kernel launches, not by batch size (about 9 minutes per round), and the blind folds of up to
  15 candidates take about 8 minutes per round on this card (RTX 3070 laptop GPU).

### Method (proposal)
- **Targets:** ideal side chains on the target backbone, relaxed with the trial sequence by capped gradient descent
  (2,000 steps; drift 0.09–0.19 nm). Monte Carlo proposals warm-start from the parent's relaxed target (Adam, 80
  steps).
- **Competitors:** a pool of at most 250 two-bead structures per target: task 23's blind folds of these targets'
  designs, REMD of 4 random sequences per target (2 runs × 20,000 steps, this model), then each round's blind folds
  (60 snapshots of the lower two thirds of the ladder plus each run's lowest). Structures within the folded RMSD of the
  target are not competitors. At each round's start every pool structure is relaxed with each chain's sequence (Adam,
  250 steps, side chains free) and the 16 lowest become the chain's active competitors; a proposal re-relaxes them
  from the parent's relaxed coordinates (Adam, 80 steps).
- **Objective and moves:** gap = softmin over relaxed competitors (1 kT) − relaxed target; one point mutation per
  step, Metropolis on the gap, τ annealed 2 → 0.2 kT over 60 steps per round; 6 chains per target, all 30 chains in
  one GPU batch. At each round's end the 3 best distinct sequences per target are re-scored against the whole pool,
  fully relaxed (the gaps reported), and folded blind (3 runs × 20,000 steps); the next round starts from the best
  sequences so far (closest blind fold to the target, then the gap).
- **A first attempt was stopped (bug of my own, fixed):** it relaxed the targets with Adam from ideal side chains.
  A check against gradient descent (`relax26.py`, `t26_target_relax_try1.json` in the raw folder) showed those targets
  10–70 kT too high, and all β-β-α targets of one round stuck at about +2,000 kT with side chains on top of each other.
  That run (two rounds, 51 minutes of queued GPU) is discarded; its numbers are not used above.

### Results by round (measurements; best per target, and counts of 3 candidates)
| round | target | best relaxed gap | candidates with gap > 0 | best target − blind lowest | target lower | best fold to target |
|---|---|---|---|---|---|---|
| 0 | helix hairpin | +14.6 | 3 | +7.0 | 0 | 0.49 nm |
| 0 | sheet (3 strands) | +8.0 | 2 | −1.0 | 1 | 0.51 |
| 0 | bundle | +27.2 | 3 | +11.5 | 0 | 0.65 |
| 0 | sheet (4 strands) | +2.3 | 1 | +28.4 | 0 | 0.86 |
| 0 | β-β-α | +21.5 | 3 | +2.1 | 0 | 0.55 |
| 1 | helix hairpin | +17.3 | 3 | −5.6 | 1 | 0.55 |
| 1 | sheet (3 strands) | +13.9 | 2 | −3.2 | 1 | 0.66 |
| 1 | bundle | +20.5 | 3 | −1.4 | 1 | 0.45 |
| 1 | sheet (4 strands) | +1.9 | 1 | +1.3 | 0 | 0.55 |
| 1 | β-β-α | +5.8 | 1 | +21.2 | 0 | 0.54 |
| 2 | helix hairpin | +14.8 | 3 | +7.1 | 0 | 0.54 |
| 2 | sheet (3 strands) | +4.0 | 3 | +4.5 | 0 | 0.43 |
| 2 | bundle | +16.4 | 3 | +20.2 | 0 | 0.51 |
| 2 | sheet (4 strands) | +10.2 | 2 | +24.6 | 0 | 0.78 |
| 2 | β-β-α | +2.0 | 2 | +19.1 | 0 | 0.57 |

("Best fold to target": the backbone RMSD of the candidate's lowest blind-fold structure; folded would be 0.26–0.36
nm. Every candidate's 3 runs ended in 3 different folds.)

### Step 3 verdict
- The tool Justin asked for exists and is measured (relaxed energies throughout, kept competitors, more rounds, cost
  per sequence). It does not yet produce designs that fold to their targets in three rounds; the limit is the
  competitor set, which only folding each candidate enlarges.
- **Step 5 not run** (step 2 failed its check; task 26's order). The 15 designs in `t26_designs.json` are ready for it.

## Waits on Justin (all proposals)
1. **The helix term (step 2 failed its check).** Options, Claude's preference first:
   - **a. Soften the helix H-bond geometry** (report 23's proposal 2, first half, not yet approved): one distance
     (i, i+4) in a wider, softer window, so a helix H-bond costs less conformational entropy and needs less
     compensation; keep this step's nucleation term (ε_nuc = −kT ln σ) and recalibrate on the polar hosts. This
     attacks the cause measured here. Caution, measured: widening both distances to 0.10 nm alone did not help (no
     helices up to 3 kT, nearly all helix at 4.5 kT), so whether a single softer distance gives graded content is
     untested.
   - b. Keep `coop2` and calibrate ε_prop near its switch (about 6 kT) with longer runs: helices then are
     all-or-none, the sequence enters through the model's sterics more than through step 2's s, and the per-bond
     enthalpy is several times the measured one.
   - c. Keep task 23's term (`v23`): isolated helices at a quarter to a third of Zimm–Bragg's content.
   - d. Couple step 2's Zimm–Bragg partition function directly into the tertiary energy (a mean-field helix term on
     per-monomer helical states rather than on explicit H-bonds). A larger change; listed for completeness.
2. **Step 5 waits** on the helix term (task 26's order). The design loop (step 3) is ready for it.
3. **Step 1 near-misses**, for Justin to accept or not: benchmark A is 2.9 kT (against > 3) for 2–8 with one polar
   filler, and ε_self 4 does not meet benchmark B; the chosen ε_self is 5.

## Constants chosen in task 26 steps 1–3 and task 27 (all proposals)
| constant | value | what for |
|---|---|---|
| ε_self, ε_pair | 5, 20 | Born self term, buried charge–charge pairs (Justin's ranges) |
| Born radius | half the side-chain bead's diameter (0.21–0.28 nm) | self term (step 1) |
| burial table for charged monomers | `iso` (their oily isostere's h) | desolvation counted once |
| μ (charge–dipole) | 0.085 e·nm (4.1 D), ε_cd = ε_self | task 27, calibrated on benchmark B in a polar pocket |
| dipoles | uncharged side chains with donor/acceptor marks (4, 6, 7, 11, 12, 14), backbone beads; \|i − j\| ≥ 2; the burial contact switch | task 27 |
| payback saturation | U_self (1 − e^(−S/U_self)) | at most water-like solvation |
| benchmark pocket | 5 side-chain + 6 backbone neighbours at 0.555 nm (measured) | task 27 benchmarks |
| ε_nuc | −kT₀ ln 10⁻³ = 6.9 kT | step 2, Zimm–Bragg nucleation (step 2's σ) |
| ε_prop (`coop2`) | scanned 1–7.5 kT (narrow window), 1.5–4.5 kT (0.10 nm window); none chosen | step 2 |
| design: rounds, chains, Monte Carlo | 3 rounds; 6 chains per target; 60 point mutations per round, τ 2 → 0.2 kT | step 3 |
| design: relaxation | target: capped gradient descent 2,000 steps from ideal side chains; decoys: Adam 250 steps (lr 0.008, cosine); proposals: Adam 80 steps (lr 0.004) warm-started from the parent's relaxed structures | step 3 |
| design: competitors | pool ≤ 250 per target (task 23's blind folds of these targets, REMD of 4 random sequences, then each round's folds); 16 lowest active per chain; softmin at 1 kT | step 3 |
| design: folds per round | the 3 best sequences per target, 3 runs × 20,000 steps | step 3 |

## Cuts (task 27 and steps 2–3)
- Task 27: random 32-mers refolded with 4 runs × 40,000 steps (task 23: 10 × 60,000), 20 sequences (step 3's first
  20). Benchmarks are counted pockets (5 side-chain and 6 backbone neighbours at one distance), not built 3D pockets.
- Step 2: 2 runs per host and 30,000 steps in the first scans (60,000 in the last); the switch region near ε_prop
  6 kT is not converged; the first scan on step 2's oily host 7 was stopped and redone on polar hosts; the temperature
  dependence of helix content was not measured.
- Step 3: 3 rounds (not more), 6 chains and 60 Monte Carlo steps per round, 16 active competitors per chain, pool ≤ 250
  per target; blind folds of candidates 3 runs × 20,000 steps; the first attempt (bug) discarded.
- Step 5 not run (step 2's check failed). Step 4 (sheets) not considered.

## GPU time
- Queued (labels `jgol26-*`): about 197 minutes (3.3 hours). Task 27 refold 14; step 2 scans 71 (15, 12, 4 stopped,
  21, 20); step 3: 51 discarded (first attempt, bug) and 60 for the run reported.
- Run directly (short probes: model probe, relaxation test, design dry run, helix stability, target relaxation check):
  about 37 minutes.
- Total: about 3.9 hours, at the top of the 4-hour budget; of it about 55 minutes were spent on the discarded design
  attempt and the stopped scan.

## Files (task 27 and steps 2–3)
- Code (`beadfold/`): `twobead.py` (modes `elec='cd'`, `helix='coop'`/`'coop2'`; earlier modes unchanged), `run_tb.py`
  (`--model` option), `charges27.py`, `charges27_refold.py`, `helix26.py`, `helix26_fig.py`, `design26.py`,
  `design26_summary.py`, `relax26.py`, `summary26.py` (step 5, unused), `README.md`.
- Small results (`beadfold/results/`): `t27_charge_dipole.json`, `t26_step2_helix.json`, `t26_design_summary.json`,
  `t26_designs.json`, `t26_target_relax.json` (the first design attempt's target check).
- Raw (`D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task26\`): `t27\` (refold batch and log),
  `helix_scan1..5` (JSON and logs; scan 3 stopped), `design\` (state and log of the run reported), `design_try1\`
  (discarded attempt), `design_dry\`, probes (`relaxtest.py`, `helixstab.py`), and copies of `twobead.py` and
  `run_tb.py` before this task.
- Figures: `comms/from_gpu/26_helix.png`, `26_design.png`.
