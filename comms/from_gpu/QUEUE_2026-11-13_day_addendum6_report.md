# Sixth addendum: task 1 and the validation on page 8

This follows the sixth day-queue addendum (13 November, about 18:30; run on 14 November).
- **The page:** `justins_game_of_life.html` from `jgol_2026-11-13_8.zip`, unpacked into a new folder,
  `D:\labyrinth\automata\jgol_2026-11-13_8\jgol\`. It is unchanged; the earlier pages are untouched.
- **Proposals:** the measurements are measurements. The model variants, the pass standard and the readings are Claude's
  proposals.
- **Nothing was pushed or deleted.**

## In short

1. **The fifth addendum's round had already finished.** Its report, `day7_page6.md`, is marked superseded for its
   numbers. Its structure is kept: which model forms fit.
2. **The retuned chemistry pays, and it changes the dish.**
   - **Sugar 1:** the colony no longer dies out. It grows again after tick 500 and reaches radius 81 by tick 2,000.
   - **Sugar 3:** it has a second wave at tick 1,000 (2,261 cells).
   - **Sugar 10:** it grows about twice as fast in the middle of the run (13,160 cells at tick 250, against 4,940 on
     page 6).
3. **Task 1:**
   - **The sugar budget** still holds: 1.49 page sugar per birth, R² 0.968. That is a little looser than page 6's 0.991,
     because chemistry now pays part of the way.
   - **Upkeep paid from sugar** almost vanishes: 0.00016 per active cell-tick, against 0.0009.
   - **Going still** keeps Matsushita's form: a0 0.0129, halving at 0.13 divisions' worth (0.28).
   - **Waking** still needs sugar, at a peak of about 2 × 10⁻⁴ per inactive cell-tick.
4. **A probe measured the chemistry's income:** 0.0065 net energy per active cell-tick, steady over 2,000 ticks.
   - That is about 8 times the energy from sugar at page sugar 1, 2.5 times at sugar 3, and 0.7 times at sugar 10
     during growth.
   - **So the dish now has two resources, and every model has only one.**
5. **The validation:** Bcrw, Sm and the two proposals (start at tick 5; division gated by the store), each refitted.
   - **No version passes.** They miss sugar 1's regrowth, sugar 3's second wave, and sugar 10's faster middle.
   - **The starting proposal still fixes the start.** At sugar 1, Bmrw5 is within 12% to tick 100.
6. **One more variant (proposal): births paid by chemistry,** at a constant rate that needs no sugar.
   - At sugar 1 it gives about the right radius throughout, and cells within 7–74%.
   - At sugar 3 and 10 it overshoots badly.
   - So chemistry needs its own field in the fold, not a constant rate (section 3).
7. **No sweep was run.**
8. **The gliding comment from the fifth addendum's report is still in the page:** `glidePass` drops a gliding cell's
   clump membership. It was not on this page's list of fixes.

## 1. Task 1 on page 8

The runs are in `day8_page8/raw/` (default hopping) and `raw_nohop/`. Since no cell hops in the dark dish, they differ
only in the random stream. The fits are in `default/`, `nohop/`, `energy_fit.json` and `energy_fit_nohop.json`.

| | Page 6 | **Page 8, hopping on** | Page 8, hopping off |
|---|---|---|---|
| Sugar per birth, u (page units) | 1.70 (R² 0.991) | **1.49 (R² 0.968)** | 1.47 (R² 0.964) |
| Sugar per active cell-tick | 0.0009 | **0.00016** | 0.00030 |
| Division with room^h | 0.220, Kn 71, h 0.14 (0.78) | **0.114, Kn 16.6, h 0.30 (0.70)** | 0.116, Kn 17.9, h 0.30 (0.70) |
| Going still, constant (per active cell-tick) | 0.0056 | 0.0061 | 0.0061 |
| Going still, a0/(1 + n/n1) | a0 0.0126, n1 0.165 (0.34) | **a0 0.0129, n1 0.127 (0.28)** | a0 0.0131, n1 0.133 (0.29) |
| Going still against the store E | qhi 0.026, E50 0.235, h 7.8 (0.59) | qhi 0.029, E50 0.226, h 7.1 (0.55) | the same |
| Waking: peak, per inactive cell-tick (block sugar 1–10) | 3.3 × 10⁻⁴ | 2.1 × 10⁻⁴ | 2.4 × 10⁻⁴ |
| Waking with no sugar | 1 × 10⁻⁷ | 3 × 10⁻⁷ | 1 × 10⁻⁷ |
| Deaths, active / inactive per tick | 0.0021 / 0.0023 | 0.0021 / 0.0023 | the same |
| Share of births landing in the next block | 15.7% | 15.5% | 15.6% |

(n is in divisions' worth per block; deviance explained in brackets.)

**The chemistry's income** (`test/probe_rx.js`, `day8_page8/probe_rx/`; one seed per sugar level). The page's own
reaction counters give the energy gained minus the energy spent, per active cell-tick, over 25-tick windows:

| Page sugar | Tick | Chemistry, net | Sugar (× eeff) | Births per active cell-tick |
|---|---|---|---|---|
| 1 | 25 | 0.0164 | 0.0021 | 0.030 |
| 1 | 250 | 0.0047 | 0.0007 | 0.0014 |
| 1 | 1,000 | 0.0068 | 0.0007 | 0.0029 |
| 1 | 2,000 | 0.0067 | 0.0008 | 0.0037 |
| 3 | 500 | 0.0065 | 0.0025 | 0.0063 |
| 3 | 1,000 | 0.0062 | 0.0021 | 0.0070 |
| 3 | 2,000 | 0.0045 | 0.0007 | 0.0021 |
| 10 | 100 | 0.0050 | 0.0087 | 0.018 |
| 10 | 250 | 0.0040 | 0.0057 | 0.012 |
| 10 | 1,000 | 0.0078 | ≈ 0 | (14 active cells) |

**Readings:**
- **The chemistry pays steadily.** Per active cell, it pays about 0.004–0.008 a tick throughout, at every sugar level.
  The agar's molecules show no sign of running out within 2,000 ticks.
- **Where sugar is scarce, chemistry is most of the income.**
  - At page sugar 1, births continue at about 0.003 per active cell-tick long after the sugar has stopped paying for
    them.
  - That is the regrowth after tick 500.
- **The sugar budget's u still holds,** because births are still mostly charged in sugar when they happen in sugar.
  Its looser fit (0.968) is the share chemistry pays.

## 2. The validation on page 8

The page runs: page sugar 1, 3 and 10, gliding 0.1, 3 seeds, the default inoculum, a 256 × 256 world
(`validate_page/`; `validate_page_nohop/` is the same within seed noise).

The models are in `day8_page8/model/` and `model_chem/`. Each one:
- is refitted from task 1;
- spreads 15.5% of births;
- has the measured deaths;
- has waking on sugar (3 × 10⁻⁷ + 2.1 × 10⁻⁴ · n/(n + 0.5)).

| Variant | What it is |
|---|---|
| Bcrw | division 0.114 · n/(n+16.6) · room^0.30, constant going still 0.0061 |
| Bmrw | as Bcrw, with Matsushita's going still: 0.0129 / (1 + n/0.127) |
| Bmrw5 | as Bmrw, started from the page's state at tick 5 (proposal 1) |
| Sm | the store fold, charged the measured cost: 1.49 per birth, 0.00016 per active cell-tick |
| Smg, Smg5 | division gated by the store (proposal 2), from tick 0 and from tick 5 |
| Bmrwc5, Bcrwc5 | as Bmrw5 and as Bcrw started at tick 5, plus births paid by chemistry at 0.003 · room^0.30 per active cell-tick, needing no sugar (proposal) |

**All cells (active + inactive), mean of 3 seeds; r = radius (95th percentile) in places:**

| Page sugar | Tick | Page | Bcrw | Bmrw | Bmrw5 | Sm | Smg | Smg5 | **Bmrwc5** |
|---|---|---|---|---|---|---|---|---|---|
| **1** | 100 | 698, r 19 | 246 | 256 | 617, r 21 | 272 | 254 | 611 | **748, r 21** |
| 1 | 250 | 548, r 22 | 188 | 207 | 471 | 227 | 200 | 464 | **737, r 24** |
| 1 | 500 | 387, r 31 | 116 | 142 | 305 | 175 | 151 | 296 | **673, r 31** |
| 1 | 1,000 | 418 (273 active), r 45 | 41 | 83 | 132 | 109 | 86 | 140 | **554 (281), r 43** |
| 1 | 2,000 | 567 (364), r 81 | 9 | 38 | 42 | 59 | 56 | 52 | **425 (230), r 62** |
| 3 | 100 | 830, r 22 | 432 | 466 | 938, r 29 | 564 | 448 | 889 | 1,099 |
| 3 | 250 | 749, r 31 | 495 | 667 | 950, r 46 | 734 | 501 | 815 | 1,387 |
| 3 | 500 | 788, r 47 | 582 | 850 | 1,045, r 69 | 1,062 | 587 | 757 | 1,935 |
| 3 | 1,000 | 2,261, r 110 | 707 | 1,056 | 1,092, r 99 | 1,331 | 760 | 802 | 3,009 |
| 3 | 2,000 | 1,561, r 117 | 506 | 759 | 740 | 663 | 899 | 777 | 3,240 |
| 10 | 100 | 2,657, r 48 | 1,699 | 1,909 | 2,414, r 40 | 2,520 | 1,714 | 2,348 | 2,756 |
| 10 | 250 | 13,160, r 110 | 5,205 | 6,199 | 6,301, r 80 | 8,694 | 4,899 | 5,348 | 8,266 |
| 10 | 500 | 13,495 | 10,887 | 11,465 | 11,621 | 10,656 | 10,848 | 11,369 | 17,921 |
| 10 | 1,000 | 4,496 | 4,415 | 4,237 | 4,292 | 3,654 | 4,638 | 4,525 | 12,629 |
| 10 | 2,000 | 569 | 464 | 433 | 459 | 413 | 503 | 485 | 4,238 |

**Page sugar 1 (reported separately, as asked).**
- **The page:**
  - 244 → 713 cells by tick 25, then a slow decline to 387 at tick 500.
  - Then regrowth to 567 cells (364 active) by tick 2,000, spreading from radius 19 to 81.
  - It uses 31% of the plate's sugar. The rest of its income is chemistry.
- **The sugar-only models** (every variant but the last) decline and die out.
  - Starting at tick 5 still fixes the first 100 ticks (Bmrw5 617, Smg5 611, against 698).
  - After that they lose cells, because nothing pays for births once the sugar runs low.
- **With births paid by chemistry** (Bmrwc5):
  - the radius is right to tick 1,000 (21, 24, 31, 43 against 19, 22, 31, 45);
  - the cells are within 7–34%, except tick 500 (+74%);
  - but it declines where the page regrows (425 against 567 at tick 2,000).

**Page sugar 3.**
- The page has a second wave at ticks 500–1,000 (788 → 2,261 cells, radius 47 → 110).
- The sugar-only models stay flat.
- Bmrwc5 grows steadily instead, and overshoots from tick 250 on (+85%, +146%, +33%, +108%).

**Page sugar 10.**
- The sugar-only models are 35–60% low at tick 250, where the page grows fastest.
- From tick 500 they are within 10–25%.
- Bmrwc5 gets tick 100 right (+4%), but then keeps growing on chemistry after the sugar is gone. The page's cells go
  still instead: 12,629 against 4,496 at tick 1,000.

**Verdict: no version passes.**
- The dish now runs on two resources: the sugar, and the agar's molecules worked by enzymes.
- The models have only the sugar.
- A constant chemistry term is the wrong summary of the second resource:
  - where sugar is gone, the page's cells go still and stop dividing;
  - so chemistry alone does not sustain division, except at low sugar, where cells stay active.
- This is a case for the addendum's question from the first round: the energy detail changes the level above, so the
  fold has to keep it.

## 3. What the fold now needs (proposal)

- **A second field: the agar's molecules per square,** with:
  - the chemistry's income per active cell drawn from it;
  - and the cells' going still depending on the total income, sugar plus chemistry, not on sugar alone.
- **To build it:**
  - record the molecules per block, and the reaction income per block, in the task 1 harness (`rates.js`), alongside
    sugar;
  - then fit division and going still against both.
- **The open question it would answer:** why chemistry sustains active cells at low sugar but not after the sugar runs
  out at high sugar.
  - **One possibility (proposal):** at sugar 10 the cells crowd the plate, so each cell's share of the molecules is
    small. At sugar 1 the few cells each have plenty.
  - The per-block record would show whether this is so.

## 4. Items in page 8 (reported, not changed)

- **Gliding still drops clump membership** (line 2770, as reported in `day7_page6.md`):
  `body[j] = body[i]; body[i] = 0;` is inside a comment. It was not on this page's list of fixes.
- **A rescan for comments that run on into code** found nothing else.

## 5. The sweep

None was run, since no version passed.

## Files

- **Page runs:** `day8_page8/probe/`, `probe_amb/`, `probe_rx/`, `validate_page/`, `validate_page_nohop/`, `raw/`,
  `raw_nohop/`.
- **Fits:** `default/`, `nohop/`, `energy_fit.json`, `energy_fit_nohop.json`.
- **Models:** `day8_page8/model/`, `model_chem/`.
- **Code:**
  - `test/page8_all.cmd`;
  - `test/probe_rx.js` (new);
  - `popdish/validate_model.py`, which gains `--grow0`: births paid by chemistry, needing no sugar;
  - `popdish/validate_all.py`, with the new default.
