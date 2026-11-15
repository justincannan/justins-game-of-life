# 15: prototype steps 1 and 2: beads and the contact table; the secondary rule

From: gpu session (scheduled check), 14 November 2026, about 21:20 New York. Answers
`to_gpu/2026-11-14_15_design-approved-prototype.md` (Justin's approval of all six choices in report 12, section 9).

**The values below are measurements of the prototype. The bead parameters and rules are proposals (Claude's),
built on Justin's approved choices.** Nothing goes into the page. Code: `beadfold/` (new folder; `fold3d/` is task 02's
lattice and stays as it was). Numbers: `beadfold/results/steps12.json`. Figures: `15_step1_table.png`,
`15_step2_secondary.png`.

## Summary
- **Step 1's checks are met.** Contacts are weak beside covalent bonds, about 50 times weaker. Screening follows
  Debye–Hückel and halves the charge attraction near 0.15 M. The 16 monomers have distinct rows. The (T, I) fit is
  good to 0.06 kJ/mol.
- **One expectation of the design did not come out (a measurement):** complement pairs are the best partners for the
  even monomers, but **not for the odd (oily) ones**. Among oily monomers, like attracts like more than large attracts
  small. Section 1.4 has the reading and a proposal.
- **The "about nine times" figure is dropped** (reply 14 asked for its source or its removal). In this table the
  one-body burial term is about **2.3 times** the pairwise term for the oily monomers. That is now a readout of the
  beads, not a design weight.
- **Step 2's checks are met.** The transfer matrix reproduces Zimm–Bragg's closed form, and helix formation is
  cooperative with length. Charge patterns raise or lower helix as they should, and salt and pH shift them.
  Alternating oily and polar patterns favour strands (after one fix to my own rule, stated below).
- **Step 3 (the off-lattice folder on the GPU) is next.** It starts at the next check. By task 15's rule it can,
  since steps 1 and 2 meet their checks.

## 1. Step 1: beads and the contact table (`beadfold/beads.py`)

### 1.1 What was built (proposals)
- **Beads:**
  - One backbone bead for all 16 monomers: P3, regular, donor + acceptor.
  - One or two side-chain beads per monomer, from a 13-level ladder: Q, P5–P1, N2–N1, C5–C1.
  - Sizes as in Martini 3: regular 0.47 nm, small 0.41 nm, tiny 0.34 nm.
  - Charges, with pKa for the titratable beads, and donor/acceptor marks.
- **Ladder:** water → oil transfer free energy at 298 K, from +18 kJ/mol (Q) to −7 kJ/mol (C1), scaled by bead size.
  - A first try at twice these values gave the largest oily monomer −30 kJ/mol. That is about twice the largest
    side-chain transfer energies usually quoted, so I halved it (now −14 kJ/mol, 5.6 kT).
  - Apolar beads get a transfer heat capacity, so the hydrophobic effect strengthens with T, in kJ/mol. In kT it stays
    nearly flat over 280–340 K.
- **Monomer assignment** (keeps the page's two rules):
  - odd = oily, with sizes paired large with small;
  - 0–8 and 2–10: opposite charges. 0 is titratable (pKa 4); 10 is a weak base (pKa 6.5, so charge +0.24 at pH 7).
  - 4–12 and 6–14: donor with acceptor;
  - 15 is tiny with a backbone that cannot donate (proline-like).
  - The full list is in `beads.py`.
- **Contact free energy:**
  - Each pair is sampled 60,000 times: centres in a 0.45–0.90 nm shell, side chains in random directions.
  - Only configurations in which the side chains touch count. Their clash share measures packing.
  - e_ab = −kT ln⟨e^(−U/kT)⟩ over touching configurations that do not clash, plus a packing term relative to the
    average pair.
  - U is made of three parts:
    - Lennard-Jones between side-chain beads (like attracts like: a mixing rule on the ladder);
    - a donor–acceptor well;
    - Debye–Hückel charges, with l_B and λ_D computed at T and I.
  - Backbones only exclude volume. Backbone H-bonds belong to steps 2 and 3.
- **Burial h_a:** the sum of the side-chain beads' transfer free energies (one-body, kept separate from e_ab).
- **Grid and fit:** T = 280–340 K (7 values) and I = 5 mM–1 M (6 values), at pH 7. Each e_ab is fitted as a
  quadratic in t = (T − 300)/20 and x = log10 I (6 coefficients). Each h_a is fitted as a quadratic in t.

### 1.2 Checks against section 1's targets (measurements, 300 K, 150 mM, pH 7)
| target | measured |
|---|---|
| Bjerrum length ≈ 0.7 nm | 0.716 nm (298 K) |
| Debye length 0.304/√I nm | 0.785 nm at 150 mM; 0.304 at 1 M |
| single contacts about 1–2 kT (H-bond, apolar), weak beside a C–C bond (≈ 140 kT) | effective contact (e_ab plus 1/6 of both burials): apolar −1.1 to −2.7 kT; donor–acceptor −1.3 to −1.9 kT; strongest 2.7 kT, so about 50 times weaker than a C–C bond |
| salt bridge a little stronger unscreened, halved at about physiological salt | electrostatic part of 0–8: −1.27 kT at 1 mM, −0.68 kT at 150 mM (halved near 0.17 M), −0.23 kT at 1 M |
| partitioning ladder in Martini's shape | monotone by construction (Q ≫ P > N > C) |
| no degeneracy (distinct monomers) | smallest distance between two monomers' rows (e and h): 0.52 kT; all 16 distinct |
| fitted table usable without reopening | largest fit error 0.063 kJ/mol (0.025 kT); sampling error between two independent samplings ≤ 0.054 kT |
| cost | all 42 tables in 6.9 s on one CPU thread (not minutes on the GPU, as estimated) |

Marginal stability (8–25 kT) is a readout of the folded chain, so it waits for step 3.

### 1.3 Charges, pH and salt (measurements)
- Salt bridges screen as Debye–Hückel says (figure, right).
- **The titratable pair responds to pH:** 2–10 is −1.03 kT at pH 5, −0.55 at pH 7 and −0.40 at pH 9, because 10
  gains its charge below its pKa.
- Once burial is counted, **a buried salt bridge does not pay**: 0–8's effective contact is +1.1 kT. Burying two
  charges costs more than they gain.
  - Reading (proposal): this is the usual picture that salt bridges help little in folds, except at the surface.
    Not re-checked against a source in this visit.
  - The pKa shift on burial (report 12, section 1) is not yet in the table. It would ease this cost; it belongs to
    step 3, where burial is known.

### 1.4 Complement pairs (measurement, and a proposal)
Where m's complement (m ^ 8) ranks among m's 16 partners (1 = best):

| m | 0 | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 1 | 3 | 5 | 7 | 9 | 11 | 13 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| rank of m ^ 8 | 1 | 2 | 1 | 2 | 1 | 1 | 1 | 2 | 11 | 6 | 5 | 13 | 12 | 11 | 2 | 11 |

- **Even monomers:** the complement is the best or second-best partner. Charge pairs and donor–acceptor pairs come
  out of the beads, as the design meant. But donor–acceptor contacts are not specific among themselves: 4 binds
  11, 12 and 14 almost equally (−2.3 to −2.4 kT).
- **Odd monomers:** the complement is not favoured. The large oily monomers (1, 3, 7) attract each other most
  (−0.6 to −0.8 kT); a large one with a tiny one gains about 0. The clash share depends mostly on how many beads
  the side chains have (0.3 with one bead, 0.6 with two), not on whether sizes complement.
- **Reading (proposal):** packing large with small ("knobs into holes") is a property of a packed core, with many
  neighbours at once. One isolated pair in water cannot show it. So the test belongs to step 3, which packs real
  cores.
  - If step 3 also shows no preference, odd complement pairs will be ordinary contacts in the new model. The page's
    rule "m pairs with m ^ 8" would then survive for the even monomers only.
  - Whether that matters is **Justin's call**. It changes nothing yet, and it is a consequence of approved choice 2,
    not a new choice. I will report it again after step 3.

## 2. Step 2: the secondary rule (`beadfold/secondary.py`)

### 2.1 What was built (proposals)
- **Helix:** a Zimm–Bragg transfer matrix with σ = 10⁻³. The forward–backward sum gives each monomer's helix
  probability exactly, in O(n).
- **Propagation weight s from the beads:**
  - medium unbranched side chains 1.30 (1.10 for small ones);
  - branched 0.85; charged 1.0; tiny 0.45;
  - non-donor backbone 0.05.
  - **Charges at i−3 and i−4:** a screened Debye–Hückel energy at 0.62 nm multiplies s by e^(−u). This is an
    approximation: the pair energy is credited to the later monomer.
- **Strand:** a propensity b from the beads (branched and oily side chains favour it; charged and tiny ones do not).
  - It is multiplied by (1 + number of neighbours of the other oiliness) and lowered by like charges at i ± 2.
  - The share of the non-helical probability in strand is b/(1 + b).
  - **One fix of my own rule:** the alternation factor was first 1 + 0.5 per neighbour. Then (5 4)×12 came out
    less stranded than 5×24, failing the design's own aim ("alternation favours strands strongly"). It is now
    1 + 1.0 per neighbour.

### 2.2 Checks (measurements, 300 K, 150 mM, pH 7 unless stated)
- **Against Zimm–Bragg's closed form:** in the interior of a 400-mer, the transfer matrix and the infinite-chain
  formula agree to 4 decimals, for every monomer (figure, left).
- **Cooperativity (s = 1.3):**

  | length | 8 | 12 | 16 | 24 | 32 | 64 | 200 |
  |---|---|---|---|---|---|---|---|
  | helix fraction | 0.05 | 0.16 | 0.35 | 0.67 | 0.78 | 0.89 | 0.95 |

  - The transition in s is sharp: 100-mers go from 0.06 at s = 0.9 to 0.61 at s = 1.05.
- **Charge patterns (24-mers, host = monomer 7, helix 0.67):**
  - opposite charges at i, i+4 raise the helix: (0000 8888)×3 gives 0.84, and the host with 0 and 8 four apart
    gives 0.74;
  - like charges at i, i+4 lower it: the host with 0 every fourth place gives 0.19;
  - runs of like charge do not coil (Lehninger's point): 0×24 and 8×24 give 0.0015;
  - **salt** weakens both effects: (0000 8888)×3 gives 0.86 at 5 mM and 0.52 at 1 M; 0×24 gives 0.0007 at 5 mM and
    0.010 at 1 M;
  - **pH 3** neutralises 0: 0×24 rises to 0.08;
  - a single 15 (proline-like) in the middle of the host cuts the helix from 0.67 to 0.25.
- **Strands:**

  | pattern | helix | strand | coil |
  |---|---|---|---|
  | 5×24 | 0.02 | 0.62 | 0.36 |
  | (5 4)×12, alternating | 0.06 | 0.64 | 0.30 |
  | (5 5 4 4)×6 | 0.06 | 0.56 | 0.38 |
  | 9×24, tiny | 0.00 | 0.13 | 0.87 |
- **Random 32-mers (2,000):**
  - mean helix 0.09;
  - Spearman correlation 0.28 between a monomer's own s and its helix probability. Its neighbours matter, as
    cooperativity says they should.
- **Cost:** 0.65 ms per 32-mer in plain Python. That is not the page's speed. A JavaScript version should take
  microseconds to tens of microseconds, but this is not measured.

## 3. What comes next
- **Step 3:** the off-lattice tertiary folder on the GPU, using `beads.py`'s table, burial and the secondary
  probabilities as biases. It measures uniqueness, the two-state ratio, the spread of Tm, the share of foldable
  random sequences and the cost per domain, against task 02. Marginal stability (8–25 kT) and odd-pair packing
  (section 1.4) are checked there.
- **Lehninger chapter 2 (offer in task 15):** one check would help. Do the chapter's numbers for an H-bond and for a
  salt bridge in water fit the effective contacts in section 1.2 (−1.3 to −1.9 kT, and +1.1 kT for a buried salt
  bridge)? Only the numbers are needed, not the text.
