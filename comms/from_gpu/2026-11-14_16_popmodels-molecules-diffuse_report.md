# 16: the population models' molecules spread as the page's do

From: gpu session (scheduled check), 14 November 2026, about 21:20 New York. Answers
`to_gpu/2026-11-14_16_popmodels-molecules-diffuse.md` (Justin's decision, item 1).

Measurements as measurements. Readings are proposals (Claude's).

## Summary
- **The page's rate, measured in the dish:**
  - the wetness factor is 1.000 on the plate's mean, in every run;
  - the page spreads molecules at D = 0.24 per tick between coarse squares, that is 0.06 coarse squares² (0.96
    places²) a tick.
- **Correction to the task's premise:** `store2.py` already spread its molecule field (Dc = 0.02), at half the page's
  rate. Only `pop2_gpu.py` did not spread its molecules.
- **Both models now spread at the page's rate:** `pop2_gpu.py --Dm 0.06`, and `store2.py --Dc 0.0384` (the same rate
  on 10 × 10 blocks).
- **Fine grid (report 07's test): no change.**
  - Box dimension, boundary roughness and counts move by 1–3%. No arms appear at any sugar level or sugar diffusion.
  - Reason (measurement): on the fine grid, cells use only 5–9% of the plate's molecule energy by tick 2,000 at sugar
    1 and 3, and 50% at sugar 10. Chemistry income is near its ceiling where cells are, so spreading the field
    cannot set a diffusion limit.
- **Store fold (report 06's best, u8g5): no fold passes.**
  - With the page's spreading, sugar 10's crash is still reproduced (649 active at tick 500, page 631).
  - It still fails at sugar 1: 38–65 active cells against the page's 145–364.
  - It still fails at sugar 3: no second wave, 16 active at tick 2,000 against 505.
  - So **task 10 stays waiting**, as its rule says.
- Proposal (reading): the missing piece is more likely heritability and costs, the measurement task 13 asks for,
  than the molecules' transport.

## 1. The page's rate (step 1)
- **The code (chemStep):** each coarse square's molecules change by D · ww · (mean of 4 neighbours − own).
  - D = min(0.24, 2 · chdiff) = 0.24 (chdiff 0.15);
  - ww = min(1, water / wrain) when water is on (it is, in the dish).
- **Probe:** `jgol_2026-11-13/test/probe_wet.js`, read-only on the page.
  - Runs: sugar 1, 3 and 10; gliding 0.1; 3 seeds; 2,000 ticks; 256 × 256; through the CPU queue.
  - ww was read over the plate's squares every 25 ticks.

| sugar | lowest plate-mean ww | lowest ww of any square | lowest ww under cells | mean effective D |
|---|---|---|---|---|
| 1 | 0.9995 | 0.82 | 0.981 | 0.240 |
| 3 | 0.9997 | 0.78 | 0.990 | 0.240 |
| 10 | 0.9997 | 0.79 | 0.997 | 0.240 |

- **So wetness is 1** for the purpose of the models. In the coarse squares' Laplacian form (n += D_lap · lap n):
  - the page's rate is D_lap = 0.24/4 = 0.06 coarse squares² a tick, which is 0.96 places² a tick;
  - on store2's 10 × 10 blocks, it is 0.0096 blocks², so Dc = 0.0384 in store2's form (Dc · 0.25 · lap);
  - store2 had 0.02 (0.5 places²).
- **Sugar is unchanged in both models,** as the task says. The page's own sugar rate, for the record, is D = 0.2 per
  tick (energyStep), 0.8 places² a tick. The models use their fitted values: 0.025 coarse² on the fine grid, and Dn
  0.016 in store2.

## 2. Fine grid (step 2; `pop2_gpu.py`, report 07's runs with `--Dm 0.06`)
- **Runs:** as report 07: 1,000 × 1,000 (radius 480) and the page's plate (256 × 256, radius 121.6); sugar 1, 3 and
  10; sugar diffusion 0.025, 0.008, 0.0025 and 0.0008; 3 seeds; 2,000 ticks; GPU queue (about 30 s per setting).
- **Figures:** `16_fine_sugar1.png`, `…3.png`, `…10.png`. The page is on top, then the four sugar diffusion rates.
  The figure's title still reads "Task 07": it is report 07's script, rerun.

**Fine grid**, seed mean. Each cell gives report 07 → this run.

| sugar | tick | D | live cells | roughness | box dimension |
|---|---|---|---|---|---|
| 1 | 2,000 | 0.025 | 17,063 → 16,857 | 90.9 → 91.7 | 1.70 → 1.69 |
| 1 | 2,000 | 0.0008 | 12,576 → 12,338 | 83.5 → 83.7 | 1.68 → 1.68 |
| 3 | 2,000 | 0.025 | 35,126 → 34,021 | 123.9 → 122.9 | 1.72 → 1.72 |
| 3 | 2,000 | 0.0008 | 26,882 → 26,511 | 118.2 → 118.6 | 1.72 → 1.72 |
| 10 | 2,000 | 0.025 | 178,509 → 179,117 | 269.8 → 268.7 | 1.76 → 1.76 |
| 10 | 2,000 | 0.0008 | 171,590 → 171,850 | 276.6 → 276.4 | 1.76 → 1.76 |

**Page-size plate**, seed mean, with the page alongside. The middle columns give report 07 → this run.

| sugar | tick | page live (box dimension) | D 0.025 live | D 0.025 box dimension | D 0.0008 live | D 0.0008 box dimension |
|---|---|---|---|---|---|---|
| 1 | 2,000 | 567 (1.17) | 5,638 → 5,538 | 1.54 → 1.54 | 8,163 → 8,482 | 1.63 → 1.64 |
| 3 | 2,000 | 1,561 (1.18) | 2,000 → 1,963 | 1.25 → 1.24 | 2,505 → 2,710 | 1.32 → 1.35 |
| 10 | 2,000 | 569 (0.80) | 443 → 448 | 0.72 → 0.73 | 438 → 436 | 0.72 → 0.72 |

- **Arms: none.** At every setting the colony stays a compact disc with a rough rim, as in report 07 (figures).
- **Why (measurement):** the plate's molecule energy on the fine grid, seed 1, D 0.025:
  - sugar 1: 4.03 M at tick 100, 3.83 M at tick 2,000 (5% used);
  - sugar 3: 3.67 M at tick 2,000 (9% used);
  - sugar 10: 2.03 M at tick 2,000 (50% used).
- At 89 mE per coarse square and a half-saturation of 8.4 mE per active cell, a square must be nearly emptied before
  income falls. Cells move into fresh agar faster than they empty it. So the molecules do not limit the front, and
  spreading them changes nothing. Reading (proposal): report 07's idea, that the field's lack of spreading was what
  removed the diffusion limit behind branching, is not borne out in this model.

## 3. Store fold (step 3; `store2.py`, report 06's u8g5 with the page's spread)
- **Runs:** sugar 1, 3 and 10; 3 seeds; 2,000 ticks; CPU queue. Started from the page's runs in
  `results/2026-11-13/day9_repo/validate_page`, as report 06 did.
- **Variants:** u8g5 = upk 0.008, grow 0.5 (Dc 0.02, as in report 06, rerun here), and u8g5Dc = the same with
  Dc 0.0384.

All cells, with active cells in brackets, then r95.

| sugar | variant | tick 100 | tick 250 | tick 500 | tick 1,000 | tick 2,000 |
|---|---|---|---|---|---|---|
| 1 | page | 698 (599) r19 | 548 (178) r22 | 387 (145) r31 | 418 (273) r45 | 567 (364) r81 |
| 1 | u8g5 | 776 (112) r26 | 673 (57) r39 | 599 (74) r63 | 610 (77) r87 | 607 (67) r117 |
| 1 | u8g5Dc | 779 (111) r26 | 636 (35) r32 | 488 (38) r44 | 505 (62) r82 | 597 (65) r117 |
| 3 | page | 830 (649) r22 | 749 (295) r31 | 788 (374) r46 | 2,261 (1,349) r110 | 1,561 (505) r117 |
| 3 | u8g5 | 1,418 (422) r45 | 2,282 (560) r80 | 3,947 (802) r114 | 2,532 (116) r121 | 394 (20) r123 |
| 3 | u8g5Dc | 1,425 (402) r41 | 2,096 (492) r75 | 3,380 (628) r113 | 2,319 (145) r122 | 354 (16) r124 |
| 10 | page | 2,657 (2,211) r48 | 13,160 (8,167) r110 | 13,495 (631) r120 | 4,496 (52) r120 | 569 (45) r119 |
| 10 | u8g5 | 3,570 (1,791) r48 | 11,910 (4,293) r96 | 13,321 (527) r121 | 4,465 (20) r123 | 473 (9) r123 |
| 10 | u8g5Dc | 3,588 (1,823) r49 | 11,849 (4,167) r97 | 13,384 (649) r121 | 4,568 (39) r123 | 473 (10) r124 |

- With the page's spreading, sugar 1's spread (r95) comes closer to the page in the first 500 ticks (r44 against
  r31, before r63). But active cells stay far too few. Sugar 3 still crashes instead of the page's second wave.
  Sugar 10 is as before.
- **No fold passes,** so no sweep (task 03's rule), and task 10 does not begin.

## Files
- **Probe:** `jgol_2026-11-13/test/probe_wet.js`.
- **Models:** `jgol_2026-11-13/popdish/pop2_gpu.py` (new option `--Dm`; the default 0 keeps report 07's runs) and
  `store2.py` (unchanged; run with `--Dc 0.0384`).
- **Results:** `jgol_2026-11-13/results/2026-11-14/task16_wet/`, `task16/fine`, `task16/pagesize`, `task16/store2`,
  and `task16/figs` (tables as JSON).
