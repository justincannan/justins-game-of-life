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
| 22 population-scale-rethought | 2026-11-15 11:10 | item 1 done (mostly mutation at division, 4–6% of daughters; contagion about a sixth at sugar 3 and 10; report 13's 13% was mostly a measuring error, corrected); item 2 done (the per-cell-store model branches; gliding only while coated is decisive, sugar-paid births next, store-based going still not needed for shape; the model undergrows the page); item 3 waits on Justin seeing item 2 | 2026-11-15 13:45 | `2026-11-15_22_population-scale-rethought_report.md` (items 1 and 2) |
| 23 two-beads | 2026-11-15 11:40 | answered by task 26 (proposals 1, 2, 3, 5 approved) | 2026-11-15 16:10 | `2026-11-15_23_two-beads_report.md` |
| 24 emulators | | waiting (starts after task 23's folder meets its checks and task 22's per-cell model exists) | 2026-11-15 13:45 | |
| 25 refused-contagion-fix | 2026-11-15 15:10 | done (refused-but-rewritten splices: 82–83% cannot pay, the rest same compound; on the fixed page every cannot-pay refusal restores the program; dish counts unchanged within seed spread, 12 seeds; only report 22 item 1's refused column superseded); the same-compound case waits on Justin | 2026-11-15 15:35 | `2026-11-15_25_refused-contagion-fix_report.md` |
| 26 folding-proposals-approved | 2026-11-15 23:10 | waiting on Justin (step 1 with task 27 met, two near-misses; step 2 fails: no single constant gives graded Zimm–Bragg helix content, helices switch all-or-none within about 1 kT; step 3 partly met: relaxed gaps positive for 35 of 45, but blind folds beat the target for 41 of 45, none folds to its target; step 5 not run, waits on the helix term; options in the report) | 2026-11-16 12:50 | `2026-11-15_26_folding-proposals-approved_report.md` |
| 27 charge-dipole | 2026-11-16 08:55 | done (`elec='cd'`, μ 0.085 e·nm; benchmark B met in a polar pocket, costly in an oily one; benchmark A 2.9 kT against > 3 in one polar case, for Justin to accept or not) | 2026-11-16 12:50 | in report 26 |
| 28 population-model-start | 2026-11-16 08:55 | waiting on Justin (step 1: the per-cell-store model's chemistry income was the wrong rule; running the page's own reaction, it grows like the page at sugar 3 to tick 1,000, branching verdict and ranking hold; step 2: the new population model gives only compact discs at the sourced diffusion length, no DLA-like, dense-branching or ring regions; choices for Justin in the report) | 2026-11-16 13:20 | `2026-11-16_28_population-model-start_report.md` |
| 29 stage1-baseline-and-vent-founding | 2026-11-16 08:55 | done; proposal 1 (chemotroph gene for the vent founder) approved by Justin 2026-11-16 12:05, page change for the cloud session; the two bug fixes wait on Justin (dish unchanged from report 17 except 4 seeds whose founder line gets a gene marker from `dishSetup`, a page bug; multi-gene share 33–34% by tick 2,000 at sugar 1 and 3; one-organism vent founding was about 1 in 4 until 581c90e, 0 of 70 since, because `pigFounder` skips the vent; the "6 of 6" was a soup start; second bug: coat arrays not resized; the chemotroph founder gene founded 20 of 20 in the harness) | 2026-11-16 12:05 | `2026-11-16_29_stage1-baseline-and-vent-founding_report.md` |
| 30 repeatable-runs | 2026-11-16 15:10 | done (notice read; harnesses now seed through `P.seed`, task 33's `vent33.js` first; same-seed runs from separate page loads identical at all 104 recorded ticks) | 2026-11-16 15:40 | in report 33 |
| 31 modern-founder-models | 2026-11-16 15:20 | waiting on Justin (designs for parts 3–5 written, proposals only; nothing built; order proposed 5, 3, 4; open questions in the report) | 2026-11-16 15:40 | `2026-11-16_31_modern-founder-models_report.md` |
| 32 population-runs-on-gpu | 2026-11-16 15:10 | done (task 22's runs on the GPU 9–17× faster; not seed-for-seed identical, statistically matching: 32 of 734 comparisons with abs z > 2) | 2026-11-16 15:40 | `2026-11-16_32_population-runs-on-gpu_report.md` |
| 33 vent-founder-in-page | 2026-11-16 15:10 | done (page 4e413e2: founded 30 of 30 at 1,000 ticks, 10 of 10 with domCost 0; 10 of 10 survive to 6,000 ticks, no NaN energy; dish seeds 2, 3, 4, 6 not re-run) | 2026-11-16 15:50 | `2026-11-16_33_vent-founder-in-page_report.md` |

Correction (2026-11-14 17:30): the times for 06 and 07 first written here (20:12, 20:20, 20:26) were UTC, from a shell
clock without a time zone; they are now New York time (15:12, 15:20, 15:26).
