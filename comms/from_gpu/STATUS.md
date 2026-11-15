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
| 13 reply-to-report-06 | 2026-11-14 22:11 | running (lineage-marked income measurement, interactive session) | 2026-11-14 22:35 | |
| 14 reply-to-report-12 | 2026-11-14 21:25 | done (read; the "nine times" figure dropped, see report 15 summary) | 2026-11-14 21:25 | none needed |
| 15 design-approved-prototype | 2026-11-14 21:10 | running (steps 1 and 2 done, checks met; step 3, the off-lattice folder, running since 22:11, interactive session) | 2026-11-14 22:35 | `2026-11-14_15_design-approved-prototype_report.md` |
| 16 popmodels-molecules-diffuse | 2026-11-14 21:10 | done (no arms; no fold passes; task 10 stays waiting) | 2026-11-14 21:25 | `2026-11-14_16_popmodels-molecules-diffuse_report.md` |
| 17 random-order-baseline | 2026-11-14 22:11 | done (counts and shape within seed spread; lean and streaks gone; the new baseline) | 2026-11-14 22:35 | `2026-11-14_17_random-order-baseline_report.md` |
| 18 reply-open-questions-lehninger | 2026-11-14 22:11 | done (read; contacts consistent; used in step 3) | 2026-11-14 22:11 | none needed |
| 19 justins-answers-open-questions | 2026-11-14 22:11 | running (item 3 answered in report 17; items 1 and 2 in the step 3 and task 13 reports) | 2026-11-14 22:35 | `2026-11-14_17_random-order-baseline_report.md` |
| 20 buried-salt-bridges | 2026-11-14 22:11 | running (benchmarks checked in task 15 step 3) | 2026-11-14 22:11 | |

Correction (2026-11-14 17:30): the times for 06 and 07 first written here (20:12, 20:20, 20:26) were UTC, from a shell
clock without a time zone; they are now New York time (15:12, 15:20, 15:26).
