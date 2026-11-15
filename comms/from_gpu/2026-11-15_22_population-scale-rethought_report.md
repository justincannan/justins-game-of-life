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

## Item 2: the per-cell-store test

From: gpu session, 15 November 2026, about 13:05 New York. This is report 17's proposal 5, approved in task 22, item 2.
Item 3 is not started; it waits on Justin seeing this.

Measurements are measurements. The model's form, its calibrated constants and the readings are proposals (Claude's).

### In short
1. **It branches.** With all three ingredients on, task 07's fine-grid model grows thin arms with active tips at
   sugar 3 (figure `22_sugar3.png`). The arms are about 2.5–3 places wide, like the page's (2.9–3.2), and they carry
   gaps of empty agar between them. At sugar 10 it makes a dense branched front, and at sugar 1 a ring with short
   arms. Task 07's model, and this one with all three ingredients off, grow a filled, ragged disc.
2. **Gliding matters most.** Gliding only while active and coated is ingredient (b).
   - **Switched off,** with every active cell gliding at 0.1 a tick as in task 07, the colony becomes a spreading
     scatter. At sugar 3, 33–63% of live places have no live neighbour at ticks 500–1,000, against the page's 5–13%.
     By tick 1,000 it covers the plate.
   - **Measured on the page:** a cell glides only 0.0003–0.009 times per active cell-tick, 10–300 times less than
     task 07's 0.1. Most cells have too little coat.
3. **Births paid from sugar matter next.** This is ingredient (c).
   - **Switched off,** so that task 07's fitted birth rates and chemistry-paid births return, the colony grows as a
     filled disc with a ragged rim. It covers 70–82% of the circles through its footprint at sugar 3, against the
     page's 15% and the full model's 20–40%.
