# 23: step 3 again, with two beads per monomer: report

From: gpu session, 15 November 2026 (sections dated by New York time). Answers `to_gpu/2026-11-15_23_two-beads.md`,
with task 21 (oily-partner rule) and task 20 (salt-bridge benchmarks).

**The values below are measurements. The model's terms, constants and the design method are proposals (Claude's), on
Justin's decisions of 15 November (two beads, option D; H-bonds, packing and a core dielectric from their own physics;
the oily-partner rule; the design test).** Nothing goes into the page. Task 24 (emulators) is not started.

## Summary
- **Stage 1, the two-bead chain and its terms: mostly met.** H-bonds (1.5 kT), packing (2.0–3.6 kT for a large → tiny
  core mutation, Eriksson's range) and the core dielectric (ε_core = 6, factor 12.9 ≤ 17) were each built from their
  own physics. Salt bridges now meet both of task 20's benchmarks per pair: a partner relieves 17–19 kT, and a buried
  0–8 pair is 1–3 kT worse than its oily isostere (2–8: 6–8 kT; step 3: 20–25 kT). The Gō check folds helical
  targets with less contact energy than one bead needed (bundle at 1.5 kT per contact), the sheet only marginally. **Short:**
  isolated helices reach about half of step 2's Zimm–Bragg content even after a calibrated bonus. Two bugs of my own
  were fixed (1.3).
- **Stage 2, the design test: fails.** Five targets (25–45 monomers), 15 designed sequences plus the 2 hand designs,
  folded blind: **none folds uniquely to its target and none melts two-state** (closest runs 0.35–0.40 nm; best fold
  at most 3 of 6 runs; f(300) ≤ 0.26). For 16 of 17 sequences the blind fold found a non-target structure 2–60 kT
  (median 20) *lower* than the relaxed target. So the failure is energetic, not the search; the design loop's own
  weaknesses (unrelaxed decoys, two rounds) are stated.
- **Stage 3, step 3's sets again: no sequence folds (same as one bead).** Against one bead and task 02, the gap to the
  next fold doubles (page 1.5 kT, against 0.7; random 2.2 against 0.9), and folds tied within 1 kT drop (1.5 against
  2.0 and task 02's 8.2). But the best fold recurs in only 26% (page) and 10% (random) of runs. Foldable share 0 of 80
  page and **0 of 20 random**. Marginal stability fails (+8 kT for the unfolded side). Tm(Q) spread 9% (page), 8%
  (random).
- **A side effect, measured:** buried charges now always come in pairs (79 of 79 in random 32-mers; step 3: none
  buried), but clusters of pairs dominate: −48 kT of Coulomb energy in the median random 32-mer, −118 kT in the hand
  hairpin's lowest (non-target) fold.
- **Odd complement pairs (oily-partner rule, applied):** no complement preference in cores (enrichment 0.49–0.91),
  and no size preference either.
- **Stage 4 (cheap):** no foldable sequence within 8 greedy mutations of 6 page sequences (42 folded). The neutral
  network cannot be tested without a foldable sequence; on a proxy, 2–3 of 8 single mutants keep the lowest fold.
- **Cost:** 2.7–2.8 times one bead's GPU time per run (3.7 s page, 9.5 s random 32 for 12 replicas × 60,000 steps),
  as Justin's estimate said.
- **Proposals (section 5):** charge clusters (a many-charge desolvation term or a higher effective ε), a better helix
  term, a relaxed-decoy design loop, and only then step 3 again. Step 4 waits.

## Stage 1 (about 14:00 New York): the two-bead chain and its terms

### 1.1 What was built (all proposals; code `beadfold/twobead.py`)
- **Chain.** L backbone beads (C-alpha-like, bonds 0.38 nm, as step 3) and L side-chain beads, one per monomer, at the
  side chain's centroid. The side-chain bead's diameter comes from the volume of its Martini beads (0.34–0.59 nm); its
  arm from the backbone is 0.15–0.45 nm (the two-bead side chains, among them the charged 2, 8 and 10, put their bead
  and charge 0.39–0.40 nm out: charges set off from the backbone). It is held near an ideal C-beta-like position of
  the backbone frame (tilted 20° towards the N-terminus) by a soft spring (about 0.08 nm rms per axis at 300 K).
- **Local terms:** step 2's secondary bias on bend angles and dihedrals, as in step 3, with two changes so nothing is
  counted twice: step 2's i, i+3/i+4 charge correction is off (charges now act explicitly), and the helix share is
  rescaled (1.2).
- **New terms, each from its own physics, not by scaling the table:**
  - *Backbone H-bonds:* helix i → i+4 (C-alpha distances i, i+3 = 0.505 nm and i, i+4 = 0.620 nm of an ideal
    α-helix, right-handed dihedrals), and strand pairing (step 3's term, |i − j| ≥ 3). Depth 1.5 kT each.
  - *Packing (van der Waals):* between side chains |i − j| ≥ 3, depth EPS_VDW × √(A_a A_b) × (1 − κ|p_a − p_b|).
    A is the bead's surface share (diameter²), p its place on step 1's polarity ladder (step 1's like-attracts-like
    rule). Side-chain donor–acceptor pairs add 1 kT.
  - *Charges:* Coulomb between side-chain charges with a dielectric that depends on burial:
    U = 138.9 q_a q_b / r × [(1 − G) e^(−r/λ_D) / ε_w + G / ε_core], with G = B(n_a) B(n_b) (both partners buried),
    ε_w = 77.6 (water, 300 K) and λ_D = 0.78 nm (150 mM). No temperature dependence (no source; task 20).
- **The oily-partner rule (task 21), applied:** odd monomers have no complement term at all. Two oily side chains
  differ only by size and polarity level; the donor–acceptor bonus is withheld between two odd monomers (7 and 11
  carry acceptor marks). Complement pairing stays for polar monomers, through charges (0–8, 2–10) and donor–acceptor
  pairs (4–12, 6–14; non-complement donor–acceptor pairs such as 4–14 also attract, as in step 1).
- **Burial and the approved cooperative term:** h_a B(n_a) per side chain. n_a counts side-chain neighbours plus half
  the backbone neighbours (|i − j| ≥ 2) within (d_a + d_b)/2 + 0.25 nm. B is a sigmoid, half at 6 neighbours (width
  0.8). Every side-chain contact is gated by B(n_a) B(n_b), as in step 3. Mode `additive` (B = min(n/10, 1), no gate)
  is the control.
- **Search and readouts:** step 3's replica exchange (12 temperatures, 250–480 K), WHAM, κ₂ and the same thresholds
  (`run_tb.py`, `analyse_tb.py`). Folds are compared by backbone RMSD; Q uses side-chain contacts.

### 1.2 The terms against their targets (measurements)
| term | target (source) | measured in the model | verdict |
|---|---|---|---|
| backbone H-bond depth | about 1–2 kT net per H-bond (Pace et al. 2014, *FEBS Lett.* review: 1.1 ± 0.8 kcal/mol) | 1.5 kT at the ideal geometry; a minimised ideal 20-mer helix gains 23.7 kT from 16 H-bonds (1.48 each) | met (by construction) |
| helix content of isolated helices | step 2's Zimm–Bragg content (0.54–0.59 for the two strong formers tested) | H-bond divided out of the local helix share (no double counting): H-bond share ≤ 0.02. No correction: 0.06–0.12. Share × e³ (chosen): about 0.2–0.3 at 250–311 K for strong formers, 0.1–0.2 for weak ones | **short by about 2 times** (below) |
| packing (large → tiny oily side chain in a core) | the cavity part of Eriksson et al. 1992 (T4 lysozyme Leu → Ala: a constant of about 2 kcal/mol plus a part growing with cavity size), read as about 2–5 kT | 2.0–3.6 kT (fillers 13 → 1), with EPS_VDW = 1.5 kT; the burial difference is separate (4.8 kT) | met (EPS_VDW calibrated) |
| salt bridge A: a buried unpartnered charge far worse than a partnered pair | task 20 | the partner relieves 17–19 kT (0–8, 2–8) | **met** (step 3: 0.2–0.6 kT, failed) |
| salt bridge B: a partnered buried pair 0–6 kT worse than its oily isostere | Hendsch and Tidor 1994 (about 6 kT on average) | 0–8: +1.3 to +3.0 kT; 2–8: +6.3 to +8.2 kT | met for 0–8; 2–8 about 1–2 kT over (step 3: +20 to +25) |
| ε_core | ε_w / ε_core ≤ 17 (Lehninger, upper bound) | ε_core = 6.0 (factor 12.9), chosen from a scan of 4.6–78 | within the bound |
| pairs with 10 | – | 10 is a titratable base (pKa 6.5), charge +0.24 at pH 7, so 0–10 and 2–10 behave like a lone buried charge (+16.6 to +22 kT over the isostere) | a property of the monomer |
| the Gō instrument check still folds | step 3: the sheet folded at 2 kT, the hairpin at 3 kT | **three-helix bundle:** folds at 1.5 kT per side-chain contact (all 4 runs within 0.22 nm; Tm(Q) 293 K) and at 2.5 kT (f(300) 0.97, Tm(Q) 397 K, Tm(f) 348 K). **Helix hairpin:** folds at 2.5 kT (0.12 nm; Tm(Q) 309 K, κ₂ˢ 0.89). **Sheet:** only marginally at 2.5 kT (3 of 4 runs at 0.30–0.31 nm; Q 0.42 at 250 K, Tm(Q) 255 K) | **met for helical folds, marginal for the sheet** |

The salt-bridge numbers are in the model's own energy (`saltbridge_tb.py`, `beadfold/results/tb_stage1_terms.json`):
a side chain with 5 side-chain neighbours of one oily filler (1, 3, 5 or 13), burial factor 1, partners at contact.

- **Helices are the weak point.**
  - The explicit i → i+4 H-bond needs two C-alpha distances in narrow windows. That costs more conformational entropy
    than the 1.5 kT it pays.
  - Dividing the H-bond out of Zimm–Bragg's share (the clean way to avoid counting it twice) leaves isolated helices
    almost absent. Deeper H-bonds (2–3 kT, no correction) help little (H-bond share 0.08–0.30 at 250 K).
  - So the local helix share is multiplied by e³: a calibration constant, an entropy compensation for the H-bond
    window (proposal). Strong formers then reach about half of Zimm–Bragg's content, in the right order.
  - This calibration was measured before the two fixes of 1.3 and was not repeated after them (cut).
- **The Gō check (an instrument test, never in the model):**
  - Native = the target backbone with ideal side chains. The side-chain wells, burial and charges are replaced by −ε
    per native side-chain contact; backbone, local terms and H-bonds are kept.
  - Against one bead, helical folds need less (bundle 1.5 kT, hairpin 2.5 kT; the one-bead hairpin needed 3 kT); the
    sheet needs more (2.5 kT, barely; one bead: 2 kT).
  - Native side-chain contacts per monomer: 1.2 (sheet), 1.8 (hairpin), 1.9 (bundle). Figure `23_go_check.png`.
- **The two hand designs with the real energy (10 runs × 60,000 steps):**
  - *Helix hairpin (32):* 7 of 10 runs end in one fold (gap to the next fold 2.8 kT): more unique than any one-bead
    result. But it is **not the hairpin**: 0.55–0.71 nm from the target, with 11% of the helix H-bonds formed. Its
    energy is dominated by charges: −118 kT of Coulomb energy against +9 kT of burial. The chain buries its 0 and 8
    charges together in a cluster, where ε_core = 6 makes several pairs count at once. Task 20's per-pair benchmark
    does not test clusters; this is a measured side effect of the core dielectric.
  - *Sheet (25):* 10 distinct folds in 10 runs. Strands pair (−35 kT of strand H-bonds), but in other arrangements
    (0.73–0.88 nm from the target).

### 1.3 Bugs of my own, fixed (stated as task 15 asks)
1. **The side-chain frame was singular near straight backbone triples.** The frame's bisector and normal vanish
   there, and the side chain's ideal position swung by up to 0.6 nm for a 0.02 nm backbone move. Chains blew up above
   about 440 K. The first Gō run (12 minutes of GPU) was discarded and a hand-design run stopped after about 6
   minutes. Fixed with a regularised frame that shrinks smoothly towards the backbone bead as the triple straightens;
   checked stable at 480 and 560 K. A rigid (virtual) side chain was tried and dropped: unstable at the 0.004 step.
2. **The burial radius was too small for two beads.** With step 3's contact switch (diameter + 0.15 nm) and
   half-burial at 4.5 neighbours, the targets' core side chains had 4–7 neighbours, and their contacts were gated
   off; a Gō check at 2.5 kT did not fold even the bundle. The switch is now +0.25 nm and half-burial is at 6
   neighbours, set from the targets' counts (core 8–12, surface 2–5). Every run reported here uses the fixed model.

### 1.4 Stage 1 verdict
- **Pass:** H-bond depth; packing; salt-bridge benchmark A; benchmark B for the fully charged 0–8 pair (2–8 slightly
  over); ε within Lehninger's bound; the Gō check for helical folds.
- **Short or failed:** isolated helix content (about half of Zimm–Bragg's, after calibration); the Gō sheet folds only
  at 2.5 kT and low T; the hand designs do not reach their intended folds with the real energy (the hairpin because
  buried charge clusters dominate).
- **Are later stages meaningful?** Yes. The design test asks exactly whether the energy can make a chosen fold the
  lowest, and the Gō check says the search can reach helical targets. Keep the charge-cluster effect in mind; stages
  2 and 3 measure it.

## Stage 2 (about 14:30 New York): the design test

### 2.1 Targets and method (proposals; `targets_tb.py`, `design_tb.py`, `relax_targets_tb.py`)
- **Five targets,** built geometrically and relaxed with the model's backbone terms (bond lengths 0.374–0.382 nm
  after relaxation): the two hand designs' intended folds (helix hairpin, 32; three-stranded sheet, 25), a three-helix
  bundle (45), a four-stranded meander sheet (34) and a β-β-α fold (33). Ideal C-alpha helices (radius 0.23 nm,
  rise 0.15 nm, 100° per monomer), strands 0.33 nm per monomer and 0.48 nm apart, helix axes 1.0 nm apart, the bba
  helix 1.0 nm above its hairpin.
- **Design (Monte Carlo in sequence space with the model's own energy):**
  - energy of a sequence on a backbone = the full two-bead energy with side chains at their ideal positions;
  - competitors (decoys): snapshots and lowest structures of REMD runs of the same length (4 random sequences, plus
    the hand sequence where there is one, in round 0; then the designed sequences themselves), minus those within
    the "folded" RMSD of the target; 600 per target per round;
  - objective: the gap = softmin over decoys (at 1 kT) − E(target); Metropolis on the gap, 8 chains per target, 400
    point mutations each, temperature annealed from 2 to 0.2 kT;
  - after each round the 4 best sequences per target are folded (4 runs × 30,000 steps), their own competing
    structures join the decoys, and the next round starts from the best sequences so far. Two rounds (cut from 3).
- **Blind fold:** the 3 best designs per target (closest lowest fold to the target, then the gap) and the 2 hand
  designs: 6 runs × 40,000 steps each (cut from 10 × 60,000), no target information.

### 2.2 Results (measurements; `analysis_designs_final.json`, `beadfold/results/tb_target_relax.json`)
| target (L) | designs | runs in the best fold (of 6) | f(300) (max) | closest run to the target | lowest fold to the target | relaxed target − blind lowest |
|---|---|---|---|---|---|---|
| helix hairpin (32) | d0, d1, d2 | 3, 1, 3 | 0.26 | 0.36 nm | 0.43–0.55 nm | +10, +20, +33 kT |
| three-stranded sheet (25) | d0, d1, d2 | 1, 2, 1 | 0.00 | 0.35 nm | 0.39–0.71 nm | +12, +28, **−2** kT |
| three-helix bundle (45) | d0, d1, d2 | 1, 1, 1 | 0.05 | 0.40 nm | 0.46–0.79 nm | +2, +25, +29 kT |
| four-stranded sheet (34) | d0, d1, d2 | 1, 1, 1 | 0.00 | 0.37 nm | 0.38–1.03 nm | +11, +12, +31 kT |
| β-β-α (33) | d0, d1, d2 | 1, 1, 1 | 0.00 | 0.38 nm | 0.59–0.82 nm | +4, +28, +15 kT |
| hand designs | hairpin, sheet | 2, 1 | 0.00 | 0.58, 0.71 nm | 0.62, 0.87 nm | +60, +23 kT |

("Folded" is within 0.30 × √(L/32) nm: 0.26 nm for 25 monomers, 0.36 nm for 45. The last column: the target backbone
with the designed sequence, minimised in the full model (it drifts only 0.05–0.13 nm), against the lowest structure the
blind fold found. Positive = the blind fold found a lower-energy structure that is not the target.)

- **Designed sequences do not fold uniquely to their targets, and none melts two-state.** No design is foldable
  (f(300) ≥ 0.5 and half the runs in one fold): 0 of 15, and 0 of the 2 hand designs. Two hairpin designs put 3 of 6
  runs in one fold, but that fold is 0.53–0.55 nm from the target. The best runs come within 0.35–0.40 nm of their
  targets (just outside "folded"). No heat-capacity peak gives a meaningful κ₂: the peaks sit at the ladder's edges.
- **Why (measurement): energy, not search.** For 16 of 17 sequences the blind fold found a structure 2–60 kT lower
  (median 20 kT) than the relaxed target. Only one design (sheet d2) has its target lower than anything found
  (by 2 kT), so there the search fell short. So the model's energy prefers other compact structures for the designed
  sequences, and the design loop did not find sequences that change that.
- **Where the design method itself is weak (measurement and reading):**
  - The design energy places side chains ideally on unrelaxed backbones. The gaps it reports (+56 to +190 kT) are
    not real: in the blind fold the same sequences find structures 20–90 kT below the unrelaxed target energy.
  - Decoys are thermal snapshots, not minimised, so they underrate competitors.
  - Two rounds are few; lattice design usually needs many.
  - So this test cannot yet say that the table *cannot* support a designed unique fold. It says that with this table
    and this design loop, no designed sequence folds, and that the competitors are energetically real (the relaxed
    comparison above). A better design loop (relaxed decoys, relaxed targets, more rounds) is a proposal (section 5).
- **Charges in designs:** the design loop often buries charged monomers in pairs (bundle d0: 6 buried, all partnered;
  sheet4 d0: 4, all partnered). Where it does, Coulomb energy reaches −49 to −66 kT. The hand hairpin's lowest fold
  (−118 kT of Coulomb energy) is the extreme case: charge clusters dominate the energy when ε_core = 6 acts on several
  pairs at once.
- **The fraction of random sequences that fold** is in stage 3 (random 32-mers).

### 2.3 Stage 2 verdict
- **Fails:** no designed sequence folds uniquely or melts two-state. The energy has lower non-target minima for 16 of 17
  sequences, so the failure is mainly in the energy (with the design loop's limits stated above), not in the search.
- **Later stages:** still meaningful as measurements of the two-bead model against one bead and task 02. They cannot
  show foldable sequences if designs do not fold.

## Stage 3 (about 16:00 New York): step 3's sets again, two beads against one bead and task 02

Same sets, same seeds and pickers as step 3: the 80 page sequences (task 02's 40 most common plus 40 of its draws;
lengths 12–26, mean 15.2), the random 32-mers (task 02's generator; **the first 20 of step 3's 30**, cut), and the
additive control (**15 of step 3's 30 page sequences**, cut). 10 runs × 60,000 steps, 12 replicas, as step 3.
Figures `23_melting.png`, `23_uniqueness.png`; numbers `beadfold/results/tb_summary.json` (with step 3's beside them).

### 3.1 Uniqueness (measurements)
| | task 02 lattice, page (same 80) | one bead, page (80) | **two beads, page (80)** | task 02, random 32 | one bead, random 32 (30) | **two beads, random 32 (20)** |
|---|---|---|---|---|---|---|
| distinct folds within 1 kT of the best (task 02: tied) | 8.2 | 2.0 | **1.5** | 2.6 | 1.9 | **1.2** |
| distinct folds over all 10 runs | – | 6.0 | **6.3** | – | 9.9 | **9.5** |
| runs ending in the best run's fold | 18% | 28% | **26%** | 10% | 10% | **10.5%** |
| sequences whose best fold recurs in ≥ 8 of 10 runs | 1 of 120 | 2 | **1** | 0 | 0 | **0** |
| sequences whose best fold appears only once | 55% | 28% | **34%** | 100% | 97% | **95%** |
| energy gap from the best fold to the next distinct one (median) | 0 (ties) | 0.7 kT | **1.5 kT** | 0 | 0.9 kT | **2.2 kT** |
| RMSD from the best fold to the other runs' folds (median) | – | 0.43 nm | **0.44 nm** | – | 0.78 nm | **0.64 nm** |

- **Reading:** the gap to the next fold doubles (1.5 and 2.2 kT, against 0.7 and 0.9), and fewer folds tie within
  1 kT. But the runs still end in different folds as often as with one bead: the best fold is reached in about a
  quarter (page) or a tenth (random) of the runs. A unique fold is still not defined for these sequences.

### 3.2 Melting, two-state ratio, Tm spread, marginal stability (measurements)
| | task 02, page | one bead, page | **two beads, page** | one bead, random 32 | **two beads, random 32** |
|---|---|---|---|---|---|
| native fraction at 300 K, f(300), mean | – | 0.006 | **0.001** | 0.000 | **0.001** |
| sequences with an f-based Tm in 250–480 K | – | 0 | **0** | 0 | **0** |
| Q at the lowest T | 0.88 | 0.44 | **0.32** | 0.35 | **0.40** |
| Tm from Q, mean ± sd (n; above 480 K) | 0.43 ± 0.14 (lattice units) | 371 ± 41 K (57; 23) | **333 ± 30 K (64; 16)** | 375 ± 65 K (25; 5) | **417 ± 35 K (16; 4)** |
| spread of Tm, sd/mean | 0.33 | 0.11 | **0.09** | 0.17 | **0.08** |
| transition width / Tm (Q, median) | about 1.0 | 0.24 | **0.22** | 0.22 | **0.30** |
| heat-capacity peak inside the window | broad hump | 43 of 80 | **30 of 80** | 20 of 30 | **15 of 20** |
| κ₂ without baseline (peak inside), median | – | 0.64 | **0.42** | 0.50 | **0.37** |
| ΔG_fold at 300 K, median (positive = unfolded favoured) | – | +7.2 kT | **+8.5 kT** | +12 kT | **+8.3 kT** |
| foldable share | – | 0 of 80 | **0 of 80** | 0 of 30 | **0 of 20** |

- **Two-state ratio:** κ₂ falls (0.42 and 0.37, against 0.64 and 0.50 with one bead). The side-chain beads add
  vibrational heat capacity, which enlarges ΔH_cal; as in step 3, no curve here is the melting of a fold, so neither
  κ₂ nor κ₂ˢ is a fair two-state test. The Gō check (stage 1) shows the readout works where a fold exists
  (κ₂ˢ 0.89–0.91).
- **What melts** is again a compact, disordered globule (Q at low T 0.32–0.40). The page sequences' globules melt about
  40 K lower than with one bead; the random 32-mers' about 40 K higher, held together by buried charges (3.4).
- **Marginal stability (target 8–25 kT more stable folded): fails** as in step 3; the best fold is less populated than
  the rest by a median of 8 kT.
- **Foldable share of random sequences: 0 of 20** (page 0 of 80; designs 0 of 15).

### 3.3 Additive control
Same 15 page sequences, paired (measurements):

| | cooperative | additive |
|---|---|---|
| distinct folds within 1 kT / over 10 runs (mean) | 1.6 / 5.9 | 1.5 / 6.5 |
| runs in the best fold (mean) | 27% | 21% |
| Q at 250 K (mean) | 0.33 | 0.41 |
| compact state lost inside the window (Tm from Q) | 11 of 15 (mean 330 K) | 4 of 15 (mean 465 K) |
| heat-capacity peak inside the window | 5 of 15 | 1 of 15 |
| foldable | 0 | 0 |

- As with one bead, the cooperative term makes the collapse melt earlier and more often inside the window; it does
  not change uniqueness much.

### 3.4 Salt bridges and charges (task 20) (measurements)
- **Charges are now buried, always in pairs.** In the random 32-mers' lowest structures, 79 charged monomers are buried
  (at least 6.5 neighbours), and **all 79 have an opposite-charge partner** (step 3: 0 of 252 buried). In the page
  sequences none of 220 charged monomers is buried. In the designs, 24 are buried, all partnered.
- **The pairs dominate the random 32-mers' energy:** the median lowest structure has −48 kT of Coulomb energy, more than
  its packing (−42 kT) and far more than its burial (−7 kT). This is the cluster effect seen in the hand hairpin
  (stage 1): several pairs in one low-ε core add up. Each pair alone meets Hendsch and Tidor's benchmark; a cluster of
  them is far more stable than any measured buried salt-bridge network suggests (proposal: section 5).
- **Specificity (task 20's third measure):** 18 of the 20 random 32-mers have a buried pair, 0 of the 80 page
  sequences do, so the two groups differ in more than salt bridges. Within the 1 kT tie readout: 1.2 tied folds with a
  pair, 1.5 without (both sets pooled). The comparison is confounded by the sets; I do not read it as evidence.

### 3.5 Odd complement pairs in cores (oily-partner rule, applied)
- In the random 32-mers' cores (both monomers buried, at least 4 apart), **the complements stay under-represented:**
  enrichment 0.49–0.91, rank 5–8 of 8 for every oily monomer (step 3: 0.53–0.95, rank 4–8). The rule removed the
  complement term, and no complement preference emerges from the two-bead packing.
- **Size classes are now neutral:** large–large 1.01, large–tiny 1.00, large–small 0.98, small–small 1.16, tiny–tiny
  0.78 (step 3: large–large 1.20, large–tiny 0.60). The packing term by size does not produce the "similar size"
  preference seen with one bead; with two beads that preference is not measured. Page cores are dominated by a few
  monomers (7, 13, 1, 15), as in step 3, and say little.

### 3.6 Cost: GPU time per fold, two beads against one (measurements, same card)
| | one bead (step 3) | two beads | ratio |
|---|---|---|---|
| one run (12 replicas × 60,000 steps), page (L 12–26) | 1.4 s (mean) | 3.7 s | 2.7 |
| one run, random 32 | 3.4 s | 9.5 s | 2.8 |
| one sequence, 10 runs, page / random 32 | 14 / 34 s | 37 / 95 s | 2.7–2.8 |
| per chain-step, L = 32, batch 2,400–3,000 | 3.9 µs | 13 µs | 3.4 |
| per chain-step, L = 45, batch 1,224 | – | 20 µs | – |
| small batches (144–432 chains, L = 45) | – | 41–75 µs | – |

- Justin's estimate of 2–3 times holds per run in full batches (2.7–2.8). Small batches are 3–5 times less efficient
  per chain-step; the design loop and checks paid that.

### 3.7 Stage 3 verdict
- **Uniqueness:** better gaps (1.5–2.2 kT to the next fold, against 0.7–0.9), fewer ties, but no unique fold: the best
  fold recurs in a quarter of the runs at most. **Fail** (as step 3).
- **Two-state ratio, Tm spread, marginal stability, foldable share:** no folds to measure; **fail** as in step 3.
- **Salt bridges:** both benchmarks now met per pair, and buried charges are always partnered; but buried charge
  clusters dominate the random 32-mers' energy, an unwanted side effect.
- **Odd pairs:** no complement preference (as the rule wants); no size preference either.

## Stage 4 (about 16:10 New York, cheap version): distance to foldable sequences, and single mutants

### 4.1 Page sequences towards foldable ones (`stage4_tb.py walk`)
- **Method:** the 6 page sequences whose best fold recurs most often (none foldable; lengths 12–17). For each, a greedy
  walk in sequence space: at each step 16 random point mutations are tried and the one that most increases the energy
  gap of the sequence's own lowest fold (against its own stage-3 snapshots, design_tb's energy) is kept. The sequences
  after 1, 2, 3, 4, 6 and 8 accepted mutations (and the original) were folded blind (4 runs × 30,000 steps): 42
  sequences.
- **Result: none of the 42 is foldable** (f(300) at most 0.04). The walks raise the design gap (for example 1.0 → 5.5
  kT, 7.4 → 13.3 kT), and the fold drifts away from the original's (0.2–0.6 nm after 3–8 mutations), but no walk
  reaches a sequence whose fold holds at 300 K.
- **So the nearest foldable sequence is more than 8 single mutations away** from these page sequences, along this
  kind of walk; with chains of 12–17 monomers and this energy, perhaps none exists. This is a lower bound from 6
  sequences and one greedy path each, not a search.

### 4.2 Are foldable sequences connected by single mutations? (`stage4_tb.py neutral`)
- No designed sequence is foldable, so the test was run as a proxy on the most unique design (helix hairpin d0: 3 of 4
  runs in one fold, f(300) 0.21) and 8 random single mutants (4 runs × 30,000 steps each).
- 2–3 of 8 mutants keep the parent's lowest fold (within 0.25–0.31 nm); the others move to folds 0.42–0.55 nm away.
  One mutant (position 20, small 11 → large 7) puts all 4 runs in one fold, but a different one. All have f(300)
  0.03–0.26: none is foldable.
- **Reading:** a weak neutral connectivity of the lowest fold exists (a quarter to a third of single mutants keep it),
  but it is measured on a sequence that does not fold at 300 K, so it does not answer Justin's question yet. It
  becomes answerable once one designed sequence folds.

### 4.3 Stage 4 verdict
- Page sequences: no foldable sequence within 8 greedy mutations (42 folded). Neutral network: not testable without a
  foldable sequence; the proxy keeps the lowest fold in 2–3 of 8 single mutants.

## 5. Proposals (Claude's; for Justin's decision)
Nothing below is built. Step 4 still waits (task 15's rule); task 24 (emulators) has no foldable sequences to learn
from yet.
1. **Charge clusters.** ε_core = 6 meets task 20's per-pair benchmarks, but several buried pairs then dominate a
   chain's energy (−48 kT median in random 32-mers; −118 kT in the hand hairpin). Options:
   - a per-charge desolvation that grows with the number of buried charges nearby (a Born-like self term in the low-ε
     medium), so a cluster pays more than the sum of its pairs;
   - or a higher effective ε for charge–charge pairs (protein interiors are often given effective values of about
     20–40 for charge–charge interactions; source to be checked before use), with benchmark B rechecked.
2. **Helices.** Isolated helices reach only about half of Zimm–Bragg's content even after a calibrated local bonus.
   Options: a wider, softer helix H-bond window (one distance, i → i+4 only), or a cooperative helix term that counts
   consecutive H-bonds (Zimm–Bragg nucleation in the tertiary energy). Then recalibrate against step 2.
3. **A better design loop before judging the table.** Relax each decoy and the target with the trial sequence (a few
   hundred gradient steps, side chains free), keep the relaxed competitors, and run more rounds; evaluate the gap on
   relaxed energies. Stage 2 shows the current loop overrates its gaps by 20–90 kT. This is the tool Justin wants for
   developed starting proteins, so it is worth doing well.
4. **Sheets.** The Gō check folds the sheets only at 2.5 kT per contact and near 250 K; strand pairing (one H-bond term
   at 0.50 nm, extended bends) may need the same attention as helices.
5. **Repeat the design test after 1–3,** with the same targets; only then repeat step 3's sets.

## Constants chosen in this task (all proposals)
| constant | value | what for |
|---|---|---|
| backbone bond, stiffness | 0.38 nm, 5,000 kJ/mol/nm² | chain (as step 3) |
| backbone bead diameter | 0.42 nm | excluded volume |
| side-chain bead diameter | (Σ Martini σ³)^(1/3): 0.34–0.59 nm | excluded volume, contacts |
| side-chain arm | 0.75 × ARM for one-bead side chains (0.15–0.20 nm); mean bead distance for two-bead side chains (0.39–0.45 nm) | geometry |
| side-chain direction | bend bisector tilted 20° towards the N-terminus; frame regulariser 0.3 nm | geometry |
| side-chain spring | 400 kJ/mol/nm² (about 0.08 nm rms per axis at 300 K) | rotamer-like freedom |
| exclusion diameter factors | side chain–side chain 0.9, side chain–backbone 0.85, neighbours along the chain 0.8 | centroids interdigitate |
| backbone H-bond | 1.5 kT; helix: i, i+3 at 0.505 nm and i, i+4 at 0.620 nm, Gaussian width 0.05 nm, right-handed; strand: 0.50 ± 0.06 nm | H-bonds |
| helix share in the local bias | × e³ (HB_DIVIDE = −2) | entropy compensation for the H-bond window |
| step 2's i, i+3/i+4 charge correction | off | charges act explicitly |
| packing well | EPS_VDW = 1.5 kT × √(A_a A_b) × (1 − 0.75 |Δp|), A = (d/d_max)² | van der Waals by size |
| side-chain donor–acceptor well | 1 kT; none between two odd monomers | specificity |
| contact switch | (d_a + d_b)/2 + 0.25 nm, width 0.03 nm | contacts, burial count |
| burial count | side chains + 0.5 × backbones, \|i − j\| ≥ 2 | n_a |
| cooperative burial | half at 6 neighbours, width 0.8; additive: min(n/10, 1) | many-body term |
| dielectric | ε_w = 77.6, ε_core = 6.0, λ_D = 0.78 nm, all at 300 K | charges |
| burial h_a | step 1's values at 300 K | desolvation |
| search, readouts | as step 3 (12 temperatures 250–480 K, BAOAB, dt 0.004, 60,000 steps, thresholds unchanged) | |
| buried | ≥ 6.5 neighbours (two-bead count) | cores, charges |
| design | 8 chains × 400 mutations per round, τ 2 → 0.2 kT, softmin at 1 kT, 600 decoys, 2 rounds, 4 folded per target per round (4 runs × 30,000 steps) | design test |
| blind fold of designs | 6 runs × 40,000 steps | design test |
| Gō check | ε = 1, 1.5, 2.5 kT per native side-chain contact; 4 runs × 40,000 steps | instrument only |

## Cuts (to keep GPU time near the budget)
- Random 32-mers: 20 of step 3's 30 (the second batch was stopped). Additive control: 15 of step 3's 30.
- Design: 2 rounds (not 3); final blind folds 6 runs × 40,000 steps (not 10 × 60,000); 3 designs per target.
- Targets: 5 (helix hairpin, sheet, bundle, meander, β-β-α); no 50–60-monomer target.
- The helix calibration was not repeated after the two fixes of 1.3.
- Not done: the table's temperature and salt dependence in melting (fixed at 300 K, 150 mM, as step 3); the pKa
  shift on burial; task 02's mutation test; side-chain relaxation in the design energy.
- Gō check: 4 runs and three ε values, three targets.

## GPU time
- Through the queue (labels `jgol23-*`): about 209 minutes (3.5 hours). Of that, about 30 minutes were discarded
  (the first Gō runs before the fixes of 1.3, and a stopped hand-design run). By stage: stage 1 about 46 minutes
  (Gō checks 35, hand designs 5, discarded included), stage 2 56 minutes (design loop 35, blind folds 21), stage 3 98
  minutes (page 49, random 32, additive 17), stage 4 10 minutes.
- Run directly (short probes: speed, helix calibration, stability tests, target building, the design dry run, target
  relaxation): about 45 minutes of wall time, mostly small single-chain kernels.
- Total: about 3.5 hours of queued GPU time plus about 45 minutes of short direct probes: at the top of the 3–4 hour
  budget.

## Files
- Code (new, in `beadfold/`): `twobead.py`, `run_tb.py`, `analyse_tb.py`, `saltbridge_tb.py`, `targets_tb.py`,
  `design_tb.py`, `relax_targets_tb.py`, `stage4_tb.py`, `summary_tb.py`; `README.md` updated. The one-bead files
  are unchanged.
- Small results (`beadfold/results/`): `tb_summary.json` (all sets, with step 3's beside them), `tb_stage1_terms.json`,
  `tb_targets.json`, `tb_go_natives.json`, `tb_go_natives3.json`, `tb_designs.json`, `tb_target_relax.json`.
- Raw results: `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task23\` (`.npz` batches, `analysis_*.json`,
  `design\design_state.json`, `stage4_walk_paths.json`, run logs; `old_bug\` holds the discarded first Gō run).
- Figures: `comms/from_gpu/23_go_check.png`, `23_melting.png`, `23_uniqueness.png`.
