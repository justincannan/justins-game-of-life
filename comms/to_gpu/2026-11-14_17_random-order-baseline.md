# 17: the page now visits places in random order: re-baseline the dish

From: cloud session, 14 November 2026, about 22:00. Justin's decision (THEORY_NOTES.md, "Decision (Justin, 14 November,
about 21:23): random visiting order").

**What changed in the page** (commit after 4ba5198):
- The feeding loop and the birth scan in `step()` visit places in a fresh random order each tick, using the seeded
  rng: 8 × 8 tiles in random order, and one of 32 random orders inside each tile.
- `P.randOrder = false` restores row order.
- The colony's lean towards the top is gone (THEORY_NOTES, "The uneven spreading", and the decision below it).

**Tasks.**
1. Rerun the page side of the dish comparisons at sugar 1, 3 and 10, 3 seeds each, with the new page:
   - counts (active and still);
   - box dimension and boundary roughness;
   - the cell-scale maps of 03a.
   Report any change from the row-order page beyond seed spread.
2. Use the new baseline for task 16 and every later dish comparison.

Report in `comms/from_gpu/2026-11-14_17_random-order-baseline_report.md`. CPU queue; after task 16's runs if they
compete.
