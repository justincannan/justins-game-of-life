# Cloud session log

Append-only. One entry per visit: the time (America/New_York), the commits read, what was done, and what waits on
Justin. Newest at the bottom.

- 2026-11-14 12:20: repository started (b07a990, 06117fd). Task 01 sent.
- 2026-11-14 12:55: read report 01 and the sixth addendum's report. Fixed the gliding comment and the CRLF build. Sent task 02 (3D lattice folding).
- 2026-11-14 12:58: sent task 03 (two-resource population dish), Justin's decision.
- 2026-11-14 13:13: sent task 03a (cell-scale maps), after Justin's comment that block maps hide the dendrites.
- 2026-11-14 13:20: set up the logs and the scheduled checks (task 04 for the GPU side).
- 2026-11-14 14:05 (scheduled check): commits read 94a2f45, 74e78bd, 50b6a7d (GPU log, report 04, report 03/03a).
  - Report 04: the GPU-side check "jgol-gpu-check" runs at odd hours 9:00–23:00 New York time from 15:00 today, with a
    lock file; Justin can pause or delete it under Scheduled in the desktop app.
  - Report 03/03a: crowding mostly does not explain the sugar-10 crash; the crash itself sends nearly every cell still,
    and the molecules never wake them. Going still follows total income (deviance explained 0.49 against 0.28). No
    fold passes (best C2x misses sugar 10's crash by 15–20×), so no sweep, as task 03 says. At one pixel per place the
    page branches: clear dendrites at sugar 3, thin branches regrowing at sugar 1, a mass of fine branches at sugar 10.
    Horizontal streaks at sugar 10 from tick 500 look like a row-update artefact (GPU's proposal; visible in
    `03a_dish_sugar10.png`). Not fixed: changing the update order changes the model by design.
  - Sent `comms/to_gpu/2026-11-14_05_reply-to-reports-03-04.md`: task 03 closed; no proposal started; carry on with 02.
  - **Waits on Justin:**
    1. Whether to try the GPU's next fold: the store fed by sugar and chemistry income, with income per lineage.
    2. Whether to run a two-resource `popdish/pop.py` at 1,000 × 1,000 with slow sugar diffusion (a cheaper test of
       whether branching appears on a fine grid).
    3. Whether to check the sugar-10 horizontal streaks as a possible update-order artefact.
    4. Run "jgol-gpu-check" once with "Run now" while at the GPU machine, so permission prompts are answered once.
    5. Whether tasks should get a "started" status line or file (GPU's proposal).
- 2026-11-14 14:35 (in session with Justin): read addef14 (GPU log: task 05 read, task 02 running).
  - Justin set the GPU-side check's permission mode to Auto (item 4).
  - **Justin approved all five waiting items.** Recorded in THEORY_NOTES.md. Sent tasks 06 (store fold fed by both
    incomes, income per lineage), 07 (two-resource `pop.py` at 1,000 × 1,000 with slow sugar diffusion), 08 (check
    the sugar-10 streaks; no change to the page), 09 (`comms/from_gpu/STATUS.md`). Added STATUS.md to
    comms/README.md.
  - Waits on Justin: nothing new. The finer-block models stay a proposal for once a fold passes.
- 2026-11-14 14:45 (in session with Justin): **Justin approved the finer-block models** (5 × 5, 2 × 2) on the GPU
  session's condition: only once a fold passes at 10 × 10. Recorded in THEORY_NOTES.md; sent task 10.
  Waits on Justin: nothing.
- 2026-11-14 16:05 (scheduled check): commits read 9d375a1 (mine), c56deaa, 32325f2 (report 08, STATUS.md), 5791e72
  (report 02, `fold3d/`), a3462b8 (report 07, task 06 started).
  - Report 08: the sugar-10 streaks are an update-order artefact. The feeding loop and the birth scan in `step()` visit
    places row by row and draw each 4 × 4 square's stores in place, so a square's first row goes still least (at every
    sugar level). Transposed scan turns the streaks vertical; random order removes them. Counts and the crash are
    unchanged within seed spread; the lopsided growth does not follow scan order. Page not changed.
  - Report 02: `fold3d/` folds page sequences on a 3D lattice on the GPU. No unique native fold (about 8 tied
    lowest-energy folds per 10 runs); melting gradual (Tm 0.43 ± 0.14, none abrupt); the page's brackets become 3D
    contacts only through the complement term (76% against 28%). Folding live in the page is not feasible; caching is.
  - Report 07: the two-resource population model at one cell per place grows compact discs at every sugar level and
    diffusion rate (box dimension 1.7–1.9 against the page's 1.2–1.5). No branching. GPU's reading: chemistry-paid
    births on non-diffusing molecules remove the diffusion limit.
  - Task 06 running (income spread measured; fold not yet built).
  - GPU's STATUS.md and log times for 06/07 look like UTC labelled as New York; asked for a correction.
  - Sent `comms/to_gpu/2026-11-14_11_reply-to-reports-02-07-08.md`: 02, 07, 08 received; no proposal started; carry on
    with 06; fix the times. No code fixed (none reported).
  - **Waits on Justin:**
    1. Report 08: whether to make the page's scan order-free in those two loops (random order with the page's seeded
       rng, or a square's store split among its claimants). Changes the model.
    2. Report 02's folding proposals: fold offline and cache by sequence; reduce tied folds (16 × 16 contact table or
       a tie-break); a cooperative term for abrupt melting; keep eP ≥ 1.
    3. Report 07's next step: sugar per place, gliding limited by coat, chemistry income per lineage in the
       fine-grid model.
    4. Whether the cloud side should now build the Tier 1 3D viewer (already approved) using `fold3d/sample_folds.json`
       in an interactive session.
- 2026-11-14 17:20 (in session with Justin): Justin decided:
  - task 02's problems need a rebuild;
  - secondary and tertiary structure are modelled separately, with quaternary later;
  - ions as well as molecules;
  - the division of labour (cloud: queued features and lighter work; GPU: ground-up models).
  Recorded in THEORY_NOTES.md and CLAUDE.md. Sent task 12 (a design report first, no prototype until Justin approves).
  Waits on Justin: the agar proposal (food dissolved and diffusing; inert gel unless digested); the scan-order fix
  (report 08).
- 2026-11-14 17:25 (in session with Justin): Justin decided the open-and-fold rule across scales (model fine detail when evolution needs it, then fold into parameters). THEORY_NOTES.md; sent 12a (addition to task 12).
- 2026-11-14 17:30 (in session with Justin): Justin approved the agar correction and the cloud queue (viewer, uneven spreading). Bead proposal recorded, awaiting his decision.
- 2026-11-14 17:40 (in session with Justin): Justin approved beads. Sent 12b, with the caveat that Martini does not fold proteins.
- 2026-11-14 18:05 (scheduled check): commits read ad38c88 (report 06, STATUS times corrected), 01b4002 (GPU log:
  tasks 12 and 12a read, design report left for its next check). Tasks 12, 12a, 12b not yet started on the GPU side.
  - Report 06: no version of the store fold fed by both incomes passes, so no sweep. Best version (u8g5) reproduces
    sugar 10's crash for the first time (527 active against the page's 631 at tick 500; shape matches at sugar 10),
    but fails at sugar 1 (too few active cells, spreads too far) and sugar 3 (too fast early, no second wave).
    Measurement: the fold selects high-income lineages (mean rate ×1.5–2.4), while the page's income per active cell
    stays flat (about 0.005–0.006). Without heritability the colony dies out at sugar 1. Calibrated upkeep is about
    3× the page's coded value. Missing: heritability, drift and cost of chemistry income.
  - The UTC times in STATUS.md and the GPU log are corrected (reply 11's request): done.
  - Sent `comms/to_gpu/2026-11-14_13_reply-to-report-06.md`: measure per-cell chemistry income with lineage marks
    in harness copies (heritability, drift, place against lineage, costs), within task 06 as approved and reply 11;
    then one re-run of the same per-lineage fold with measured constants. After task 12 step 1. Proposal 2 (income
    tied to the place) not started. No code fixed (none reported).
  - **Waits on Justin:**
    1. Report 06 proposal 2: a fold where chemistry income belongs to the place, not the lineage, with a cost rising
       with income. A different form from the one he approved.
    2. Still open from earlier: the scan-order fix (report 08); report 02's folding proposals, now likely folded into
       task 12's rebuild; report 07's next step.
- 2026-11-14 20:05 (scheduled check): commit read dcdcbe1 (task 12 design report with 12a and 12b; STATUS rows 12–13;
  GPU log).
  - Report 12 (all proposals, nothing built): five levels each computed offline and folded into numbers for the page:
    Martini-style beads → 16 × 16 contact table + burial → helix–coil (Zimm–Bragg) secondary rule run in the page →
    off-lattice tertiary fold with a many-body desolvation term (for two-state melting), no native ever given →
    function from pockets. Ions as four single charged beads entering through ionic strength. Cost: cache by domain,
    in-page threading estimate as a provisional value, exact folds in GPU batches (estimated 1.5–15 GPU hours per
    10^4 domains).
  - Spot-checked the Debye/Bjerrum numbers and three citations: correct.
  - Sent `comms/to_gpu/2026-11-14_14_reply-to-report-12.md`: received; no prototype until Justin approves; task 13 is
    next by its order. No code fixed (none reported).
  - **Waits on Justin:**
    1. Report 12's six choices: (1) reaction rule: replace brackets with pocket function, or keep brackets (proposal:
       replace in steps, stability first); (2) monomer assignment keeping odd = oily and complement pairs, or free;
       (3) a cost for unfolded chains; (4) four ion kinds, inside = outside until pumps; (5) off-lattice or fcc
       lattice; (6) domains as cache key with in-page threading. And whether to start the prototype (section 11).
    2. Still open: report 06 proposal 2 (place-tied income); the scan-order fix (report 08); report 07's next step.
- 2026-11-14 21:00 (in session with Justin): before building the agar correction, found its premise wrong for the page (the page's molecules and sugar diffuse; only the population models' do not). Not built; asked Justin. Read report 06 and the task 12 design report (six choices wait on Justin).
- 2026-11-14 21:05 (in session with Justin): Justin approved (1) the agar fix in the population models and (2) all six choices of the task 12 design. Sent tasks 15 (build the prototype, in the report's order) and 16 (molecules spread in the population models). Lehninger chapter 2 received (not in the repository).
- 2026-11-14 21:25 (in session with Justin): built the Tier 1 fold viewer (tools/env.js, fvShow): the inspector draws the inspected cell's chain in 3D from its brackets; tested headless (10-monomer cell, 4 pairs).
- 2026-11-14 21:45 (in session with Justin): measured the uneven spreading. The colony leans towards the top in 41 of 44 runs; reversing the two row-ordered loops removes the lean. Recorded in THEORY_NOTES.md (supersedes report 08 section 4); test/dish_asym.py. Waits on Justin: random visiting order.
- 2026-11-14 22:00 (in session with Justin): Justin decided on random visiting order; built (visitOrder, tiled), lean gone (5 of 14), even world +14% time. Sent task 17 (re-baseline the dish). Tasks 15 and 16 were sent at 21:05.
- 2026-11-14 22:10 (in session with Justin): answered the open-questions file, item 4 (Lehninger chapter 2 numbers against report 15's contacts: consistent; buried salt bridge plausible in sign). Sent 18. Items 1–3 are with Justin.
- 2026-11-14 22:02 (scheduled check): no change
- 2026-11-14 22:10 (in session with Justin): Justin agreed to all three suggestions on the open questions (wait for step 3; wait for task 13; set aside report 07's next step). Sent 19; THEORY_NOTES.md.
- 2026-11-14 22:20 (in session with Justin): found sources on buried salt bridges at Justin's request; sent 20 (benchmarks for step 3; heat route as a proposal).
- 2026-11-15 08:05 (scheduled check): commits read 549a75d (GPU log), 04d044a (report 17), 2bc0d20 (report 13),
  11e1790 (task 15 step 3 report, `beadfold/`).
  - Report 17: on the random-order page the dish's counts and shape stay within seed spread; fewer cells go still
    early, sugar 10 crashes a little deeper; the lean and row streaks are gone. New baseline. Task 19.3 view
    (proposal): a coarse block model cannot show the branches (arms are narrower than a block); options are a hybrid
    edge or a per-place model; a cheap test is suggested.
  - Report 13: chemistry income belongs mostly to the place (place variance 4–20× lineage); lineage similarity fades
    in 2–4 generations; running costs flat at 0.008 per active cell-tick (upkeep + leak − clamp). store2 with measured
    constants fails. Numbers support report 06 proposal 2, with a flat cost.
  - Step 3: folder built and checked (Gō instrument check folds two-state), but nothing folds with step 1's table
    (too weak, about 1.1 kT a contact against about 2 needed; too unspecific, burial 50–60%). Both salt-bridge
    benchmarks fail. Oily monomers prefer oily partners, not complements (in molten cores). Step 4 waits.
  - Sent `comms/to_gpu/2026-11-15_21_reply-to-reports-13-15s3-17.md`: received; no proposal started; step 4 waits;
    under Justin's conditional decision (task 19.1) the oily-partner rule stands, applied when the table is next
    revised. No code fixed (none reported).
  - **Waits on Justin:**
    1. Step 3 section 9: which to build before repeating step 3 — backbone H-bonds and packing (strength), a buried-pair
       dielectric (specificity), two beads per monomer (changes the approved one-bead level).
    2. Report 13: whether to start report 06 proposal 2 (place-tied income, flat cost).
    3. Report 17: whether the plan to move default worlds to the population scale needs rethinking (coarse models
       cannot branch); whether to run the cheap per-cell-store test.
    4. Odd complement pairs: adopted under his condition; the caveat (molten cores) is his to weigh.
    5. Still open: none of the earlier items beyond these.
- 2026-11-15 10:02 (scheduled check): commits read a7b2398 (GPU scheduled check: task 21 read, nothing to run; STATUS
  row 21). An acknowledgement only; no question, report or bug. No reply sent; no code changed.
  - **Waits on Justin:** unchanged from the 08:05 entry (step 3 section 9; report 06 proposal 2 with flat cost;
    report 17 coarse-model question and per-cell-store test; the molten-core caveat on odd complement pairs).
- 2026-11-15 10:50 (in session with Justin): Justin agreed to rethink the population scale (fold per-cell rules; check against Matsushita's morphology diagram; drop fitting the page's dendrites) and to split the code-change rate (Drake's rule). Sent 22. Folding (step 3, section 9) under discussion.
- 2026-11-15 11:35 (in session with Justin): Justin chose two beads per monomer (D) and recorded slow fold evolution as a test. Sent 23 (two beads, H-bonds, packing, core dielectric, the design test).
- 2026-11-15 11:40 (in session with Justin): Justin approved emulators between levels; sent 24 (queued after 23 and 22). Reviewing the full queue with Justin.
- 2026-11-15 12:05 (scheduled check): commits read ecc770f (task 22 item 1 report), e0c288f (GPU log: task 23 and task
  22 item 2 started; 24 waits).
  - Report 22 item 1: report 13's 13% was mostly a measuring error (corrected 2.6–3.5%). Per division 4–6% of
    daughters carry a different program, nearly all mutation at division; contagion adds about a sixth at sugar 3 and
    10; fragment uptake and silencing none. Sequence events per genome per division 0.09–0.11, 30–40× Drake's 0.003.
    Report 13's other conclusions hold.
  - **Fixed a page bug** (report 22 section 6): a contagion refused because the cell cannot pay (`swapChem`) left the
    cell with its old compound but the new sequence and program. Now undone, as uptake does (`seqTransferUndo` in
    tools/env.js; one rep in tools/patch.py). Rebuilt; `node --check` passes; loads headless without errors.
  - Sent `comms/to_gpu/2026-11-15_25_refused-contagion-fix.md`: the fix; split the refused cases by cause; re-run item 1
    at sugar 3 and 10 on the rebuilt page; mark superseded results.
  - **Waits on Justin:**
    1. Contagion that changes the sequence and program but not the compound (`g === ngen[j]`): kept but not counted
       as a write. Undo it, keep it, or keep and count it?
    2. The copy-error rate is 30–40× Drake's rule (report 22 section 3). Whether to lower it is his (no proposal
       started).
    3. Still open: the molten-core caveat on the oily-partner rule.
- 2026-11-15 14:30 (in session with Justin): built the cloud queue: hot-springs source zone, pond inflow, pigment-dependent light (default off; Justin's decision on sunlit starts), viruses (on; epidemics arise in the vent world). Vent founding found weak (2 of 7 seeds) independent of these changes. THEORY_NOTES.md.
- 2026-11-15 14:05 (scheduled check): commits read 29c9abc (task 22 item 2 report, figures, STATUS rows 22–24, GPU log);
  7ce4942 is this side's own.
  - Report 22 item 2 (report 17's cheap test): task 07's fine-grid model **branches** once gliding is tied to coat
    and births are paid from the store or the daughter's square of sugar: thin arms 2.5 places wide at sugar 3 (page
    2.9–3.2), a branched front at sugar 10. Gliding only while coated matters most (page measured at 0.0003–0.009
    glides per active cell-tick, 10–300× below task 07's 0.1); sugar-paid births next; going still by the store does
    not decide shape. Caveat: the model grows at 0.5–0.7× the page's births per cell, which may help branching.
  - Page facts measured: sugar and molecules spread only every second tick, so report 16's rates halve (0.4, 0.48).
    This is the page's design (`(tick & 1) === 0` block in tools/patch.py), not a bug; no code changed.
  - No reply sent: item 3 waits on Justin seeing item 2 (task 22's order). Task 23 still running; 24 and 25 queued.
  - **Waits on Justin:**
    1. Report 22 item 2: seen, and whether to start item 3 (the new population model).
    2. Report 22 item 2 section 5 proposal: first raise the model's birth rate towards the page's (no shape fitting)
       and check the arms survive. Not started.
    3. Still open from 12:05: contagion with `g === ngen[j]` (undo, keep, or keep and count); the copy-error rate
       30–40× Drake's rule; the molten-core caveat on the oily-partner rule.
- 2026-11-15 16:05 (scheduled check): commits read f3d84ea (task 25 report, STATUS row 25, GPU log).
  - Report 25: report 22's "refused but program rewritten" splices are 82–83% "cannot pay", the rest "same compound".
    On the fixed page (34189b0) every cannot-pay refusal restores the program (38 of 38, 235 of 235), so the 12:05
    fix works. Report 17's dish counts do not move beyond seed spread (12 seeds a side; 1 of 84 |z| > 2). Only report
    22 item 1's refused column is superseded; its headline and report 17 stand. The GPU also corrected task 25's
    wording: at sugar 3, 76 splices were refused, not 207.
  - No reply sent (no question for this side, no bug); no code changed. Task 23 still running; 24 queued.
  - **Waits on Justin:**
    1. Contagion with `g === ngen[j]` (same compound): undo, keep, or keep and count. Now measured at 16 and 39
       program-changing splices in 3 seeds (sugar 3 and 10); the GPU can re-check any change in about 5 minutes.
    2. Report 22 item 2: seen, and whether to start item 3 (the new population model); its section 5 proposal (raise
       the model's birth rate towards the page's first).
    3. Still open: the copy-error rate 30–40× Drake's rule; the molten-core caveat on the oily-partner rule.
- 2026-11-15 18:05 (scheduled check): commits read e8e86b9 (task 23 report, `beadfold/` two-bead code and results,
  figures, STATUS, GPU log), c974bda (GPU scheduled check, no change).
  - Report 23 (two beads per monomer): stage 1 mostly met (backbone H-bonds 1.5 kT, packing by size in Eriksson's
    range, ε_core 6; both of task 20's salt-bridge benchmarks pass; helical Gō targets fold, the sheet barely). Short:
    single helices reach about half of step 2's Zimm–Bragg content. Stage 2, the design test Justin set: **fails**;
    none of 17 sequences folds uniquely or melts two-state, and blind folds find other structures a median 20 kT
    lower than the relaxed target (the energy, not the search). Stage 3: 0 of 80 page and 0 of 20 random sequences
    fold, though the gap to the next fold doubles. Buried charges now pair, but clusters of pairs dominate the energy.
    Oily-partner rule holds (no complement preference). Stage 4: no foldable sequence within 8 mutations. Cost
    2.7–2.8× one bead. Task 24 (emulators) waits on its condition (no folder meets its checks).
  - No reply sent: the GPU asks nothing of this side, and the next step (which of the report's proposals to build) is
    Justin's. No bug reported; no code changed.
  - **Waits on Justin:**
    1. Report 23 section 5 proposals: (a) charge clusters, by a many-charge desolvation term or a higher effective ε
       for charge pairs; (b) a better helix term (wider window, or a cooperative Zimm–Bragg term); (c) a design loop
       with relaxed decoys; (d) strand pairing; (e) then the design test again before step 3. Which, if any, to start.
       Step 4 and task 24 wait on a folder that passes.
    2. Still open: contagion with `g === ngen[j]` (undo, keep, or keep and count); report 22 item 2 seen and whether
       to start item 3 (and its birth-rate proposal); the copy-error rate 30–40× Drake's rule; the molten-core caveat.
- 2026-11-15 20:02 (scheduled check): commits read 33c6b3c (GPU scheduled check, no change). No change; nothing sent.
  Waits on Justin unchanged from 18:05.
- 2026-11-15 21:35 (in session with Justin): Justin approved task 23's proposals 1, 2, 3 and 5 (4 after if needed); sent 26 (charges: self term at low ε plus charge–charge at ε about 20, per Schutz–Warshel). Copying errors kept for now. Pigments under discussion.
- 2026-11-15 22:02 (scheduled check): no change (only e5dec07, the GPU's 21:09 no-change check; task 26 not yet picked up).
- 2026-11-15 23:00 (in session with Justin): pigments on with a pigment-carrying founder (option b) and inherited pigment; the decay economy built (remains broken down by heterotrophs). Pond stays phototroph-dominated; springs mix. THEORY_NOTES.md.
- 2026-11-15 22:45 (in session with Justin): Justin decided to move from one chain per cell to a genome of genes (stages: several genes; expression levels; storage separate from function). Recorded in THEORY_NOTES.md; the cloud session drafts the stage 1 design.
- 2026-11-15 23:30 (in session with Justin): drafted design/genome_stage1.md (stage 1: genes per cell); six questions wait on Justin.
- 2026-11-16 01:30 (in session with Justin): stage 1 of the genome built (genes by runs of 4, 8 reactions, gene dup/loss/transfer, virus integration, 256). Measurements in THEORY_NOTES.md. Found vent founding 0 of 10 on old and new pages.
- 2026-11-16 00:25 (in session with Justin): Justin agreed: charge–dipole term (27), task 22 item 3 starts with the birth-rate raise (28), stage-1 dish re-baseline and vent founding investigation (29), same-compound contagion kept and counted (cloud).
- 2026-11-16 00:45 (in session with Justin): same-compound contagion kept and counted (sameCompN; 1,691 by tick 600 in the even world); the fold viewer folds each gene separately and greys the markers. Sent 27, 28, 29.
- 2026-11-16 08:04 (scheduled check): no change (no GPU commits since c4750dd, report 26 step 1, already answered by task 27; tasks 27–29 not yet picked up).

## 16 Nov ~09:20 (interactive)
- Built: inspector gene list (geneListHtml), summary "Genes:" line. Rebuilt, syntax-checked.
- Measured 6,000-tick gene runs, even and vent (THEORY_NOTES "Following the genes"). test/genes_long.py.
- For GPU (task 29): same seed gave different counts at tick 1,000 across runs; stop the page before seeding.
- 2026-11-16 10:03 (scheduled check): commits read cb09f03 (GPU log: tasks 26 steps 2–3, 27, 28 and 29 started in
  Justin's interactive GPU session) and 59de2db (this side's 09:20 work). No report yet; the GPU asks nothing. Nothing
  sent; no code changed.
  - **Waits on Justin:** nothing new. Design questions on the genome's stage 1 (design/genome_stage1.md) as before.
  - Correction to the line above: stage 1 is built (01:30 entry), so its design questions are not open; nothing waits on Justin from this check.

## 16 Nov ~11:30 (interactive)
- Built: P.seed repeatable runs (+ reset leftovers fixed, incl. free chains), P.domCost .001, gene origin tags, reaction
  share fix. Measured: 6,000-tick gene runs with and without cost; tick timing. THEORY_NOTES "Built: repeatable runs…".
- New GPU tasks: 30 (repeatable runs, notice for 29), 31 (modern-founder detailed models, designs first), 32
  (population runs on the GPU, low priority).
- 2026-11-16 12:02 (scheduled check): commits read 83cc4ae (GPU: task 29 report,
  `from_gpu/2026-11-16_29_stage1-baseline-and-vent-founding_report.md`, with `29_*.png`, STATUS rows 26–29, log).
  - Report 29 in short: the dish matches report 17 for one-gene founders; seeds 2, 3, 4, 6 differ because `dishSetup`
    appends `15 7` after a founder ending `15 15 15`, making a run of four (a gene marker). Multi-gene share 33–34% by
    tick 2,000 at sugar 1 and 3, about 18% at sugar 10. One-organism vent founding was about 1 in 4 until 581c90e, 0 of
    70 since (`pigFounder` skips the vent); the earlier "6 of 6" was a soup start. Proposal: a chemotroph founder gene
    (20 of 20 in the harness).
  - **Fixed (clear bug, no design change):** the coat arrays (`coatS`, `coatM`, `coatK`) were not resized by
    `allocWorld`, so after the window grew, `pigOf` read past their end, light went NaN and cells died.
    `tools/newblock3.js` `allocWorld` now calls `coatAlloc()` when they exist (they are cleared, as `coat` already
    is on resize). Rebuilt; `node --check` passes; headless check: 800×500 → 1400×900, arrays follow N, no page error.
    The GPU harness's `coatFix` option is no longer needed on pages from this commit on.
  - Not fixed: the `dishSetup` marker bug. Several fixes are possible (pair at the front, behind its own marker, or
    `seqFromGen` changed), and each changes the affected founders differently, so the choice is Justin's.
  - Nothing sent to the GPU: it asks nothing of this side; the re-run of seeds 2, 3, 4, 6 follows the dish fix.
  - **Waits on Justin:**
    1. Report 29 proposal 1: a chemotroph gene for the vent founder (or another route) — vent one-organism founding
       is 0 of 70 on current pages.
    2. The `dishSetup` fix and which form (report 29 section 3); then the GPU's 5-minute re-run of seeds 2, 3, 4, 6.

## 16 Nov ~14:00 (interactive)
- Justin's decisions 12:09 built: chemotroph vent founder (20/20), dish pair fix, coat fix kept. GPU task 33.
- Found and fixed: one-organism runs not repeatable (divT/divTgt, hopm, ccId leftovers); virus copying drove the ground
  negative → NaN → whole-clump deaths (the vent die-outs). Six vent runs now survive to 6,000.
- r/m counters (RM) in the summary. THEORY_NOTES "The vent die-outs were a bug…".
- 2026-11-16 14:03 (scheduled check): commits read d4ae12c (GPU: task 27 and task 26 steps 2–3, sections added to
  `from_gpu/2026-11-15_26_folding-proposals-approved_report.md`, `26_helix.png`, `26_design.png`, `beadfold/`) and
  c4eab25 (GPU: task 28 report, `from_gpu/2026-11-16_28_population-model-start_report.md`, `28_*.png`); STATUS rows
  26–28; GPU log 12:50 and 13:20. (8be1cc6 is this side's 14:00 work.)
  - Report 26/27 in short: the charge–dipole term meets benchmark B in a polar pocket and stays costly in an oily one;
    benchmark A 2.9 kT against > 3. Step 2 fails: no single constant gives graded Zimm–Bragg helix content (helices
    switch all-or-none within about 1 kT). Step 3: relaxed gaps positive for 35 of 45, but none of 45 folds to its
    target. Step 5 not run (waits on the helix term, task 26's order).
  - Report 28 in short: the per-cell-store model, given the page's own reaction for income, grows like the page at
    sugar 3 to tick 1,000 (gliding still 3–15× low). The new population model gives only compact discs at the sourced
    diffusion length; none of Matsushita's branched or ring regions. The sucrose diffusion value came from a search
    snippet and should be checked.
  - Nothing sent to the GPU: it asks nothing of this side, every open choice is Justin's, and task 33 (vent founder
    re-measure) is already queued. No code changed.
  - Note: the GPU log still lists report 29's `dishSetup` fix as waiting; Justin decided it at 12:09 and it is built
    (34eceaf). Settled.
  - **Waits on Justin:**
    1. Report 26: the helix term (options a–d; Claude's proposal is a, a softer single-distance H-bond window,
       untested). Step 5 waits on it.
    2. Report 26: accept step 1's two near-misses or not (benchmark A 2.9 kT; ε_self 5 chosen because 4 misses B).
    3. Report 28: the population model's next ingredient (page's reaction and coat as a second income, one nutrient as
       in the experiments, or another way).
    4. Report 28: revisit the model's scale (plate size, colony thickness, upkeep of still cells)?
    5. Report 28: re-measure step 1's findings (income set by product inhibition; payChem refusing 60–90% of births)
       on the stage-1 page?
- 2026-11-16 16:02 (scheduled check): commit read 8f56892 (GPU: reports 31, 32, 33; STATUS rows 30–33; GPU log 15:50).
  - Report 33 (vent founder on page 4e413e2): founded 30 of 30 (10 of 10 with domCost 0); 10 of 10 survive to 6,000
    ticks (29,667–65,917 cells), no non-finite energy at any record; r/m at 6,000 about 7 (4.6–11.7). Task 30 applied:
    same seed from separate page loads identical at all 104 records. Report 29's 0 of 70 is superseded. Dish seeds
    2, 3, 4, 6 not re-run; not needed, since this side already found all 12 dish founders to be one gene.
  - Report 32 (task 22's models on the GPU): 9–17× faster; not seed-for-seed identical (CUDA random stream), but
    statistically matching (32 of 734 comparisons with |z| > 2). Task 22's conclusions stand.
  - Report 31 (modern founder, parts 3–5): designs only, all proposals, nothing built. Every part 3/4 design needs a
    per-cell inside pool first (a page change). Source figures were written from memory and are marked to check.
  - Nothing sent to the GPU: it asks nothing of this side, and every open choice is Justin's. No code changed.
  - **Waits on Justin:**
    1. Report 31: the order of parts 3–5 (GPU proposes 5, 3, 4); the per-cell inside pool and what it holds; whether
       part 3 waits for the helix term; lipids made or given; cell walls with the membrane or later; coupling ion
       (sodium-like or a new proton); synthase into `light` or a separate ATP-like store; membrane potential from the
       start or later; number of precursor kinds and whether they replace `payChem`'s direct use of the ground; which
       letter family first.
    2. Report 32 proposal: population-model work on the GPU by default (CPU path kept for checks).
    3. Still open from 14:03: report 26's helix term and step 1's near-misses; report 28's three choices.
- 2026-11-16 18:02 (scheduled check): commit read cbd076f (GPU log 17:08: read this side's 16:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 (report 31's part 3–5 choices; report 32's GPU-by-default proposal;
    report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-16 20:02 (scheduled check): commit read 0ad6abd (GPU log 19:08: read this side's 18:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 (report 31's part 3–5 choices; report 32's GPU-by-default proposal;
    report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-16 22:02 (scheduled check): commit read 4868de1 (GPU log 21:08: read this side's 20:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 (report 31's part 3–5 choices; report 32's GPU-by-default proposal;
    report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 08:02 (scheduled check): commit read 003d0c2 (GPU log 04:08: read this side's 22:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 (report 31's part 3–5 choices; report 32's GPU-by-default proposal;
    report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 10:02 (scheduled check): commit read b0252b9 (GPU log 14:08: read this side's 08:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 12:02 (scheduled check): commit read 035f64a (GPU log 16:08: read this side's 10:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 14:02 (scheduled check): commit read 0be724e (GPU log 18:09: read this side's 12:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 16:02 (scheduled check): commit read f80feeb (GPU log 20:08: read this side's 14:02 check; no new
  tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 18:02 (scheduled check): commit read 8f9daa1 (GPU log 17:08 New York: read this side's 16:02 check; no
  new tasks; no change; also notes its earlier log times today were UTC, not New York time). No new reports,
  nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 20:02 (scheduled check): commit read 8fd766d (GPU log 19:08 New York: read this side's 18:02 check; no
  new tasks; no change). No new reports, nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-17 22:02 (scheduled check): commit read 1ea0d22 (GPU log entry headed 2026-11-18 02:08, committed 21:09
  New York, so that heading is UTC again: read this side's 20:02 check; no new tasks; no change). No new reports,
  nothing sent to the GPU, no code changed.
  - **Waits on Justin:** unchanged from 16:02 on 16 November (report 31's part 3–5 choices; report 32's
    GPU-by-default proposal; report 26's helix term and step 1's near-misses; report 28's three choices).
- 2026-11-18 08:03 (scheduled check): no change (commit read f06e240, GPU log 23:09 on 17 November: no change).
- 2026-11-18 10:02 (scheduled check): no change (commit read 7d2d80d, GPU log 09:09: no change).
- 2026-11-18 12:02 (scheduled check): no change (commit read 2137a00, GPU log 16:08: no change; also saw this side's interactive commit bfef8e7, founder switch and genome-code design proposal, nothing for the GPU).
