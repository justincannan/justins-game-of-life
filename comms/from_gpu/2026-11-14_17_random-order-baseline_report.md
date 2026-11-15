# 17: the dish on the random-order page: the new baseline

From: gpu session, 14 November 2026, about 22:30 New York. Answers `comms/to_gpu/2026-11-14_17_random-order-baseline.md`,
and item 3 of `comms/to_gpu/2026-11-14_19_justins-answers-open-questions.md` (last section).

Measurements are measurements. Readings marked as proposals are Claude's; Justin decides.

## The page
- `build/justins_game_of_life.html` at 821a258 (the repository at 549a75d). It has `visitOrder()` and `randOrder:true`
  in its defaults. The page was not changed.
- The harness sets nothing new for the random runs, so they use the page's default (random order). The control runs set
  `P.randOrder = false` (harness copy `test/validate17.js`, which only adds that option).

## In short
1. **Control:** row order on the current page gives report 03's runs place for place. Sugar 1, 3 and 10, seeds 1–3:
   every 25-tick record and every snapshot is identical. So the only difference below is the visiting order.
2. **Counts: no change beyond seed spread at most ticks.** Sugar 10 still crashes, sugar 3 still has its second wave,
   sugar 1 still dips and regrows. Two small changes stand out over 12 seeds (section 2):
   - **fewer cells go still early.** At tick 100, gone-still cells are 173 ± 54 against 321 ± 157 at sugar 10 (z −3.1),
     and 35 ± 25 against 64 ± 41 at sugar 1 (z −2.1). Sugar 3 points the same way (z −1.3).
   - **the crash at sugar 10 is a little deeper.** Active cells at tick 500 are 216 ± 277 against 674 ± 682 (z −2.2), and
     at ticks 1,000–2,000 about 16–23 against 47–62 (z −1.7).
   - Everything else is within about 2 standard errors. With about 200 comparisons a few |z| > 2 are expected by chance,
     so I count only the two above, because they repeat across ticks or sugar levels.
3. **Shape: unchanged.** Box dimension and roughness agree within seed spread at every sugar and tick. The dendrites at
   sugar 3 and the thin arms at sugar 1 are still there (figures).
4. **The lean towards the top is gone.** At sugar 3, tick 1,000: row order has the centre above the plate's centre in
   12 of 12 runs (mean −0.27 plate radii); random order in 7 of 12 (mean +0.004). The same holds at every sugar.
5. **The streaks are gone.** The gone-still fraction is flat over y mod 4, and the row-minus-column autocorrelation is at
   noise (section 4).
6. **Seed spread is smaller under random order at sugar 10.** For example, active cells at tick 250 (seeds 1–3) are
   9,379 ± 313 against 8,167 ± 2,483, and roughness at tick 500 is 81.7 ± 1.6 against 79.3 ± 5.8 (12 seeds).

## 1. Runs
- `rates_driver.py` with `validate17.js`: sugar 1, 3 and 10; glide 0.1; W 256; 2,000 ticks; snapshots at 100, 250,
  500, 750, 1,000, 1,500 and 2,000; seeds 1–12. Port 8793, CPU queue (`jgol17-dish`, about 10 minutes).
- Random order (the default) and row order (`randOrder 0`), 36 runs each, all finished.
- Seeds 1–3 of the row-order runs are report 03's runs (control above), so "row order" below is report 03's baseline,
  extended to 12 seeds.

## 2. Counts
Mean ± sd over seeds. The first four columns are seeds 1–3 (as in report 03). z is the difference over its standard
error for 12 seeds each (random minus row). From the snapshots.

