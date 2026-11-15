# 12 (with 12a, 12b): folding and interactions from the ground up: design report

From: gpu session (scheduled check), 14 November 2026, about 19:10 New York. Answers
`to_gpu/2026-11-14_12_folding-from-the-ground-up.md`, with the additions `12a` (open and fold across scales) and
`12b` (beads as the base level).

**Everything in this report is a proposal (Claude's), awaiting Justin's approval.** Nothing has been built or run.
Justin's decisions it builds on: rebuild rather than patch; secondary and tertiary separate, quaternary later; ions;
beads (Martini-style) as the base level; open and fold across scales; polarity and marginal stability (adopted
earlier). The choices marked **"Choice for Justin"** in section 9 change the page's model and are his to make.

## Summary
- **Five levels**, each computed in detail offline and folded into a few numbers the page receives:
  beads → monomer contact table → secondary structure → tertiary fold → function (pocket, rate, stability at T).
- **Beads:** each of the 16 monomers is a shared backbone bead plus one or two side-chain beads of the Martini
  classes Q (charged), P (polar), N (intermediate), C (apolar), with levels within each class. Ions are single Q beads.
  The 16 × 16 contact table, plus a one-body burial term per monomer, is derived from the beads, never set by hand.
- **Secondary:** a one-dimensional helix–coil rule (Zimm–Bragg type) per segment, cheap enough to run in the page.
  Strands and turns from local propensities; strands pair only in the tertiary step.
- **Tertiary:** an off-lattice chain of one bead per monomer, its local geometry biased (not fixed) by the secondary
  step, held together by the contact table, burial, and a **many-body desolvation term** that makes melting
  cooperative. No native structure is ever an input, so Martini's limitation (imposed secondary structure, Gō or
  elastic networks for tertiary) is not inherited.
- **Function:** a pocket is a cluster of partly exposed monomers on the folded surface. Its lining, scored with the
  same contact table against the 16 molecules (which are the monomers, so they have beads too), gives specificity
  and rate. Activity = rate × fraction folded at the cell's temperature.
- **Cost:** folding every distinct sequence in full is too slow for the page (task 02: 0.1–0.3 s of GPU time each on a
  lattice; off-lattice will be several times more). So: cache by **domain** sequence; give a new domain an immediate
  provisional value from a cheap in-page estimate (threading onto cached folds), and fold it exactly in GPU batches
  between runs. The provisional value is computed from the new sequence itself, so no variant is limited to values
  already in the table.

## 1. The interactions (bead level)

### What a monomer carries
Each monomer = one backbone bead (the same for all 16) + one or two side-chain beads. Each bead has:
- **class and level** (Martini 3's four classes Q, P, N, C, each split into levels, about 20 types in all; Souza et al.
  2021, *Nat. Methods* 18: 382). The level sets its water/oil transfer free energy.
- **charge** q ∈ {−2, −1, 0, +1, +2}, and for some Q beads a **pKa**, so the charge depends on the surroundings:
  fraction charged = 1/(1 + 10^(±(pH − pKa))). Burial shifts the effective pKa (a buried charge is costly, so it tends
  to neutralise): proposal, a fixed shift per buried neighbour.
- **H-bond character:** donor, acceptor, both, or neither (Martini 3 marks donor/acceptor sub-types). The backbone
  bead is donor + acceptor, which is what lets helices and strands form at all.
- **size:** regular, small, tiny (Martini maps about four, three or two heavy atoms per bead). Size sets packing and
  pocket shape.

### Proposed assignment of the 16 monomers (keeps the page's two rules)
The page has two rules worth keeping: odd monomers are oily, and m pairs with its complement m ^ 8.
- **Odd monomers (8):** apolar or intermediate side chains (C and N levels), in four sizes. Complement pairs
  (m, m ^ 8) are **size-complementary** (large with small), so they pack well together ("knobs into holes").
- **Even monomers (8):** polar or charged. Complement pairs are **charge- or H-bond-complementary**: two pairs of
  opposite charges (salt bridges; one of each pair titratable), two pairs of donor with acceptor.
- So a complement pair is still a specially favourable contact, as eP made it in task 02, but now as a consequence of
  the beads, not a separate energy. The 16 monomers also get distinct values, which removes the two-letter
  degeneracy that gave task 02 its tied folds (Li, Helling, Tang and Wingreen 1996: degeneracy is a property of
  two-letter alphabets).

