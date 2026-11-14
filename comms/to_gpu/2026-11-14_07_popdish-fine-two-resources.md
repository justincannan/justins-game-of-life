# 07: the population dish at 1,000 × 1,000 with two resources

From: cloud session, 14 November 2026. Follows report 03/03a, section 5.

Justin's decision (14 November): run your proposed cheaper test of whether branching appears on a fine grid.

## The run
- Extend `popdish/pop.py` with the second field (the agar's molecules), using the two-resource rates fitted in task 03
  (`fit_two.json`) and the molecule field's run-down (no regrowth, as the page's ground rules say).
- Run at 1,000 × 1,000 with **slow sugar diffusion**. Try a few diffusion rates, from the page's own rate downwards,
  and report which ones you used and why.
- Sugar levels matching the page's 1, 3 and 10; 3 seeds each; to the equivalent of 2,000 ticks.

## Report
- Pictures at one pixel per place, in 03a's colours, beside the page's dishes at the same ticks.
- Roughness and box-counting dimension, beside the page's (03a's table).
- Whether branching appears, and at which sugar and diffusion. A visual likeness to Matsushita's dishes is a proposal,
  not a test.

## Deliver
- `comms/from_gpu/2026-11-14_07_popdish-fine-two-resources_report.md`, with figures.
