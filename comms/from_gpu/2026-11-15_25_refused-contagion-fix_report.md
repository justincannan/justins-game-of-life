# Report on task 25: refused contagion split by cause; task 22 item 1 re-run on the fixed page

From: gpu session (scheduled check), 15 November 2026, about 15:45 New York. Answers
`to_gpu/2026-11-15_25_refused-contagion-fix.md`. **Everything below is a measurement**, except where it says
*proposal*. Nothing in the page was changed, and the same-compound case (item 2) was left alone, as asked.

## In short
- **Report 22's "contagion refused but program already rewritten" is mostly "cannot pay".** At sugar 10, 234 of 284
  (82%) are "cannot pay" and 50 are "same compound". At sugar 3, 63 of 76 (83%) are "cannot pay" and 13 are "same
  compound".
- A correction to task 25's wording: at sugar 3, report 22's numbers were 283 program-changing splices, **of which 207
  were kept**, so 76 were refused, not 207.
- **On the fixed page (34189b0), every "cannot pay" refusal leaves the program as it was:** 38 of 38 at sugar 3 and
  235 of 235 at sugar 10. What remains in the category is the same-compound case only (16 and 39 splices). That case
  is Justin's call.
- **The dish's counts do not move beyond seed spread.** Across report 17's counts at 7 ticks, at sugar 3 and 10, with
  12 seeds a side, 1 of 84 comparisons has |z| > 2 (largest 2.2), and none has |z| > 3. By chance about 4 would pass 2.
- **Superseded:** only report 22 item 1's "refused but rewritten" column (section 4) and the contagion share it fed.
  The headline (mutation at division dominates) stands. Report 17 stands. Section 4 lists the rest.

## 1. Method
- **Pages:**
  - before the fix: task 13's lineage-marked copy, made from the page at 821a258 (task 22's);
  - after the fix: the page at commit 34189b0, the fix alone. Its only difference from 821a258 is the undo (checked
    with `git diff`).
  - The current build (7ce4942) also adds hot springs, pond inflow and viruses, so it was not used: those would
    confound the comparison.
- **Hooks:** `test/split25_page.py` adds task 22's hooks plus one hook at each refusal: type 8, same compound
  (`g === ngen[j]`); type 9, cannot pay (`swapChem` fails). On the fixed page the hook comes after
  `seqTransferUndo`, and the recorder checks whether the program is back to its value before the splice (type 10 if
  it is).
- **Recorder:** `test/split25.js`, which is `split22.js` plus that relabelling.
- **Runs** (`test/task25_runs.cmd`, `test/task25_v17x12.cmd`, CPU queue, port 8810): task 22's settings (glide 0.1,
  2000 ticks, 256 × 256, random order), sugar 3 and 10.
  - The split: seeds 1–3 on both pages.
  - Report 17's counts (`validate17.js`, unhooked fixed page): seeds 1–12, against task 17's 12 random-order runs.
- **Analysis:** `popdish/split25.py`, `popdish/dish25.py`. Results are in `results/2026-11-15/task25/`, in
  `D:\labyrinth\automata\jgol_2026-11-13`.

**Checks:**
- The hooked page before the fix reproduces task 22's runs at every tick, 1–2000 (0 ticks differ in 6 of 6 runs).
- The hooked fixed page equals the unhooked fixed page at every tick (0 differ in 6 of 6), so the hooks change
  nothing.
- `validate17.js` on the unhooked page before the fix gives task 17's seeds 1–3 exactly. Task 17's 12 runs are
  therefore the "before" sample.
- The fixed page first departs from the old page at ticks 407–1781 at sugar 3, and at ticks 56–204 at sugar 10.

## 2. The split (sum of seeds 1–3)

| sugar | page | divisions (sequence copies) | splices that changed the program | kept | refused: same compound | refused: cannot pay | of which program restored |
|---|---|---|---|---|---|---|---|
| 3 | before the fix | 174,228 | 283 | 207 | 13 | 63 | 0 |
| 3 | fixed | 196,534 | 171 | 117 | 16 | 38 | **38** |
| 10 | before the fix | 311,134 | 661 | 377 | 50 | 234 | 0 |
| 10 | fixed | 297,170 | 815 | 541 | 39 | 235 | **235** |

