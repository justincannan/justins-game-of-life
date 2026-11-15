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
- 2026-11-14 19:10 (scheduled check): commits read fde11d5 (task 12b, beads), be9a909 (cloud check; reply 13).
  - **Task 12 step 1 done** (with 12a and 12b): `comms/from_gpu/2026-11-14_12_design_report.md`. All proposals; nothing
    built or run.
    - Five levels, each computed offline and folded into a few numbers: beads → 16 × 16 contact table (+ burial per
      monomer) → secondary (Zimm–Bragg-type rule, cheap enough for the page) → off-lattice tertiary fold with a
      many-body desolvation term for two-state melting → function from pockets.
    - Martini-style beads (Q, P, N, C with levels); ions as single Q beads, four kinds, screening through ionic
      strength (Debye length). No native structure is ever an input, so Martini's Gō/elastic-network limitation is
      not inherited.
    - Cost: cache by domain; a threading estimate in the page as a provisional value computed from the new sequence;
      exact folds in GPU batches between runs (estimated 0.5–5 s of GPU time per domain).
    - Sources checked online briefly: Martini 3 (Souza 2021), Kaya and Chan 2000, Taverna and Goldstein 2002,
      Miyazawa–Jernigan reviews. Others cited from notes, marked as not re-checked.
  - STATUS.md: 12, 12a, 12b waiting on Justin; 13 not started.
  - **Task 13 not started:** it comes after 12 step 1 by its own order; the harness measurement is next check's work.
  - Waits on Justin: the design report's six choices (section 9): the page's reaction rule (brackets or pockets); the
    monomer assignment; a cost for unfolded chains; four ion kinds; off-lattice or fcc lattice; domains as cache key
    with in-page threading. Still open from earlier: report 06 proposal 2; the scan-order fix (report 08); report 07's
    next step.
  - Waits on cloud: nothing.
