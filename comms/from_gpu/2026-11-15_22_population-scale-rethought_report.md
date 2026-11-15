# Report on task 22: item 1 (the code-change split)

From: gpu session (scheduled check), 15 November 2026, about 11:30. Items 2 and 3 are not started; item 2 is next, on
the CPU queue, at a later check. Item 3 waits on Justin seeing item 2.

## Summary
- **Report 13's "about 13%" was mostly my own measuring error.** Task 13 gave a cell that died within the 50-tick window
  the program 0 at the window's end. About 10 of the 13 points are such pairs. Corrected, about 2.6–3.5% of
  parent–daughter pairs differ in program at the window's end.
- **Per division (measurement),** 3.9% (sugar 1), 5.5% (sugar 3) and 5.6% (sugar 10) of daughters are born with a
  program different from the parent's at that moment. Nearly all of it is mutation at division. Crossing with a second
  parent adds 0.02–0.4 points. Nothing else contributes.
- **Code transfer during life** changes a program 0.001 (sugar 1), 0.009 (sugar 3) and 0.009 (sugar 10) times per
  division. That is about a sixth of the mutation rate at sugar 3 and 10, and almost nothing at sugar 1. All of it is
  contagion. Fragment uptake and soma silencing never changed a program in these runs.
- **Per genome per division,** a copy carries 0.09–0.11 sequence events (point errors, duplications, domain
  duplications, deletions). Drake's rule is about 0.003 per genome per replication for DNA microbes, so the page copies
  with about 30–40 times as many errors. About 0.04–0.06 of these events per division change the program.
- **Report 13's other conclusions hold.** Corrected, they move by a few percent at most: place outweighs lineage, the
  spreads are the same, and so is the persistence per generation. Its genotype figures change. A changed program shifts
  income more than reported (D 0.24–0.39, not 0.05–0.17). The "change per cell-window by fragment uptake or contagion"
  was 0.06; it is 0.000–0.001.
- **A possible page bug, for the cloud side.** Contagion rewrites the recipient's sequence and program before the page
  decides to keep the change. When the page refuses (same compound, or `swapChem` cannot pay), the cell keeps its old
  compound (`ngen`) but its new sequence and program. That is 43% of program-changing contagions at sugar 10 and 27% at
  sugar 3.

## 1. Method
- The page is the one task 13 used. It is byte-identical to the repository's current `build/justins_game_of_life.html`.
  Task 13's lineage-marked harness copy has extra hooks (`test/split22_page.py`) at every place where a cell's program
  (`rx`, `rxStr`) can change:
  - the copy at division: point errors, duplications, domain duplications, deletions, crossing with a second parent;
  - contagion (`seqTransfer`), and whether the page keeps it;
  - fragment uptake.
  The recorder `test/split22.js` is task 13's `lineage.js` plus these records, and wrappers of `regApply`,
  `regRestore` and `seqFromGen`. The hooks only read; they draw no random numbers.
- The settings are task 13's: sugar 1, 3 and 10, glide 0.1, 3 seeds each, 2000 ticks, a 256 × 256 world.
- **No-change check:** in all 9 runs the per-tick record (active, still, births, stores, sugar, place hash) equals task
  13's marked run at every tick (0 of 2000 ticks differ).
- Analysis: `popdish/split22.py`. Results: `results/2026-11-15/task22/` (in `D:\labyrinth\automata\jgol_2026-11-13`).
- Program = `rx` × 256 + `rxStr`, the genotype task 13 compared.

## 2. Per division (measurement; mean of 3 seeds, range in brackets)

| sugar | divisions | daughter's program differs | by a changed copy (one parent) | by a cross | other | copies that change the sequence | of those, change the program |
|---|---|---|---|---|---|---|---|
| 1 | 5296 | 0.039 (0.034–0.045) | 0.039 | 0.0002 | 0 | 0.104 | 0.38 |
| 3 | 28774 | 0.055 (0.047–0.060) | 0.054 | 0.0011 | 0 | 0.108 | 0.51 |
| 10 | 77397 | 0.056 (0.052–0.058) | 0.052 | 0.0043 | 0 | 0.087 | 0.59 |

- "Other" would be a daughter with an exact copy of the sequence but a different program (a silenced parent). There
  are none; soma cells do not breed.
- Crossing happens in 0.15%, 0.28% and 0.85% of divisions.
- The page also copies a sequence for each birth it then refuses (no room, not enough to pay): 3–6 copies per
  birth that happens. Only births that happen are counted here.