- Refusals with no program change (counted, not in the table):
  - before the fix: 20 and 85 "cannot pay", 28 and 129 "same compound", at sugar 3 and 10;
  - fixed: 7 and 68 "cannot pay", 21 and 151 "same compound".
- **Kept contagion per 1,000 divisions:**
  - before the fix: 1.19 (sugar 3) and 1.21 (sugar 10);
  - fixed: 0.60 and 1.82.
  - The change is driven by single seeds. At sugar 3, seed 2 has 115 kept before and 48 after; at sugar 10, seed 3
    has 171 and 300. With 3 seeds this is not a measured effect of the fix.
- Report 22's own per-division figures were 0.001–0.009 kept contagions per division. They are unchanged within
  that range.

## 3. Report 17's counts, before and after the fix (12 seeds a side)

| sugar | tick | active, before | active, fixed | z | still, before | still, fixed | z |
|---|---|---|---|---|---|---|---|
| 3 | 500 | 803 ± 488 | 784 ± 489 | −0.1 | 786 ± 461 | 788 ± 462 | 0.0 |
| 3 | 1,000 | 1,184 ± 343 | 1,240 ± 302 | +0.4 | 1,704 ± 1,006 | 1,475 ± 951 | −0.6 |
| 3 | 2,000 | 333 ± 236 | 449 ± 346 | +1.0 | 1,109 ± 398 | 1,019 ± 308 | −0.6 |
| 10 | 250 | 8,981 ± 1,265 | 9,122 ± 1,295 | +0.3 | 5,460 ± 2,041 | 5,586 ± 2,170 | +0.1 |
| 10 | 1,000 | 16.5 ± 22.5 | 25.8 ± 34.1 | +0.8 | 4,366 ± 262 | 4,369 ± 230 | 0.0 |
| 10 | 2,000 | 22.6 ± 31.1 | 29.0 ± 44.9 | +0.4 | 490 ± 46 | 492 ± 43 | +0.1 |

- The values are mean ± sd over seeds. z = difference / √(sd₁²/12 + sd₂²/12).
- The other ticks (100, 250, 750, 1,500) and the other measures (remains, sugar left, r95, cover) are in
  `dish25.json`. The only |z| > 2 is sugar left at sugar 10, tick 1,500: 43.3 ± 2.9 before, 40.1 ± 4.0 fixed,
  z −2.2.
- These are `validate17.js`'s series fields, the same script on both sides. Report 17's table read its counts from
  the snapshots, so its absolute numbers differ from these; the comparison here is like with like.
- Report 17's shape measures (roughness, box dimension) were not recomputed.

## 4. What this supersedes (README rule)
- **Superseded:**
  - report 22 item 1, section 4: the column "contagion refused but program already rewritten" (284 at sugar 10, 76
    at sugar 3), and any sum that counted it as contagion changing a program;
  - on the fixed page that path is closed for "cannot pay". The remaining same-compound splices are 16 and 39
    (3 seeds).
- **Not superseded** (the dish's counts do not move beyond seed spread):
  - report 22 item 1's headline: mutation at division dominates, 3.9–5.6% of daughters;
  - report 13 as corrected in report 22;
  - report 17's baseline.
- **Report 22 item 2's page facts** (gliding 0.0003–0.009 per active cell-tick, the calibrated constants) were
  measured with `probe22.js` at about 11:41–11:50, on the page before the fix (committed at 12:04). They were not
  re-measured. The fix touches only refused contagions, and the dish counts are unchanged, so I expect them to stand.
  That is an expectation, not a measurement.

## 5. Waits on Justin (not mine to decide)
- The same-compound case (`g === ngen[j]`): undo it, keep it, or keep and count it. This report measures it (16 and
  39 program-changing splices in 3 seeds); it does not change it.
- *Proposal:* if the same-compound case is changed, the same harness (`split25_page.py`, `split25.js`) can re-check it
  in about 5 minutes of CPU.
