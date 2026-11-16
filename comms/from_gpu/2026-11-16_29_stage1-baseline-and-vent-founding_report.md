# 29: the dish on the stage-1 page; vent founding

From: gpu session, 16 November 2026, about 11:25 New York. Answers
`comms/to_gpu/2026-11-16_29_stage1-baseline-and-vent-founding.md` (Justin's decision 3 of 16 November, about 00:19).

Measurements are measurements. Readings and fixes are Claude's proposals; Justin decides. The page was not changed.

## In short
1. **The dish (b4ceffa, 12 seeds a sugar) is unchanged from report 17's baseline beyond seed spread, except in the 4
   seeds whose founder starts as a broken two-gene genome.**
   - With all 12 seeds, 6 of 210 comparisons have |z| > 2 (about 10 expected by chance), largest 2.5. The ones that
     repeat are early: more gone-still cells at tick 100 at every sugar (z +2.1, +1.8, +2.2). At sugar 10, more active
     cells are left after the crash (87 against 13 at tick 750, z +2.1).
   - **All of these come from seeds 2, 3, 4 and 6.** In those seeds the dish founder's line ends `15 15 15 15 7`. The
     page builds the founder's line from its compound, which has three 15s in these seeds, and `dishSetup` then
     appends the pair `15 7`. The result is a run of four 15s, which stage 1 reads as a gene marker. So the founder:
     - becomes a two-gene genome (`1 2 2 2 14 14 14 | 7`);
     - loses the `15·7` domain the dish gives every inoculum (reaction word 0 instead of `0xf0`);
     - and has a different compound.

     These founders go still early (350–765 gone still at tick 100, against 5–282 in the other seeds), and keep a few
     hundred active cells after the sugar-10 crash.
   - **The 8 seeds with one-gene founders match report 17. 0 of 105 comparisons have |z| > 2** (active, still,
     remains, roughness and box dimension; 7 ticks; 3 sugars; largest 1.75).
   - **Shape:** box dimension and roughness agree within a few hundredths and a few percent at every sugar and tick,
     on all 12 seeds. The pictures show the same arms. There is no lean.
2. **Multi-gene genomes in the dish.** In the 8 seeds with one-gene founders, the share of live cells with 2 or more
   genes:
   - sugar 1 and 3: about 2% at tick 100, rising to 33–34% at tick 2,000;
   - sugar 10: about 18% by tick 250, then flat (the colony is mostly still after the crash).

   Cells using more than 4 reactions reach 22%, 15% and 6% at tick 2,000 (sugar 1, 3, 10). In the 4 seeds that start
   with the broken two-gene founder, the share falls from 100% to 16–38%: the broken line is selected against.
3. **Vent founding from one organism broke at 581c90e (pigments on), and it was never 6 of 6.**
   - **The "6 of 6" of 13 November was a soup start.** It came from `test/ventodds.py`, which starts with
     `reset('soup')`, at 600 ticks, on the page that became b07a990. The soup start still founds there: 10 of 10 on b07a990, seeds 11–20, at tick 1,000. On b4ceffa it founds in
     7 of 10, so pigments weaken the soup start too.
   - **The one-organism start founded in about 1 in 4 seeds from the dark-vent retune to 7ce4942:**
     39 of 157 runs pooled over b07a990, caee6ba, 1f4a805, 821a258, 34189b0 and 7ce4942 (7 of 40 on b07a990 itself, 9 of 30 on 7ce4942).
   - **From 581c90e on, it founded in 0 of 70 runs** (581c90e, 5b491ee, 6995cd7, b4ceffa).
   - **Why:** 581c90e turned `pigment` on, and `pigFounder()` skips the vent world. So the vent founder cannot absorb
     light at all. Its founding rested on the ambient light that `reset` fills to 1 on every place, a start-up store
     about as large as the cells' own. Without it, the first divisions get about 9 times fewer births (about 115
     against 920–1,110 by tick 50). No line of descent lasts long enough to evolve a reaction: in the 40 stage-1 runs, no record ever
     showed more than 2 cells with a reaction word, and every run was empty by tick 200.
   - **The dim glow itself never pays.** At most about 0.001 a tick per cell, against upkeep 0.01.
   - **Pigment off on the current page brings back the old rate** (9 of 36; 7 of 28 with row order as well).
   - **Other suspects are cleared:** the random visiting order (821a258: 10 of 37 with random order against 6 of 30 with row order on 821a258), viruses and the contagion fix
     (34189b0, 7ce4942: 8 of 30 and 9 of 30), stage 1 (with pigment off it founds as before), and world size.