## 3. Per genome per division (one-parent copies; measurement)

| sugar | sequence events | point errors that change the monomer | duplications | domain duplications | deletions | point draws of the same monomer (silent) | events that change the program |
|---|---|---|---|---|---|---|---|
| 1 | 0.109 | 0.046 | 0.018 | 0.011 | 0.034 | 0.002 | 0.039 |
| 3 | 0.114 | 0.054 | 0.017 | 0.011 | 0.032 | 0.003 | 0.055 |
| 10 | 0.092 | 0.036 | 0.018 | 0.009 | 0.029 | 0.002 | 0.052 |

- **Against Drake's rule** (about 0.003 mutations per genome per replication, DNA microbes; Drake 1991): the page's
  copies carry about 30–40 times as many sequence events. Even counting only events that change the program, the rate
  is 13–18 times higher.
- The settings behind them: `seqMu` 1 (scaled per birth by the zone's rate, the proofreading enzyme and temperature),
  `seqDup` 0.02, `seqDel` 0.02, `domDup` 0.01. The rate per monomer is not measured here.

## 4. During life, per division (measurement)

| sugar | contagion kept, program changed | contagion refused but program already rewritten | fragment uptake | soma silencing | contagion splices (any) |
|---|---|---|---|---|---|
| 1 | 0.0009 | 0 | 0 | 0 | 0.003 |
| 3 | 0.0068 | 0.0024 | 0 | 0 | 0.014 |
| 10 | 0.0049 | 0.0037 | 0 | 0 | 0.013 |

- Splices that leave the program unchanged are counted in the last column only.
- No fragment was taken up in any run, and no clump silenced its soma.
- Per genome per division: transfer during life changes a program about 0.001, 0.009 and 0.009 times, against 0.04–0.06
  for mutation at division.

## 5. Report 13's pair measure, rebuilt and split (measurement)
These are parent and daughter rows in the same window, both active at least 20 ticks, compared by program at the
window's end. The pairs are as in task 13.

| sugar | pairs that differ (task 13) | one of the two died in the window | mutation at division | transfer during either life | cross | mixed |
|---|---|---|---|---|---|---|
| 1 | 0.126 | 0.103 | 0.023 | 0.0001 | 0.0002 | 0 |
| 3 | 0.133 | 0.102 | 0.028 | 0.0023 | 0.0006 | 0.0002 |
| 10 | 0.127 | 0.098 | 0.025 | 0.0020 | 0.0018 | 0.0002 |

Report 13's analysis was re-run with those rows dropped (`popdish/lineage13_alive.py`; the marked runs are unchanged).

| sugar | parent–daughter differ (13 → corrected) | own change per window | D, changed program | lineage sd (csd) | share place | persistence (k = 1–4 D) |
|---|---|---|---|---|---|---|
| 1 | 0.126 → 0.026 | 0.058 → 0.000 | 0.053 → 0.236 | 0.181 → 0.181 | 1.09 → 1.09 | unchanged within 0.002 |
| 3 | 0.133 → 0.035 | 0.060 → 0.001 | 0.102 → 0.328 | 0.267 → 0.266 | 0.86 → 0.87 | unchanged within 0.006 |
| 10 | 0.127 → 0.032 | 0.064 → 0.001 | 0.167 → 0.389 | 0.341 → 0.330 | 0.67 → 0.66 | unchanged within 0.025 |

- The store2 re-run in report 13 used cmu 0.13. The measured value is about 0.03–0.05. A slower walk keeps even more
  per generation, so store2's failure to match the page's fast loss of lineage similarity stands.
- I have marked report 13's figures as superseded in this report. Report 13 itself is not edited.

## 6. The contagion order (measurement; possible bug, for the cloud side)
- `seqTransfer(i, j)` writes the stretch into j's sequence, refolds, and sets `rx`, `rxStr`, `cat` and `cH` of j. Then the
  contagion loop checks `g === ngen[j]` and `swapChem(...)`, and on either `continue`s without restoring j's sequence.
- Measured: 661 program-changing splices at sugar 10, of which 377 were kept. 284 left the cell with its old compound
  and a new program. At sugar 3, 283 and 207. Fragment uptake does restore the sequence when it refuses; contagion does
  not.
- Proposal (Claude): restore j's sequence and program when the page refuses, as uptake does. Whether this is intended
  is the cloud side's and Justin's call. I changed nothing.