4. **Going still by the store (ingredient a) does not decide the shape.** Switched off (task 07's block rates), the
   arms are still there. Their widths are the same (2.4–2.5 places) and the cover is a little lower (0.14–0.28
   against 0.20–0.40 for the full model at sugar 3). It changes the counts: fewer cells
   stay active.
5. **The full model undergrows the page.** Per active cell it gives birth at 0.5–0.7 times the page's rate, and at
   0.3 times at sugar 10 after tick 250. At sugar 3 it reaches the page's tick-500 radius only at about tick
   1,500–2,000, with fewer live cells (about 700 against 1,600). Section 5 says what this does and does not limit.
6. **Facts about the page found along the way (measurements):**
   - **Gliding:** 0.0003–0.009 glides per active cell-tick (point 2).
   - **Sugar-paid births use the daughter's square.** A birth paid from sugar is checked and paid at the square
     where the daughter is born (`en[cmap[i]]`, i the empty place), not the parent's square. Proposal 5 said "the
     cell's own square"; the model follows the page.
   - **Both fields spread only every second tick.** Sugar (`energyStep`) and the molecules (`chemStep`) spread
     inside the `(tick & 1) === 0` block. So the page's sugar spreads at 0.4 places² a tick, not 0.8, and the
     molecules at 0.48, not 0.96. Report 16's two rates are twice the effective ones. Task 07's fitted sugar rate
     (0.025 coarse squares² a tick) is the page's effective rate.

### 1. The model (proposal)
`jgol_2026-11-13/popdish/pop22_store.py`, a new file; `pop2_gpu.py` is unchanged.
- It keeps task 07's lattice: one place holds one cell; 4 × 4 coarse squares hold the sugar and the molecules; the
  page's plate size (256 × 256, radius 121.6) and task 07's inoculum ring; and task 07's fitted death rates.
- It adds a store E and a coat to every cell. Each tick an active cell:
  - gains chemistry income;
  - pays upkeep;
  - leaks 0.01 into its square's sugar every second tick, while E > 0.01;
  - tops its store up towards 0.4 from its square's sugar.
  All of this is the page's code, with the numbers in section 2.
- **Ingredient (a), going still by the store.**
  - A cell whose store is below 0 after its costs goes still.
  - A cell whose store is below 0.03 goes still with chance 0.15 a tick (the page's `sporePass`).
  - A still cell with E > 0.3 wakes with chance 0.03 a tick.
  - Off: task 07's block rates of going still and waking.
- **Ingredient (b), gliding only while active and coated.**
  - Coat comes from chemistry and decays by 0.98⁸ every 8 ticks.
  - An active cell with coat ≥ 0.05 glides with chance 0.1 · min(1, coat) and spends 0.05 of its coat (the page's
    `glidePass`).
  - Off: every active cell glides at 0.1 a tick.
- **Ingredient (c), births paid from sugar.**
  - Each tick an active cell picks a random empty neighbour (the page's `divPick`). Where several cells pick the same
    place, one wins at random.
  - A birth is paid from the store if E ≥ 0.4032. It costs 0.2032.
  - Otherwise it is paid from the daughter's square if E ≥ 0.2032 and that square holds 0.5 sugar. It burns 0.5
    sugar.
  - Chemistry pays for no birth directly.
  - Off: task 07's fitted attempt rates, including chemistry-paid births.
- In every variant a daughter takes half the parent's store.
- With all three off, this is task 07's model with store bookkeeping that never acts back on the cells.
- **Runs:**
  - sugar 1, 3 and 10; five variants (all on, each one off, all off); 6 seeds; 2,000 ticks;
  - torch on the CPU, through the CPU queue (`jgol22-main-s1`, `-s3`, `-s10`, about an hour each).
  - The page's baseline is task 17's random-order runs, 12 seeds.
- **Per-cell probe of the page:** `test/probe22.js`, read-only, 3 seeds per sugar, port 8795, CPU queue. It gives the
  gliding, coat, store, chemistry and birth numbers used here.

### 2. Constants
**Calibrated or measured for this test** (all from `probe22.js` on the page, sugar 1, 3 and 10, 3 seeds):
- **Chemistry income per active cell-tick: c = 0.0067 · x/(x + 4.25).**
  - x is the molecules' stored energy per active cell in the square.
  - The fit is weighted least squares over the reaction calls (2.4 to 5.9 million per sugar level), in 12 bins of x.
  - Task 07 had 0.0065 and 8.4, fitted on 10 × 10 blocks.
- **Molecule energy drawn: 2.7 per unit of income** (measured 2.5–3.4). Task 07 had 6.0.
- **Spread of income: exponential about c, redrawn every cell-tick.**
  - On the page, 14–17% of calls pay more than 0.008 and 1–5% more than 0.02. An exponential with the same mean gives
    23% and 3%.
  - Without the spread, no store ever passes the 0.4032 a store-paid birth needs.
  - Keeping a cell's draw for 50 or 500 ticks was tried (3 seeds, 1,000 ticks) and grew no better, so the
    every-tick form is used.
- **Coat per unit of chemistry income: 0.42**, pooled over sugar levels and windows (0.16–0.70).
- **Nothing else was tuned.** No constant was fitted to the colony's counts or shape.

**From the page's code** (`build/justins_game_of_life.html`, unchanged): the page's parameter defaults, and the
inoculum's gene strengths read from its `xg` value.
- Store and upkeep:
  - upkeep 0.0028 = cost 0.01 × dishUpkeep 0.24 × 1.18, as in report 13; a still cell pays 0.1 of it;
  - leak 0.01 every second tick while E > 0.01, returned to the square's sugar;
  - top-up towards 0.4 at up to 0.06 a tick (a still cell 0.015), at 0.4 store per sugar, at most 0.3 sugar a tick;
  - the inoculum starts with E = 1.
- Going still and waking:
  - going still below E 0 always, and below 0.03 with chance 0.15 a tick;
  - waking above 0.3 with chance 0.03 a tick.
- Births: cost 0.2 plus 0.0032 for the sequence (seqCost 0.0004 × length 8); a store-paid birth needs E ≥ 0.4032.
- Coat and gliding: coat decays by 0.98⁸ every 8 ticks; gliding needs coat ≥ 0.05 and costs 0.05 coat; glide chance
  0.1 · min(1, coat).
- Spreading every second tick: sugar 0.2 × (mean of 4 − own); molecules 0.24 × (mean of 4 − own).

**Task 07's** (`fit_two.json`, used only where an ingredient is off), together with the deaths, which every variant
uses:
- going still 0.0231/(1 + sb/0.51 + c/0.00088);
- waking 0.00031 · sb/(sb + 2.4);
- birth attempts 6 × (0.238 · sb/(sb + 96.8) + 0.63 · c), with sugar-paid births costing 1.49 sugar;
- deaths 0.0029 (active) and 0.0028 (still), close to the page's measured 0.002–0.010 and 0.0021–0.0024.

**Left out (proposal):**
- the molecules a child's compound takes (`payChem`);
- the page's lysis of remains: the page's remains disappear after about 500 ticks, the model's stay;
- lineages and mutation.

### 3. Per-cell rates, page against the full model
Per active cell-tick; mean of 3 seeds for the page and 6 for the model. Each cell gives page / model.

| sugar | ticks | births | going still | glides | chemistry income | store (mean) | sugar into the store |
|---|---|---|---|---|---|---|---|
| 1 | 1–250 | 0.0056 / 0.0039 | 0.0044 / 0.0008 | 0.0003 / 0.0017 | 0.0054 / 0.0048 | 0.32 / 0.28 | 0.0026 / 0.0025 |
| 1 | 251–1,000 | 0.0034 / 0.0020 | 0.0006 / 0.0007 | 0.0020 / 0.0046 | 0.0068 / 0.0059 | 0.32 / 0.23 | 0.0032 / 0.0027 |
| 3 | 1–250 | 0.0074 / 0.0052 | 0.0045 / 0.0009 | 0.0011 / 0.0014 | 0.0051 / 0.0048 | 0.31 / 0.27 | 0.0042 / 0.0035 |
| 3 | 251–1,000 | 0.0067 / 0.0034 | 0.0033 / 0.0004 | 0.0054 / 0.0046 | 0.0062 / 0.0058 | 0.32 / 0.26 | 0.0044 / 0.0035 |
| 10 | 1–250 | 0.0178 / 0.0114 | 0.0057 / 0.0005 | 0.0007 / 0.0015 | 0.0053 / 0.0048 | 0.29 / 0.26 | 0.0101 / 0.0058 |
| 10 | 251–1,000 | 0.0079 / 0.0023 | 0.0141 / 0.0011 | 0.0013 / 0.0038 | 0.0027 / 0.0054 | 0.24 / 0.22 | 0.0068 / 0.0028 |

- Chemistry, the store and the sugar into the store agree within about 30%, except at sugar 10 late.
- Gliding is within a factor of 1–5 of the page. Task 07's 0.1 was 10–300 times too high. With (b) off, the model
  glides 0.080 a tick at sugar 3.
- **Births are low by a factor of 1.4–2 (3.4 at sugar 10 late). Going still is low by 5–13 times early.** On the
  page, more cells both divide and go still, which means its stores spread wider than the model's. I did not tune
  for this.
- "Sugar into the store" on the page is `enTaken` × 0.4. That counter also takes in sugar-paid births, so the two
  columns differ slightly in what they count.

### 4. Shape against the page
Mean over seeds (page 12, model 6), live places = active + gone still.
- r95: the live places' 95th-percentile radius.
- rough: boundary roughness. dim: box dimension of the live places (both as in 03a).
- arms and width: runs of 2 or more live places along circles at 0.5–0.9 of r95, as a count and a mean width in places.
- cover: footprint cover, the share of those circles covered by live places or remains.
- isolated: the share of live places with no live neighbour.

**Sugar 3:**

| | tick | r95 | live (active) | rough | dim | arms | width | cover | isolated |
|---|---|---|---|---|---|---|---|---|---|
| page | 250 | 39 | 1,118 (503) | 18.6 | 1.52 | 5.7 | 3.2 | 0.32 | 0.01 |
| page | 500 | 66 | 1,588 (803) | 26.9 | 1.48 | 4.8 | 3.2 | 0.15 | 0.05 |
| page | 1,000 | 107 | 2,889 (1,184) | 41.4 | 1.45 | 6.5 | 2.9 | 0.15 | 0.13 |
| all on | 1,000 | 53 | 496 (448) | 20.5 | 1.23 | 1.7 | 2.5 | 0.22 | 0.26 |
| all on | 2,000 | 82 | 698 (658) | 24.9 | 1.16 | 1.3 | 2.5 | 0.20 | 0.29 |
| (a) off | 2,000 | 83 | 494 (244) | 20.2 | 1.05 | 1.1 | 2.4 | 0.14 | 0.27 |
| (b) off | 500 | 97 | 2,874 (2,738) | 52.3 | 1.54 | 4.2 | 2.3 | 0.16 | 0.33 |
| (b) off | 1,000 | 118 | 2,285 (2,058) | 50.8 | 1.32 | 0.9 | 2.3 | 0.20 | 0.63 |
| (c) off | 2,000 | 60 | 1,299 (556) | 27.3 | 1.43 | 5.1 | 3.0 | 0.70 | 0.12 |
| all off | 1,000 | 81 | 6,007 (3,381) | 54.5 | 1.72 | 19.7 | 3.3 | 0.75 | 0.06 |

**Sugar 1:**

| | tick | r95 | live (active) | rough | dim | width | cover | isolated |
|---|---|---|---|---|---|---|---|---|
| page | 1,000 | 50 | 481 (303) | 18.3 | 1.34 | 2.7 | 0.13 | 0.17 |
| page | 2,000 | 79 | 563 (352) | 20.4 | 1.15 | 2.7 | 0.05 | 0.25 |
| all on | 2,000 | 37 | 97 (92) | 10.0 | 0.91 | 2.1 | 0.40 | 0.40 |
| (a) off | 2,000 | 33 | 18 (8) | 4.1 | 0.71 | 2.0 | 0.47 | 0.52 |
| (b) off | 2,000 | 109 | 598 (575) | 26.4 | 0.94 | 2.2 | 0.08 | 0.73 |
| (c) off | 2,000 | 49 | 471 (158) | 17.5 | 1.17 | 2.9 | 0.52 | 0.16 |
| all off | 2,000 | 107 | 7,140 (3,617) | 62.9 | 1.63 | 3.1 | 0.85 | 0.10 |

**Sugar 10:**

| | tick | r95 | live (active) | rough | dim | arms | width | cover | isolated |
|---|---|---|---|---|---|---|---|---|---|
| page | 250 | 110 | 14,441 (8,981) | 55.5 | 1.80 | 36.0 | 4.0 | 0.44 | 0.01 |
| page | 500 | 120 | 13,484 (216) | 81.7 | 1.78 | 25.9 | 2.9 | 0.52 | 0.05 |
| page | 1,000 | 120 | 4,382 (16) | 65.4 | 1.53 | 4.3 | 2.4 | 0.28 | 0.38 |
| all on | 250 | 90 | 9,328 (8,841) | 54.4 | 1.79 | 28.9 | 3.4 | 0.47 | 0.02 |
| all on | 500 | 118 | 10,368 (8,131) | 82.7 | 1.74 | 18.9 | 2.7 | 0.49 | 0.11 |
| all on | 1,000 | 118 | 2,738 (1,273) | 54.7 | 1.38 | 1.6 | 2.4 | 0.50 | 0.55 |
| (b) off | 250 | 110 | 15,906 (14,779) | 80.0 | 1.84 | 30.3 | 3.5 | 0.53 | 0.02 |
| (c) off | 1,000 | 77 | 4,156 (2,343) | 41.3 | 1.63 | 15.6 | 3.5 | 0.64 | 0.06 |
| all off | 1,000 | 119 | 12,215 (4,250) | 84.5 | 1.77 | 20.1 | 2.9 | 0.93 | 0.09 |

All ticks and every measure with its sd: `results/2026-11-15/task22/item2/analysis/task22_item2_summary.json`.

**Reading the measures:**
- **Filled against branched.** Footprint cover separates them: 0.70–0.93 for (c) off and all off, against 0.14–0.22
  for the page, the full model and (a) off at sugar 3.
- **Scatter against arms.** The isolated share separates them: 0.33–0.63 for (b) off, against 0.05–0.29 for the page
  and the full model.
- **No single measure decides.** The arm count along circles cannot tell a scatter from thin arms. Box dimension and
  roughness depend strongly on size, and the sizes differ (section 5). So the verdict rests on all of them together
  with the pictures.

**Pictures:**
- `22_sugar1.png`, `22_sugar3.png`, `22_sugar10.png`: seed 1, ticks 250, 500, 1,000 and 2,000, one place per pixel.
  The page is at the top, then all on, (a) off, (b) off, (c) off and all off. Colours are 03a's: green active, purple
  gone still, grey remains, black agar.
- `22_closeup_sugar1.png`, `…3.png`, `…10.png`: 64 × 64 places on the +x edge, at 3×.

**By eye:**
- **Sugar 3:** the full model and (a) off grow 4–8 thin arms from the inoculum ring, with active tips and empty agar
  between them, like the page's tick 500–1,000. (b) off is a cloud that fills the plate. (c) off is a filled blob of
  remains with a ragged rim. All off is a filled disc.
- **Sugar 10:** the full model's front is radially branched with gaps, like the page's tick 250. It crashes after
  tick 500 more slowly than the page (1,273 active at tick 1,000, against 16).
- **Sugar 1:** the full model keeps a ring with a few short arms. The page's thin arms from tick 750 are not
  reproduced, since the colony barely grows.

### 5. What the undergrowth means for the verdict
- **The comparison between ingredients is fair.** Every variant shares the same per-cell bookkeeping, and the
  verdicts on (b) and (c) are not about size.
  - Switching (b) off makes the colony larger and scattered.
  - Switching (c) off makes it a filled disc that is smaller than the page but larger than the full model.
  - Neither is a branched colony at any size reached.
- **Whether "it branches" holds depends on matching sizes.** The full model's sugar-3 colony at tick 2,000 (r95 82)
  is about the page's size at ticks 500–750 (r95 66–95). It has fewer live cells there (about 700 against
  1,600–2,400), fewer arms crossing each circle (1.3 against about 5) and a lower box dimension (1.16 against 1.44–1.48).
  - Its arms are as thin as the page's (2.5 against 2.9–3.2 places) and its footprint is as sparse (cover 0.20
    against 0.15).
  - So its arms are of the page's kind, but there are fewer of them, and they are sparser.
- **The undergrowth limits the verdict in one direction only.** A model that grows half as fast per cell is more
  starved at its tips, and starved tips favour branching. So "it branches" may be partly helped by the slower growth.
- **A test that would settle this (proposal, not run):**
  - raise the model's birth rate towards the page's, with no constant fitted to shape;
  - for example, by giving each cell a persistent income spread or a wider top-up, measured from the page's store
    distribution;
  - then check that the arms survive.
  I did not tune further, as the brief asked.
- **At sugar 1 the model barely grows,** so it says little about the page's thin sugar-1 arms either way.

### 6. Reading (proposal)
- **Report 17's point 2 is borne out in one part.** Task 07's fine model failed to branch mainly because every
  active cell glided at 0.1 a tick, which fills the gaps between arms, and because chemistry paid for births
  everywhere. With gliding tied to coat (as the page does) and births paid from the store or local sugar, the same
  lattice branches.
- **The per-cell store's threshold for going still is not the missing piece.** Task 07's block rates of going still
  give the same shape.
- **Lineage is not needed for this shape.** The model has no lineages.
- **For item 3:** the gliding rate is part of what Justin's decision calls agar firmness entering as motility. On
  the page, gliding is already low, and a population model would need it low too, and tied to the cells that grow.

### Files (item 2)
- **Model:** `D:\labyrinth\automata\jgol_2026-11-13\popdish\pop22_store.py` (new; `pop2_gpu.py` unchanged).
- **Analysis and figures:** `popdish\task22_analyze.py`.
- **Page probe:** `test\probe22.js`, run by `test\task22_probe.cmd` through `rates_driver.py` on port 8795.
- **Queue scripts:**
  - `popdish\task22_main_s1.cmd`, `…s3.cmd`, `…s10.cmd`: the main runs;
  - `popdish\task22_check.cmd`: a first check, before the chemistry was measured per call; superseded;
  - `popdish\task22_tau.cmd`: the persistence check.
- **Results:** `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-15\task22\item2\`
  - `probe\` (and `probe_v1\`, the first probe without the chemistry bins);
  - `main\`: per variant and sugar, a JSON file of measures and per-cell rates, and an `.npz` of states at the
    snapshot ticks;
  - `analysis\`: measures, summary, the figures and `analyze.log`;
  - `check\` and `tau\`: the calibration runs.
- **Figures in this folder:** `22_sugar1.png`, `22_sugar3.png`, `22_sugar10.png`, `22_closeup_sugar1.png`,
  `22_closeup_sugar3.png`, `22_closeup_sugar10.png`.