- 2026-11-14 21:25 (scheduled check): commits read 76ef9c7 (reply 14), 46aeed6, 9f04e63 (tasks 15 and 16, Justin's
  approval), 1f4a805 (fold viewer), 4ba5198 (uneven spreading measured).
  - **Task 14** read: no prototype until approved (now approved by task 15). The "nine times" figure is dropped; in the
    new table, burial is about 2.3 times the pairwise term for oily monomers, as a readout.
  - **Task 15, steps 1 and 2 done; checks met** (report pushed; code in `beadfold/`).
    - Step 1: Martini-style beads → 16 × 16 table e_ab(T, I) and burial h_a(T). Contacts are 1–2.7 kT, about 50 times
      weaker than a C–C bond. Debye–Hückel screening halves the salt bridge near 0.17 M. Rows are distinct. The fit
      is good to 0.06 kJ/mol.
    - Measurement: complement pairs are the best partners for even monomers, not for odd ones (like attracts like).
      To be tested again in step 3's packed cores.
    - Step 2: Zimm–Bragg matrix exact against the closed form; cooperative with length; charge, salt and pH patterns
      as expected. One fix of my own strand-alternation factor (0.5 → 1.0), stated in the report.
    - **Step 3 (off-lattice folder on the GPU) starts next check.**
  - **Task 16 done** (report pushed).
    - The page's dish spreads molecules at D 0.24 (wetness measured 1.000): 0.96 places² a tick.
    - Correction: store2.py already spread its molecules (Dc 0.02, half the page's rate); only pop2_gpu.py did not.
    - With the page's rate: the fine grid shows no change (box dimension and roughness within 1–3%, no arms).
      Molecules are not limiting at the front (5–9% used by tick 2,000 at sugar 1 and 3).
    - The store fold still fails at sugar 1 and 3, so task 10 stays waiting.
  - **Task 13 not started:** task 15 took this visit by Justin's priority; next check, alongside step 3.
  - Waits on Justin: report 15, section 1.4 (odd complement pairs, informational until step 3). Still open: report 06
    proposal 2, the scan-order fix (report 08), report 07's next step.
  - Waits on cloud: nothing (report 15 asks for one Lehninger chapter 2 number check, optional).
- 2026-11-14 21:55 (interactive session): commits read 4ba5198, 147c9d1, 821a258 (random visiting order; task 17).
  - Task 17 is left for the 23:00 scheduled check, as Justin asked.
  - At Justin's request, the questions still open in the GPU reports are gathered in
    `comms/from_gpu/2026-11-14_open-questions.md`: odd complement pairs (report 15, section 1.4); report 06, proposal 2;
    report 07's next step; the optional Lehninger chapter 2 check. Report 08's scan-order question is closed by the
    21:23 decision.
  - Waits on Justin: the three questions in that file. Waits on cloud: the optional Lehninger check.
- 2026-11-14 22:11 (interactive session): commits read 54d2ee3 (reply 18), 35fc547, 6ec4867 (task 19, Justin's answers).
  **Started tasks 17, 13 and task 15 step 3 now, at Justin's request**, in this interactive session; the 23:00
  scheduled check should not start them again (it holds off: this session has the check's lock until it finishes).
  - 18 read: the contacts are consistent with Lehninger chapter 2; the buried salt bridge's size will be sourced or
    marked a proposal in step 3's report.
  - 19 read: odd complement pairs are reported explicitly in step 3; task 13's report says which of report 06's
    proposals its numbers support; after task 17, a view on whether a coarse population model can branch.
  - Waits on Justin: nothing new. Waits on cloud: nothing.
- 2026-11-14 22:35 (interactive session): **Task 17 done** (report pushed). The random-order page's dish, sugar 1, 3
  and 10, 12 seeds, against row order (a row-order control reproduces report 03 place for place).
  - Counts and shape (box dimension, roughness) within seed spread. Two small changes: fewer cells go still early, and
    sugar 10's crash is a little deeper.
  - The lean towards the top and the row streaks are gone. Seed spread is smaller at sugar 10.
  - Task 19 item 3 (proposal, in the report): a coarse block model cannot branch below its block size; a hybrid edge
    or a per-place model is suggested, with a cheap test to decide.
  - This is the new baseline for task 13 and later dish comparisons. Tasks 13 and 15 step 3 still running.
  - Waits on Justin: report 17's last section (proposal). Waits on cloud: nothing.
- 2026-11-14 22:40 (interactive session): **Task 13 done** (report pushed). Lineage-marked harness copies of the
  random-order page; the marks change nothing (9 of 9 runs identical to the unmarked page at every tick, and to task 17).
  - Parent–daughter income correlates (r 0.87–0.97), but a non-kin cell in the same square does almost as well. The
    place variance is 4–20 times the lineage variance; lineage similarity fades in 2–4 generations, with no trend.
  - Costs per cell do not rise with income: a flat 0.008 per active cell-tick (upkeep 0.0028 with the gene factor,
    plus the energy molecule's leak, minus the clamp), which accounts for the calibrated upkeep.
  - store2 re-run with the measured spread and drift: fails (sugar 1 dies out; no second wave at sugar 3). No sweep.
  - Task 19 item 2: the numbers support report 06's proposal 2 (income tied to the place), but with a flat cost, not
    a rising one. Not started.
  - Waits on Justin: whether to start proposal 2 (with a flat cost). Waits on cloud: nothing. Task 15 step 3 still
    running.
- 2026-11-15 00:05 (interactive session): **Task 15 step 3 built; its checks are not met** (report pushed with
  `beadfold/`). Step 4 waits, by task 15's rule.
  - Off-lattice one-bead chain on the GPU, with step 1's table and burial, step 2's local bias and the cooperative
    term. 0 of 80 page sequences, 0 of 30 random 32-mers and 0 of 2 designed sequences fold: compact, molten globules.
  - The search is not the cause: five-times-longer runs reach the same energies, and a Gō energy (as an instrument
    check only) folds the same chains two-state. The table is too weak (about 1.1 kT a contact; about 2 kT needed) and
    too unspecific (burial is 50–60% of the energy).
  - Against task 02: 2.0 folds within 1 kT of the lowest against 8.2 tied; no fold-based Tm.
  - Task 19 item 1: in random cores oily monomers prefer oily partners of similar size, not their complements, which
    meets Justin's condition, with caveats (the cores are molten).
  - Task 20: both salt-bridge benchmarks fail (a buried pair is 20–25 kT worse than an oily pair).
  - Cost 1.1–4.1 s GPU per run. About 90 minutes of GPU time.
  - Waits on Justin: report section 9's proposals (backbone H-bonds and a packing term for strength; an
    environment-dependent dielectric for specificity), and whether to adopt the oily-partner rule now. Also report 13:
    whether to start report 06's proposal 2 with a flat cost. Waits on cloud: nothing.
  - This session held the scheduled check's lock from 22:11 to 00:05, so the 23:00 check skipped.
- 2026-11-15 09:10 (scheduled check): commits read de2e333; task 21 (reply to reports 13, 15 step 3 and 17) read: nothing to run (no proposal started; task 15 step 4 waits; the oily-partner rule stands, to apply at the next contact-table revision); STATUS row 21 added. Waits on Justin: step 3 section 9 proposals; report 06 proposal 2 (flat cost); report 17 coarse-model question and the cheap per-cell-store test; the molten-core caveat on the oily-partner rule; waits on cloud: nothing.
