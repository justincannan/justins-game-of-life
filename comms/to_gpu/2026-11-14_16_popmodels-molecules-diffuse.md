# 16: the population models' molecules spread as the page's do

From: cloud session, 14 November 2026, about 21:05. Justin's decision (THEORY_NOTES.md, same section as task 15, item 1).

**Background.** In the page's dish, the 16 molecules spread: chemStep, rate D = min(0.24, 2·chdiff) times the wetness
factor. Sugar spreads too: energyStep, D = 0.2. In `pop2_gpu.py` and `store2.py` the molecule field does not spread.
Report 07 proposed that this is what removes the diffusion limit behind branching.

**Tasks.**
1. Give the molecule field in both models the page's diffusion, measured from the page if the wetness factor in the
   dish is not 1. Keep sugar's as it is.
2. **Rerun report 07's fine-grid test** at sugar 1, 3 and 10. Report:
   - box dimension;
   - boundary roughness;
   - whether arms appear.
3. **Rerun report 06's best store fold** with the spreading field, against the page at sugar 1, 3 and 10.
4. If a fold now passes, task 10 (finer blocks) may begin, as already approved.

Report in `comms/from_gpu/2026-11-14_16_popmodels-molecules-diffuse_report.md`. Task 15 has priority on the GPU; run
this one on the CPU queue alongside it if the queues allow.
