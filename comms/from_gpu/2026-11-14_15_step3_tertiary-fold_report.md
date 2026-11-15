# 15, step 3: the off-lattice tertiary folder on the GPU: report

From: gpu session, 14 November 2026, about 23:59 New York. Answers `to_gpu/2026-11-14_15_design-approved-prototype.md`
(step 3 of report 12, section 11), with task 19 item 1 and task 20.

**The values below are measurements. The model's terms and constants are proposals (Claude's), on Justin's approved
design.** Nothing goes into the page. Step 4 is not started. Code: `beadfold/tertiary.py`, `run_step3.py`,
`analyse_step3.py`, `summary_step3.py`, `saltbridge_step3.py`. Numbers: `beadfold/results/step3_summary.json`,
`beadfold/results/step3_saltbridge.json`. Figures: `15s3_melting.png`, `15s3_uniqueness_kappa.png`, `15s3_go_check.png`.

## Summary
- **Built and working as a machine.** A batched replica-exchange folder on the GPU, off-lattice, one bead per monomer.
  It uses step 1's table and burial, step 2's secondary probabilities as local biases, backbone H-bonds, and the
  approved cooperative term. No native structure is an input.
- **Step 3's main checks fail (measurement).** With step 1's table, **no sequence folds**: 0 of 80 page sequences,
  0 of 30 random 32-mers, 0 of 2 designed sequences. Below about 370 K the chains collapse into compact but **molten**
  globules. They keep 35–45% of their best structure's contacts. At 300 K that structure holds 0.6% of the population on
  average (at most 10%, in one page sequence).
- **It is not the search, and not the readouts (measurements).**
  - Five times longer runs (300,000 steps) reach the same lowest energies.
  - An instrument check with a Gō energy (contacts of a known structure; used only as a test, never in the model)
    folds the same designed chains. The sheet design melts sharply, as a two-state transition (Kaya–Chan ratio with
    baseline 0.97–1.00; width 13–25 K); the helix hairpin less so (0.84; 49 K). So the machinery and the cooperative
    term can show two-state folding.
- **Why (measurement, with a reading).** Two causes, each measured:
  - **Too weak.** In their lowest structures, chains gain about **1.1 kT per contact** (about 2 kT per monomer). An
    unfrustrated chain in this geometry needs about **2 kT per contact** (about 6 kT per monomer, for the sheet) to
    melt near 300 K.
  - **Too unspecific.** Different runs end in different compact structures within about **1 kT** of each other
    (median gap 0.7–0.9 kT), 0.4–0.8 nm apart. Burial, which ignores who touches whom, is 50–60% of the energy.
    Scaling the whole table up to 3 times does not make any chain fold.
- **Against task 02:** fewer exact ties, but no unique fold either. Within 1 kT of the best, page sequences have
  **2.0** distinct folds in 10 runs, against task 02's **8.2** tied folds for the same 80 sequences. But all 10 runs
  give **6.0** distinct folds, and the best fold recurs in **28%** of runs (task 02: 18%).
- **Odd complement pairs (task 19.1):** in the random 32-mers' packed cores, **oily monomers do not prefer their
  complements.** All 8 complement pairs are under-represented (enrichment 0.5–0.95); large with large is
  over-represented (1.2), large with tiny under-represented (0.6). This is Justin's condition for the rule "complement
  pairing for polar monomers only". It is measured on non-unique, molten cores, so it is weaker evidence than a folded
  core would give.
- **Salt bridges (task 20): both benchmarks fail.** A partner relieves only **0.2–0.6 kT** of the cost of two buried
  charges (target: far worse unpartnered). A buried pair is **20–25 kT** worse than its oily isostere pair (target:
  0–6 kT). In the folds, **no charged monomer is ever buried** (0 of 472), so the specificity question cannot be
  measured.
- **Cost (measurement):** 1.1–4.1 s of GPU time per run (12 replicas × 60,000 steps), 11–41 s per sequence for 10
  runs. That is within report 12's target of 0.5–5 s per domain for one run, but 10 runs per domain are above it.
