# 29: re-baseline the dish on the stage-1 page; investigate vent founding

From: cloud session, 16 November 2026, about 00:25. Justin's decisions (THEORY_NOTES.md, "Decisions (Justin, 16
November, about 00:19)").

**The page changed** (commit 6995cd7, "Stage 1 of the genome"). Genes are marked by runs of 4 identical monomers and
fold separately. Cells can have 8 reactions. Genes are duplicated, lost and transferred whole, and virus chains can
integrate. Lines go up to 256 monomers. See design/genome_stage1.md and THEORY_NOTES.md.

1. **Re-baseline the dish** at sugar 1, 3 and 10, 3 seeds each:
   - counts;
   - box dimension and roughness;
   - cell-scale maps.
   Report any change from report 17's baseline beyond seed spread, and the share of multi-gene genomes in the dish.
2. **Vent founding.** From one organism, the vent world founded life in 0 of 10 seeds (11–20) on both the previous
   page (5b491ee) and the stage-1 page, harness world 476 × 248, no autoRestart. Earlier notes said 6 of 6 (13
   November). Find when it broke and why:
   - bisect over commits if useful;
   - check the dark vents' energy budget for the founder's first few divisions;
   - report the page's own default world size, if it differs.
   Propose a fix; do not change the page.
3. CPU queue, after task 28 item 1 if they compete.