| sugar | tick | active, row | active, random | still, row | still, random | z active (12) | z still (12) |
|---|---|---|---|---|---|---|---|
| 1 | 100 | 599 ± 85 | 645 ± 52 | 100 ± 37 | 60 ± 27 | +0.5 | **−2.1** |
| 1 | 250 | 178 ± 26 | 151 ± 20 | 370 ± 28 | 411 ± 14 | −0.9 | +2.0 |
| 1 | 500 | 145 ± 39 | 134 ± 8 | 242 ± 18 | 250 ± 7 | +0.1 | +0.2 |
| 1 | 750 | 232 ± 76 | 218 ± 11 | 162 ± 20 | 151 ± 11 | +0.1 | −0.1 |
| 1 | 1,000 | 273 ± 103 | 257 ± 44 | 144 ± 19 | 108 ± 6 | 0.0 | −0.8 |
| 1 | 1,500 | 264 ± 115 | 228 ± 38 | 159 ± 74 | 97 ± 19 | +0.6 | −0.4 |
| 1 | 2,000 | 364 ± 177 | 234 ± 39 | 203 ± 150 | 85 ± 16 | +0.5 | −0.1 |
| 3 | 100 | 649 ± 131 | 751 ± 112 | 181 ± 83 | 115 ± 48 | +0.3 | −1.3 |
| 3 | 250 | 295 ± 29 | 384 ± 72 | 454 ± 33 | 504 ± 48 | +0.1 | +0.4 |
| 3 | 500 | 374 ± 93 | 859 ± 483 | 414 ± 79 | 570 ± 198 | +0.4 | +0.4 |
| 3 | 750 | 805 ± 161 | 1,027 ± 419 | 477 ± 145 | 1,058 ± 560 | +0.8 | +0.6 |
| 3 | 1,000 | 1,349 ± 469 | 1,361 ± 681 | 912 ± 423 | 1,564 ± 889 | +0.8 | +1.0 |
| 3 | 1,500 | 650 ± 11 | 833 ± 170 | 1,614 ± 844 | 1,684 ± 915 | +0.9 | **+2.4** |
| 3 | 2,000 | 505 ± 268 | 436 ± 118 | 1,056 ± 500 | 1,150 ± 252 | −1.0 | +1.5 |
| 10 | 100 | 2,211 ± 530 | 2,339 ± 403 | 446 ± 113 | 172 ± 52 | −0.1 | **−3.1** |
| 10 | 250 | 8,167 ± 2,483 | 9,379 ± 313 | 4,993 ± 1,858 | 4,819 ± 1,740 | +1.5 | −0.6 |
| 10 | 500 | 631 ± 634 | 113 ± 98 | 12,864 ± 639 | 13,355 ± 1,007 | **−2.2** | +1.2 |
| 10 | 750 | 52 ± 68 | 10 ± 11 | 7,687 ± 189 | 7,610 ± 564 | −1.1 | −0.9 |
| 10 | 1,000 | 52 ± 59 | 15 ± 13 | 4,443 ± 143 | 4,361 ± 284 | −1.7 | −1.5 |
| 10 | 1,500 | 58 ± 70 | 31 ± 31 | 1,521 ± 70 | 1,462 ± 98 | −1.6 | −1.8 |
| 10 | 2,000 | 45 ± 41 | 44 ± 50 | 524 ± 14 | 504 ± 65 | −1.7 | −1.7 |

12-seed means (row / random), for reference: sugar 10, tick 500, active 674 / 216; tick 1,000 active 47 / 16, still
4,578 / 4,366. Sugar 3, tick 1,000, active 1,052 / 1,184, still 1,359 / 1,704. Sugar 1, tick 2,000, active 324 / 352.

Remains: within seed spread everywhere except sugar 3 at tick 1,500 (3,021 ± 577 against 2,313 ± 638, z +2.9), which
goes with the still cells above.

**Reading (proposal).** The early gone-still cells under row order are the starved lower rows of each 4 × 4 square
(report 08). Random order shares the square's store more evenly, so fewer cells fall below the threshold early. The
deeper crash at sugar 10 may be the other side of the same thing: under row order the first rows of a square keep a
few cells active after the sugar runs out. These are small effects, and the dish's story is unchanged.

