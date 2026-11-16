# 31: detailed models for the modern-baseline founder: designs for parts 3–5

From: gpu session (scheduled check), 16 November 2026, about 15:30 New York. Answers
`to_gpu/2026-11-16_31_modern-founder-models.md` (Justin's decisions of 16 November, about 09:37–10:06, items 2–4).

**Everything below is a proposal.** Justin decides each part, its level of detail and the order. Nothing was built and
the page was not changed. The source figures quoted are standard textbook values written from memory in this
automated check, not re-read; each is marked *(to check)* and should be checked against the sources before anything is
calibrated on it.

## 0. How the page stands now (what the parts would change)
- A cell has no inside pool: its reactions (`domReactW`) run on its **square's** molecules, and a birth or a rewritten
  compound takes its molecules straight from the ground (`payChem`, `swapChem`). Uptake of chains from the water is a
  rule in `fragStep`.
- There are 16 molecule kinds (the monomers), each with an energy `RXE`; reactions come from domain shape.
- Four ion kinds were approved on 14 November (report 12, section 2): a sodium-like and a potassium-like monovalent
  cation, a chloride-like anion, a divalent (magnesium/calcium-like) cation; inside = outside until channels and pumps
  exist. There is **no proton** among them.
- The bead model (`beadfold/`) folds chains in implicit water; its helix term still waits on Justin (report 26, step 2:
  helices switch all-or-none).

So parts 3 and 4 both need, first, **an inside for each cell**: per-cell amounts of some molecule kinds and of the four
ions, separate from the square's. That is page code (the cloud's folded form), but every design below assumes it.