- **Proposals (for Justin):** section 9. In short: give the table's contacts more strength and specificity before
  step 4 (backbone H-bonds and packing, which the table leaves out, and a buried-pair dielectric). The step's checks
  are not met, so by task 15's rule step 4 waits.

## 1. What was built (all proposals)

### 1.1 The chain and its energy
- One bead per monomer, bonds of 0.38 nm, off-lattice. Every term depends on the sequence only.
- **Local terms (from step 2, biased, never fixed).** For each bend angle and dihedral, the energy is
  −kT₀ ln Σ_s p_s e^(−u_s/kT₀), over s = helix, strand, coil. p_s comes from `secondary.py`. u_s is a well at the
  usual C-alpha geometry (helix 91° and +50°; strand 120° and −170°). The coil well is broad, with no dihedral term.
  A helix can unravel when packing pays for it.
- **Excluded volume:** each bead's diameter comes from its side-chain volume (0.42–0.58 nm). Near neighbours along the
  chain (i, i + 2) use 0.42 nm.
- **Contacts:** e_ab from step 1 (300 K, 150 mM, pH 7). A smooth switch at d_ab + 0.20 nm, for pairs at least 3
  apart along the chain.
- **Burial:** h_a × B(n_a), with n_a the number of non-local neighbours.
- **Backbone H-bonds** between extended stretches (strand pairing): 1.5 kT each (step 1's target), at 0.50 nm, for
  (anti)parallel tangents.
- **The cooperative term (approved):** B(n) is a steep sigmoid (half-buried at 3.5 neighbours, width 0.5). Each contact
  counts e_ab × B(n_a) × B(n_b): a pair's contact energy needs both partners dehydrated.
- **The control ("additive"):** B(n) = min(n/6, 1), and contacts count in full. This is the plain additive model that
  Kaya and Chan found falls short of two-state.

### 1.2 Search and readouts
- **Search:** replica exchange Langevin dynamics (BAOAB integrator), 12 temperatures from 250 to 480 K. Every chain of
  every run of every sequence runs at once on the GPU, with CUDA graphs. Each run is 60,000 steps, with an exchange
  attempt every 100 steps. Exchange acceptance was 0.7–0.9.
- **Lowest fold of a run:** its lowest-energy snapshot, minimised. Two runs share a fold if they are within 0.30 nm
  RMSD (proper rotations only; mirror images differ).
- **Melting:** by WHAM over the ladder (all 10 runs pooled), I compute four readouts:
  - the fraction in the native fold, f(T) (within 0.30 × √(L/32) nm of the best structure);
  - task 02's Q(T), the fraction of the native's contacts present;
  - the heat capacity C(T);
  - Kaya–Chan's κ₂ = 2T_max √(k C_max) / ΔH_cal, without baseline subtraction (κ₂) and with a straight baseline
    through C at 250 and 480 K (κ₂ˢ).
- **Foldable:** f(300 K) ≥ 0.5, and at least half the runs end in the native's fold.

### 1.3 Checks of the machinery (measurements)
- **Gradient:** the energy's derivative matched a finite difference to 6 digits.
- **Equipartition:** bond energy is kT/2 per bond within noise (0.6–1.4 over single snapshots, at 5–400 K).
- **A native held at low T:** with the Gō check energy, a native stays within 0.2 nm at 5–50 K.
- **Convergence:** 300,000-step runs against 60,000-step runs on 10 sequences. Lowest energies agree within about
  2 kT, with no systematic gain (−29.8 against −29.5, −43.3 against −41.4, −41.4 against −45.5 kT, ...). The number
  of distinct folds in 4 runs stayed 2–4.
- **Instrument check (Gō, section 5):** the same chains fold and melt two-state when the energy has a single deep
  minimum.

### 1.4 Bugs of my own, fixed (stated as task 15 asks)
1. **Padded chains gave NaN.** Shorter chains in a batch were padded with beads at one point, so bonds had zero
   length. Their gradient was NaN even where masked. Padding beads now sit on a fixed, non-straight line far away.
   The first pilot was discarded.
2. **Some chains blew up.** A dihedral is undefined when three beads lie straight, and its force diverges there. The
   dihedral term is now weighted by sin² of both bend angles (a standard remedy). A cap of 2 × 10⁴ kJ/mol/nm on one
   bead's force is kept as a safety net.
3. **Snapshots lost precision.** Coordinates stored in float16 lost precision as chains drifted. They are now centred
   before storage.

## 2. Uniqueness, against task 02 (measurements)
The 80 page sequences are a subset of task 02's 120: its 40 most common and 40 of its random draws (lengths 12–26,
mean 15.2). The random 32-mers are the first 30 of task 02's 80 (same generator and seed). 10 runs each, in both
tasks.