4. **Page's own world size:** 1200 × 756 in a full-screen 1920 × 1080 window (772 × 516 at 1366 × 768; 680 × 376 in the
   harness frame). Size does not rescue founding (section 6). **A second page bug turned up here:** the coat arrays
   (`coatM`, `coatK`, `coatS`) are not resized by `allocWorld`. With pigments on, if the world grows past its load-time
   size (a bigger window, full screen), `pigOf()` reads past the end of the arrays and every cell beyond the old size
   gets NaN light and dies on the next tick. This happened to all 219 vent founders at 1024 × 560 in the harness.
5. **Proposed fix (Justin decides):** give the vent founder a chemotroph gene, as the sunlit worlds' founder gets a
   pigment gene and the dish's gets the `15·7` pair. The gene is one closed domain behind a marker, found by search so
   that its reaction runs downhill on a molecule plentiful at the founding vent, with the compound unchanged. Tested in
   the harness (not in the page): 20 of 20 seeds (11–30) on b4ceffa founded. Giving it the sunlit pigment gene instead does not work (0 of
   10). That is option 1 of 13 November ("a chemotroph inoculum"); Justin chose option 3 (the retune) then.

## 1. The dish: method
- **Page:** `build/justins_game_of_life.html` at b4ceffa (the stage-1 page plus the same-compound counter). Copy:
  `results/2026-11-16/task29/pages/jgol_b4ceffa.html`.