### How attraction is computed (offline)
Between two beads i and j at distance r, in implicit water at temperature T, ionic strength I and pH:
- **Short-range (Lennard-Jones-like) term** with a well depth from the Martini-style interaction matrix between levels:
  like attracts like; apolar–polar weak; this is what water/oil partitioning is calibrated on.
- **Screened charge–charge term** (Debye–Hückel): E = q_i q_j · l_B · kT · e^(−r/λ_D) / r, with the Bjerrum length
  l_B ≈ 0.7 nm in water and the Debye length λ_D ≈ 0.304 nm / √I(M) for a 1:1 salt at 25 °C (about 0.8 nm at
  150 mM). More salt → shorter λ_D → weaker attractions and repulsions. This is where ions enter folding.
- **Polar contacts (H-bond-like):** an extra well for donor–acceptor pairs, with an angular factor in the tertiary
  model (one directional vector per backbone bead).
- **Hydrophobic effect as burial,** a one-body term: each bead pays its transfer free energy times the fraction of its
  surface exposed to water. Burial is counted from neighbours within a cut-off. The Miyazawa–Jernigan analysis of
  real proteins found the one-body desolvation part to dominate their contact energies (about nine times the
  pairwise mixing part, in one review), so this term carries most of the driving force by design.

### From beads to the 16 × 16 table
- For each pair of monomers (a, b): sample their relative orientations at contact (Monte Carlo over the side-chain
  beads' positions), compute the free energy of contact e_ab(T, I, pH), and separately the burial term h_a.
- The page and the tertiary model receive: the 16 × 16 table e_ab, 16 burial values h_a, 16 secondary propensities
  (section 3), and the net charge of each monomer at pH. Each is fitted over the calibrated range as a small
  polynomial in T and log I, so it can be evaluated without reopening.
- Cost: 136 pairs × a few hundred thousand orientation samples: minutes on the GPU, once per bead parameter set.

### Calibration targets (12b; targets, not mechanism)
- **Weak against covalent:** single non-covalent contacts a few kJ/mol (about 1–2 kT for H-bond-like and apolar
  contacts, a little more for an unscreened salt bridge), against roughly 350 kJ/mol for a C–C bond: 10–100 times
  weaker. Covalent bonds are not broken in this model; the chain's bonds are fixed.
- **Marginal stability:** folded only 20–60 kJ/mol (about 8–25 kT) more stable than unfolded for a small domain,
  the small difference of two large opposed terms. This is not set; it is a readout the prototype must reproduce.
  Taverna and Goldstein (2002, *Proteins* 46: 105) argue it arises without selection for it, because most sequences
  near any stable one are less stable; the page should show it emerging from mutation and selection, as a check.
- **Screening:** attraction between opposite charges halves at roughly physiological salt over a few tenths of a nm
  (falls out of the Debye term; check λ_D against the formula).
- **Partitioning:** each bead level's water → oil transfer free energy on a ladder like Martini's (calibrated there
  against measured octanol/water and hexadecane/water partitioning). We take the ladder's shape, not its numbers
  verbatim.

## 2. Ions
- **Kinds (proposal: four):** two monovalent cations (sodium-like and potassium-like, so pumps can later tell them
  apart), one monovalent anion (chloride-like), one divalent cation (magnesium/calcium-like, also usable as a
  cofactor in pockets). A phosphate-like divalent anion could come later with energy chemistry.
- **Each ion is a single Q bead:** charged, never folding, never polymerising. It enters folding only through the
  ionic strength I = ½ Σ c_k z_k², which sets λ_D in the contact table, and through divalent ions binding in pockets.
- **What the page tracks:**
  - per square: 4 concentrations (float32), diffusing like the dissolved food (approved agar correction);
  - per cell, inside the membrane: 4 concentrations, which change only by division (halved) and, later, by channel
    and pump domains (section 5). Before pumps exist, the cell's ions equal its square's at birth and then drift
    with what it takes in and out with water, which the page does not yet model, so proposal: inside = outside until
    channels/pumps are approved.
  - per cell, derived each tick or when its ions change: I_in, and so which row of the T × I table its domains use.
- **Membranes, later:** a lipid is a C tail + a P or Q head; a membrane is impermeable to ions. A domain with an
  exposed apolar belt (a readout from the fold) is a membrane-spanning candidate; a channel is one with a polar pore.
  This is room left, not a design.
- Memory: 8 float32 per square and per cell. Negligible.

## 3. Secondary structure
- **A local rule run on the sequence alone,** in one dimension:
  - **Helix:** a Zimm–Bragg-type transfer matrix. Each monomer has a propagation weight s_a (from its beads: medium
    side chains favour helix; tiny ones and those that cannot donate backbone H-bonds break it) and there is one
    nucleation cost σ. Same-sign charges at i, i+4 lower s; opposite charges at i, i+4 raise it (a salt bridge along
    the helix). The partition function is exact in O(n) and gives each monomer's helix probability. Helix formation
    is cooperative along the chain for free, through σ.
  - **Strand:** a propensity per monomer (large, branched apolar side chains favour it; alternating apolar/polar
    patterns favour it strongly). A strand is only a candidate: it is stabilised only if it finds a partner strand in
    the tertiary step.
  - **Turn/coil:** tiny and polar monomers, and runs of like charge (Lehninger: a run of like charges cannot coil;
    proposal 3 earlier).
- **Output:** per monomer, probabilities of helix, strand and coil, and segments with their free energy. This is cheap
  (microseconds per sequence), so it can run in the page itself.
- **The page's nested brackets:** they are an RNA-like pairing, while protein tertiary contacts cross freely (task 02).
  Proposal: they are **replaced as the mechanism of folding**. Complement pairs stay favourable contacts (section 1),
  so bracket pairs will often still touch in 3D. What becomes of the page's reaction rule built on brackets (taken
  monomer, inner sum, adaptors) is **Choice for Justin 1** (section 9).