## 3. Shape
Box dimension (live places) and roughness (perimeter over that of a circle of equal area), 12 seeds, mean ± sd, row /
random. Measured as in report 03a (`snaps_analyze.py`'s functions).

| sugar | tick | roughness | box dimension (live) | box dimension (live + remains) |
|---|---|---|---|---|
| 1 | 250 | 14.0 ± 1.2 / 13.8 ± 1.1 | 1.53 ± 0.05 / 1.53 ± 0.03 | 1.56 / 1.55 |
| 1 | 1,000 | 18.6 ± 2.5 / 18.3 ± 3.5 | 1.35 ± 0.07 / 1.34 ± 0.07 | 1.50 / 1.50 |
| 1 | 2,000 | 20.6 ± 3.2 / 20.4 ± 7.2 | 1.15 ± 0.08 / 1.15 ± 0.09 | 1.35 / 1.33 |
| 3 | 500 | 26.7 ± 6.3 / 26.9 ± 6.4 | 1.48 ± 0.05 / 1.48 ± 0.07 | 1.55 / 1.54 |
| 3 | 1,000 | 39.0 ± 5.2 / 41.4 ± 8.7 | 1.44 ± 0.04 / 1.45 ± 0.05 | 1.56 / 1.57 |
| 3 | 2,000 | 33.6 ± 5.4 / 36.1 ± 5.4 | 1.11 ± 0.11 / 1.09 ± 0.13 | 1.36 / 1.37 |
| 10 | 250 | 55.5 ± 7.5 / 55.5 ± 6.1 | 1.79 ± 0.04 / 1.80 ± 0.03 | 1.80 / 1.81 |
| 10 | 500 | 79.3 ± 5.8 / 81.7 ± 1.6 | 1.78 ± 0.03 / 1.78 ± 0.01 | 1.85 / 1.85 |
| 10 | 2,000 | 26.3 ± 2.1 / 24.9 ± 1.3 | 0.81 ± 0.06 / 0.77 ± 0.04 | 1.19 / 1.16 |

- Differences are a few hundredths in dimension and a few percent in roughness.
- Two exceptions near 2–3 standard errors: dimension at sugar 1, tick 500 (1.51 against 1.46, z +2.7), and roughness
  at sugar 3, tick 1,500 (44.0 against 39.1, z +2.6). Neither repeats at the next tick, so I read them as chance.
- **Pictures** (seed 1, row order above random order; 03a's colours: green active, purple gone still, grey remains,
  black empty agar):
  - `17_dish_sugar1.png`, `…3.png`, `…10.png`: the whole dish at one place per 2 × 2 pixels;
  - `17_closeup_sugar1.png`, `…3.png`, `…10.png`: 64 × 64 places on the +x edge at 4×.
- **What they show (by eye):**
  - sugar 3: branched arms with active tips from tick 500 to 1,500 under both orders. Under row order, seed 1's arms run
    mostly up and to the left; under random order they spread on all sides.
  - sugar 1: the ring of gone-still cells, then thin arms with active tips from tick 750, under both orders.
  - sugar 10: the dense branched front at tick 100–250 and the crash, under both orders. The horizontal streaks of
    gone-still places are visible under row order from tick 500, and absent under random order.

## 4. The lean and the streaks
**The lean.** Centre of the live places measured from the plate's centre, in plate radii (THEORY_NOTES' measure,
`test/dish_asym.py`; y < 0 is towards the top). 12 seeds each.

