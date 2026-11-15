# 13: chemistry income per lineage, measured in the page: report

From: gpu session, 14 November 2026, about 22:35 New York. Answers `comms/to_gpu/2026-11-14_13_reply-to-report-06.md`,
and item 2 of `to_gpu/2026-11-14_19_justins-answers-open-questions.md`.

- Measurements are measurements. Readings, the store2 constants and anything about a new form are proposals (Claude's).
- **Page:** harness copies of `build/justins_game_of_life.html` at commit 821a258 (random visiting order on). The
  repository's page is not changed.
- **Runs:** sugar 1, 3 and 10; gliding 0.1; 3 seeds; 2,000 ticks; 256 × 256; CPU queue (`jgol13-`).

## In short

1. **Income is set mostly by the place, not the lineage.** Across the dish, a cell's income differs from a non-kin
   cell's by D = 0.13 (sugar 1), 0.62 (sugar 3) and 3.4 (sugar 10). Within one chemistry square it is only 0.04, 0.10
   and 0.20. D is half the mean squared difference of log income (see "Measures").
2. **Parent and daughter correlate strongly (r 0.87–0.97), but mostly because they sit side by side.** An unrelated
   cell in the parent's square is almost as close to the daughter (r 0.87–0.96).
3. **What is inherited is real but small, and it fades in 2–4 generations.** The lineage's share of the spread is an
   sd of log income of about 0.18–0.34. Report 06 used csd 0.5. About 13% of daughters carry a different reaction
   program from their parent (report 06 used cmu 0.05). The similarity to an ancestor is gone by k ≈ 4 at sugar 3 and
   10.
4. **Costs per tick do not rise with income.** Upkeep and the leak are flat across income quintiles. Only birth costs
   rise, because cells with more income divide more.
5. **The gap between 0.0024 and 0.008 is made up as follows.** The coded upkeep is 0.0024 × 1.18 from the gene
   factors, which gives 0.0028. To that add the energy molecule the cell leaks to the agar (0.0053–0.0059), motility
   and production. Then subtract the clamp, which forgives a debt below zero. **Net: 0.0081 per active cell-tick at
   every sugar level**, which is the calibrated 0.008.
6. **No-change check: passed.** In all 9 runs, the marked and unmarked pages are identical at every tick, 2,000 ticks
   each. The unmarked counts also equal task 17's random-order runs exactly.
7. **The store2 re-run with the measured constants: FAILS.** It does worse than u8g5 at sugar 1. As task 03's rule
   says, I stopped there with no sweep.
8. **Which of report 06's proposals the numbers support: proposal 2,** income tied to the place. See the section
   below. That proposal is not started.

## 1. How it was measured

- **Harness copy:** `test/lineage_page.py` writes two copies to `results/2026-11-14/task13/pages/`:
  - `page_plain.html`, a byte copy of the repository page (sha256 e26573519401c47b…);
  - `page_lineage.html`, the same page with 14 hooks inserted as `__LM && __LM.f(...)`.
  - The hooks only read the page's state and write the harness's own arrays. They draw no random numbers and change
    no order. With `__LM` null, which is the case on the plain page, they do nothing.
- **Marks (`test/lineage.js`):**
  - each cell gets an id at birth (inoculum cells have parent 0);
  - the id moves with the cell on hops, glides and drift;
  - per cell, per 50-tick window, every change of the cell's store (`light[i]`) is added up by cause.
- **The causes found in the page's code:**
  - chemistry: the net change across `domReact`, with downhill gains and uphill costs split;
  - upkeep: active and still;
  - the reserve;
  - sugar burned by the heterotroph gene;
  - the clamp at −1e-6;
  - the energy molecule leaked (`energyStep`, eleak 0.01 every second tick, paid in light);
  - production;
  - contagion;
  - motility (hop cost × 0.4 a tick);
  - hops;
  - birth (the parent's store lost, the daughter's share);
  - clump pooling;
  - a remainder ("other").
- **Accounting closes:** "other" is under 0.00004 per active cell-tick in every run.
- **Rows:** a cell's window counts if it was active ≥ 20 ticks of the 50 and had positive chemistry income. That
  leaves 89–99.9% of the active windows, 9,000–48,000 rows per run.

**Measures.**
- **Income:** chemistry income per active tick, on a log scale.
- **D:** half the mean squared log difference between two cells in the same window. D equals the variance when the two
  are independent, and is 0 when they are equal.
- **Place:** the page's chemistry square, 4 × 4 places, which shares its molecules.
- **Kin:** cells with an ancestor in common within 3 generations.
- **Lineage marker:** the cell's reaction program (`rx`, `rxStr`).

## 2. No-change check (measurement)

| check | result |
|---|---|
| marked against unmarked page, same seed: active, still, births, the sum of all stores (exact double), the sugar, a hash of the occupied places, every tick 1–2,000 | identical in 9 of 9 runs (18,000 tick records) |
| cells without a mark | 0 |
| unmarked page with lineage.js against validate.js (25-tick series) | identical, 9 of 9 |
| my unmarked counts against task 17's `random/` runs | identical, 9 of 9 |

Tick 0 is excluded. Its `births` value is left over from the page's own animation before the harness stops it; it is
the same on both pages once the run starts.

## 3. Heritability: parent and daughter (measurement; mean of 3 seeds)

| sugar | parent–daughter pairs in the same window | r of log income | slope | share in the same square | r with a non-kin cell in the parent's square (same square / adjacent square) | r with the parent (same square / adjacent square) |
|---|---|---|---|---|---|---|
| 1 | 5,900 | 0.87 | 0.85 | 0.64 | 0.92 / 0.73 | 0.97 / 0.80 |
| 3 | 24,800 | 0.89 | 0.86 | 0.60 | 0.87 / 0.70 | 0.96 / 0.79 |
| 10 | 34,200 | 0.97 | 0.94 | 0.67 | 0.96 / 0.91 | 0.99 / 0.93 |

**D for the same pairs:**

| sugar | same square: parent | same square: non-kin | adjacent square: parent | adjacent square: non-kin in the parent's square |
|---|---|---|---|---|
| 1 | 0.018 | 0.038 | 0.093 | 0.129 |
| 3 | 0.029 | 0.102 | 0.193 | 0.278 |
| 10 | 0.066 | 0.195 | 0.393 | 0.488 |

- **Within one square,** the daughter shares 54%, 71% and 66% of the spread with her parent (1 − D_parent/D_non-kin).
  But that spread is small next to the spread between places (section 5).
- **Over time,** a cell's own income from one window to the next has r 0.63, 0.66 and 0.44.
- **The parent's income in the window of the birth** against the daughter's in her first full window has r 0.10, 0.26
  and 0.07. The place changes faster than the lineage carries anything.

## 4. Drift between generations (measurement)

| sugar | daughters with a different reaction program | change per cell-window by fragment uptake or contagion | D, parent–daughter in the same square, same program / changed program | mean change of log income, daughter minus parent | slope of log income on generation, within a square and window |
|---|---|---|---|---|---|
| 1 | 0.126 | 0.058 | 0.005 / 0.053 | +0.020 | +0.010 |
| 3 | 0.133 | 0.060 | 0.012 / 0.102 | +0.034 | +0.009 |
| 10 | 0.127 | 0.064 | 0.043 / 0.167 | −0.002 | −0.009 |

**A cell against its k-th ancestor** (same square and window) against matched non-kin; figure
`13_ancestor_decay.png`:

| sugar | k = 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|
| 1 | 0.011 / 0.041 | 0.022 / 0.063 | 0.027 / 0.052 | 0.022 / 0.046 | 0.043 / 0.048 | 0.14 / 0.04 (31 pairs) |
| 3 | 0.024 / 0.099 | 0.039 / 0.114 | 0.057 / 0.114 | 0.096 / 0.115 | 0.114 / 0.121 | 0.16 / 0.18 |
| 10 | 0.059 / 0.199 | 0.108 / 0.204 | 0.166 / 0.199 | 0.257 / 0.255 | 0.44 / 0.44 | 0.61 / 0.53 |

- **Persistence per generation,** fitted for k = 1–4: about 0.88 (sugar 1, noisy), 0.65 (sugar 3) and 0.48 (sugar 10).
- **In store2's form,** a 7-class walk at cmu 0.13 keeps 0.99 per generation, and even cmu 1 keeps 0.92.
- **There is no directional drift.** The mean daughter-minus-parent change is within ±0.04, and the slope on
  generation is within ±0.01. Mean income per active cell stays at 0.0055–0.0077 from tick 250 on (sugar 10 at tick
  500: 0.0018, at the crash).

## 5. Place against lineage (measurement; non-kin pairs, same window)

| sugar | same square, same program | same square, different program | far apart (≥ 2 squares), same program | far apart, different program | anywhere |
|---|---|---|---|---|---|
| 1 | 0.005 | 0.137 | 0.148 | 0.118 | 0.132 |
| 3 | 0.031 | 0.316 | 0.563 | 0.641 | 0.617 |
| 10 | 0.079 | 0.451 | 2.36 | 4.06 | 3.42 |

**Components (proposal, read from these D values):**
- **Noise:** same square, same program, which is 0.005, 0.031 and 0.079.
- **Lineage:** the same-square non-kin D minus the noise. That is 0.033, 0.071 and 0.116, or an sd of log income of
  **0.18, 0.27 and 0.34**.
- **Place:** far apart with the same program, minus the noise. That is 0.14, 0.53 and 2.3, an sd of **0.38, 0.73 and
  1.5**.

So one lineage in different squares differs about as much as different lineages anywhere do. Different lineages in one
square are close. At sugar 3 and 10 the place carries 5–20 times the variance the lineage does. At sugar 1 the two are
nearer, but the place still carries about 4 times as much.

## 6. Costs per cell, and the gap to 0.008 (measurement)

**All active cell-ticks** (store units per active cell-tick; mean of 3 seeds):

| sugar | chemistry (net) | sugar burned | upkeep | leak to agar | motility | production | clamp (given back) | upkeep + leak + motility + production − clamp | birth cost (parent's loss beyond the daughter's share) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00627 | 0.00293 | 0.00284 | 0.00530 | 0.00020 | 0.00002 | 0.00030 | **0.00806** | 0.00072 |
| 3 | 0.00571 | 0.00408 | 0.00277 | 0.00541 | 0.00064 | 0.00028 | 0.00105 | **0.00805** | 0.00083 |
| 10 | 0.00397 | 0.00635 | 0.00275 | 0.00594 | 0.00093 | 0.00243 | 0.00389 | **0.00816** | 0.00042 |

**The gap, cause by cause:**
- **Upkeep is the coded value.** 0.0024 × 1.18 (the factor for the inoculum's two genes, heterotroph and dormancy)
  gives 0.0028.
- **The leak supplies most of the rest.** Each active cell with a store above 0.01 pays 0.01 every second tick into
  the agar's sugar. Reading: some of it can be eaten back at eeff 0.4.
- **Motility and production** add a little more at sugar 3 and 10.
- **The clamp gives part back.** A charge that would take the store below zero is forgiven at −1e-6.
- **Net running cost:** 0.0081 at all three sugar levels, the calibrated 0.008.
- **Uphill reactions and coat work** (0.0001–0.0006) are already inside the net chemistry income, as in report 03.

**Costs against income, by quintile of a cell-window's chemistry income** (sugar 3; sugar 1 and 10 look the same):

| quintile | income | upkeep | leak | birth cost | births per tick |
|---|---|---|---|---|---|
| 1 | 0.0010 | 0.00277 | 0.00509 | 0.00001 | 0.0005 |
| 2 | 0.0032 | 0.00277 | 0.00503 | 0.00003 | 0.0005 |
| 3 | 0.0049 | 0.00277 | 0.00502 | 0.00014 | 0.0013 |
| 4 | 0.0067 | 0.00278 | 0.00499 | 0.00074 | 0.0047 |
| 5 | 0.0131 | 0.00275 | 0.00496 | 0.00348 | 0.0219 |

- **Running costs are flat in income.** Across rows, r(income, upkeep + leak + motility + production) is −0.10, 0.02
  and 0.18.
- **Only birth costs rise with income** (r 0.50, 0.62, 0.38). They are what income is spent on, not a tax on it.
- Production rises a little with income at sugar 10 (r 0.21).

## 7. The store2 re-run with the measured constants (proposal, validated as report 06)

- **Changed from u8g5:** csd is the measured lineage sd per sugar level (0.18, 0.27, 0.34), and cmu is 0.13 (the share
  of daughters with a different reaction program).
- **As in task 16's u8g5Dc:** upk 0.008, grow 0.5, Dc 0.0384.
- **Validated against the random-order page:** my unmarked runs, `task13/validate_plain`, identical to task 17's.
- **u8g5Dc** was rerun beside it as the reference.

All cells, with active cells in brackets, then r95; mean of 3 seeds.

| sugar | variant | tick 100 | 250 | 500 | 1,000 | 2,000 |
|---|---|---|---|---|---|---|
| 1 | page | 705 (645) r19 | 562 (151) r22 | 383 (134) r29 | 365 (257) r38 | 319 (234) r63 |
| 1 | u8g5Dc | 799 (116) r30 | 675 (52) r39 | 531 (35) r55 | 382 (36) r85 | 454 (43) r110 |
| 1 | measured | 786 (101) r30 | 616 (23) r36 | 415 (12) r53 | 190 (8) r71 | 68 (9) r78 |
| 3 | page | 866 (751) r24 | 888 (384) r38 | 1,430 (859) r69 | 2,925 (1,361) r108 | 1,587 (436) r117 |
| 3 | u8g5Dc | 1,389 (399) r43 | 2,278 (579) r76 | 3,807 (728) r112 | 2,750 (161) r122 | 374 (15) r124 |
| 3 | measured | 1,381 (382) r44 | 2,043 (447) r80 | 3,640 (635) r115 | 2,193 (98) r121 | 285 (1) r122 |
| 10 | page | 2,511 (2,339) r46 | 14,197 (9,379) r109 | 13,469 (113) r120 | 4,376 (15) r120 | 548 (44) r119 |
| 10 | u8g5Dc | 3,841 (1,977) r48 | 12,498 (4,454) r97 | 13,485 (633) r121 | 4,608 (49) r124 | 503 (19) r125 |
| 10 | measured | 3,292 (1,636) r47 | 11,195 (3,819) r95 | 13,007 (483) r121 | 4,179 (20) r121 | 445 (2) r123 |

- **Result: FAIL.**
  - **Sugar 1** dies out (68 cells at tick 2,000 against the page's 319), as report 06's no-heritability control did.
  - **Sugar 3** still has no second wave.
  - **Sugar 10's crash** is still reproduced in total cells. With random order the page now keeps only 113 active
    cells at tick 500 (row order had 631), so both versions keep too many active cells there.
- **Stopped here** (no sweep), as task 03 says.
- **Reading (proposal):** store2's lineage classes cannot carry what was measured.
  - The page's heritable part is small and short-lived: about 0.5–0.9 per generation, where the class walk keeps
    ≥ 0.92.
  - Most of the spread belongs to the place, which store2 averages over 10 × 10 blocks (about 6 chemistry squares).
  - The narrower measured spread removes the selection that kept u8g5's sugar-1 colony going, and nothing replaces it.

## Which of report 06's proposals the numbers support (reading, proposal)

**Proposal 2 (income tied to the place)** is the one these numbers support. Proposal 1 (income per lineage) is not.

- **Place dominates.** Income depends on where a cell is (its chemistry square, at that time) far more than on its
  lineage. The place variance is 4–20 times the lineage variance.
- **Kinship adds little beyond place.** A non-kin neighbour in the same square predicts a cell's income almost as well
  as its parent does.
- **The lineage part fades.** It lasts 2–4 generations, and drives no upward trend. That is why the page shows no
  selection, as report 06 saw.
- **One part of proposal 2 is not borne out.** Running costs do not rise with income.
  - In the page, the costs per cell are a flat 0.008 per active tick: upkeep plus leak, minus the clamp.
  - Only birth spending rises with income.
  - A place-tied fold would need a flat cost, not one that rises with income.
- Proposal 2 is not started. Whether to start it is Justin's decision.

## Files

- **Harness (GPU machine, `jgol_2026-11-13/`):**
  - `test/lineage_page.py`: makes the copies;
  - `test/lineage.js`: the marks and the per-tick check record;
  - `test/task13_runs.cmd`: the runs.
- **Analysis:**
  - `popdish/lineage13.py`: per-run measures;
  - `popdish/lineage13_table.py`: per-sugar means and the store2 constants;
  - `popdish/lineage13_fig.py`: the figure;
  - `popdish/task13_store2.cmd`: the re-run. `store2.py` is unchanged.
- **Results (`results/2026-11-14/task13/`):**
  - `pages/`: the harness copies;
  - `lineage/`: marked runs;
  - `plain_check/`: unmarked runs;
  - `validate_plain/`: unmarked validate.js runs;
  - `nochange_check.json` and `check13.py`: the no-change check;
  - `lineage_analysis.json`: per run;
  - `lineage_table.json`: per sugar level;
  - `store2/`, `store2_pages/` and `store2_s*.log`: the re-run;
  - `smoke_*`: 200- and 400-tick tests.
- **Figure:** `comms/from_gpu/13_ancestor_decay.png`.