## 4. Tertiary structure
### The model
- **Chain:** off-lattice, one bead per monomer (its side chain's properties folded into the monomer), bond length
  fixed, bond-angle and dihedral terms biased towards the geometry its secondary state prefers (helix, strand,
  coil), weighted by the secondary probabilities but **never fixed**: a helix can unravel if packing pays for it.
  Proposal: off-lattice rather than task 02's cubic lattice, because helices and sheets cannot be represented on a
  cubic lattice, and tied folds were partly a lattice artefact. Alternative: a face-centred cubic lattice (12
  neighbours), cheaper but cruder (**Choice for Justin 5**).
- **Energy:**
  1. contact term Σ e_ab over pairs within a switching distance, from the table;
  2. burial term Σ h_a × (exposure of a);
  3. backbone H-bond term between strands and within helices (directional), which makes sheets;
  4. **a many-body desolvation term** (the cooperative term). A contact's full energy counts only when the pair is
     dehydrated, that is, when both partners are buried beyond a threshold: E_ab · g(b_a) · g(b_b), with g a steep
     sigmoid of burial. Partly formed cores then gain little, so the chain is either packed or not: this is what
     makes melting two-state. Kaya and Chan (2000, *Proteins* 40: 637) showed that additive lattice contact models
     fall short of calorimetric two-state behaviour; desolvation-type many-body terms are the kind proposed in that
     line of work. The prototype must show it works here (below).
- **Search:** replica exchange, batched on the GPU (the task 02 machinery, moved off-lattice), many chains at once.
- **Native** = the most populated cluster of structures at the cell's temperature. **Uniqueness** is then a measured
  number (that cluster's population), not an assumption.

### Stability against heat
- From the replica-exchange runs (all temperatures at once, reweighted): the fraction folded f(T), Tm, the enthalpy at
  the midpoint ΔH_m, and the heat-capacity change ΔCp. These three numbers give ΔG_fold(T) anywhere in the
  calibrated range (Gibbs–Helmholtz), so the page evaluates stability at any T without reopening the fold.
- **Two-state test (readout):** the ratio of van 't Hoff to calorimetric enthalpy (Kaya and Chan's criterion); near 1
  means two-state. Target for the prototype: most foldable sequences near 1, against task 02's gradual melting.
- Heat tolerance is then emergent: a sequence whose core is larger or better packed has a higher Tm.

### A domain's job from its shape
- **Pocket:** after folding, find concave surface clusters of partly exposed monomers (a cluster of 3–8 lining monomers
  with burial between thresholds). A domain may have none (no job), one, or several.
- **Binding:** the 16 molecules are the monomers, so each has beads. Binding free energy of molecule x in pocket p =
  Σ over lining monomers of e(lining, x) − x's desolvation cost + a size-fit term (pocket volume class against x's
  size). Specificity = the Boltzmann-weighted share over the 16 molecules.
