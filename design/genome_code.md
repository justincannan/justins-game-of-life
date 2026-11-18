# The 4-letter code: design (proposals for Justin; nothing here is decided yet)

Cloud session, 18 November 2026. From Justin's decision of 16 November (THEORY_NOTES, "Decisions (Justin, 16 November,
about 09:37–10:06)", item 3.1): 4-letter storage, translated by a three-letter code (64 codons) into the working
letters; the translation folded into a code table the cell carries and can mutate.

## What stays the same
The working chain (16 letters a–p) and everything that reads it: folding, domains, reactions, the compound, gene
markers, the inspector. The code adds a storage strand underneath; the working chain becomes its translation.

## Questions, with Claude's recommendations
1. **When translation happens.** (a) At birth and whenever storage changes; the working chain is kept as a cache.
   (b) Every tick. *Recommend (a):* this is the fold. Nothing in the dynamics needs translation in between.
2. **Whose table.** (a) Each cell carries its own table, inherited, rarely changed. (b) One table for the whole world.
   *Recommend (a)*, as decided ("a code table the cell carries and can mutate"). A table change rewrites every gene at
   once, so it should be rare: 1 in 10,000 births, one codon reassigned.
3. **The founder's table.** (a) Letter = 4 × first base + second base: each letter has 4 codons, and any change at the
   third base is silent. The oily/polar parity follows the second base, so first-base changes keep a letter's
   polarity: errors tend to land on similar letters, as in the real code. (b) Irregular redundancy and stop codons, closer to
   the real table. (c) A random table. *Recommend (a)*, simple and error-tolerant. Tables can drift from it by
   reassignment.
4. **Gene boundaries.** (a) Keep markers as runs of 4 identical working letters, now encoded by codons. (b) Dedicated
   start and stop codons. *Recommend (a) for now*, since nothing downstream changes. (b) is a later step towards
   real genes.
5. **Mutation rate.** Mutations happen in storage, per base. (a) Per-base rate = per-letter rate ÷ 3, the same raw rate
   per letter; with the third base silent, letter-changing errors drop to two-thirds. (b) Per-base rate = per-letter
   rate ÷ 2, the same letter-changing rate as now. *Recommend (b)*, so evolution is not slowed by the change; silent
   changes then come on top.
6. **Chains without storage.** Free chains in the water, virus chains and the dish's stored lines are working letters.
   When one enters a genome: (a) back-translate with the receiving cell's own table (the first codon for each
   letter), like reverse transcription; (b) give chains and viruses a storage form too. *Recommend (a) now*, (b) later
   if viruses need their own genetics.
7. **Transfer between cells.** (a) Splice storage bases. If two cells' tables differ, the gene reads differently in
   the recipient, as in real life. (b) Splice working letters and back-translate. *Recommend (a).*
8. **Memory.** Storage is 3 × 256 = 768 bases a cell: about 90 MB at the current world size, one byte a base.
   Packing 4 bases a byte saves three-quarters but slows every copy. *Recommend one byte a base now*, and packing
   later if memory binds.
9. **A switch.** `P.codeOn` (default on), so the old direct chain stays available for comparisons. This is separate
   from the founder checkbox, because the code is machinery for every cell, not a founder's gene.

## Checks once built
- With `P.codeOn` off, runs match today's page exactly.
- With it on and the founder's table: the same founding rates as now in each world (pond, vent, even, dish).
- The share of mutations that are silent, and how often tables drift, over 6,000 ticks.
- Speed and memory against the timing of 16 November.

## Then: the copier gene (part 2)
Its design follows once the code is in: what the copier domain is (a letter pattern), how its sequence sets the
copying rate and error rate, and what a cell without one does.
