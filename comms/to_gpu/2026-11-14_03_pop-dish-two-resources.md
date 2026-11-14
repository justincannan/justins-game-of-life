# 03: the population dish with two resources (sugar and the agar's molecules)

From: cloud session, 14 November 2026. Answers `comms/from_gpu/QUEUE_2026-11-13_day_addendum6_report.md`, section 3.

Justin's decision (14 November): queue the GPU session's proposal from that report: a second field for the agar's
molecules in the population dish, with going still depending on total income.

## The page
Use the current `build/justins_game_of_life.html` (commit caee6ba or later). It differs from page 8 by:
- the gliding fix (a gliding cell now keeps its clump membership);
- the build writing LF line endings.
Neither should touch the dark dish, which has no gliding clumps. Check this quickly: rerun one seed at sugar 1 and
compare it with page 8. If they differ, report how.

## Tasks
1. **Extend the harness** (`rates.js`). Per block and per window, alongside sugar, record:
   - the agar's molecules (the page's `chem` per square, summed over the block, by kind if cheap);
   - the reaction income: net energy from `domReact`, from the page's counters or by block.
2. **Answer the open question first.** Why does chemistry sustain active cells at low sugar but not after the sugar
   runs out at high sugar? Test your crowding proposal: the molecules per active cell at sugar 1, 3 and 10, over time,
   in the ring and in the still core.
3. **Fit, against sugar s and molecules m per block:**
   - division;
   - going still, as a function of total income (sugar income plus chemistry income), compared with sugar alone;
   - waking.
   Fit the molecule field's own dynamics as well:
   - use by active cells;
   - regrowth or diffusion, from the page's ground rules.
4. **Validate the two-resource fold** against the page at sugar 1, 3 and 10, by the same standard as before. Report:
   - sugar 1's regrowth;
   - sugar 3's second wave;
   - sugar 10's faster middle;
   - the front, a ring around a still core, which the earlier models lacked.
5. **If a version passes,** run the sweep from the earlier queue. If none passes, say what is missing and stop there.

## Order with task 02
Run this one on the CPU queue alongside task 02 on the GPU, if the queues allow it. If only one can run at a time, do
this one first, because the migration of the default worlds to the population scale waits on it.

## Deliver
- A report at `comms/from_gpu/2026-11-14_03_pop-dish-two-resources_report.md`, with block maps.
- Mark proposals as proposals and measurements as measurements.
