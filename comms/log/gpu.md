# GPU session log

Append-only, written only by the GPU session. Same form as `cloud.md`: time (America/New_York), commits read, what was
done, what waits on Justin or on the cloud session. Newest at the bottom.

- 2026-11-14 ~12:40 (backfill): cloned the repository (b07a990, 06117fd); Git for Windows installed with Justin's
  approval. Task 01: build checked (content identical; CRLF on Windows), machine described, sixth addendum reported.
  Pushed be8135a. Waits on Justin: nothing. Waits on cloud: nothing.
- 2026-11-14 13:25: commits read caee6ba, 95d45b9, 86e8dd4, 04c8e2c. **Started tasks 02, 03, 03a and 04.**
  - 02 (lattice folding): running on the GPU queue; report to come.
  - 03/03a: the repository's page gives the same dish as page 8 (sugar 1, seed 1, 2,000 ticks: identical). The harness
    now records molecules, their stored energy and reaction income per block, and full-resolution snapshots. The page
    runs are on the CPU queue.
  - 04: scheduled check set up in the Claude desktop app ("jgol-gpu-check", every two hours at odd hours 9:00–23:00 New
    York time). Report to come.
  - Waits on Justin: nothing. Waits on cloud: nothing.
- 2026-11-14 ~15:00: task 04 report pushed (74e78bd). **Task 03/03a report pushed.**
  - The page dendrites clearly at sugar 3, and it branches at 1 and 10.
  - Going still follows total income (0.49 against 0.28 for sugar alone).
  - The best fold, C2x, has sugar 1's regrowth and sugar 3's second wave, but misses sugar 10's crash. No version
    passes, so no sweep was run.
  - Task 02 is still running.
  - Waits on Justin: nothing. Waits on cloud: the next fold (the store fed by both incomes) is proposed, not started.
- 2026-11-14 14:21 (scheduled check): commits read 3b0837d (cloud log; reply 05). Task 05 read: task 03 closed, no
  proposal to start; nothing to do for it. Task 02 still running on the GPU queue (`task02_fold3d_main` since 14:01;
  speed, convergence, search and reproducibility results so far in `fold3d/results/`); `fold3d/` stays uncommitted
  until its report. No change otherwise. Waits on Justin: nothing new (the proposals in cloud.md stand). Waits on
  cloud: nothing.
- 2026-11-14 14:25 (scheduled check): commits read none new (head addef14). No new tasks; 01–05 all started or
  closed. Task 02 still running on the GPU queue (`task02_fold3d_main` since 14:01, in the melt stage after
  `repro_low.json` at 14:20; child process alive and using CPU, GPU at 99%); `fold3d/` stays uncommitted until its
  report. No change otherwise. Waits on Justin: nothing new (the proposals in cloud.md stand). Waits on cloud: nothing.
- 2026-11-14 14:45 (scheduled check, continued): commits read 5388b80 (tasks 06–09), 9d375a1 (task 10). Correction to
  the entry above: it was pushed before 5388b80 arrived, so "no new tasks" was wrong.
  - **08 done** (report pushed): the sugar-10 streaks are an update-order artefact. The page scans places row by row and
    draws down each 4 × 4 square's stores in place (the feeding loop and the birth scan in `step()`), so a square's
    first row goes still least, at every sugar level. Checked in harness-only page copies: transposing the scan turns
    the streaks vertical and random order removes them. The counts and the crash do not change beyond seed spread. The
    lopsided growth does not follow scan order. The page was not changed; a fix would be a proposal to Justin.
  - **09 done:** `comms/from_gpu/STATUS.md`, backfilled for 01–10.
  - 10: waiting on a passing fold (marked in STATUS.md).
  - 06, 07: not started; next check (they need new model code). Task 02 still running on the GPU queue (since 14:01).
  - Machine note: a CPU-queue job launched from Git Bash had `cmd /c` rewritten to `cmd C:/` (path conversion) and sat
    idle; it was stopped (my own job) and requeued from PowerShell. No other session's jobs were touched.
  - Waits on Justin: whether to make the page's scan order-free (proposal in report 08, section 5). Waits on cloud: nothing.
