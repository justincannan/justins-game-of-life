# The copier gene: design (proposals for Justin; nothing here is decided yet)

Cloud session, 18 November 2026. From Justin's decisions of 16 November: a copier gene, with copying by pairing kept
folded most of the time into a rate and an error rate set by that gene.

## What the page has now
Copying is done by the page: every dividing cell's sequence is copied at the same speed. A cell whose catalyst is of
class 5, "copying fidelity", cuts its copying errors by up to a quarter. Nothing else about copying depends on genes.

## Questions, with Claude's recommendations
1. **What a copier is.** (a) A working domain of a new kind, with its own letter pattern: the copier. (b) The existing
   copying-fidelity catalyst, extended to speed as well. *Recommend (a)*: a gene of its own that can be duplicated,
   lost, transferred, and diverge, like real polymerases. The fidelity catalyst stays as proofreading.
2. **A cell without a copier.** (a) It cannot divide at all. (b) It still copies, but slowly and with many errors
   (copying without an enzyme, by bare pairing). *Recommend (b)*: no sudden cliff, so evolution can find and improve
   copiers; the simple founder still works. Strictness can rise later.
3. **What the copier's sequence sets.** Two folded numbers: speed (from the domain's strength, its same-kind pairs)
   and accuracy (from how closely its pairs match). *Recommend both*, with a trade-off, so a copier cannot be fastest
   and most accurate at once. Speed against accuracy is a real trade-off for polymerases (to be checked against sources
   before building).
4. **What copying speed does.** (a) Copying takes time in proportion to genome length ÷ copier speed; a cell cannot
   divide again until its copy is done. (b) Speed only lowers the energy cost of copying. *Recommend (a)*: long
   genomes then divide more slowly, the natural cost of length that the 256 cap stands in for now (16 November's
   question 1).
5. **Several copiers in one cell.** (a) Use the best. (b) Speeds add (dosage). *Recommend (a)* to start: simple, and
   a duplicate is then free to drift into something else.
6. **The modern founder** carries one copier gene of middling speed and accuracy; the simple founder carries none.
7. **Opening the fold.** Later, the GPU session can model copying by pairing in detail (letter by letter, with the
   pair strengths) to calibrate the speed and accuracy curves; the page uses the folded curves.
8. **A switch.** `P.copierOn` (default on), so runs can be compared with today's page exactly.

## Checks once built
- With `P.copierOn` off, runs match the current page exactly.
- Founding in each world with the modern and simple founders.
- Whether copiers evolve (speed and accuracy over 6,000 ticks), and whether genome length now levels off without
  the cap.
- Whether an error threshold shows: lines with high error and long genomes failing.
