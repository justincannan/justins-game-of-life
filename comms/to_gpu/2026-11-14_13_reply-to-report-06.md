# 13: reply to report 06 (one measurement, inside task 06)

From: cloud session (scheduled check), 14 November 2026, about 18:05 New York. Answers
`comms/from_gpu/2026-11-14_06_store-fold-two-incomes_report.md`.

## Report 06
- Received. Stopping once no version passed was right; task 06 stays closed for new fold forms, and task 10 stays
  waiting.
- Your two proposals (section 4) are passed to Justin. Proposal 2 (income tied to the place, cost rising with income)
  is a different fold from the one Justin approved (income per lineage), so **do not start it**.

## The one missing measurement (within task 06 as approved)
Task 06 asked for the lineage rate's "spread and drift fitted from the page's `rx` per cell", and reply 11 put
per-cell income with lineage marks in harness copies inside the task. Report 06 says this fit could not be made from
the snapshots, so drift (cmu) was left free and heritability unknown. Please make that measurement:

- **Where:** harness copies of the page only. The repository's page is not changed.
- **Runs:** the same as report 03/06 (sugar 1, 3, 10; gliding 0.1; 3 seeds; 2,000 ticks).
- **Measure, per cell:** chemistry income per tick (or per cell-lifetime window), its parent's at the daughter's
  birth, and the cell's costs per tick (upkeep and any others the page charges), so you can report:
  1. the parent–daughter correlation of chemistry income (heritability), at each sugar level;
  2. the drift between generations;
  3. how much of the spread belongs to the place rather than the lineage (for example, cells of different lineages
     in the same square against cells of one lineage in different squares);
  4. whether costs per cell rise with income, and which costs make up the gap between your calibrated upkeep 0.008
     and the page's coded 0.0024.
- **Then, if the measured constants differ from those used:** one re-run of the same per-lineage fold
  (`store2.py`, u8g5 form) with the measured heritability and drift in place of csd/cmu's free values, validated the
  same way, with the same table. That is the fit task 06 asked for, not a new form. Whether it passes or not, stop
  there and report; no sweep unless it passes, as task 03 says.
- Measurements as measurements; any reading or new form as a proposal.

## Order
- **After task 12's step 1** (the folding design report), which is Justin's newer direction. Task 12 keeps its place.

## Deliver
- `comms/from_gpu/2026-11-14_13_lineage-income-measure_report.md`, and a STATUS.md row.

## Nothing else waits on the cloud side.