| sugar | tick | row: above / 12, mean y (sd) | random: above / 12, mean y (sd) | row: mean x | random: mean x |
|---|---|---|---|---|---|
| 1 | 500 | 12, −0.029 (0.033) | 7, −0.010 (0.038) | +0.007 | +0.009 |
| 1 | 1,000 | 11, −0.115 (0.081) | 8, −0.037 (0.094) | +0.003 | +0.022 |
| 1 | 2,000 | 12, −0.251 (0.122) | 8, −0.064 (0.139) | −0.037 | +0.011 |
| 3 | 250 | 11, −0.028 (0.027) | 5, +0.001 (0.019) | −0.001 | −0.011 |
| 3 | 500 | 11, −0.111 (0.074) | 5, +0.007 (0.068) | −0.047 | −0.002 |
| **3** | **1,000** | **12, −0.266 (0.107)** | **7, +0.004 (0.199)** | **−0.175** | **+0.029** |
| 3 | 2,000 | 7, −0.023 (0.127) | 7, −0.001 (0.132) | +0.032 | −0.028 |
| 10 | 250 | 11, −0.140 (0.132) | 8, −0.007 (0.066) | −0.056 | +0.025 |
| 10 | 1,000 | 0, +0.063 (0.057) | 7, −0.002 (0.022) | +0.013 | +0.009 |

- **Under random order the lean is gone at every sugar and tick.** The mean is within about one standard error of
  zero, and the count above is near half.
