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