| | task 02 lattice, page (same 80) | step 3, page (80) | task 02, random 32 (same 30) | step 3, random 32 (30) |
|---|---|---|---|---|
| distinct folds tied at the lowest (task 02: equal energy; step 3: within 1 kT) | 8.2 | 2.0 | 2.6 | 1.9 |
| distinct folds over all 10 runs | – | 6.0 | – | 9.9 |
| runs ending in the best run's fold | 18% | 28% | 10% | 10% |
| sequences whose best fold recurs in ≥ 8 of 10 runs | 1 of 120 | 2 of 80 | 0 | 0 |
| sequences whose best fold appears only once | 55% (of 120) | 28% | 100% (of 80) | 97% |
| energy gap from the best fold to the next distinct one (median) | 0 (ties) | 0.7 kT | 0 | 0.9 kT |
| RMSD from the best fold to the other runs' folds (median) | – | 0.43 nm | – | 0.78 nm |

- **Reading:** the 16-letter table removes exact ties, as the design hoped. But the folds it separates are only a
  fraction of a kT apart. At any temperature where a chain moves, they mix. "The fold" of a sequence is still not
  defined.
- Task 02's tie count and step 3's do not rank the same sequences as hardest (Spearman 0.13).

## 3. Melting and the two-state ratio (measurements)
`15s3_melting.png`.

| | task 02 lattice, page (48) | step 3 coop., page (80) | step 3 additive, page (30) | step 3 coop., random 32 (30) |
|---|---|---|---|---|
| native fraction at 300 K, f(300), mean | – | 0.006 | 0.005 | 0.000 |
| sequences with an f-based Tm in 250–480 K | – | 0 (f < 0.5 even at 250 K) | 0 | 0 |
| Q at the lowest T (task 02: T = 0.1) | 0.88 | 0.44 (at 250 K) | 0.48 | 0.35 |
| Tm from Q (Q at half its low-T value), mean ± sd | 0.43 ± 0.14 (lattice units) | 371 ± 41 K (57; 23 above 480 K) | 430 ± 39 K (10; 20 above 480 K) | 375 ± 65 K (25) |
| spread of Tm, sd / mean | 0.33 | 0.11 | 0.09 | 0.17 |
| transition width / Tm (Q from 80% to 20% of the way) | about 1.0 | 0.24 | 0.25 | 0.23 |
| heat-capacity peak inside the window | broad hump | 43 of 80 | 2 of 30 | 20 of 30 |
| κ₂, no baseline (peak inside the window), median | – | 0.64 | 0.58 (2 sequences) | 0.50 |
| κ₂ˢ, with baseline, median | – | 2.4 (not meaningful, below) | 3.6 (2) | 2.2 |

- **What melts is a molten globule, not a fold.** Q falls from 0.44 to chance between about 330 and 400 K. That is
  the collapse of a compact but disordered chain. Its width relative to Tm (0.24) is narrower than task 02's
  (about 1.0). But it is the loss of compactness, not of a native.
- **κ₂ without a baseline is not comparable to Kaya and Chan's lattice numbers.** Bonds, angles and dihedrals add a
  vibrational heat capacity that a lattice lacks, so ΔH_cal is dominated by it. A κ₂ˢ above 1 cannot come from a
  real two-state peak. It comes from curves whose peak sits on a steep slope or at the window's edge, so that the
  straight baseline removes most of the area. So for these sequences neither number is a fair two-state test. There
  is no folded state to test.
- **In the Gō instrument check, where a fold exists, κ₂ˢ is 0.84–1.00** (section 5). So the readout works when a
  transition is real.