## 1. Part 3: a membrane with transporters
**Modelled in detail (bead level, proposal):**
- The membrane as an **implicit slab** added to the bead model: an oily core about 3 nm thick between two polar
  interface layers, entered as a depth-dependent transfer free energy for each bead class (the implicit-membrane
  approach, e.g. Lazaridis's IMM1 *(to check)*). No explicit lipids.
- A domain is folded with the slab present. Two readouts:
  1. **Insertion:** does the folded domain sit across the slab (an exposed oily belt about the slab's thickness), and
     with what free energy relative to staying in water.
  2. **Pore:** if inserted, is there a polar-lined passage through it; its narrowest radius and the charge of its
     lining. For each of the 16 molecule kinds and 4 ions (each given a size and a charge), the free-energy profile
     along the pore axis is computed from the same bead interactions, and its highest barrier gives a crossing rate.
- Passive pores only at first (flux down a concentration difference). Active uptake (coupled to an ion gradient, a
  symporter) would come with part 4, reusing the same pore readout.
- Bare membrane: a fixed leak per kind from the slab alone (oily small kinds leak, ions essentially not).

**Folded output to the page (proposal):**
- per transporter domain: a **permeability vector** p_k over the 20 kinds (16 molecules, 4 ions) and a saturation
  constant; flux J_k = p_k (c_out,k − c_in,k), saturating at high concentration;
- per cell: the bare-membrane leak vector (one table for all cells);
- cost: the existing running cost per working domain (`P.domCost`), plus optionally a cost per membrane domain for
  insertion (open question);
- the dependence on sequence comes through the emulator (task 24's approach): a cache keyed by domain sequence, with a
  learned estimate for sequences not yet folded.

**Checked against sources (proposal; figures to check):**
- the bare bilayer's permeability ordering: water and small nonpolar molecules fastest, sugars much slower, ions slower
  by many orders of magnitude *(to check: Alberts, Molecular Biology of the Cell, membrane transport chapter)*;
- a membrane-spanning helix needs about 20 residues to cross the oily core *(to check)*;
- channels select by size and by the charge of their narrowest point; carriers saturate (Michaelis–Menten) and are far
  slower per protein than channels *(to check)*.

**Expected GPU time (rough estimate, not measured):** a folded domain in report 26 cost up to 240 s of GPU for a final
design; insertion plus a pore profile might cost 30–120 s per domain. An emulator training set of 500–2,000 domains is
then about 4–60 hours of GPU. A first test on 50 domains (does anything insert? do pores form?) is about 1–2 hours.

**Open questions for Justin:**
1. A per-cell inside pool is the big page change. Which kinds does it hold: all 16 molecules and 4 ions, or only some?
2. Membrane-spanning domains in real cells are mostly helices. The bead model's helix term is still open (report 26);
   should part 3 wait for it, or start with whatever the current fold gives?
3. Lipids: made by the cell (a precursor, part 5) or given (the membrane simply exists)?
4. Justin's earlier wish for realistic cell walls: a separate outer layer later, or part of this membrane model?

## 2. Part 4: an ion gradient driving an ATP-synthase-like gene
**Modelled in detail (proposal):** mostly **rate equations**, not beads.
- Each cell carries inside amounts of the four ions. The gradient's energy per ion moved is the electrochemical
  difference Δμ = kT ln(c_out/c_in) + z e Δψ.
- **Which ion couples** (proposal): the sodium-like cation, so no fifth ion is needed. Sodium-driven ATP synthases do
  exist, and sodium coupling has been argued to be old (Mulkidjanian and others, 2008) *(to check)*. The alternative is
  to add a proton (pH is already a parameter of the bead model).
- **Pump:** a domain that couples a downhill reaction (from the existing reactions from shape) to moving ions out; a
  light-driven pump could couple to the pigment the same way.
- **Synthase-like gene:** a domain that lets ions back in and adds to the cell's energy store. Its fold sets
  **n, the ions per unit of energy stored** (in real synthases, the size of the rotor ring sets the ions per ATP
  *(to check)*); here n could be read from the number of repeats of a motif in the gene. It runs backwards (as a pump)
  when the gradient is too weak, as real synthases can *(to check)*. The rotary mechanism is not modelled: the fold
  gives n, the ion it passes (part 3's pore readout) and a maximum rate; thermodynamics bounds the rest (no energy
  stored beyond n Δμ per unit).
- **Leak:** the bare membrane's ion leak (part 3) plus any pore that passes the coupling ion.
- Δψ: proposal to start with concentrations only, and add the membrane potential (from net charge and a membrane
  capacitance) once the first version works.
- Time scale: real gradients settle in milliseconds, far below a tick, so the gradient can be solved at steady state
  each tick rather than integrated.

**Folded output to the page (proposal):** per synthase gene: n, its ion, its maximum rate; per pump: ions per
reaction turn (or per unit of light), its ion; per cell: leak per ion kind; cost through `P.domCost`. Energy yield per
unit of gradient = n × Δμ × an efficiency below 1.

**Checked against sources (figures to check, Lehninger was the project's source in task 18):** the free energy of ATP
synthesis in a living cell, about 45–55 kJ/mol; a typical proton-motive force, about 150–200 mV; protons per ATP from
rotor sizes of 8–15 subunits, about 2.7–5; membrane capacitance about 1 µF/cm².

**Expected GPU time:** the rate equations need none. Only the pump's and synthase's ion selectivity uses part 3's pore
model, a small extra over part 3.

**Open questions for Justin:**
1. The coupling ion: sodium-like (no new species) or a new proton?
2. Does the synthase feed the existing energy store (`light`), or is a separate ATP-like currency wanted?
3. Membrane potential from the start, or concentrations only first?

## 3. Part 5: simplified building-block metabolism
**Modelled in detail (proposal):** a small **reaction network**, rate equations and bookkeeping; no beads.
- A few **precursor kinds** (proposal: 3–5), made from food by reactions that domains can run (the existing reactions
  from shape), or taken up (part 3). Real cells build all their building blocks from about a dozen central precursor
  metabolites (twelve in *E. coli*, Neidhardt and others *(to check)*); a few here would keep the same shape.
- Copying a monomer takes its precursors plus energy, by a table need[monomer][precursor]. With part 1 (4-letter
  storage and 16 working letters) there are two families to cover.
- The GPU side's work: check that the network is energetically consistent with `RXE` (no free energy from cycles), and
  compute what each monomer costs in energy and precursors when the network is run as a whole (a flux-balance or
  kinetic calculation). Real amino acids differ several-fold in their cost to make (Akashi and Gojobori, 2002, about
  12–74 high-energy bonds each *(to check)*); a spread like that would give selection on composition.
- What could emerge: cells that lose a precursor pathway and take the precursor from neighbours (auxotrophy,
  cross-feeding; the Black Queen idea of Morris and others, 2012 *(to check)*). That needs no script, only the cost.

**Folded output to the page (proposal):** the table need[monomer][precursor]; the precursor-making reactions and their
energies, placed in the existing reaction catalogue; an energy cost per monomer that replaces the flat `P.seqCost`
(light per monomer copied).

**Checked against sources:** the precursor scheme and the cost spread above *(to check)*.

**Expected GPU time:** none needed; minutes on the CPU.

**Open questions for Justin:**
1. How many precursor kinds, and does the precursor table replace `payChem`'s direct use of the ground's molecules?
2. Which family first: the 16 working letters, the 4 storage letters, or both together?

## 4. Order (proposal; Justin decides)
- Part 5 first: it is the cheapest, needs no membrane, and works on the current page.
- Then part 3, which needs the inside pool and probably the helix term.
- Then part 4, which needs part 3's membrane and pores.

The GPU side will not start any of the builds until Justin chooses.
