# 03 and 03a: the population dish with two resources, and the dish at the scale of single cells: report

From: gpu session, 14 November 2026. This answers `comms/to_gpu/2026-11-14_03_pop-dish-two-resources.md` and
`comms/to_gpu/2026-11-14_03a_maps-at-cell-scale.md`.

- **Measurements are measurements.** The model forms, the pass standard and the readings are proposals.
- **The page:** `build/justins_game_of_life.html` at caee6ba or later. It is unchanged.

## In short

1. **The repository's page gives the same dish as page 8, as expected.** At sugar 1, seed 1, over 2,000 ticks, the
   series and the block maps are identical.
2. **The harness now records the second resource,** per block and window:
   - the agar's molecules;
   - their stored energy above the lowest kind (`RXE[k] − RXE[0]`), called mE below;
   - the reaction income: the net change in cells' stores across `domReact`.

   `validate.js` also takes full-resolution snapshots.
3. **The open question: why chemistry sustains active cells at low sugar but not after the sugar crash at high sugar.**
   The answer is not my crowding proposal, or only a little of it (section 2).
   - **Late at sugar 10,** the active cells earn as much from chemistry as at sugar 1, about 0.003–0.005 per cell-tick,
     with as many molecules per active cell.
   - **The difference is the crash itself.** At sugar 10 the sugar runs out over the whole plate within about 100
     ticks. Nearly every cell goes still at once (12,600 of 13,500 at tick 500).
   - **Still cells wake only where there is sugar.** The molecules add nothing to waking. So chemistry keeps the few
     remaining active cells going but never wakes the rest.
   - **Crowding does lower chemistry income during the boom,** from about 0.006 to 0.0035 per cell-tick where
     molecules per active cell fall below about 15. That is a modest effect.
4. **Fits (measurements):**
   - **Going still follows total income** (sugar plus chemistry) much better than sugar alone: deviance explained 0.49
     against 0.28. Its rate falls about 15-fold as chemistry income rises from 0 to 0.016 per cell-tick.
   - **Division** gains from a chemistry term: 0.69 against 0.60.
   - **Waking** depends on sugar only.
   - **The molecule field** runs down by about 6 units of mE per unit of income earned. It does not re-form in the dish.
5. **The validation: no version passes, so no sweep was run.**
   - **The best is the two-resource fold with income set per active cell (C2x):**
     - **sugar 1:** within about 25% through tick 1,000;
     - **sugar 3:** the second wave is right at tick 1,000, but there is 50–80% too much at ticks 250–500 and 2,000;
     - **sugar 10:** right at ticks 100 and 500, but it misses the crash. The page's active cells fall from 8,200 to 630
       between ticks 250 and 500; the fold keeps about 9,900.
   - **What is missing (proposal):** the store, as the link from income to going still. In the page a cell goes still
     when its store falls below a threshold, and the store falls fast once the sugar is gone, even with some chemistry
     income. A block-mean income misses that.
6. **03a: the page branches.**
   - **At one pixel per place:**
     - at sugar 3, ticks 500–1,000, there are clear dendrites: branched arms with active tips that cross the plate;
     - at sugar 10, ticks 100–250, the front is a mass of thin branches with active tips;
     - at sugar 1, from tick 750 on, branches one to three places wide grow out from a ring of cells gone still.
   - **Box-counting dimension of the live places:** 1.2–1.5 at sugar 1, 1.2–1.6 at sugar 3, and 1.7–1.8 at sugar 10
     during growth.
   - **Roughness** (perimeter over that of a circle of equal area): 9–20 at sugar 1, 10–41 at sugar 3, and 21–80 at
     sugar 10.
   - **Block models show none of this.** The finer-block models (5 × 5, 2 × 2) were not run (section 4).

## 1. The check, and the harness

- **The check:** the current page against page 8, at sugar 1, seed 1, 2,000 ticks. Every 25-tick record and every
  block map is identical, so neither the gliding fix nor the LF build touches the dark dish.
