# 10: the finer-block models, once a fold passes

From: cloud session, 14 November 2026. Follows 03a (the proposal) and report 03/03a, section 5.

Justin's decision (14 November): approve the finer-block models **on your condition**: run them only once a fold
passes at 10 × 10 (task 06, or a later fold).

## Until then
- Do not start. Mark it "waiting on a passing fold" in `STATUS.md`.
- If task 06 closes with no fold passing, this stays waiting; say so in the 06 report.

## When a fold passes
1. Repeat task 1's rate measurements at 5 × 5 blocks (and 2 × 2 if affordable; say what it would cost first).
2. Refit every rate of the passing fold at each block size.
3. Validate against the page at sugar 1, 3 and 10 by the same standard as task 03.
4. Draw the models' maps at their block size, labelled as block maps, beside the page's maps at one pixel per place.
   Give roughness and box-counting dimension at each block size, as in 03a.
5. Report whether branching appears at all at the finer scale, and compare with task 07's fine-grid dish.

## Deliver
- `comms/from_gpu/2026-11-14_10_finer-blocks_report.md`.
