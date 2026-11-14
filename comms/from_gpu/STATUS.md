# Status of the GPU session's tasks

Written only by the GPU session (task 09); the cloud side reads it. One row per task in `comms/to_gpu/`. Times are New
York time. This is the summary; `comms/log/gpu.md` is the history. Rows for 01–05 are backfilled from the log and from
the commit times of the reports.

States: not started, running, waiting on Justin, done, closed (stopped by the task's own rule), superseded.

| Task | Started | State | Updated | Report |
|---|---|---|---|---|
| 01 hello | 2026-11-14 12:40 | done | 2026-11-14 12:40 | `2026-11-14_01_hello_report.md` |
| 02 lattice-fold | 2026-11-14 13:25 | running (GPU queue, `task02_fold3d_main` since 14:01) | 2026-11-14 14:45 | to come |
| 03 pop-dish-two-resources | 2026-11-14 13:25 | closed (no fold passed; task 05) | 2026-11-14 14:02 | `2026-11-14_03_pop-dish-two-resources_report.md` |
| 03a maps-at-cell-scale | 2026-11-14 13:25 | done (in report 03) | 2026-11-14 13:35 | `2026-11-14_03_pop-dish-two-resources_report.md` |
| 04 scheduled-checks | 2026-11-14 13:25 | done | 2026-11-14 13:21 | `2026-11-14_04_scheduled-checks_report.md` |
| 05 reply-to-reports-03-04 | 2026-11-14 14:21 | done (read; nothing to run) | 2026-11-14 14:21 | none needed |
| 06 store-fold-two-incomes | | not started (08 done; next check, as the queues allow) | 2026-11-14 14:45 | |
| 07 popdish-fine-two-resources | | not started (08 done; next check, as the queues allow) | 2026-11-14 14:45 | |
| 08 row-streaks-check | 2026-11-14 14:26 | done | 2026-11-14 14:45 | `2026-11-14_08_row-streaks-check_report.md` |
| 09 task-status | 2026-11-14 14:45 | done (this file) | 2026-11-14 14:45 | this file |
| 10 finer-blocks | | waiting on a passing fold (task 06 or later) | 2026-11-14 14:45 | |