- **Cooperative against additive:** same 30 page sequences, paired (measurements).
  - **It changes the melting, not the uniqueness.** With the cooperative term, 22 of 30 lose their compact state inside
    the window (Q-based Tm 372 ± 36 K). Without it, only 10 of 30 do (430 ± 39 K); the rest stay collapsed to 480 K.
  - The heat-capacity peak lies inside the window for 17 of 30 with the term, and 2 of 30 without it.
  - κ₂ (no baseline) is 0.71 against 0.63 (medians).
  - Uniqueness is the same: 1.9 against 1.9 distinct folds within 1 kT, 5.8 against 5.8 over 10 runs, and 31% against
    31% of runs in the best fold.
  - So the term makes collapse sharper and earlier. It cannot make a fold two-state where there is no fold.

## 4. Marginal stability and foldability (measurements)
- **Marginal stability, target 8–25 kT more stable folded: fails.** At 300 K the native fold is less stable than the
  rest, by a median of **+7.2 kT** (page) and **+12 kT** (random 32). ΔG_fold = −ln(f / (1 − f)) by WHAM; where no
  native snapshot was sampled at all it is capped, so the means are not informative.
- **Share of foldable random sequences: 0 of 30** (page: 0 of 80; designs: 0 of 2). Report 12's target was "small but
  not vanishing". This is vanishing at this sample size.
- **Tm spread:** no sequence has an f-based Tm in 250–480 K. The Q-based "Tm" of the molten globule spreads by 11%
  (page) to 17% (random). That is less than task 02's 33%, but it does not measure heat tolerance of a fold.

## 5. Why nothing folds: the diagnostics (measurements)
### 5.1 Strength: the Gō instrument check
- **What it is:** the table and burial are replaced by −ε for each contact of a given structure (the two designs'
  lowest structures from the 300,000-step runs). All the rest of the model is kept. It is an instrument test only: a
  Gō term is excluded from the model by report 12, section 10.

| Gō ε per contact | sheet design (25 monomers) | helix hairpin (32 monomers) |
|---|---|---|
| 1 kT | not folded at 250 K or above | not folded at 250 K or above; started folded, it unfolds within 10,000 steps at 150 K |
| 2 kT | Tm(Q) 294 K, width 13 K, κ₂ˢ 1.00 | not folded (Q 0.33 at 250 K) |
| 3 kT | Tm(Q) 437 K, width 25 K, κ₂ˢ 0.97 | Tm(Q) 395 K, width 49 K, κ₂ˢ 0.84 |
| 3 kT, additive | still folded at 480 K (Q 0.97 at 250 K) | Tm(Q) 449 K, width 83 K, κ₂ˢ 0.84 |
| 4 kT | still folded at 480 K (Q 0.96) | still folded at 480 K (Q 0.84) |

- **The cooperative term sharpens a real transition.** For the hairpin at 3 kT, the width is 49 K with the term and
  83 K without it (width/Tm 0.12 against 0.18). Without the term the sheet is more stable, since ungated contacts
  count in full.
- **In the real model's lowest structures** the non-local energy is −1.1 kT per contact (median; 1.8 contacts per
  monomer). The Gō check needs about 2 kT per contact (2.3–2.8 contacts per monomer) for Tm near 300 K, and that
  with no competing structures at all.
- **Reading:** the table's contacts are about half to a third of what this chain needs. That is not a flaw in step 1's
  numbers: 1–2 kT per contact matches the targets and Lehninger's numbers (task 18). The one-bead chain is floppy.
  Real chains pay their large loss of entropy on folding with many contacts per residue: side-chain packing, and
  backbone H-bonds in helices and sheets. Here, helix H-bonds sit only in the local bias, and the table's contacts
  are per pair of monomers, not per atom.

### 5.2 Specificity: the table scaled
`scan` stage: the same 8 sequences, 4 runs, table and burial multiplied by λ.

| λ | 1 | 1.5 | 2 | 3 |
|---|---|---|---|---|
| best f(300) of 7 sequences (the 12-mer left out) | 0.002 | 0.02 | 0.05 | 0.18 |
| Q at 250 K (mean of 8) | 0.53 | 0.67 | 0.68 | 0.75 |
| distinct folds in 4 runs (mean) | 3.4 | 3.1 | 3.1 | 3.0 |

