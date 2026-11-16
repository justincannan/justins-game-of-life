# Stage 1 design: from one chain to a genome of genes

Draft by the cloud session, 15 November 2026, for Justin's review. Justin decided to follow this line (THEORY_NOTES.md,
"Decision (Justin, 15 November, about 22:42)"). Everything below is a proposal unless marked as a measurement. Nothing is
built.

## 1. Where we start (measured, 15 November)
Today each cell has one line of up to 128 monomers (`seq`, `slen`). It folds by nested complementary pairs (`infold`):
- the closed pairs are domains;
- up to 4 working domains give the cell's reactions (`rx`, one byte each);
- domains before the first unpaired monomer act as adapters, remapping codes (`sCode`);
- the unpaired monomers make the compound (`gen`), which sets the rules and the building cost.

One run per world, tick 1,000:
- **Lines are short:** mean 9 monomers, longest 29, in the even world from a soup. The 128 limit is far away; length is
  held down by `seqCost` per monomer and by copying errors.
- **The reaction cap binds:** 39% of cells (30,320 of 77,508) already run the maximum of 4 reactions.
- **Runs of identical monomers are not rare:** 10% of lines contain a run of 3 or more, 2.3% a run of 4 or more.

The second point is the plainest sign that one chain is limiting.

## 2. The proposal in one paragraph
- **Genes:** the line stays one heritable string, but marker motifs divide it into genes.
- **Folding:** each gene folds on its own; pairs never cross a marker.
- **The cell's abilities:** the union of its genes' working domains, up to a larger cap.
- **Identity:** the compound stays the unpaired monomers summed over the genes, so a one-gene genome behaves exactly as
  today.
- **New ways for genomes to change:** genes can be born by fission (a marker arising inside a gene); genes can fuse (a
  marker lost); whole genes can be duplicated, lost and transferred.

Stage 2 (expression levels) and stage 3 (storage separate from function) build on this without changing it.

## 3. Choices for Justin

### 3.1 How a gene boundary is marked
**A. A motif of ordinary monomers: a run of 4 identical monomers.** (Proposed.)
- *For:* made of the same chemistry as everything else, as real promoters and terminators are made of ordinary
  nucleotides. Boundaries can arise and vanish by ordinary mutation, so gene fission and fusion emerge. No letter is
  privileged.
- *Against:*
  - 2.3% of today's lines contain such a run and would split at once; that is harmless, they become two-gene genomes;
  - runs of 4 become impossible inside a gene, a small constraint on folds.
- *Variant:* a run of 3. It is more evolvable (fission easier), but 10% of today's lines would split, and it
  constrains folds more.

**B. A separator symbol outside the 16 monomers.**
- *For:* no accidental splits, simplest to read.
- *Against:* not made of chemistry, so it costs nothing and cannot be made or broken by the ground's molecules. Gene
  fission and fusion would need their own invented mutation operator rather than arising.

### 3.2 What a gene's fold gives the cell
- **Each gene folds separately** with `infold` over its own range. Adapters act within their own gene only, so each gene
  carries its own regulation (closer to real cis-regulation).
- **Reactions:** the union over genes, cap raised from 4 to 8. This needs a second 32-bit word per cell (`rx2`) and a
  matching strength word. `domReact` loops over up to 8; worst-case cost about double for the cells that use all 8.
- **Whether to keep a per-gene cap:** say 4, so that one long gene cannot take all 8 slots. Proposed: yes, 4 per gene,
  8 per cell.

### 3.3 The compound (identity, rules, building cost)
- **Proposed:** the unpaired monomers summed over all genes, capped at 3 per kind, as today. A one-gene genome is then
  unchanged. Separating genes does not by itself change a cell's identity, only its folds.
- **Alternative:** the compound of the first gene only (a "chassis" gene), with the other genes as pure function. It is
  cleaner, but a large change to how cells are identified and costed.

### 3.4 How genomes change
Existing operators keep acting on the whole line:
- point mutation (`seqMu`);
- segment duplication and deletion (`seqDup`, `seqDel`);
- domain duplication (`domDup`);
- crossover with a partner;
- homologous uptake of chains.

Markers arise and vanish through them. New, whole-gene operators (proposed rates are starting points):
- **gene duplication** (`geneDup`, about 0.005 per division): a copy of one gene inserted after it. This is the main
  route to new functions in real genomes: a spare copy is free to change;
- **gene loss** (`geneDel`, about 0.005 per division);
- **gene transfer:** contagion and the viruses' chains can carry a whole gene and insert it as a new gene rather than
  overwrite a stretch. This ties in with the viruses: a chain that inserts as a gene is a prophage, so lysogeny could
  arise rather than being written in.

### 3.5 Size and cost
- **Maximum line:** 128 now; proposed 256, with at most 8 genes.
- **Cost:** `seqCost` per monomer as now, so more genes cost more to copy, as in real cells. Marker monomers cost like
  any other.
- **Do lines lengthen?** Whether they do, given the copying cost, is itself a measure of whether more genes pay.

### 3.6 Fit with folding (tasks 23, 26, 24)
- **The cache:** each gene's chain is the unit that gets folded and cached by the two-bead folder, and learned by the
  emulators. Short separate chains are cheaper to fold and easier to learn than one long one.
- **Until folds are ready,** the page keeps today's bracket folding per gene. The switch to real folds is per gene and
  can come later without changing this design.

### 3.7 Display
- The inspector lists the genes, each with its domains and reactions.
- The fold viewer gets one drawing per gene.
- The census can show genes per cell and gene families (shared sequences).

## 4. Compatibility
- **A line with no marker is one gene and behaves as today,** apart from the second reaction word, which stays empty
  when 4 or fewer reactions are used.
- **The 2.3% of today's lines with a run of 4 split on switching.** No saved worlds need converting, because worlds
  start fresh.
- **The founder** (`seqFromGen`) is built without runs of 4. The pigment fold (`pigFounder`) becomes a second gene
  rather than an appended domain: the same fold, now separate.

## 5. What to measure once it is built
- Genes per cell over time, and line length, in each world. Do multi-gene genomes win?
- The share of cells using more than 4 reactions.
- Gene duplications that later diverge (a duplicate whose reaction changes): new functions by duplication.
- Gene transfer between lineages, and whether virus chains insert as genes (lysogeny).
- The dish and the validation baselines (report 17), checked for drift.

## 6. Questions for Justin
1. Boundary marker: A (a run of 4, proposed), the run-of-3 variant, or B (a separator symbol)?
2. Reaction cap: 8 per cell with 4 per gene (proposed), or something else?
3. Compound: summed over genes (proposed), or a chassis gene?
4. Whole-gene duplication, loss and transfer, including virus chains inserting as genes: yes?
5. Maximum line 256 and at most 8 genes: yes?
6. Build now on bracket folds (per gene), or wait for real folds? Proposed: build now. It does not depend on the folder,
   and it lets us see whether more genes pay before folding arrives.
