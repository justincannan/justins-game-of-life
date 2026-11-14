# 08: are the horizontal streaks at sugar 10 an artefact of update order?

From: cloud session, 14 November 2026. Follows report 03/03a, section 5 (`03a_dish_sugar10.png`, tick 500 on).

Justin's decision (14 November): check it. **A check only: do not change the page.** If the update order needs to
change, that changes the model, and it comes back to Justin as a proposal.

## The check
1. Find in the page's code where cells are updated (division, going still, waking, remains), and say in which order
   places are visited: row by row, random, or a mix. Name the functions and the source file in `tools/` or the base.
2. Measure the streaks: for example, the autocorrelation of the gone-still map along rows against along columns, or
   its power spectrum, at ticks 500 and 1,000, sugar 10, 3 seeds. Do the same at sugar 1 and 3.
3. If the harness can do it without changing the page, rerun one seed at sugar 10 with the scan order randomised (or
   reversed, or transposed) **in the harness only**, and say whether the streaks go and whether the counts change.
4. Also say whether the colony's growth is lopsided (`03a_dish_sugar10.png`, tick 250, grows more to one side), and
   whether that follows the scan order too.

## Deliver
- `comms/from_gpu/2026-11-14_08_row-streaks-check_report.md`. Cheap; run it first.
