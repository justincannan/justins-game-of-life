# 06: the store fold fed by both incomes: report

From: gpu session (scheduled check), 14 November 2026. Answers `comms/to_gpu/2026-11-14_06_store-fold-two-incomes.md`.

- **Measurements are measurements.** The fold, its form for lineages, the calibrated constants and the readings are
  proposals.
- **The page:** the same runs as report 03 (`day9_repo/validate_page/`: sugar 1, 3, 10; gliding 0.1; 3 seeds; 2,000
  ticks). The page is unchanged.

## In short

1. **No version passes, so no sweep was run** (the task's own rule). Task 06 is closed; task 10 stays waiting.
2. **The fold gets sugar 10's crash** for the first time. Best version, u8g5: active cells 527 at tick 500 against the
   page's 631; all cells 13,321 against 13,495 at tick 500, and 4,465 against 4,496 at tick 1,000.
3. **It fails at sugar 1 and 3.**
   - **Sugar 1:** the totals are about right, but too few cells are active (57–112 against 145–599), and the colony
     spreads too far (radius 117 against 81 at tick 2,000).
   - **Sugar 3:** it grows 2–5 times too fast before tick 500, and has no second wave.
4. **The main finding: the fold selects lineages far harder than the page does.**
   - **In the fold,** the active cells' mean income rate rises 1.5–2.4-fold over 2,000 ticks. Their chemistry income
     reaches 0.008–0.013 per cell-tick.
   - **In the page,** income per active cell stays flat at about 0.005–0.006 at every sugar level and tick
     (`lineage_income.json`; report 03's measurements agree).
   - **Without heritability** (the control: each daughter's rate drawn afresh), the fold has no selection, but the
     colony dies out at sugar 1 (95 cells at tick 2,000 against 563 with inheritance).
   - **Reading (proposal):** in the page, cells keep going on chemistry because each cell's income is close to its
     costs, not because lineages that earn more are selected. A heritable spread as wide as the measured spread
     between cells (sd of log income about 0.5) is selected far too fast.
   - Either most of that spread is not heritable (it is noise, or it belongs to the place), or the page's costs rise
     with income.
5. **What is missing (proposal):** a measured heritability and cost of chemistry income. The snapshots cannot give
   either: their income per place over 100 ticks mixes occupants. The next step would be per-cell income with lineage
   marks, in harness copies of the page (within task 06's scope, as reply 11 says). I have not started it, because the
   task's rule says to stop once no version passes. If it is wanted, it can be sent as a task.

## 1. The fold (proposal; `jgol_2026-11-13/popdish/store2.py`)

- **Geometry and start:** as report 03. There is one square per 10 × 10 block, started from the page's map at tick 5,
  with the molecule field taken block by block from the page's first snapshot.
- **Lineages:** each square holds 7 income classes, with counts of active and still cells and the mean store of the
  active cells.
  - Class k's chemistry rate is multiplied by m_k = exp(csd · z_k − csd²/2), with z in [−1.5, 1.5].
  - The classes start in proportion to a normal density, so the rates start log-normal with sd csd.
  - **Fitted:** csd = 0.5, the measured within-square sd of log income at tick 100 (0.36–0.62).
  - **Drift:** a daughter moves one class up or down with probability cmu (0.05). This is not measurable from the
    snapshots, so it is a free constant.
- **Chemistry:** income per active cell c_k = 0.00653 · m_k · x/(x + Kc), where x = mE per active cell in the square
  (report 03's per-cell fit; Kc 8.43). The income goes into the store, and the field runs down by 6 per unit earned.
- **Upkeep:** upk per active cell-tick from the store.
  - **Calibrated:** 0.008. That is about 3 times the page's coded 0.01 × dishUpkeep 0.24. The difference may be other
    costs I have not counted, such as sequence costs or the gene factors.
- **Sugar:** the store refills towards 0.4 at up to 0.06 a tick (hetFill 0.02 × gene strength 3). It costs 1/eeff (0.4)
  page units per unit, and is capped by the sugar present.
- **Division:** grow · room^0.61 · G(E).
  - G is a Hill gate at E = 0.4, the page's birth 0.2 plus 2 × divKeep 0.1.
  - The parent pays 0.3, and the daughter starts with 0.1.
  - 15.5% of births land in a neighbouring square.
  - **Calibrated:** grow 0.5.
- **Going still:** the measured Hill form in the store, 0.029 / (1 + (E/0.226)^7.1).
- **Waking:** measured, from sugar only. A woken cell starts with E 0.2.
- **Deaths:** as measured.

## 2. The validation (all cells, with active cells in brackets; r = 95th-percentile radius in places; mean of 3 seeds)

**Variants (proposals):**
- **u8g5:** upk 0.008, grow 0.5.
- **u6K20:** upk 0.006, Kc 20, so income is more sensitive to crowding.
- **u7c8:** upk 0.007, with a wider spread (csd 0.8).
- **u8g5 shuffle:** u8g5 with no heritability.

Grid 1 (`task06/grid1.log`) also has upk 0.006 and 0.010, grow 0.238, and hfill 0.12. Grid 2 (`grid2.log`) also has
csd 0.8 at upk 0.008, cmu 0.01, and hfill 0.03. None does better than the variants below.

| Page sugar | Tick | Page | u8g5 | u6K20 | u7c8 | u8g5 shuffle (grid 1, with hfill 0.12) |
|---|---|---|---|---|---|---|
| 1 | 100 | 698 (599), r 19 | 776 (112), r 26 | 837 (137) | 890 (204) | 823 (118) |
| 1 | 500 | 387 (145), r 31 | 599 (74), r 63 | 959 (156) | 3,069 (1,055) | 460 (27) |
| 1 | 1,000 | 418 (273), r 45 | 610 (77), r 87 | 1,355 (189) | 8,941 (2,071) | 277 (19) |
| 1 | 2,000 | 567 (364), r 81 | 607 (67), r 117 | 789 (63) | 7,049 (676) | 95 (13) |
| 3 | 250 | 749 (295), r 31 | 2,282 (560), r 80 | 2,600 (705) | 3,148 (1,114) | 3,379 (861) |
| 3 | 500 | 788 (374), r 46 | 3,947 (802), r 114 | 4,432 (743) | 7,261 (1,935) | 4,143 (291) |
| 3 | 1,000 | 2,261 (1,349), r 110 | 2,532 (116) | 2,770 (149) | 7,373 (1,025) | 1,884 (39) |
| 3 | 2,000 | 1,561 (505) | 394 (20) | 415 (21) | 3,748 (405) | 211 (1) |
| 10 | 100 | 2,657 (2,211), r 48 | 3,570 (1,791), r 48 | 3,425 (1,713) | 3,771 (2,105) | 6,050 (3,217) |
| 10 | 250 | 13,160 (8,167), r 110 | 11,910 (4,293), r 96 | 11,434 (3,923) | 14,632 (6,217) | 19,233 (3,985) |
| 10 | 500 | 13,495 (631) | **13,321 (527)** | 13,282 (561) | 19,344 (2,897) | 11,604 (85) |
| 10 | 1,000 | 4,496 (52) | **4,465 (20)** | 4,464 (41) | 10,743 (767) | 3,697 (6) |
| 10 | 2,000 | 569 (45) | **473 (9)** | 486 (14) | 2,324 (108) | 373 (0) |

**Sugar 10's crash** (active cells from about 8,200 to 630 between ticks 250 and 500):
- u8g5 falls from 4,293 to 527, and u6K20 from 3,923 to 561. The size of the crash is right; the peak is half the
  page's.
- C2x (report 03) kept 9,916 active cells.
- **Measurement of the fold:** the crash comes from the store. Once the sugar is gone, the income of most lineages
  (crowded: about 13 mE per active cell) is below upkeep. The stores empty, and the cells go still by the measured
  Hill form.

**Mean chemistry rate of the active cells in the fold** (m, 1 at the start) and their income per cell-tick:

| Variant | Sugar | Tick 100 | Tick 500 | Tick 2,000 |
|---|---|---|---|---|
| u8g5 | 1 | 1.28, 0.0078 | 1.68, 0.0104 | 1.78, 0.0110 |
| u8g5 | 10 | 1.21, 0.0056 | 1.50, 0.0084 | 1.87, 0.0103 |
| u7c8 | 1 | 1.67, 0.0098 | 2.33, 0.0127 | 2.40, 0.0127 |

For comparison, the page's measured income per active cell is 0.0055–0.0065 at sugar 1 for ticks 100–2,000, with no
upward trend.

## 3. Shape at block scale (roughness / box dimension, as in 03a; mean of 3 seeds)

| Page sugar | Tick | Page | u8g5 | u6K20 |
|---|---|---|---|---|
| 1 | 1,000 | 1.87 / 1.47 | 2.70 / 1.40 | 3.25 / 1.49 |
| 1 | 2,000 | 2.92 / 1.36 | 5.39 / 1.34 | 6.33 / 1.44 |
| 3 | 1,000 | 2.56 / 1.58 | 3.02 / 1.78 | 2.96 / 1.82 |
| 3 | 2,000 | 4.63 / 1.64 | 9.03 / 1.31 | 8.58 / 1.35 |
| 10 | 500 | 1.30 / 1.93 | 1.34 / 1.93 | 1.31 / 1.94 |
| 10 | 2,000 | 7.40 / 1.57 | 7.96 / 1.57 | 8.32 / 1.56 |

- **At sugar 10** the shape matches through the whole run.
- **At sugar 1 and 3** the fold scatters thinly over too much of the plate: roughness is too high, and the radius
  overshoots.

**Figures:** `06_blockmaps_sugar1.png`, `…3.png`, `…10.png` show the page against u8g5, u6K20 and u7c8, seed 1.
- These are block maps (one pixel per 10 × 10 places).
- Green is active cells, and purple is cells gone still.
- The page has no block map at tick 100.

## 4. Order and other tasks

- **Task 10** (finer blocks) stays "waiting on a passing fold", as it says.
- **Proposals for Justin** (not started):
  1. Measure per-cell chemistry income with lineage marks in harness copies of the page. This would give the
     heritability (parent–daughter correlation of income), the drift, and whether costs scale with income. This is
     the missing piece for any per-lineage fold.
  2. Alternatively, a fold in which income per cell is not heritable but tied to the place, with a cost that rises
     with the income earned.

## Files

- **Code:** `jgol_2026-11-13/popdish/store2.py` (the fold, and the validation table) and `store2_fig.py` (the
  figures).
- **Results:** `jgol_2026-11-13/results/2026-11-14/task06/`, on the GPU machine:
  - `grid1/` and `grid2/`, with per-run series and maps and `summary.json`;
  - `grid1.log` and `grid2.log`;
  - `lineage_income.json`.
