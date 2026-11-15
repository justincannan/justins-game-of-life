# 25: refused contagion now undone (report 22 section 6); a small check

From: cloud session (scheduled check), 15 November 2026, about 12:05. Answers report 22 item 1, section 6.

1. **Fixed (a bug, not a design change).** When the page refuses a contagion because the cell cannot pay for its new
   compound (`swapChem` fails), the recipient's sequence, `cat`, `rx`, `rxStr` and `cH` now go back to what they were,
   as fragment uptake already does. `seqTransfer` keeps the overwritten stretch; `seqTransferUndo(j)` restores it.
   Draws no random numbers. Files: `tools/env.js`, one new rep in `tools/patch.py`; page rebuilt, script checked with
   `node --check`, loads headless without errors.
2. **Not changed: the same-compound case** (`g === ngen[j]`). There the splice changes the sequence and program but
   not the compound; the page keeps it (as uptake keeps same-compound splices) but does not count it as a write or mark
   the cell changed. Whether that should be undone, kept, or counted is Justin's call; it is in the cloud log under
   "Waits on Justin". Please do not change it.
3. **Small check (CPU, after item 2 of task 22, before item 3):**
   - Split report 22's "contagion refused but program already rewritten" (284 of 661 at sugar 10; 207 of 283 at
     sugar 3, as reported) into the two causes: cannot pay, and same compound.
   - Re-run report 22 item 1 at sugar 3 and 10 (3 seeds) on the rebuilt page. Expected: "cannot pay" cases leave the
     program unchanged. Report whether the dish's counts (report 17's measures) move beyond seed spread.
   - Mark which earlier page results this supersedes, if any (README rule).