- **What it makes:** Lehninger chapter 6: a good enzyme fits the transition state, not the substrate. Proposal: a
  conversion x → y is catalysed in proportion to how much better the pocket binds the "midway" between x and y (the
  mean of their bead compositions) than x itself. So the product is set by the pocket's shape and chemistry, and a
  mutation in the lining changes what is made. This would replace the inner-sum rule: **Choice for Justin 1**.
- **Cofactors:** a pocket lined by two or more negatively charged monomers binds the divalent ion strongly; a reaction
  could require it (Lehninger: many enzymes need metal ions). Room left; a proposal, not designed further.
- **Activity given to the page:** rate × fraction folded at the cell's T and I.

## 5. Quaternary, later (room left)
- Each cached fold records its **surface patches** (exposed apolar or charged clusters with their composition and
  position). Two cached folds can be docked as rigid bodies with the same table, giving an association free energy:
  cached by the pair of domain keys.
- **Binding that changes fit (allostery):** the fold model can compute a domain's ensemble with and without a molecule
  in a second pocket. If the bound state shifts which structure is most populated, the pocket's activity changes.
  The cache key then includes the ligand state. Room left only.
- **Ion pumps and channels** are quaternary-like assemblies in membranes and use the same parts.

## 6. Selection and foldability
- **Foldability is not given.** With a 16-letter sequence-dependent energy and no native input, most random sequences
  should fold poorly: low native population, low two-state ratio, low Tm. The prototype must measure the share of
  random sequences that fold uniquely; targets from the literature: in HP lattice counts about 0.3% have a unique
  ground state (Li et al. 1996, noted in THEORY_NOTES); in real random libraries, functional proteins are rare
  (Keefe and Szostak 2001 found about one ATP-binder in 10^11). The page's own number should be small but not
  vanishing, so evolution has a foothold.
- **Fitness:** a domain works only as much as it is folded: activity = rate × f_folded(T_cell). Proposal: unfolded
  chains also **cost** (they must be cleared or they clump: a small upkeep per unfolded copy). Then selection acts on
  stability both ways (a fold too weak is useless and costly; extra stability gains nothing), and marginal stability
  can appear as a readout, not a setting.
- Expected emergent effects to check, not to build in: stability buffering mutations (Bloom et al. 2006, *PNAS*:
  more stable proteins tolerate more mutations, so stability promotes evolvability); heat-tolerant lineages in a
  hot zone differing from cool ones by a few mutations (Lehninger).

## 7. Cost
- **What is cached:** domains, not whole sequences (domains are moved whole by duplication and contagion, so the same
  domain recurs in many sequences). Key = domain sequence (+ ligand state, later).
- **Distinct sequences a run makes (measured in task 02, tick 1,000):** even world 400–1,000; vent world about 10,900
  (one seed). Domains are fewer. Proposal: estimate 10^4–10^5 distinct domains in a 10,000-tick vent run; to be
  measured once the prototype exists.
- **Per distinct domain (estimates, to be measured):**
  - secondary: microseconds (in the page);
  - contact table: none (looked up);
  - tertiary off-lattice replica exchange: task 02's lattice runs took 0.08 s (length 16) to 0.3 s (length 32) of GPU
    time per sequence at batch 4,096. Off-lattice dynamics is estimated at 5–20 times more: about 0.5–5 s per domain
    of length 16–40. So 10^4 domains ≈ 1.5–15 GPU hours: feasible offline in batches, not live.
  - pockets and binding: milliseconds once folded.
- **So, three tiers:**
  1. **In the page, at once:** secondary rule plus a **threading estimate**: score the new domain on each of the
     nearest cached folds (same length class), with the contact table, burial and the cooperative term; take the best.
     Milliseconds. The value is computed from the new sequence, so a new variant can exceed anything in the table.
  2. **Queued:** the new domain key goes into a list the page exports.
  3. **Offline, batched on the GPU:** fold the queue exactly; the cache (a JSON or binary file the page loads) grows.
     A readout shows the share of working domains still on provisional values.

## 8. Open and fold, level by level (12a)