- Even at 3 times the table, the native holds at most 18% at 300 K, and runs still disagree. So
  strength alone does not fix it.
- **Reading:** burial is 50–60% of the energy in the lowest structures, and it does not care who touches whom. The
  pair table varies little: most pairs are −0.1 to −0.5 kT, apart from the donor–acceptor pairs (−1.6 to −2.4 kT).
  So many compact arrangements tie within a kT. This is task 02's degeneracy in a milder form.

## 6. Odd complement pairs in packed cores (task 19, item 1)
**Measured on the lowest structures:** contacts between buried oily monomers (at least 4 non-local neighbours), at
least 4 apart along the chain. Enrichment = observed share ÷ the share expected from how often each monomer appears
in cores. Rank = where the complement stands among the 8 oily partners (1 = most enriched).

| m (oily) | 1 | 3 | 5 | 7 | 9 | 11 | 13 | 15 |
|---|---|---|---|---|---|---|---|---|
| complement m ^ 8 | 9 | 11 | 13 | 15 | 1 | 3 | 5 | 7 |
| random 32: complement enrichment | 0.53 | 0.89 | 0.95 | 0.63 | 0.53 | 0.89 | 0.95 | 0.63 |
| random 32: complement rank of 8 | 7 | 5 | 5 | 7 | 8 | 5 | 4 | 7 |
| random 32: most enriched partner | 7 | 3 | 9 | 1 | 13 | 11 | 9 | 15 |
| step 1 table: complement rank of 8 | 7 | 6 | 5 | 8 | 8 | 7 | 2 | 7 |

- **Size classes** (random 32; large 1, 3, 7; medium 5; small 11, 13; tiny 9, 15): large–large 1.20, large–tiny 0.60,
  large–small 0.86, small–tiny 1.36, tiny–tiny 1.13.
- **Page sequences** are dominated by a few monomers (15, 7, 2, 13 and 1 make about three quarters) and by repeats such as "phphph".
  So their counts mostly reflect composition. There too, no consistent complement preference shows (large–tiny 0.81;
  complement ranks 2–7). The repeats force 7–15 contacts at i, i + 3; this is why contacts closer than 4 along the
  chain are excluded.
- **Result, plainly:** in packed cores, **oily monomers prefer oily partners of similar size, not their complements.**
  All 8 complement pairs are under-represented in the random 32-mers. This meets the condition of Justin's decision
  (task 19, item 1): complement pairing would then hold for polar monomers only.
