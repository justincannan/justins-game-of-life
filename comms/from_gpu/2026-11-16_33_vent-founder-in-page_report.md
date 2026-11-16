# 33: vent founding on the page with the chemotroph founder (re-measured)

From: gpu session (scheduled check), 16 November 2026, about 15:50 New York. Answers
`to_gpu/2026-11-16_33_vent-founder-in-page.md` (including its 14:00 addition), and applies task 30.

## Method
- **Page:** 4e413e2 (`build/justins_game_of_life.html` at that commit; copy in
  `jgol_2026-11-13/results/2026-11-16/task33/pages/`). It has `chemoFounder()`, the `dishSetup` fix, the coat fix, the
  repeatable-run fixes and the fix for virus copying driving molecules negative.
- **Harness:** `test/vent33.js`, task 29's `vent29.js` with the seeding changed as task 30 asks: the harness sets
  `P.seed` and calls `reset('organism')`; it no longer replaces `rng` or calls `geoSeed()`. The founder's chemotroph
  gene comes from the page's own `chemoFounder()` (the harness's `chemVent` test is off). Added records: cells with
  non-finite energy, the page's r/m counters, and the gene `chemoFounder` chose.
- **World:** vent, one-organism start, 476 × 248, `P.autoRestart` off, page defaults (`P.domCost` 0.001).
- **Runs** (CPU queue `jgol33-vent`, port 8811, driver `vent29_driver.py`): seeds 11–40 for 1,000 ticks; seeds 11–20
  for 1,000 ticks with `P.domCost` 0; seeds 11–20 for 6,000 ticks. No run failed to start.
- **Founded** = cells alive at tick 1,000 (as in report 29).

## Results (measured)
1. **Founding: 30 of 30** (seeds 11–40), against 0 of 70 on the pages from 581c90e to b4ceffa (report 29). With
   `P.domCost` 0: 10 of 10. Cells at tick 1,000: 11,687 to 49,905 (median 29,631; domCost 0: median 35,098).
2. **The gene chosen:** `4 4 4 4 15 0 8 7` (`eeeepaih`) in 26 seeds, `2 2 2 2 13 2 10 5` (`ccccnckf`) in seeds 19,
   30, 34 and 39. This agrees with the cloud's check for seeds 19 and 30.
3. **The founding dip:** the population first falls from the founders (about 210) before it grows; its lowest count
   was 131–243 in 29 seeds, and 2 cells in seed 38, which still recovered (19,671 cells at tick 1,000).
4. **Survival to 6,000 ticks: 10 of 10** (seeds 11–20). Cells at tick 6,000: 29,667 to 65,917. After tick 1,000 no run
   fell below 20,427 cells, and in no run did the count halve between records (every 100 ticks). **No cell had
   non-finite energy at any record in any run** (the NaN deaths of the 14:00 note do not appear).
5. **r/m at tick 6,000** (the page's counters: monomers changed by splices per monomer changed by copying error):
   4.6 to 11.7, median about 7.
6. **Repeatability (task 30):** seed 11 run twice from separate page loads (a 200-tick smoke run and the 1,000-tick
   run) gave identical cell counts and birth totals at all 104 shared records.

## Not done
- The dish seeds 2, 3, 4 and 6 (asked "if useful") were not re-run in this check. They can be run at the next check
  if wanted; the cloud's check already found all 12 dish founders to be one gene.

## Superseded
- Report 29's vent-founding numbers (0 of 70) describe the pages before 34eceaf; on this page the vent founds.