| level | kept open (computed in detail), when | folds into (what the page gets) | reopened when | keeping new variants possible |
|---|---|---|---|---|
| beads → contact table | offline, once per bead parameter set | 16 × 16 e_ab, 16 h_a, charges, propensities, each as a function of T and I | bead parameters change (Justin's choice); T, I or pH outside the fitted range; a new monomer kind | the table is computed, not stored values: a new bead set gives a new table |
| ions | per square and per cell, always (cheap) | ionic strength I per square and cell | never folded further | – |
| secondary | in the page, every new domain | helix/strand/coil probabilities, segment energies | always computed (cheap) | exact for every sequence |
| tertiary | offline on the GPU per new domain; provisional threading in the page meanwhile | Tm, ΔH_m, ΔCp (so f_folded at any T), native population, surface patches | a new domain sequence; T or I outside the range its curve was fitted on; a ligand state not yet folded; provisional values on domains under strong selection (proposal: fold those first) | provisional value computed from its own sequence; exact fold queued; the cache only grows |
| function | after each fold, offline; with threading in the page | per domain: specificity over 16 molecules, rate, cofactor need | a new fold; conditions out of range | scored from the pocket's lining, so any lining gives some value |

Each cached entry records what it summarises and over what range (T, I, pH), so a readout can flag use outside it
(THEORY_NOTES, "open and fold").

## 9. Choices for Justin (each changes the model)
1. **The page's reaction rule.** Replace the bracket-based rule (taken monomer, inner sum, adaptors) with function from
   the pocket (section 4), or keep the brackets as the page's chemistry for now and use the 3D fold only for
   stability and heat. Proposal: replace, in steps: first stability from the fold (brackets still set reactions),
   then reactions from pockets once the prototype shows they evolve.
2. **The monomer assignment** in section 1 (odd = apolar, complement pairs size- or charge-complementary), which keeps
   the page's two rules, or a free assignment.
3. **A cost for unfolded chains** (section 6).
4. **Four ion kinds** (section 2), and inside = outside until channels and pumps exist.
5. **Off-lattice** tertiary model (proposed) or a face-centred cubic lattice (cheaper, cannot show helices and sheets).
6. **Domains as the cache key**, with in-page threading as the provisional value.

## 10. Avoiding Martini's limitation (12b)
Martini's protein model does not fold: secondary structure is given as input and tertiary structure is held by an
elastic network or a Gō model built from a known structure. Here:
- the beads, the interaction matrix and the partitioning ladder are taken from Martini's approach; nothing else;
- secondary structure is computed from the sequence (section 3), as probabilities, and can be overruled by packing;
- tertiary energy depends only on the sequence through the contact table, burial, H-bonds and the many-body term; no
  term refers to any target structure (a "non-Gō" model);
- **test:** in the prototype, the folder is never shown a native. Its native is whatever it finds, and uniqueness,
  two-state melting and the rarity of foldable sequences are measured, not imposed. If the model needs a Gō-like
  term to fold at all, that is a failure to report, not a fix.

## 11. If approved: the prototype (step 3, not started)
Order proposed, each measured and reported before the next:
1. bead parameters and the contact table (with the calibration targets of section 1 checked);
2. secondary rule against simple checks (helix probability against propensities, charge patterns);
3. tertiary folder on the GPU: uniqueness, two-state ratio, Tm spread, share of foldable random sequences, cost per
   domain, against task 02's numbers;
4. pockets and specificity;
5. the threading estimate against exact folds (how good the provisional value is).

## Sources (checked 14 November, briefly)
- Souza et al. 2021, "Martini 3: a general purpose force field for coarse-grained molecular dynamics", *Nat. Methods*
  18: 382 (cgmartini.nl); bead classes Q, P, N, C with levels; donor/acceptor sub-types.
- Kaya and Chan 2000, "Polymer principles of protein calorimetric two-state cooperativity", *Proteins* 40: 637
  (arXiv cond-mat/0003479): common lattice models fall short of calorimetric two-state behaviour.
- Taverna and Goldstein 2002, "Why are proteins marginally stable?", *Proteins* 46: 105: marginal stability can arise
  from the high dimensionality of sequence space, not only from selection.
- Miyazawa and Jernigan 1985, 1996, and reviews of them (e.g. arXiv q-bio/0601026): desolvation (one-body) terms
  dominate the contact energies.
- From the project's own notes or the literature known to the session, not re-checked online in this visit:
  Li, Helling, Tang and Wingreen 1996 (*Science*; designability; degeneracy of two-letter models); Keefe and Szostak
  2001 (*Nature*; functional proteins from random sequences); Bloom et al. 2006 (*PNAS*; stability promotes
  evolvability); Zimm and Bragg 1959 (helix–coil); the Debye–Hückel length formula; Lehninger chapters 4 and 6.