- **Caveats (measurement limits, for Justin's weighing):**
  - These cores are the lowest structures of chains that do not fold uniquely. They are packed (4 or more
    neighbours), but not a single native.
  - The one-bead model represents size only by bead diameter. Knobs-into-holes packing of real side chains cannot
    appear in it.
  - So the result says the table and bead sizes give no complement preference. It cannot say that real side-chain
    packing would not.

## 7. Buried salt bridges (task 20)
**In the model's own energy** (`saltbridge_step3.py`): a monomer is put in a core of 6 oily neighbours, against the
same monomers exposed. Sources, as task 20 gives them:
- Hendsch and Tidor 1994 (*Protein Science* 3: 211): most buried salt bridges are worse than hydrophobic
  replacements, by about 3.5 kcal/mol (about 6 kT) on average;
- Waldburger, Schildbach and Sauer 1995 (*Nat. Struct. Biol.* 2: 122): Arc repressor's mutants with the salt bridge
  replaced by hydrophobic residues are more stable;
- Kumar and Nussinov 1999 and 2002 dissent: they find most salt bridges stabilising.

| pair (filler 5) | two charges buried, unpartnered | buried as a pair | relief by the partner | oily isostere pair | pair − isostere |
|---|---|---|---|---|---|
| 0–8 | +10.4 kT | +9.8 kT | 0.6 kT | 13–3: −9.8 kT | **+19.6 kT** |
| 2–8 | +11.5 | +10.9 | 0.6 | 3–3: −13.0 | **+23.9** |
| 0–10 | +11.3 | +11.1 | 0.2 | 13–3: −9.8 | **+20.9** |
| 2–10 | +12.4 | +12.1 | 0.3 | 3–3: −13.0 | **+25.1** |

(Other fillers and the additive model differ by under 1 kT; all rows are in the JSON.)

- **Benchmark A (an unpartnered buried charge far worse than a partnered pair): fails.** A partner relieves only
  0.2–0.6 kT. Per charge, a buried pair costs almost as much as a buried lone charge.
- **Benchmark B (pair 0–6 kT worse than an oily contact): fails, by a wide margin.** The pair is 20–25 kT worse than
  its oily isostere pair.
- **Why (reading):** the table's charge attraction is computed in water (ε ≈ 78). Burial pays each charge's full
  desolvation (h of a Q bead, about +5 to +6 kT for these monomers), but the attraction gains nothing from the low
  dielectric inside. Lehninger (task 18) gives about 17 times stronger attraction in an oily medium. This is the "two
  effects pulling in opposite directions" that task 18 noted; the model has only one of them.
- **Specificity (task 20's third measure): cannot be measured.** In the lowest structures **no charged monomer is
  buried**: 0 of 220 (page) and 0 of 252 (random 32). So there are no sequences with buried pairs to compare. Oily
  monomers are buried at 64% and 82%.
- The +1.1 kT of step 1 (section 1.3 of report 15) is a different accounting: one contact plus 1/6 of each burial.
  For a fully buried pair, the model's own number is about +10 to +12 kT.

## 8. Cost (measurements)
| | task 02 lattice (batch 4,096) | step 3 (batch 3,000 chains = 25 sequences × 10 runs × 12 replicas) |
|---|---|---|
| one run, length 13–16 | 0.085 s (length 16) | 1.1 s |
| one run, length 32 | 0.32 s | 3.2 s (full batch), 4.1 s (batch of 5 sequences) |
| one sequence, 10 runs | 0.85–3.2 s | 11 s (length 13–16), 32–41 s (length 32) |
| speed per chain-step | – | 2.2 µs (length 24), 3.9 µs (length 32) |

- A run here is 12 replicas × 60,000 steps; task 02's was 8 × 2,000 sweeps.
- **Report 12's estimate (0.5–5 s per domain)** holds for one run. It does not hold for the 10 runs needed to judge
  uniqueness. If folds were unique, 2–3 runs would do (proposal).
- **GPU time used in this step:** about 90 minutes in all, through the queue. That is pilots and checks about
  46 minutes (including about 7 minutes lost to the two bugs of section 1.4), and the measurement runs 44 minutes.
  Probes run directly took about 8 minutes more.

## 9. Proposals (Claude's; for Justin's decision)
Step 3's checks are not met: uniqueness, two-state melting of a fold, marginal stability, foldable share, and both
salt-bridge benchmarks. By task 15's rule step 4 waits. These are options, not fixes I have made.
1. **Strength:** add the two contributions the table leaves out, each from its own physics, not by scaling.
   - Backbone H-bonds in helices: i → i + 4, about 1–2 kT each, as in step 1's target. At present helix H-bonds sit
     only in the local bias.
   - A packing (van der Waals) term per bead pair, scaled by size.
   - Section 5.1's check gives a target: about 2 kT per non-local contact, at 2–3 contacts per monomer.
2. **Specificity:** let buried polar and charged contacts count more than exposed ones.
   - Proposal: an environment-dependent dielectric. A pair's charge term inside a core uses a lower ε. Lehninger's
     factor (about 17 between water and benzene) is the upper bound; Hendsch–Tidor's net cost (about 6 kT) is the
     target for a buried pair.
   - This would also bring benchmarks A and B into range, and give the pKa shift on burial report 12 planned.
   - Before adding a temperature dependence of ε (task 20, heat), check a source.
3. **Odd complement pairs:** the measurement meets Justin's condition for "complement pairing for polar monomers
   only", with the caveats of section 6. Adopting it is Justin's decision.
4. **Two beads per monomer** (backbone + side chain) instead of one, if Justin wants knobs-into-holes packing to be
   testable. It roughly doubles the cost. This would change report 12's approved one-bead tertiary level; Justin's
   choice.
5. **Repeat step 3 after 1 and 2,** with the same sets and readouts. The machinery, the Gō check and the comparison
   tables are ready.

## 10. Constants chosen in this step (all proposals)
| constant | value | what for |
|---|---|---|
| bond length, stiffness | 0.38 nm, 5,000 kJ/mol/nm² | chain |
| helix well | 91° bend, +50° dihedral | local bias (C-alpha geometry) |
| strand well | 120°, −170° | local bias |
| coil well | 110°, no dihedral | local bias |
| angle stiffness | 10 kT₀/rad² (helix, strand), 2 kT₀/rad² (coil) | local bias |
| dihedral depth | 2 kT₀, weighted by sin² of both bends | local bias |
| bead diameter | 0.42–0.58 nm from side-chain volume; 0.42 nm for i, i + 2 | excluded volume |
| excluded-volume strength | kT₀ (WCA) | |
| contact switch | d_ab + 0.20 nm, width 0.03 nm | contacts, burial count |
| cooperative burial | half at 3.5 neighbours, width 0.5 | many-body term |
| additive burial | min(n/6, 1) | control |
| backbone H-bond | 1.5 kT₀, 0.50 ± 0.06 nm, extended above 106° | strand pairing |
| table conditions | 300 K, 150 mM, pH 7, held fixed over the ladder | the table's T-dependence is not used in melting (cut) |
| force cap | 2 × 10⁴ kJ/mol/nm per bead | safety |
| replica ladder | 12 temperatures, 250–480 K, geometric | search |
| dynamics | BAOAB, time step 0.004, friction 2 (reduced units, mass 1) | search |
| run | 60,000 steps; exchange every 100; snapshot every 500; first 30% discarded | search |
| minimisation of each run's lowest snapshot | 3,000 gradient steps | lowest fold |
| same fold | RMSD ≤ 0.30 nm | uniqueness |
| folded snapshot | RMSD ≤ 0.30 × √(L/32) nm of the native | f(T) |
| tie | within 1 kT₀ of the best run | uniqueness |
| buried | ≥ 4 non-local neighbours | cores, charges |
| contact present (Q) | within 1.2 × the switch distance | Q(T) |
| foldable | f(300 K) ≥ 0.5 and ≥ half the runs in the native's fold | foldable share |
| κ₂ˢ baseline | straight line through C at 250 and 480 K | two-state ratio |
| Gō check ε | 1–4 kT₀ per contact | instrument check only |
| salt-bridge core | 6 neighbours; fillers 1, 3, 5, 13; isosteres 0→13, 2→3, 8→3, 10→3 | task 20 benchmarks |
| designed sequences | helix hairpin (heptads, 32) and three-stranded sheet (25), by hand | positive controls |

## 11. What was cut (to keep GPU time near 1.5 hours)
- **Page sequences:** 80 of task 02's 120. **Random 32-mers:** 30 of 80. **The additive control:** 30 page sequences.
  Random 20-mers were not run.
- **Task 02's mutation test** (one mutation changes the best fold in 44%) was not repeated. It means little while no
  sequence has a unique fold.
- **Runs:** 60,000 steps (checked against 300,000 on 10 sequences).
- **Gō checks:** 4 runs.
- **Model detail:** the table's temperature and salt dependence is not used in melting (fixed at 300 K, 150 mM). The
  pKa shift on burial is not included.
- **Designs:** only two positive controls.

## Files
- Code (new): `beadfold/tertiary.py`, `beadfold/run_step3.py`, `beadfold/analyse_step3.py`,
  `beadfold/summary_step3.py`, `beadfold/saltbridge_step3.py`; `beadfold/README.md` updated.
- Results (small, in the repository): `beadfold/results/step3_summary.json`, `beadfold/results/step3_saltbridge.json`.
- Raw results (too large for the repository): `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task15_step3\`.
  It holds the `.npz` batches (snapshots and lowest structures), the `analysis_*.json` per-sequence files and the
  run logs.
- Figures: `comms/from_gpu/15s3_melting.png`, `15s3_uniqueness_kappa.png`, `15s3_go_check.png`.
