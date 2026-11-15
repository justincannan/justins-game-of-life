# 22: the population scale rethought; the code-change split

From: cloud session, 15 November 2026, about 10:50. Justin's decisions: THEORY_NOTES.md, "Decisions on reports 13 and
17".

1. **The split (CPU, small).** Split report 13's "about 13% of daughters carry a different reaction program" into:
   - mutation at division;
   - code transfer (contagion) during the parent's or daughter's life;
   - anything else.
   Give each per division, and per genome per division. Compare with Drake's rule, about 0.003 mutations per genome
   per replication in DNA microbes (Drake 1991).
2. **Report 17's cheap test (proposal 5 there), approved.** The task 07 fine-grid model with:
   - a per-cell store and threshold for going still;
   - gliding only while active and coated;
   - births paid from sugar at the cell's own square.
   Report whether it branches, and which ingredient matters (switch them off one at a time).
3. **Then the new population model.** Not fitted to the page's colony shape. It carries the page's per-cell rules,
   measured where needed:
   - growth, going still, waking, costs;
   - income from the local nutrient.
   It runs them with a nutrient diffusion length that is realistic relative to cell size. State your source for the
   scale; do not guess. Agar firmness enters as cell motility.
   - Run it across nutrient level and firmness, and compare the shapes with Matsushita's morphology diagram:
     DLA-like, Eden-like, dense branching, concentric rings, homogeneous disc. Use Fujikawa and Matsushita 1990 and the
     later diagram papers, abstracts or open copies only.
   - Report which regions appear.
   - Its opening into single cells (the page's model in a patch) is designed once the shapes are right.
4. **Dropped as goals:**
   - fitting a coarse model to the page's dendrites;
   - report 06's proposal 2 on its own (its place-set income is part of item 3);
   - task 10 (finer blocks).

Order: item 1, then item 2, on the CPU queue. Item 3 after Justin sees item 2's result. Task 15's next step on the GPU
waits on Justin's folding decision.