- **`test/rates.js`** (task 1's harness) gains three fields per block and 25-tick window:
  - `mol`: the molecules;
  - `molE`: their stored energy above the lowest kind;
  - `rx`: the net change in cells' stores across `domReact`, summed over the block. It is read by wrapping
    `domReact`, which changes nothing.
- **`test/validate.js`** gains full-resolution snapshots (`--snaps 100,250,500,750,1000,1500,2000`), recording:
  - each place's state: empty agar, active, gone still, remains;
  - sugar and molE per coarse square;
  - the reaction income per place since the previous snapshot.
- **The runs:**
  - task 1's grid: 105 runs, page sugar 0.5–20, gliding 0/0.1/0.3, 5 seeds;
  - the dish: page sugar 1, 3 and 10, gliding 0.1, 3 seeds, 2,000 ticks.
  - **Hopping off was not repeated:** in the dark dish no cell hops, so on page 8 hopping on and off gave the same
    dish within seed noise.
- **The molecules hold far more energy than the sugar.** At sugar 10, tick 250, the plate held about 232,000 units of
  molE against about 10,000 of sugar. It is not laid evenly: 80–230 per coarse square at tick 100.
  - **Income is limited by how fast the enzymes work, not by how many molecules there are.** Above about 450 mE per
    block it is flat, at about 0.005–0.006 per active cell-tick.

## 2. The open question: ring and core, over time

**The split.** Active cells are divided by radius:
- **ring:** beyond the colony's 95th-percentile radius less 15 places;
- **core:** inside that.

A split by distance to empty agar does not work, because the colony is so ragged that empty agar lies within a few
places of nearly every cell.

**Means over 3 seeds** (`day9_repo/figs/snaps_measures.json`):

| Page sugar | Tick | Where | Active cells | mE per active cell in the square | Sugar per square | Chemistry income per cell-tick |
|---|---|---|---|---|---|---|
| 1 | 100 | ring | 598 | 25 | 0.00 | 0.0059 |
| 1 | 1,000 | ring / core | 125 / 149 | 36 / 53 | 0.03 / 0.01 | 0.0037 / 0.0044 |
| 1 | 2,000 | ring / core | 133 / 232 | 29 / 50 | 0.02 / 0.02 | 0.0016 / 0.0026 |
| 3 | 1,000 | ring / core | 308 / 1,041 | 18 / 30 | 0.12 / 0.04 | 0.0023 / 0.0031 |
| 10 | 100 | ring / core | 942 / 1,268 | 13 / 22 | 1.27 / 0.14 | 0.0024 / 0.0027 |
| 10 | 250 | ring / core | 2,373 / 5,794 | 9 / 15 | 0.61 / 0.18 | 0.0020 / 0.0022 |
| 10 | 500 | ring / core | 425 / 206 | 41 / 45 | 0.06 / 0.00 | 0.0015 / 0.0029 |
| 10 | 1,000 | ring / core | 17 / 35 | 27 / 36 | 0.00 / 0.01 | 0.0034 / 0.0036 |

**Reading:**
- **The crowding proposal is mostly wrong.**
  - After the crash at sugar 10, the few active cells earn as much as active cells at sugar 1, with as many molecules
    each.
  - During the boom, crowding does halve income per cell: 9–15 mE per active cell against 25–50.
- **What differs is how many cells are active,** not what each earns. The sugar crash sends nearly every cell still,
  and the molecules never wake them.
- **Income runs down slowly everywhere** (0.006 → 0.002 per cell-tick over 2,000 ticks at sugar 1), as the cells
  convert the high-energy molecules into lower ones.

## 3. Fits against sugar and molecules

The fits are in `fit_two.json`: per block and 25-tick window, Poisson maximum likelihood.
- s = page sugar per block.
- c = the observed chemistry income per active cell-tick in the block.
- Deviance explained is in brackets.

| What | Sugar alone | Two resources |
|---|---|---|
| Division | 0.138 · s/(s+23.5) · room^0.79 (0.60) | **(0.238 · s/(s+96.8) + 0.63 · c) · room^0.61 (0.69)** |
| Going still | 0.0129 / (1 + s/0.19) (0.28) | **0.0231 / (1 + s/0.51 + c/0.00088) (0.49)** |
| Waking | 0.00031 · s/(s+2.4) (0.24) | adding the molecules: no gain (0.24) |
| Chemistry income per active cell | — | 0.0089 · mE/(mE+494) per block (weighted R² 0.03); per active cell, x = mE per active cell: 0.0065 · x/(x+8.4) (0.05) |
| The molecule field | — | d(mE) = −6.0 × income per window (R² 0.25); no regrowth in the dish (the page's ground rules: "everything is laid once") |

**Going still against chemistry income** (binned, per active cell-tick):

| Income | 0.00004 | 0.002 | 0.0034 | 0.0045 | 0.0061 | 0.0086 | 0.016 |
|---|---|---|---|---|---|---|---|
| Still per cell-tick | 0.0166 | 0.0067 | 0.0042 | 0.0027 | 0.0016 | 0.0012 | 0.0011 |

- **The sugar budget is unchanged:** 1.49 page sugar per birth paid from sugar (R² 0.968), as on page 8.
- **The income fits are poor (R² 0.03–0.05).** Income per cell varies far more between cells than between blocks:
  it depends on each cell's own folds (its `rx` domains), which are inherited and mutate.
  - **Proposal:** chemistry income is partly a property of lineages, not only of place. A fold that keeps it as a
    block mean will always blur that.

## 4. The validation

The models are in `day9_repo/model/` and `model_x/`. Each one:
- starts from the page's state at tick 5 (after the inoculum's store-paid births);
- spreads 15.5% of births;
- has the measured deaths;
- has waking on sugar.

The two-resource folds take their starting molecule field block by block from the page's first snapshot.

| Variant | What it is (proposal) |
|---|---|
| Bmrw5 | sugar only: the best of the earlier rounds, refitted |
| C2m | two resources: chemistry income per block, chemistry-paid births; going still from sugar alone |
| C2 | as C2m, with going still from total income |
| **C2x** | as C2, with chemistry income set by the molecules per active cell (crowding) |

**All cells (active + inactive), mean of 3 seeds; r = radius (95th percentile) in places:**

| Page sugar | Tick | Page | Bmrw5 | C2m | C2 | **C2x** |
|---|---|---|---|---|---|---|
| **1** | 100 | 698, r 19 | 619 | 748 | 750 | **713, r 21** |
| 1 | 250 | 548, r 22 | 461 | 718 | 724 | **674, r 23** |
| 1 | 500 | 387, r 31 | 285 | 621 | 615 | 566, r 29 |
| 1 | 1,000 | 418 (273 active), r 45 | 114 | 466 | 402 | **449 (214), r 38** |
| 1 | 2,000 | 567 (364), r 81 | 36 | 305 | 182 | 414 (195), r 51 |
| 3 | 100 | 830, r 22 | 916 | 1,074 | 1,008 | 1,010, r 27 |
| 3 | 250 | 749, r 31 | 921 | 1,295 | 1,099 | 1,143, r 38 |
| 3 | 500 | 788, r 47 | 945 | 1,635 | 1,273 | 1,418, r 59 |
| 3 | 1,000 | 2,261 (1,349 active), r 110 | 1,063 | 2,227 | 1,822 | **2,268 (1,338), r 86** |
| 3 | 2,000 | 1,561, r 117 | 700 | 2,256 | 2,051 | 2,904, r 115 |
| 10 | 100 | 2,657, r 48 | 2,715 | 2,828 | 2,741 | **2,546, r 44** |
| 10 | 250 | 13,160 (8,167 active), r 110 | 7,990 | 8,261 | 8,207 | 7,981 (6,521), r 84 |
| 10 | 500 | 13,495 (631 active) | 11,123 | 15,886 | 15,399 | **15,659** (9,916 active) |
| 10 | 1,000 | 4,496 (52 active) | 3,820 | 8,331 | 7,423 | 9,073 (3,113) |
| 10 | 2,000 | 569 | 395 | 1,342 | 959 | 2,237 |

**Page sugar 1:**
- The page dips to 387 cells at tick 500, then regrows to 567 by tick 2,000, branching outward.
- **Sugar-only (Bmrw5):** it declines to 36.
- **The two-resource folds** have the regrowth in part. C2x holds 400–450 cells from tick 1,000 on, but grows no further,
  and its radius lags (51 against 81 at tick 2,000).

**Page sugar 3:**
- The page's second wave (788 → 2,261 cells between ticks 500 and 1,000) appears only in the two-resource folds.
- C2x has it at the right size at tick 1,000. But it starts too early and does not fall back afterwards (2,904 against
  1,561 at tick 2,000).

**Page sugar 10:**
- Every fold is 35–40% low at tick 250, where the page grows fastest.
- The two-resource folds then keep 15–20 times too many active cells after the crash, because chemistry income
  holds their rate of going still down.
- In the page, nearly every cell goes still within 250 ticks of the sugar running out.

**Verdict: no version passes. So no sweep was run, as task 03 says.**
- **What is missing (proposal): the store, as the link between income and going still.**
  - In the page a cell goes still when its store falls below about 0.24, a threshold measured since page 4.
  - When the sugar is gone, the store falls faster than the chemistry income (about 0.002–0.003 a tick against the
    cell's costs) can refill it. So the cell goes still even though it earns something.
  - A block-mean rate of going still in income cannot show that. The store fold (S) has the store, but not the two
    resources.
  - **The next fold to try:** S with both incomes feeding the store, and with income set per lineage rather than per
    block.

## 5. 03a: the dish at the scale of single cells

**Figures** (seed 1; one place per 2 × 2 pixels, nearest neighbour). Colours: active green, gone still purple, remains
grey, empty agar black, off the plate dark blue.
- `03a_dish_sugar1.png`, `…3.png`, `…10.png`: per tick, the dish above its sugar per square (white is the starting
  sugar).
- `03a_closeup_sugar1.png`, `…3.png`, `…10.png`: 64 × 64 places on the colony's edge (+x side), at 4×.
- `03_blockmaps_sugar1.png`, `…3.png`, `…10.png`: block maps (10 × 10 places) of the page, Bmrw5 and C2x. These are
  **block maps** and cannot show anything finer than a block.

**What the pictures show:**
- **Sugar 10:**
  - **Tick 100:** the inoculum's ring is still visible at the centre, and the colony has grown out from it as a dense
    mass of fine branches with active tips.
  - **Tick 250:** the plate is mostly covered, and the sugar map shows the sugar eaten out behind the front.
  - **Tick 500 on:** nearly everything has gone still, and remains slowly replace it.
  - **Straight horizontal streaks** cross the plate from tick 500. They look like an artefact of row-by-row updating
    rather than biology. This is a proposal to check, not a finding.
- **Sugar 3: the clearest dendrites of the three.**
  - **To tick 250:** a slow ragged ring.
  - **Ticks 500–1,000:** branched arms with active tips (green) and cells gone still behind them (purple) run out
    across the plate. This is the second wave.
  - **The sugar map:** the eaten-out region is broader and smoother than the branches, since sugar diffuses towards
    them.
  - **By tick 1,500** the branches have reached most of the rim.
- **Sugar 1:**
  - **To tick 500:** a ring of cells gone still around the inoculum's hole, with a few active cells.
  - **From tick 750:** thin branches, one to three places wide with active tips, grow outward into fresh sugar. The
    sugar map shows each branch eating a narrow channel.
  - This is the regrowth, and it looks like Matsushita's low-nutrient branching. That is a visual likeness, a proposal,
    not a test.

**Shape, at the scale of places** (page; mean of 3 seeds):

| Page sugar | Tick | Live cells | Roughness | Box dimension (live) | Box dimension (live + remains) |
|---|---|---|---|---|---|
| 1 | 250 | 548 | 13.3 | 1.50 | 1.53 |
| 1 | 1,000 | 418 | 17.0 | 1.31 | 1.46 |
| 1 | 2,000 | 567 | 20.4 | 1.17 | 1.34 |
| 3 | 500 | 788 | 20.7 | 1.43 | 1.50 |
| 3 | 1,000 | 2,261 | 35.5 | 1.43 | 1.53 |
| 3 | 2,000 | 1,561 | 36.4 | 1.18 | 1.41 |
| 10 | 250 | 13,160 | 53.9 | 1.78 | 1.80 |
| 10 | 500 | 13,495 | 79.6 | 1.78 | 1.85 |
| 10 | 2,000 | 569 | 26.0 | 0.80 | 1.19 |

- **The colony is ragged at every sugar level.** Roughness is 9 to 80 times a circle's.
- **Its dimension depends on the sugar:**
  - **Sugar 1:** falls from 1.5 to about 1.2–1.3 as the colony becomes a few thin branches. That is lower than
    diffusion-limited aggregation's 1.7 (Witten and Sander, 1981), and closer to a sparse set of lines.
  - **Sugar 10:** 1.8–1.9 while it fills the plate.
- **Remains** keep the trace of where the colony has been, so their dimension stays higher.

**Shape at block scale (10 × 10), for the page and the models alike** (roughness / box dimension):

| Page sugar | Tick | Page | Bmrw5 | C2x |
|---|---|---|---|---|
| 1 | 1,000 | 1.87 / 1.47 | 1.39 / 1.24 | 1.77 / 1.28 |
| 1 | 2,000 | 2.92 / 1.36 | 2.53 / 1.00 | 2.28 / 1.36 |
| 3 | 1,000 | 2.56 / 1.58 | 3.22 / 1.45 | 2.01 / 1.62 |
| 3 | 2,000 | 4.63 / 1.64 | 6.63 / 1.44 | 2.73 / 1.73 |
| 10 | 500 | 1.30 / 1.93 | 1.40 / 1.93 | 1.44 / 1.93 |
| 10 | 2,000 | 7.40 / 1.57 | 8.88 / 1.48 | 2.18 / 1.89 |

- **At block scale the two-resource fold's shape is close to the page's** at sugar 1 and 3.
- **But a block cannot hold a branch one to three places wide.** Branching shows only below the block.

**The finer-block models (5 × 5 and 2 × 2) were not run** (the proposal in 03a).
- **Why:** they need task 1's measurements repeated at those block sizes, then every rate refitted. And at 10 × 10 no
  version passes yet.
- **Proposal:** run them once a fold passes at 10 × 10, since a finer grid of a failing fold would not tell us much.
- **A cheaper test of the same idea (proposal):** the earlier population dish (`popdish/pop.py`) already runs at
  1,000 × 1,000. A two-resource version of it, with slow sugar diffusion, would show whether branching appears when the
  grid is fine.

## 6. The sweep

None was run, since no version passed.

## Files

- **Harness:** `jgol_2026-11-13/test/rates.js` (molecules, molE, reaction income), `validate.js` (snapshots),
  `rates_driver.py` (`--snaps`), and `repo03_all.cmd`.
- **Analysis:**
  - `jgol_2026-11-13/popdish/fit_two.py`: the two-resource fits;
  - `snaps_analyze.py`: pictures, shape, ring and core;
  - `block_shape.py`;
  - `validate_model.py`: the `--chem`, `--cform`, `--still income` modes.
- **Results:** `jgol_2026-11-13/results/2026-11-13/day9_repo/`, on the GPU machine. They are not in the repository,
  since they are large: about 35 MB of snapshots.
- **Figures in this folder:** `03a_dish_sugar*.png`, `03a_closeup_sugar*.png`, `03_blockmaps_sugar*.png`.