- **Under row order the lean is larger here than in THEORY_NOTES** (−0.27 against about −0.06 radii at sugar 3, tick
  1,000). The settings differ (W 256, glide 0.1, the harness's seeded generator), so the numbers are not comparable one
  to one. The sign agrees.
- **Row order also leans left at sugar 3, tick 1,000** (11 of 12, −0.175). That fits the scan going left to right
  within a row. Random order: 4 of 12, +0.03.
- **At sugar 10 after the crash, row order's centre moves to the bottom** (0 of 12 above at tick 1,000). That fits
  the lower rows of each square keeping their cells longer once the upper rows have gone still and the colony has
  filled the plate. Proposal, not tested.
- So report 08's "the lopsided growth does not follow the scan order" (3 seeds) is superseded, as THEORY_NOTES says.

**The streaks** (report 08's measures, seeds 1–3). Gone-still fraction by y mod 4, sugar 10, tick 250:
- row order: .25 .42 .50 .52 / .19 .33 .38 .43 / .20 .39 .44 .45 (as in report 08);
- random order: .39 .41 .41 .41 / .25 .23 .23 .24 / .37 .35 .35 .35.

Row-minus-column autocorrelation at sugar 10, tick 500: row order +0.22, +0.09, +0.05; random order −0.05, −0.11,
+0.01. At sugar 1 and 3 the random-order profiles over y mod 4 and x mod 4 are flat within ±0.05 in every seed; under
row order they rise by 0.15–0.5 from row 0 to row 3.

## 5. The new baseline
- **From now on:** `results/2026-11-14/task17/random/`, seeds 1–12, for task 16's comparisons and later ones.
  Report 03's runs remain the row-order control, and the row runs here extend them to 12 seeds.
- **The population-model comparisons (reports 03, 06, 07, 16) do not change.** Their verdicts were "no fold passes" and
  "no arms", with misses of 2 to 20 times. The page moved by far less than that. The one place to look again is sugar
  10's crash in the store fold (report 16's u8g5Dc: 649 active at tick 500). It matched row order's 3-seed mean (631);
  random order's is 113 ± 98 (3 seeds) or 216 ± 277 (12 seeds). Both are within the page's own spread, so the fold
  still "gets the crash". But it now sits above the page rather than on it. That is a reading, not a refit.

## Can a coarse population model branch? (task 19, item 3)
My view, as a proposal. Justin decides whether the plan for population-scale default worlds needs rethinking.

**What has been measured:**
- **The branches are fine.** The page's arms are one to three places wide (03a). This baseline shows they are not an
  artefact of the visiting order: they survive random order, with unchanged dimension and roughness.
- **At 10 × 10 blocks** (task 03), the two-resource fold's block-scale shape is close to the page's (roughness 2–3,
  dimension 1.3–1.6). But a block cannot hold an arm, and the block maps show none.
- **At one place per square with block-fitted rates** (task 07): compact, ragged discs at every sugar and sugar
  diffusion rate. Without chemistry-paid births: a sparse scatter. No arms.
- **With the molecules spreading at the page's rate** (task 16): no change. The molecules are barely used where the
  cells are, so they cannot limit growth.
- **The store fold with lineages** (task 06) gets the sugar-10 crash, but not sugar 1 or 3, and selects lineages far
  harder than the page.

**My reading:**
1. **A model whose units are blocks cannot branch below its block.** That holds by construction. At 10 × 10 it can at
   best show the colony's raggedness at block scale, which the folds already do.
2. **A model with block-scale rates on a fine grid has not branched either.** The likely reason is the rates, not the
   grid. Branching of this kind needs growth at a tip to be limited by a resource that runs short right there. Behind
   the tip, cells must stop: go still, and not move or fill in. That is the class of the Kawasaki and Mimura
   reaction–diffusion colony models, where a uniform, Eden-like disc appears whenever cells spread freely or growth is
   not limited by the local nutrient.
   - The fitted rates are means over blocks and seeds. They lose the per-cell link between a cell's own store and its
     going still, and the cell-to-cell spread of income.
   - In the fine model, births paid by chemistry come from molecules that are everywhere. That removes the local limit.
   - Random gliding, and births spread at random, fill the gaps between arms.
3. **A rough scale argument (estimate, not a measurement):**
   - At sugar 3 the front moves about 0.1 places a tick (r95 from about 36 to 90–115 between ticks 250 and 1,000), and
     the page's sugar diffuses at about 0.8 places² a tick (report 16). So the diffusion length D/v is about 8 places.
   - A Mullins–Sekerka-type instability would then split the front at a spacing of a few times that, a few tens of
     places. That is roughly what the pictures show between arms.
   - So the arm spacing is about one to three 10 × 10 blocks, and the arm width is below one block. Even a working
     coarse model could at best show the spacing (where arms are), not the arms.
4. **So, as a proposal:** a coarse population model can reproduce the dish's counts and timing at best (not yet
   achieved: no fold passes). It cannot show the branching that is the dish's most visible feature.
   - If the default worlds move to the population scale, they would show the colony as a ragged disc of blocks, not a
     branched colony.
   - If branching matters in those worlds, the options I see are:
     - keep the page's per-place model where the colony's edge is, and use the population scale only behind it (a
       hybrid);
     - or build a per-place model with per-cell stores, coat-limited gliding and inherited income (task 06's form). It
       would no longer be a coarse model, and the measurement it waits on is task 13's.
5. **A test that would decide point 2 cheaply (proposal, not run):** the fine-grid model of task 07 with a per-cell
   store and threshold in place of the block rate of going still, gliding only while active and coated, and births
   paid from sugar at the cell's own square. If it branches, the missing piece was the per-cell store. If not, it is
   lineage or coat.

## Files
- **Harness:**
  - `D:\labyrinth\automata\jgol_2026-11-13\test\validate17.js`: a copy of `validate.js` that adds an optional
    `randOrder` setting and records it;
  - `test\rates_driver.py`: new optional `--randorder`; without it, runs are as before;
  - `test\task17_runs.cmd`: the runs.
- **Analysis:** `D:\labyrinth\automata\jgol_2026-11-13\popdish\task17_analyze.py`. It uses `snaps_analyze.py`'s shape
  measures and `streaks.py`'s streak measures, and makes the figures.
- **Results:** `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-14\task17\`, on the GPU machine:
  - `random\` and `row\`: 36 runs each, about 2 MB per run;
  - `random.log`, `row.log`;
  - `analysis\task17_summary.json`: control, counts, shape, lean and streaks;
  - `analysis\task17_measures.json`: per run and tick;
  - copies of the figures.
- **Figures in this folder:** `17_dish_sugar1.png`, `17_dish_sugar3.png`, `17_dish_sugar10.png`,
  `17_closeup_sugar1.png`, `17_closeup_sugar3.png`, `17_closeup_sugar10.png`.
