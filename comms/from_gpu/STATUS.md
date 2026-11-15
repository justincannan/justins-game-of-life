# Status of the GPU session's tasks

Written only by the GPU session (task 09); the cloud side reads it. One row per task in `comms/to_gpu/`. Times are New
York time. This is the summary; `comms/log/gpu.md` is the history. Rows for 01–05 are backfilled from the log and from
the commit times of the reports.

States: not started, running, waiting on Justin, done, closed (stopped by the task's own rule), superseded.

| Task | Started | State | Updated | Report |
|---|---|---|---|---|
| 01 hello | 2026-11-14 12:40 | done | 2026-11-14 12:40 | `2026-11-14_01_hello_report.md` |
| 02 lattice-fold | 2026-11-14 13:25 | done | 2026-11-14 14:50 | `2026-11-14_02_lattice-fold_report.md` |
| 03 pop-dish-two-resources | 2026-11-14 13:25 | closed (no fold passed; task 05) | 2026-11-14 14:02 | `2026-11-14_03_pop-dish-two-resources_report.md` |
| 03a maps-at-cell-scale | 2026-11-14 13:25 | done (in report 03) | 2026-11-14 13:35 | `2026-11-14_03_pop-dish-two-resources_report.md` |
| 04 scheduled-checks | 2026-11-14 13:25 | done | 2026-11-14 13:21 | `2026-11-14_04_scheduled-checks_report.md` |
| 05 reply-to-reports-03-04 | 2026-11-14 14:21 | done (read; nothing to run) | 2026-11-14 14:21 | none needed |
| 06 store-fold-two-incomes | 2026-11-14 15:20 | closed (no fold passed; sugar 10's crash reproduced; lineage selection too strong) | 2026-11-14 17:30 | `2026-11-14_06_store-fold-two-incomes_report.md` |
| 07 popdish-fine-two-resources | 2026-11-14 15:12 | done (no branching) | 2026-11-14 15:26 | `2026-11-14_07_popdish-fine-two-resources_report.md` |
| 08 row-streaks-check | 2026-11-14 14:26 | done | 2026-11-14 14:45 | `2026-11-14_08_row-streaks-check_report.md` |
| 09 task-status | 2026-11-14 14:45 | done (this file) | 2026-11-14 14:45 | this file |
| 10 finer-blocks | | waiting on a passing fold (none passed in task 06, nor in task 16's rerun) | 2026-11-14 21:25 | |
| 11 reply-to-reports-02-07-08 | 2026-11-14 17:10 | done (read; times for 06/07 corrected from UTC to New York) | 2026-11-14 17:30 | none needed |
| 12 folding-from-the-ground-up | 2026-11-14 19:10 | done (design approved by Justin; the prototype is task 15) | 2026-11-14 21:25 | `2026-11-14_12_design_report.md` |
| 12a open-and-fold-across-scales | 2026-11-14 19:10 | done (approved with the design; task 15) | 2026-11-14 21:25 | `2026-11-14_12_design_report.md` |
| 12b beads | 2026-11-14 19:10 | done (approved with the design; beads built in task 15 step 1) | 2026-11-14 21:25 | `2026-11-14_12_design_report.md` |
| 13 reply-to-report-06 | 2026-11-14 22:11 | done (place outweighs lineage; store2 re-run with measured constants fails; numbers support report 06 proposal 2, not started) | 2026-11-14 22:40 | `2026-11-14_13_lineage-income-measure_report.md` |
| 14 reply-to-report-12 | 2026-11-14 21:25 | done (read; the "nine times" figure dropped, see report 15 summary) | 2026-11-14 21:25 | none needed |
| 15 design-approved-prototype | 2026-11-14 21:10 | waiting on Justin (steps 1 and 2 done, checks met; step 3 built, checks not met: nothing folds with step 1's table; step 4 waits; proposals in step 3 report section 9) | 2026-11-15 00:05 | `2026-11-14_15_design-approved-prototype_report.md`, `2026-11-14_15_step3_tertiary-fold_report.md` |
| 16 popmodels-molecules-diffuse | 2026-11-14 21:10 | done (no arms; no fold passes; task 10 stays waiting) | 2026-11-14 21:25 | `2026-11-14_16_popmodels-molecules-diffuse_report.md` |
| 17 random-order-baseline | 2026-11-14 22:11 | done (counts and shape within seed spread; lean and streaks gone; the new baseline) | 2026-11-14 22:35 | `2026-11-14_17_random-order-baseline_report.md` |
| 18 reply-open-questions-lehninger | 2026-11-14 22:11 | done (read; contacts consistent; used in step 3) | 2026-11-14 22:11 | none needed |
| 19 justins-answers-open-questions | 2026-11-14 22:11 | done (item 3 in report 17, item 2 in report 13, item 1 in the step 3 report, section 6) | 2026-11-15 00:05 | reports 17, 13 and 15 step 3 |
| 20 buried-salt-bridges | 2026-11-14 22:11 | done (benchmarks checked in step 3: both fail; section 7) | 2026-11-15 00:05 | `2026-11-14_15_step3_tertiary-fold_report.md` |
| 21 reply-to-reports-13-15s3-17 | 2026-11-15 09:10 | done (read; nothing to run: no proposal started, step 4 waits, oily-partner rule stands for the next table revision) | 2026-11-15 09:10 | none needed |
| 22 population-scale-rethought | 2026-11-15 11:10 | item 1 done (mostly mutation at division, 4–6% of daughters; contagion about a sixth at sugar 3 and 10; report 13's 13% was mostly a measuring error, corrected); item 2 next (CPU queue); item 3 waits on Justin seeing item 2 | 2026-11-15 11:30 | `2026-11-15_22_population-scale-rethought_report.md` (item 1) |

Correction (2026-11-14 17:30): the times for 06 and 07 first written here (20:12, 20:20, 20:26) were UTC, from a shell
clock without a time zone; they are now New York time (15:12, 15:20, 15:26).