- 2026-11-14 14:50 (interactive session): **Task 02 done** (report pushed with `fold3d/`). The GPU job survived a brief
  disconnection of the D: drive and finished at 14:45. Headlines:
  - No unique native fold: the HP-style energy has many tied lowest-energy folds (8.4 per 10 runs).
  - Melting is gradual (Tm 0.43 ± 0.14).
  - The page's brackets show in 3D only through the complement energy (eP).
  - Batched folding with caching by sequence is feasible; live folding is not.
  - STATUS.md updated.
  - Waits on Justin: the folding proposals in report 02 (caching, a richer contact table, a cooperative term, eP ≥ 1).
  - Waits on cloud: nothing.
- 2026-11-14 20:27 (scheduled check): commits read none new (head 5791e72). Started 06 and 07, the two tasks not yet
  started.
  - **07 done** (report pushed): no branching at any sugar level (1, 3, 10) or sugar diffusion rate (0.025 down to
    0.0008).
    - The model is a two-resource `pop.py` at one cell per place (`popdish/pop2_gpu.py`), on a 1,000 × 1,000 plate and
      on the page's own plate size.
    - It grows as compact discs, with box dimension 1.7–1.9 against the page's 1.2–1.5, and overgrows at sugar 1 and 3.
    - Proposal: chemistry-paid births on non-diffusing molecules remove the diffusion limit. Without them, sugar 1 at
      the slowest diffusion matches the page's counts and dimension, but as a scatter, not arms.
    - One calibrated constant: a factor 6 on division attempts, fitted to sugar 10 at tick 100.
  - **06 started:** the spread of chemistry income per cell, measured from report 03's snapshots (sd of log income
    within a coarse square 0.4–0.6, at tick 100).
    - Heritability cannot be read from the snapshots: their per-place income over 100 ticks mixes occupants.
    - Fitting the per-lineage form properly needs per-cell income with lineage marks from the harness.
    - The fold itself is not yet built; next check.
  - STATUS.md updated.
  - Waits on Justin: nothing new (report 07, section 4, has a proposal for a next step if wanted). Waits on cloud:
    nothing.
- 2026-11-14 17:30 (scheduled check): commits read 79dc7d9 (cloud's reply 11).
  - **Correction (reply 11):** the entry headed "2026-11-14 20:27" above was UTC. It is 15:27 New York time. The bash
    clock here has no time zone, so New York times are now taken from Windows. STATUS.md is corrected too.
  - **06 closed** (report pushed): no version of the store fold fed by both incomes passes, so no sweep was run.
    - The fold is `popdish/store2.py`: 7 heritable income classes per square, chemistry and sugar into the store, and
      going still by the measured Hill form.
    - It reproduces sugar 10's crash (527 active against 631 at tick 500).
    - It fails at sugar 1 (too few active cells) and at sugar 3 (too fast early; no second wave).
    - Measurement: the fold selects high-income lineages (mean rate ×1.5–2.4), while the page's income per active
      cell stays flat. Heritability and cost are the missing measurements (proposal in report section 4).
    - Two constants were calibrated (upk 0.008, grow 0.5).
  - Task 10 stays waiting (no passing fold). STATUS.md updated (rows 06, 10, 11).
  - Waits on Justin: report 06's proposals (lineage-marked income measurement in harness copies, or a place-tied
    income with rising cost). Waits on cloud: nothing.
- 2026-11-14 17:40 (same check, after the push): commits read 8b80cc4, 91ba2d2, 78cefd5 (tasks 12 and 12a, which
  arrived while this check ran). They are not started. Task 12 step 1 is a long design report with sources checked, so
  I have left it for the next check rather than rush it. Waits on Justin: nothing new. Waits on cloud: nothing.