- **Runs:** task 17's settings (`test/task17_runs.cmd` copied to `test/task29_runs.cmd`):
  - sugar 1, 3 and 10; glide 0.1; W 256; 2,000 ticks; random order (the page's default); seeds 1–12;
  - snapshots at 100, 250, 500, 750, 1,000, 1,500 and 2,000.

  CPU queue, `jgol29-dish`, port 8797, about 14 minutes.
- **Script:** `test/validate29.js` = `validate17.js` plus, every 25 ticks, the number of live cells whose line has 1, 2
  or 3+ genes (the page's own `geneSegs`), cells with a second reaction word (`rx2`, more than 4 reactions), and mean
  line length. It only counts.
- **Baseline:** report 17's random-order runs (`results/2026-11-14/task17/random/`, seeds 1–12, page 821a258).
- **Analysis:**
  - `popdish/task29_analyze.py`, task 17's analysis with the two sets swapped in;
  - `popdish/task29_genes.py`, the gene shares.

## 2. The dish: counts and shape
Mean ± sd over seeds; z is the difference over its standard error. "Stage 1, 8" = the 8 seeds with one-gene founders
(1, 5, 7–12). From the snapshots, as in report 17's table.

| sugar | tick | active, report 17 (12) | active, stage 1 (12) | z | active, stage 1 (8) | z | still, report 17 | still, stage 1 (12) | z | still, stage 1 (8) | z |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 100 | 751 ± 135 | 575 ± 370 | −1.5 | 816 ± 122 | +1.1 | 35 ± 25 | 143 ± 178 | **+2.1** | 24 ± 17 | −1.2 |
| 1 | 500 | 182 ± 76 | 190 ± 100 | +0.2 | 223 ± 81 | +1.1 | 315 ± 87 | 314 ± 122 | 0.0 | 373 ± 105 | +1.3 |
| 1 | 1,000 | 303 ± 106 | 281 ± 92 | −0.5 | 297 ± 97 | −0.1 | 178 ± 114 | 206 ± 145 | +0.5 | 252 ± 155 | +1.1 |
| 1 | 2,000 | 352 ± 197 | 322 ± 115 | −0.5 | 316 ± 109 | −0.5 | 211 ± 255 | 206 ± 189 | −0.1 | 236 ± 227 | +0.2 |
| 3 | 100 | 924 ± 239 | 777 ± 479 | −0.9 | 1,085 ± 189 | +1.7 | 74 ± 59 | 193 ± 226 | +1.8 | 42 ± 41 | −1.4 |
| 3 | 500 | 803 ± 488 | 811 ± 451 | 0.0 | 921 ± 512 | +0.5 | 786 ± 461 | 780 ± 496 | 0.0 | 950 ± 530 | +0.7 |
| 3 | 1,000 | 1,184 ± 343 | 1,108 ± 240 | −0.6 | 1,164 ± 157 | −0.2 | 1,704 ± 1,005 | 1,436 ± 753 | −0.7 | 1,646 ± 774 | −0.1 |
| 3 | 2,000 | 333 ± 236 | 348 ± 182 | +0.2 | 291 ± 167 | −0.5 | 1,109 ± 398 | 1,188 ± 362 | +0.5 | 1,097 ± 337 | −0.1 |
| 10 | 100 | 2,929 ± 1,049 | 2,858 ± 1,168 | −0.2 | 3,476 ± 878 | +1.3 | 173 ± 54 | 356 ± 278 | **+2.2** | 174 ± 78 | 0.0 |
| 10 | 250 | 8,981 ± 1,265 | 7,917 ± 2,147 | −1.5 | 8,665 ± 1,813 | −0.4 | 5,460 ± 2,040 | 5,448 ± 2,361 | 0.0 | 6,293 ± 2,334 | +0.8 |
| 10 | 500 | 216 ± 277 | 583 ± 898 | +1.4 | 168 ± 309 | −0.4 | 13,268 ± 737 | 12,497 ± 1,239 | −1.9 | 13,040 ± 531 | −0.8 |
| 10 | 750 | 13 ± 22 | 87 ± 119 | **+2.1** | 14 ± 33 | +0.1 | 7,644 ± 460 | 7,414 ± 376 | −1.3 | 7,519 ± 304 | −0.7 |
| 10 | 1,000 | 16 ± 23 | 76 ± 108 | +1.9 | 12 ± 26 | −0.4 | 4,366 ± 261 | 4,262 ± 262 | −1.0 | 4,329 ± 208 | −0.3 |
| 10 | 2,000 | 23 ± 31 | 64 ± 83 | +1.6 | 13 ± 21 | −0.8 | 490 ± 46 | 509 ± 59 | +0.9 | 503 ± 55 | +0.5 |

**Shape** (12 seeds, report 17 / stage 1):

| sugar | tick | roughness | box dimension (live) |
|---|---|---|---|
| 1 | 250 | 13.8 / 13.6 | 1.53 / 1.49 |
| 1 | 1,000 | 18.3 / 18.0 | 1.34 / 1.32 |
| 1 | 2,000 | 20.4 / 20.0 | 1.15 / 1.15 |
| 3 | 500 | 26.9 / 26.9 | 1.48 / 1.49 |
| 3 | 1,000 | 41.4 / 39.6 | 1.45 / 1.43 |
| 3 | 2,000 | 36.1 / 37.5 | 1.09 / 1.13 |
| 10 | 250 | 55.5 / 54.7 | 1.80 / 1.78 |
| 10 | 500 | 81.7 / 80.1 | 1.78 / 1.77 |
| 10 | 2,000 | 24.9 / 25.9 | 0.77 / 0.80 |

- The only shape |z| > 2: box dimension at sugar 1, tick 500 (1.51 against 1.45, z −2.2; with live + remains −2.5).
  It does not repeat at the next ticks, and it is −1.3 at tick 750, so I read it as chance.
- **Lean:** the centre of the live places lies within 0.03 plate radii of the plate's centre at every sugar and tick,
  with 3–6 of 12 runs above. As in report 17's random order.
- **Pictures** (seed 1, which has a one-gene founder; report 17 above, stage 1 below; 03a's colours):
  - `29_dish_sugar1.png`, `29_dish_sugar3.png`, `29_dish_sugar10.png`: the whole dish;
  - `29_closeup_sugar1.png`, `29_closeup_sugar3.png`, `29_closeup_sugar10.png`: 64 × 64 places on the +x edge at 4×.

  By eye: the ring of gone-still cells, then thin arms at sugar 1; branched arms with active tips at sugar 3 (seed 1's
  stage-1 colony branches a little further by tick 750–1,000, within the seeds' spread); the dense front and the
  crash at sugar 10.

**Reading (proposal).** The dish has not drifted. The differences beyond seed spread are one start-up bug in
`dishSetup` under stage 1, not the new genome operators. Report 17 stays the baseline for one-gene founders.

## 3. The dish founder bug (measured)
- `test/dishfounder29.js` sets up the dish as `validate17.js` does and reads the founder's line, seeds 1–12:
  - seeds 1, 5, 7–12: one gene, for example `1 2 2 2 15 15 15 7`, reaction word `0xf0` (the dish's `15·7` pair);
  - seeds 2, 4, 6: `1 2 2 2 14 14 14 15 15 15 15 7`, genes `[0,7)` and `[11,12)`, reaction word 0;
  - seed 3: `1 2 2 2 14 14 15 15 15 15 7`, the same.
- **Cause:** `seqFromGen` writes each monomer kind as many times as its exponent (up to 3), in order, so a founder
  whose compound has three 15s ends `15 15 15`. `dishSetup` then appends `15 7`, which makes a run of 4. Before stage 1
  this was harmless. Now it is a gene marker: the `15·7` domain is split and lost, and the compound changes.
- About a third of the dish founders are affected (those whose random tag gives prime 15 exponent 3).
- **Proposed fix (Justin decides):** in `dishSetup`, put the pair where it cannot make a run of 4: at the front, or
  behind a marker of its own as `pigFounder` does. Alternatively, have `seqFromGen` never end in the kind about to be
  appended. The design note says the founder is built without runs of 4, and this path was missed.
- The same check is worth making for `pigFounder` in the sunlit worlds. It adds its domain behind a marker, so it
  should be safe; I have not measured it.

## 4. Multi-gene genomes (measured)
From `validate29.js`, every 25 ticks; `29_multigene.png` (left: the 8 seeds with one-gene founders; right: the 4 with
two-gene founders). Share of live cells whose line has 2 or more genes:

| sugar | founders | tick 100 | 500 | 1,000 | 2,000 |
|---|---|---|---|---|---|
| 1 | one gene (8) | 2.3% | 7.8% | 16.4% | 34.4% (2–84%) |
| 3 | one gene (8) | 2.2% | 13.0% | 24.7% | 32.9% (5–51%) |
| 10 | one gene (8) | 13.6% | 18.0% | 18.0% | 18.6% (7–41%) |
| 1 | two genes (4) | 90.0% | 67.9% | 41.0% | 37.7% |
| 3 | two genes (4) | 90.5% | 33.3% | 22.1% | 16.8% |
| 10 | two genes (4) | 58.7% | 15.8% | 16.9% | 28.6% |

All 12 seeds: 35.5%, 27.5% and 21.9% at tick 2,000 (sugar 1, 3, 10).

- **More than 4 reactions** (all seeds, tick 2,000): 21.6%, 14.7% and 5.5%.
- **3 or more genes:** 3–5%.
- **Mean line length** rises from 9.5 to 23.0 (sugar 1), 21.0 (sugar 3) and 11.3 (sugar 10).
- **Reading (proposal):** in the dish, multi-gene genomes arise from one-gene founders and grow steadily wherever the
  colony keeps dividing. At sugar 10 they rise fast during the boom and then freeze with the crash. The seed spread is
  large (2–84% at sugar 1), as expected when a few lineages take the plate.

## 5. Vent founding: method
- **Pages** (copies in `results/2026-11-16/task29/pages/`):
  - every commit that changed the build: b07a990, caee6ba, 1f4a805, 821a258, 34189b0, 7ce4942, 581c90e, 5b491ee,
    6995cd7, b4ceffa. Extracted with `git show <commit>:build/justins_game_of_life.html`; the working tree was not
    touched;
  - the 13 November packages before the repository (`jgol_2026-11-13`, `_1`, `_2`, `_4`, `_6`). `_8` is
    byte-identical to b07a990.
- **Harness:** `test/vent29.js` with `test/vent29_driver.py` (a job-list version of `rates_driver.py`). It follows the
  cloud harness (`test/genes.py`):
  - the page's own defaults, `P.env = 'vent'`, `P.autoRestart = false`;
  - the cloud's seeded xorshift as `rng` (`Math.random` not seeded, as in the cloud harness);
  - `allocWorld(476, 248)`, then `geoSeed(); chemCapFill(); reset('organism')`, 1,000 ticks.
- **Records:** every tick to 100, then every 25 ticks:
  - cells, births and deaths;
  - mean stored energy (`light`) and mean ambient light (`amb`) at the cells;
  - reaction income (`domReact` wrapped, adding up only) and cells with a reaction word;
  - the first-generation cells (those still on a founder's place) and their store.
- **Founded** = cells alive at tick 1,000.
- **Runs:** CPU queue, `jgol29-vent`, `jgol29-ablate`, `jgol29-final`, `jgol29-extra`; ports 8798–8805.
  - Seeds 11–20 on every page.
  - More seeds (to 40 or 50) on the pages either side of each suspect step.
  - 12 runs failed to start (Chrome exited within 1–16 s, before the page ran). Two were re-run; the other 10 are
    simply missing seeds, which is why some counts are of 9, 28, 36, 37 or 39 runs rather than 10, 30 or 40.
  - The soup runs on the 13 November packages were stopped after the first page, to leave the queue to task 28.

## 6. Vent founding: results (measured)
Runs alive at tick 1,000, one-organism start, 476 × 248, unless stated (`29_vent_founding.png`):

| page or test | alive at tick 1,000 |
|---|---|
| 13 Nov package (bright vents) | 10 of 10 |
| 13 Nov, last before dark vents | 10 of 10 |
| b07a990 dark vents (repo start) | 7 of 40 |
| caee6ba | 3 of 10 |
| 1f4a805 | 2 of 10 |
| 821a258 random visiting order | 10 of 37 |
| 821a258 with row order | 6 of 30 |
| 34189b0 | 8 of 30 |
| 7ce4942 viruses etc. (pigment off) | 9 of 30 |
| 581c90e pigments on | 0 of 10 |
| 5b491ee | 0 of 10 |
| 6995cd7 stage 1 | 0 of 10 |
| b4ceffa (current) | 0 of 40 |
| 5b491ee, pigment off | 2 of 9 |
| b4ceffa, pigment off | 9 of 36 |
| b4ceffa, pigment off, row order | 7 of 28 |
| b4ceffa, founder given pigment gene | 0 of 10 |
| b4ceffa, founder given chemotroph gene | 20 of 20 |
| b07a990, soup start | 10 of 10 |
| b4ceffa, soup start | 7 of 10 |
| b07a990 at 680 x 376 | 1 of 7 |
| b4ceffa at 680 x 376 | 0 of 10 |
| b07a990 at 1024 x 560 | 1 of 10 |
| b4ceffa at 1024 x 560 | 0 of 10 |
| b4ceffa at 1024 x 560, pigment off | 2 of 9 |
| b07a990 at 1200 x 756 | 1 of 9 |
| b4ceffa at 1200 x 756 | 0 of 10 |

**Where it broke.**
- Every page from b07a990 to 7ce4942 founds in about a quarter of seeds (pooled 39 of 157, 25%).
- Every page from 581c90e on founds in none (pooled 0 of 70).
- With `pigment` false, the current page founds as before (9 of 36; 7 of 28 with row order as well).
- The visiting order does not matter: 10 of 37 with random order against 6 of 30 with row order on 821a258.
- The pre-repository packages with bright vents (`ventGlow` 1) found in 10 of 10. The dark-vent retune (`_8` = b07a990)
  is what brought the one-organism start down to about a quarter, and nobody measured it then, because the check was
  run with the soup start.

**The founder's first divisions** (`29_vent_first_ticks.png`; mean over seeds 11–20):

| tick | b07a990: births so far, cells, ambient at cells | 7ce4942 | 581c90e (pigments on) | b4ceffa | b4ceffa, pigment off |
|---|---|---|---|---|---|
| 10 | 127, 301, 0.70 | 135, 313, 0.70 | 38, 215, 0.83 | 37, 217, 0.83 | 120, 295, 0.70 |
| 20 | 499, 623, 0.40 | 489, 616, 0.40 | 89, 231, 0.68 | 82, 224, 0.68 | 427, 560, 0.42 |
| 50 | 1,108, 950, 0.14 | 1,044, 875, 0.14 | 120, 25, 0.40 | 111, 34, 0.40 | 916, 814, 0.16 |
| 100 | 1,158, 201, 0.06 | 1,068, 157, 0.06 | 121, 1, 0.07 | 113, 1, 0.07 | 959, 185, 0.06 |
| 300 | 2,462, 686 | 1,075, 5 | 122, 0 | 113, 0 | 2,458, 819 |

- **The budget:**
  - `reset` gives every place a stored energy of 1 and an ambient light of 1.
  - The founding ring is about 220 cells. Upkeep is 0.01 a tick (`cost`). A birth needs the parent to hold
    `birth` 0.2 + `seqCost` × length + 2 × `divKeep` 0.1, so at least about 0.4, and pays 0.2.
  - Without pigments, a cell absorbs the ambient light down to its own store (`absorb` 1). The ambient at the founders
    falls from 1 to 0.14 by tick 50, giving them about as much energy again as their store. That pays for about 1,100
    births in the first 50 ticks.
  - The vents' glow sets the ambient to only `ventGlow` 0.05 × the vent field (`ltc` 0.05 at the founders). It regrows
    at `regrow` 0.02 a tick, so at most about 0.001 a tick per cell comes back, a tenth of the upkeep.
  - **So the start-up ambient light is the founding store, and the glow is not.** Reactions take over in the seeds
    that found: cells with a reaction word appear by tick 30–50 and carry the colony from tick 100 (reaction income
    1.4 a tick at tick 100, 25 at tick 300 on b07a990).
  - With pigments on and no pigment, the vent founder absorbs nothing (`pigOf` = `pigBase` 0). The ambient stays
    unused (0.68 at tick 20 against 0.40). Births stop at about 115 by tick 50, from the cells' own stores, and the
    ring dies by tick 75–150.
  - Too few divisions means too few copying errors for a working reaction to arise. In the 40 stage-1 runs, the most
    cells with a reaction word at any record was 2, against 36 on average at tick 100 on b07a990. All 40 were empty by
    tick 200.
- `pigFounder()` deliberately skips the vent ("in sunlit worlds"), so 581c90e's change, pigments on and the founder's
  pigment gene, leaves the vent founder with nothing.
- **Founding is a matter of chance even without pigments:** in about 3 of 4 seeds the burst of 1,000 births dies out
  before a reaction spreads.
- **Size.** Larger worlds do not found more often: b07a990 founds in 1 of 7 at 680 × 376, 1 of 10 at 1024 × 560 and 1 of 9 at 1200 × 756 (7 of 40 at 476 × 248). b4ceffa founds in 0 of 30 at those sizes, and in 2 of 9 at 1024 × 560 with pigment off. The founding ring and vent 0 are the same at every size, so size could only matter through the other vents, which are far away.
  - The page's own size: 1200 × 756 in a full-screen 1920 × 1080 window, 772 × 516 at 1366 × 768, 708 × 478 at
    1280 × 720, 1692 × 1032 at 2560 × 1440 (`test/size29.html`), and 680 × 376 in the harness's 900 × 700 frame. The
    vent count scales with the area (at least 4), and vent 0 is always at the centre, with s ≥ 8 and full strength.
  - **The coat arrays bug:** `allocWorld` does not resize `coatS`, `coatM` and `coatK` (`coatAlloc` is lazy). In a world
    larger than the one at load, `pigOf(i)` for i beyond the old size reads `undefined`, so the light is NaN, and the
    cell dies on the next tick (`light[i] >= 0` fails).
    - The harness hit it at 1024 × 560 (all 219 founders dead at tick 1, `test/sizeprobe29.js`). The larger-world runs
      above size the coat arrays first, as the page's own `coatAlloc()` would on a fresh load.
    - In the page, the same happens when the window grows past its load-time size, in any world where nothing has
      called `coatAlloc` since. Pages before 581c90e (pigment off) are not affected.
  - **Proposed fix:** call `coatAlloc()` in `allocWorld`, or make `coatAlloc` check `coatK.length` too.

## 7. Proposed fixes (Justin decides)
1. **A chemotroph gene for the vent founder** (main proposal). `pigFounder`'s search, with the criterion "the reaction
   runs downhill on a molecule plentiful in the founder's square" in place of "makes a pigment":
   - one closed domain behind a marker, compound unchanged;
   - in the harness test (`vent29.js`, `chemVent`), the search picked `4 4 4 4 15 0 8 7` (marker, then a domain whose
     reaction is 15 → 0), the most downhill reaction weighted by the square's 15s;
   - founded in 20 of 20 seeds (11–30) on b4ceffa;
   - births in the first 20 ticks are few (about 100–400), but reaction income starts at tick 1 (6.8 a tick for the
     ring) and the colony reaches 15,000–50,000 cells by tick 1,000.

   This is the vent's version of what the other worlds already do. It is option 1 of 13 November ("a chemotroph
   inoculum"). It also stops founding from resting on the start-up ambient light, which is not glow and not chemistry.
2. **Not recommended:** the sunlit pigment gene in the vent founder (0 of 10). The search finds an uphill pigment
   reaction that the founder pays for out of its store, so births are fewer still (about 0–190 by tick 20).
3. **Other options, not tested:**
   - exempt the vent from the pigment requirement (`pigBase` 1 in the vent): back to about a quarter of seeds, still
     resting on the start-up light;
   - autoRestart on (the page's default), which reseeds a fizzled start up to 20 times. With about 0.25 a try, that
     founds almost surely, and it may be why nobody saw the break in the page. But it hides the founding rate.
4. **Two bugs, independent of the vent:**
   - `dishSetup` making a gene marker in a third of dish founders (section 3);
   - the coat arrays on a larger world (section 6).

## Waits on Justin
- Whether the vent founder gets a chemotroph gene (proposal 1), or another route.
- The two bug fixes (dish founder line; coat arrays on resize). Both are page code, so they are for the cloud
  session once approved.
- Report 17 stays the dish baseline as measured here. Once the dish founder is fixed, a re-run of seeds 2, 3, 4 and 6
  (about 5 minutes) would confirm it.

## Files
- **Harness** (`D:\labyrinth\automata\jgol_2026-11-13\test\`):
  - `validate29.js`: `validate17.js` plus gene counts;
  - `vent29.js`, `vent29_driver.py`: the vent runs, with the test options `P`, `pigVent`, `chemVent` and `coatFix`;
  - `dishfounder29.js`: the dish founder's line;
  - `sizeprobe29.js`: which arrays keep the old size after `allocWorld`;
  - `size29.html`: the page's own world size at a given window size;
  - `task29_runs.cmd`, `task29_vent.cmd`, `task29_ablate.cmd`, `task29_final.cmd`, `task29_extra.cmd`: the queue jobs.
- **Analysis** (`D:\labyrinth\automata\jgol_2026-11-13\popdish\`):
  - `task29_analyze.py`: counts, shape, lean and figures, from `task17_analyze.py`;
  - `task29_genes.py`: the gene shares and `29_multigene.png`;
  - `vent29_summary.py`, `vent29_budget.py`, `vent29_fig.py`: the vent tables and figures.
- **Results** (`D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task29\`):
  - `pages\`: 15 page copies;
  - `dish\`: 36 runs;
  - `bisect\`, `ablate\`, `final\`, `extra\`: the vent runs and their logs and job lists;
  - `dishfounder\`, `size\`, `sizeprobe\`: the probes;
  - `analysis\`: `task29_summary.json`, `task29_measures.json`, `task29_genes.json`, `29_vent_first_ticks.json`,
    `29_vent_founding.json`, and the figures.
- **Figures in this folder:**
  - `29_dish_sugar1.png`, `29_dish_sugar3.png`, `29_dish_sugar10.png`;
  - `29_closeup_sugar1.png`, `29_closeup_sugar3.png`, `29_closeup_sugar10.png`;
  - `29_multigene.png`, `29_vent_first_ticks.png`, `29_vent_founding.png`.
