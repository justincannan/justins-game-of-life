# Report on task 28: the population model starts (task 22, item 3)

From: gpu session, 16 November 2026. Step 1 written about 11:45 New York; step 2 below it.

Measurements are measurements. The models, their constants and every reading are proposals (Claude's); Justin decides.

## Step 1: the per-cell-store model's birth rate

### In short
- **The rule the model got wrong is the chemistry income.** Task 22 fitted the income as a smooth function of the
  molecules' energy per active cell, c = 0.0067 x/(x + 4.25), and gave each cell a fresh random draw every tick
  (exponential about that mean). On the page neither holds. The income comes from the inoculum's one reaction
  (domReact), kind 15 to kind 0, at a rate set by Michaelis-Menten with the product competing:
  f = S/(rxKm + S + P). So it is high on fresh agar and falls where the product has built up.
- **Measured on the page (probe28d):** a cell's income hardly changes from tick to tick. Over 50 ticks its per-call
  variance is close to 0. The spread between cells is steady, with cv 0.47 (sugar 1), 0.49 (sugar 3) and 0.85
  (sugar 10) in ticks 1-250. The square sets it: cells in the same square have the same income to within the
  probe's resolution, while the program explains little.
- **The fix (proposal):** the model now runs the page's reaction itself. It tracks two molecule kinds per square,
  spreads them as the page does, and has no fitted income function and no per-call noise. The constants are the
  page's own (section 1.3). A second, smaller mismatch was also fixed: the page feeds the cells of a square first
  come, first served in random order, where task 22 shared a short square equally.
- **With the fix the model grows like the page at sugar 3** (figure `28_step1_growth_sugar3.png`; mean of 6 seeds,
  page 12):
  - live places 1,420 / 1,800 / 2,520 at ticks 250 / 500 / 1,000, against the page's 1,118 / 1,588 / 2,889;
  - task 22's model had 536 / 480 / 496;
  - radius r95 44 / 63 / 105 against the page's 39 / 66 / 107.
- **Where it still differs:**
  - **After tick 1,000** it crashes faster than the page: 480 live at tick 2,000 against 1,442. The model's remains never
    break down and its chemistry has no mutant programs.
  - **At sugar 1** it is about half the page's size after tick 500.
  - **At sugar 10** it grows larger early (23,212 live at tick 250 against 14,441) and dies off earlier.
- **Per-cell rates now match within about 30%** (section 1.4): births, going still, stores above 0.4 and below 0.03,
  income and its steady spread, and coat.
- **Branching verdict and ingredient ranking both hold** (section 1.5).
  - With all three ingredients on, the fixed model now branches like the page at the page's size: thin arms with
    active tips, footprint cover 0.22 against 0.15, arms 2.9-3.0 places wide.
  - (b) gliding only while coated still matters most, (c) sugar-paid births next, and (a) going still by the store
    not at all.
- **Not used:** the page's re-baseline on the stage-1 page (task 29). This step uses the page at commit 821a258, the
  page of task 17's baseline and of probe22 (copied to `results/2026-11-16/task28/page821/`). Stage 1 changes the
  genome and the reactions (8 reactions), so the chemistry numbers here would need re-measuring on the new page.

### 1.1 How it was found (measurements, page at 821a258, port 8796, CPU queue)
Six read-only probes, 3 seeds each, 256 x 256, glide 0.1, the page's random visiting order. Results:
`results/2026-11-16/task28/probe28*/`.
1. **probe28.js, the birth bookkeeping** (sugar 1, 3, 10; 1,000 ticks). For every active cell after the feeding loop, it
   records whether it has an empty place to divide into, whether it could pay from its store (E >= 0.4032) or from the
   daughter's square, and whether it divided.
   - About 0.59 of active cells have a target, on the page and in task 22's model alike.
   - Of those, **0.146 could pay from the store on the page against 0.030 in task 22's model** (sugar 3, ticks 1-250).
     This was the first sign.
   - On the page, **60-90% of chosen parents are then refused by payChem** (the daughter's square lacks a molecule kind
     of its compound; probe28b). Task 22's model has no such refusal. The page tries about 0.020 births per active
     cell-tick and makes 0.0074.
2. **probe28b.js, the sugar at the front.** After feeding, 86% of front cells' squares hold under 0.001 sugar on the
   page (97% in task 22's model). The target's square can feed a cell (en x eeff >= ZCOST) in 12.5% of cases on the
   page, against 3.5%.
3. **probe28c.js, clumps.** Only 1.5% of active cells are in a body in ticks 1-250 at sugar 3, and no soma forms.
   Clumps are not the cause early.
4. **probe28d.js, how steady a cell's income is** (sugar 1, 3, 10; 1,000 ticks; 50-tick blocks; cells active and unmoved
   for the whole block).

   | sugar | ticks | mean income per call | cv of the cells' means | per-call variance within a cell | variance within a square | within a program |
   |---|---|---|---|---|---|---|
   | 1 | 1-250 | 0.0054 | 0.47 | ~0 | ~0 | 0.75 of total |
   | 3 | 1-250 | 0.0050 | 0.49 | ~0 | ~0 | 0.8 of total |
   | 3 | 251-1,000 | 0.0051 | 0.59 | ~0 | ~0 | 0.9 of total |
   | 10 | 1-250 | 0.0031 | 0.85 | ~0 | ~0 | 0.8 of total |

   ("~0": below the probe's printed resolution of 1e-6, against totals of 4-10e-6.)
5. **probe28e.js:** the page's birth-place test can also pass on ambient light (amb >= ZCOST). In the dish amb is 0
   throughout, so only the sugar half counts. ZCOST is 0.0024. Task 22's model used the cell's upkeep 0.0028; it now uses
   0.0024.
6. **probe28f.js, store-paid births** (sugar 3). A cell that can pay from its store has a feedable target in 0.245 of
   ticks on the page. Once it has one, it is chosen in 0.78 of them. Task 22's model, even with the feeding fixed:
   0.09 and 0.71.

   So the page's store-rich cells sit beside squares that still hold sugar. That is the fresh front: fresh agar has
   both the sugar and the unused substrate. Task 22's income ignored freshness.

### 1.2 What did not explain it (tried in the model, 2-3 seeds, 260-2,000 ticks)
- **First-come feeding alone** (the page's order; `--feed order`). Stores of 0.4 or more among front cells rose from
  0.055 to 0.125 (page 0.29). Growth was unchanged: 501 live places at tick 500, against task 22's 480 and the page's
  1,588.
- **A steady random factor per square** (gamma, cv 0.3-0.7) in place of the per-call draw, with cv 0.6 matching the
  page's spread (0.48 against 0.49). The front's sugar and the store fractions came close to the page's. Births went
  only to 0.0061, and the colony to 516 live at tick 500, because the rich squares were not where the sugar was.
- **The inoculum's burst:** both page and model jump from 248 to about 660-780 cells in 5 ticks. The page keeps
  growing after it; task 22's model did not.

### 1.3 The change (proposal; `popdish/pop28_store.py`, a new file; `pop22_store.py` is unchanged)
- **Chemistry, the page's reaction** (`--chem kinds`, default). It replaces the fitted c(x) and the 89-per-square
  energy pool.
  - Per coarse square: S = kind 15 (the substrate of rx 240) and P = kind 0 (its product).
  - Both are laid at dishFood 0.5 x chemCap, chemCap = chrich 45 x ABUND[k] x 0.62 x (1 + 0.4 bump). ABUND is 0.8 for
    kind 15 and 1 for kind 0. The bump is a Gaussian about the plate's centre with sd 0.18 W (chemCapFill, dish).
  - Both spread at 0.24 x (mean of 4 - own) every second tick (chemStep).
  - Each active cell's call: f = S/(1 + S + P) (rxKm 1); the call takes amt = 0.2 f of S (rxRate 0.2, chunit 1,
    strength 1).
  - It yields 0.08 f x (RXE[15] - RXE[0]) of light (rxE 0.08; RXE[k] = ln p_k/ln 53, so 1 - ln 2/ln 53 = 0.825).
  - Of the product, 0.3 is kept as coat (coatFrac), giving coat 0.3 amt RXE[0]; 0.7 goes back to the square as kind 0.
  - A square short of S serves its calls in proportion.
  - Checks against the page: molecule energy lost per unit of income 0.165 f/0.066 f = 2.5 (probe22 measured 2.5-3.4);
    coat per unit of income 0.16 (probe22: 0.16-0.70).
- **No per-call spread** (`--cnoise 0`): the spread between cells now comes from the squares' S and P.
- **Feeding first come, first served** (`--feed order`). Within each square, cells take what they want (up to 0.3
  sugar) in a random order until the sugar runs out (the page's visitOrder and burn).
- **Birth-place test** at ZCOST 0.0024 (`--placecost`).
- **Unchanged from task 22:** everything else, including task 07's death rates and no payChem. The page's later
  mutant programs (5% of births) and their other reactions are left out.
- **Nothing was fitted to the colony's counts or shape.** The one calibration tried, the gamma factor's cv 0.6, was
  dropped with the gamma factor.

### 1.4 Per-cell rates, page against the fixed model (sugar 3)
Per active cell-tick; the page is probe22 (3 seeds), the model is 6 seeds. Each cell gives page / fixed model, with
task 22's model in brackets where report 22 gave it.

| sugar | ticks | births | going still | chemistry income | income cv (50 ticks) | store mean | store > 0.4 | store < 0.03 | glides |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1-250 | 0.0056 / 0.0056 (0.0039) | 0.0044 / 0.0027 (0.0008) | 0.0054 / 0.0061 | 0.47 / 0.41 | 0.32 / 0.34 | 0.28 / 0.28 | 0.020 / 0.013 | 0.0003 / 0.0002 |
| 1 | 251-1,000 | 0.0034 / 0.0034 (0.0020) | 0.0006 / 0.0010 | 0.0068 / 0.0065 | 0.28 / 0.22 | 0.32 / 0.26 | 0.30 / 0.11 | 0.004 / 0.005 | 0.0020 / 0.0006 |
| 3 | 1-250 | 0.0074 / 0.0088 (0.0052) | 0.0045 / 0.0036 (0.0009) | 0.0051 / 0.0065 | 0.49 / 0.56 | 0.31 / 0.31 | 0.29 / 0.26 | 0.019 / 0.015 | 0.0011 / 0.0003 |
| 3 | 251-1,000 | 0.0067 / 0.0066 (0.0034) | 0.0033 / 0.0029 (0.0004) | 0.0062 / 0.0061 | 0.59 / 0.45 | 0.32 / 0.27 | 0.31 / 0.15 | 0.016 / 0.016 | 0.0054 / 0.0004 |
| 10 | 1-250 | 0.0178 / 0.0152 (0.0114) | 0.0057 / 0.0059 (0.0005) | 0.0053 / 0.0055 | 0.85 / 0.71 | 0.29 / 0.27 | 0.27 / 0.19 | 0.019 / 0.020 | 0.0007 / 0.0000 |
| 10 | 251-1,000 | 0.0079 / 0.0006 (0.0023) | 0.0141 / 0.0200 (0.0011) | 0.0027 / 0.0011 | 1.21 / 0.79 | 0.24 / 0.19 | 0.15 / 0.04 | 0.049 / 0.065 | 0.0013 / 0.0000 |

- **Births and going still** now agree within about 20% in every window but sugar 10 late, against factors of 1.4-13
  before. At sugar 10 late the model's colony has already run out (all its cells still by tick 500); the page keeps a
  few active cells.
- **Glides are now 3-15 times too few.** The coat comes only from the inoculum's reaction (0.0010 per active cell-tick
  against the page's 0.0013-0.0029). The page's mutant programs and coat from sugar are left out. Task 22's model glided
  at about the page's rate because its coat constant was fitted.
- **Feeding order hardly matters once the chemistry is right.** With task 22's equal share the fixed chemistry grows the
  same: 1,802 live at tick 500 against 1,800 (`kinds_share`).

### 1.5 Branching and the ingredients, with the fix
Shape measures as in report 22 (`task22_analyze.py`, unchanged), sugar 3, mean of seeds (page 12, model 6). Footprint
cover is the share of the circles at 0.5-0.9 r95 covered by live places or remains; isolated is the share of live places
with no live neighbour.

| | tick | r95 | live (active) | rough | dim | arms | width | footprint cover | isolated |
|---|---|---|---|---|---|---|---|---|---|
| page | 500 | 66 | 1,588 (803) | 26.9 | 1.48 | 4.8 | 3.2 | 0.15 | 0.05 |
| page | 1,000 | 107 | 2,889 (1,184) | 41.4 | 1.45 | 6.5 | 2.9 | 0.15 | 0.13 |
| all on | 500 | 63 | 1,800 (1,001) | 30.9 | 1.51 | 7.3 | 2.9 | 0.26 | 0.06 |
| all on | 1,000 | 105 | 2,520 (1,367) | 38.4 | 1.38 | 5.6 | 3.0 | 0.22 | 0.14 |
| (a) off | 1,000 | 107 | 2,511 (1,247) | 38.6 | 1.39 | 6.0 | 2.8 | 0.20 | 0.14 |
| (b) off | 500 | 117 | 9,026 (3,668) | 83.0 | 1.72 | 13.7 | 2.6 | 0.36 | 0.16 |
| (b) off | 1,000 | 118 | 2,268 (0) | 50.6 | 1.32 | 0.9 | 2.4 | 0.35 | 0.64 |
| (c) off | 1,000 | 60 | 1,474 (534) | 27.4 | 1.48 | 5.5 | 3.2 | 0.45 | 0.10 |
| all off | 1,000 | 117 | 9,293 (2,034) | 79.0 | 1.71 | 15.1 | 2.8 | 0.59 | 0.14 |

- **By eye** (`28_step1_sugar3.png`; seed 1; the page on top, then all on, (a) off, (b) off, (c) off, all off; the
  figures keep task 22's title line):
  - **All on and (a) off** grow 10-15 thin arms with green active tips from the inoculum ring, very like the page's ticks
    500-1,000.
  - **(b) off** fills the plate with a scatter by tick 500.
  - **(c) off** is a slower, ragged blob with short thick arms.
  - **All off** is a filled disc.
  - Unlike the page, the model's footprint stays grey with remains, since they never break down.
- **Ranking:** as in report 22.
  - (b) off gives a scatter (isolated 0.16 at tick 500, rising to 0.64), growing 2-5 times faster.
  - (c) off gives a denser, slower colony (cover 0.45 against 0.22).
  - (a) changes nothing measurable.
- **Size no longer limits the verdict.** Report 22 warned that its branching might owe something to the model's slow
  growth. The fixed model grows at the page's pace and still branches, with arms as thin as the page's.
- Sugar 1 and 10: `28_step1_sugar1.png`, `28_step1_sugar10.png`. All measures:
  `results/2026-11-16/task28/step1/analysis/task22_item2_summary.json`.

### Files (step 1)
- Model: `D:\labyrinth\automata\jgol_2026-11-13\popdish\pop28_store.py` (new). Figure script:
  `popdish\task28_step1_fig.py`. Queue scripts: `popdish\task28_s1_*.cmd`.
- Probes: `D:\labyrinth\automata\jgol_2026-11-13\test\probe28.js`, `probe28b.js` … `probe28f.js`, run by
  `test\task28_probe*.cmd` through `rates_driver.py` on port 8796. The page copy: `results\2026-11-16\task28\page821\`.
- Results: `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task28\`: `probe28*`, `step1\` (`order`,
  `cal`, `kinds`, `kinds_var`, `kinds_share`, and the analysis).

## Step 2: the population model (task 22, item 3)

### In short
- **No region of Matsushita's diagram other than the compact ones appears at a realistic diffusion length.** The
  population model built from the page's per-cell rules grows compact colonies everywhere in the ranges run (D_n =
  6.7e-6 cm²/s). No DLA-like, dense-branching or concentric-ring region appears.
  - **Hard agar:** Eden-like by measure, but the edge is smooth (roughness 1.00-1.02 x a circle's), not Eden's rough
    one.
  - **With motility:** homogeneous discs, with a diffuse rim when D_b is large (figure `28_phase_main.png`).
  - **Low peptone (0.1 g/l or less) on hard agar:** the colony stops at about 1 mm and starves (marked "none").
- **Why (reading):**
  - At this scale the nutrient spreads about 1.4 mm in one generation, so it stays nearly even over the whole 11 mm
    plate. The tips are never shorter of nutrient than the centre, so nothing destabilises the edge.
  - The page's upkeep, paid by every live cell every tick, drains the plate as a whole. At low peptone it runs out
    before the colony is large.
- **Only when the nutrient spreads 70 times or more slower does anything else appear:**
  - **At Golding et al.'s assumed 1e-7 cm²/s,** 0.06 g/l on hard and nearly hard agar gives a round colony with radial
    streaks of dense and sparse cells.
    - The measures read it as dense branching: 38-40 runs across the circle at 0.7 r95, fill 0.45, box dimension
      1.67-1.72.
    - By eye it is a disc with streaks, not separate branches: a borderline DBM-like case.
    - Once, a single bright ring (1 g/l, D_b 1e-4).
  - **At 1e-9 and at the page's own 5e-12 cm²/s:** a "hollow front" at 0.06-0.1 g/l on hard agar. A dense active band
    moves out over a starved, almost empty interior. This shape is not in Matsushita's diagram.
- **Growth times are of the experiments' order, though nothing was fitted to them.** Compact colonies reach half the
  plate's half-width (2.8 mm) in about 6.6 days on hard agar and 0.5 days at D_b = 0.01. Golding et al. summarise
  Matsushita's compact colonies at intermediate agar as growing "in about a week", and those on soft agar in half a
  day.
- **Six layers of cells a place** (Golding et al.'s density unit) give the same compact shapes, only smaller.

### 2.1 The model (proposal; `popdish/pop28_pop.py`, a new file)
- **Space.** A square plate of 256 x 256 patches, no flux through the rim. Each patch holds 32 x 32 places, one cell per
  place (the page's monolayer, K = 1,024 cells a patch).
- **Cells.** Each patch counts its active and still cells by store class (17 classes, 0 to 0.4 in steps of 0.025),
  plus remains that block places. One tick is the page's tick.
- **The page's per-cell rules,** in the page's order, as patch rates:
  1. the agar's sugar spreads;
  2. every second tick a living cell with store > 0.01 leaks 0.01 into its patch's sugar (energyStep);
  3. **feeding:**
     - an active cell pays upkeep 0.0028 (a still cell 0.1 of it);
     - it then tops its store up towards 0.4, by at most 0.06 a tick (a still cell 0.015), at 0.4 store per sugar
       and at most 0.3 sugar a tick;
     - a patch's cells are fed first come, first served (step 1), so each is fed in full with chance min(1, S/W);
     - an active cell still below 0 goes still at 0;
  4. **births:**
     - an active cell with E >= 0.2032 finds an empty neighbouring place with chance 1 - (1 - f)^8, where f is the free
       share of the places it can reach;
     - 1.5/h of those places lie in the 8 neighbouring patches, weighted 4 : 1 orthogonal to diagonal, the rest in its own;
     - the daughter's patch must hold the page's 0.5 sugar per 16 places; the birth burns 0.5 sugar there;
     - the parent pays 0.0032, and parent and daughter keep half each;
  5. deaths, active 0.0029 and still 0.0024 a tick, leaving remains;
  6. **motility:** active cells hop into free room in the neighbouring patches with spreading coefficient D_b;
  7. sporePass: an active cell below 0.03 goes still at 0.15 a tick; a still cell above 0.3 wakes at 0.03 a tick;
  8. remains break down at 0.002 a tick.
- **Noise:** births, deaths, feeding, going still and waking are drawn with their binomial spread. A class holding less
  than one cell is rounded to 0 or 1 at random.
- **One nutrient, as in the experiments.** The page's chemistry income and coat are left out, so births are paid from
  sugar only. Also left out: payChem, mutation, and the opening into single cells.
- **Not fitted** to any colony's shape.

### 2.2 Constants and their sources
**Scale (sources; I checked abstracts, open copies and data pages only):**
- **A place is one cell's footprint, 1.36 µm** (the square root of 2.3 x 0.8 µm).
  - Length: *B. subtilis* in a poor medium, median 2.3 µm (Weart et al. 2007, via BioNumbers 100213; 4.7 µm in LB).
  - Width: 0.81-0.86 µm in four media (PMC106920, table 2).
- **A patch is 32 x 32 places, 43.5 µm.** The plate is 256 patches, 11.1 mm.
- **A tick is 25 minutes.**
  - In this model a well-fed cell with room divides every 2 ticks. That is the store's refill after halving: 0.1 to
    0.2032 at 0.06 a tick, less costs.
  - A generation of 50 minutes is the middle of the 30-73 minutes in PMC106920's four media. Golding et al. (1998) use
    25 minutes for optimal growth.
- **Nutrient diffusion, D_n = 6.7e-6 cm²/s:** sucrose in 2% agar, 0.72 of its value in water (Hannoun 1985, Caltech
  thesis, its table of diffusivities in gels). Glucose in water is also about 6.7e-6 cm²/s.
  - That is 531 patches² a tick. The diffusion length in one generation, sqrt(D_n x 50 min), is **1.4 mm, about
    1,000 cell lengths.**
  - The page's sugar spreads 0.4 places² a tick (report 22), about 5e-12 cm²/s at this scale. Its diffusion length in
    one generation is about 1 cell.
  - **The check run** uses the 1e-7 cm²/s that Golding et al. (1998, appendix) assume for "the diffusion coefficient of
    chemicals in agar": 8 patches² a tick, a diffusion length of 170 µm (125 cells) per generation.
  - **Two further checks:** 1e-9 cm²/s and the page's 5e-12 cm²/s, to see where the shapes change.
- **Nutrient level:** Golding et al. (1998, appendix) give 1 g/l of peptone as 0.3 mg/cm² of plate, and about 3e-12 g of
  nutrient used per cell per generation. With the page's 0.5 sugar per birth, 1 g/l is 947 sugar a patch, or 1.85
  cells' worth per place.
  - The page's sugar 3 (3 per 16 places) is therefore about 0.2 g/l; its sugar 10 is about 0.7 g/l.
  - The page's birth threshold (0.5 per 16 places) is 0.034 g/l.
- **Motility (agar firmness):** D_b is given as a multiple of 6.7e-6 cm²/s, the same multiple in every run, from 0 (hard
  agar: Golding et al. summarise that above about 0.8% agar *B. subtilis* OG-01 cannot move on the surface) up to 0.01
  (D_b = 6.7e-8 cm²/s).
  - The real swimming cells of soft agar spread faster than the top of this range. It was capped by run time: 23
    substeps a tick at 0.01.

**The page's rules** (`build/justins_game_of_life.html` at 821a258, as in step 1):
- upkeep 0.0028 (still cells 0.1 of it); leak 0.01 every second tick above 0.01;
- top-up towards 0.4 at 0.06 a tick (still 0.015), 0.4 store per sugar, at most 0.3 sugar a tick;
- births: E >= 0.2032, the daughter's square holds at least 0.5 per 16 places, 0.5 sugar burnt, 0.0032 paid, stores halved;
- going still below 0 at once, below 0.03 at 0.15 a tick; waking above 0.3 at 0.03 a tick;
- deaths 0.0029 (active) and 0.0024 (still) a tick (probe22); remains break down at 0.002 a tick.

**The model's own choices (proposal, not measured):**
- the 1.5/h share of neighbour places across a patch edge (geometry of a 32 x 32 patch, Moore neighbours);
- the 4 : 1 weights (the isotropic 9-point stencil; with 4 neighbours the colonies grew square);
- the inoculum: a disc of radius 4 patches (0.17 mm), half full, stores 0.4;
- the noise.
- For the measures, a patch counts as colony when its footprint (live cells plus remains) reaches 1% of its places.

### 2.3 Runs
All runs: seed 1 (one per setting), up to 6,000 ticks. A run stops when r95 reaches 0.85 of the half-width, or 200
ticks after the last active cell. Each run is measured at its largest (the record tick with the most live cells).
- **main:**
  - D_n = 6.7e-6 cm²/s;
  - peptone 0.04, 0.06, 0.1, 0.3, 1, 3 and 10 g/l (38-9,470 sugar a patch; the page's birth threshold is 32);
  - motility D_b = 0, 1e-4, 1e-3 and 1e-2 x 6.7e-6 cm²/s;
  - 28 runs.
- **golding:** as main, D_n = 1e-7 cm²/s.
- **slow9:** as main, D_n = 1e-9 cm²/s.
- **pageD:** as main, D_n = 5e-12 cm²/s.
- **layers6:** as main with 6 cells a place; peptone 0.04, 0.1, 0.3, 1 and 3 g/l; D_b = 0 and 1e-3.
- **Changes during the runs:**
  - **Edge bug (my error, fixed and redone):** in the first main runs at D_b = 0.01, cells were copied in from beyond
    the plate's edge.
  - **Snapshot and stopping (redone):** the hard-agar runs at 0.04-1 g/l were rerun with the 'peak' snapshot and the
    shorter stop.
  - **Motility units:** D_b was made independent of D_n before the check grids ran, so motility means the same in
    every grid.
  - **Discarded runs** are kept in `step2/old_main_firstcode/`.
- CPU queue, labels `jgol28-s2-*`; from 15 seconds to 15 minutes a run.

### 2.4 Results
Classes are read from the measures by the rules written in `task28_step2_analyze.py` before the main grid was
analysed. The "hollow front" class and the footprint (live cells plus remains) were added after the first look at the
check grids. Each class is checked by eye. "fill" is the colony share of the disc of radius r95, where a patch counts
when its footprint reaches 1% of its places.

**main (D_n = 6.7e-6 cm²/s), class by measure, with the reading by eye in brackets where it differs.** Rows are
peptone; columns are D_b / 6.7e-6 cm²/s.

| g/l | 0 | 1e-4 | 1e-3 | 1e-2 |
|---|---|---|---|---|
| 10 | Eden-like (smooth disc) | disc | disc | disc |
| 3 | Eden-like (smooth disc) | disc | disc | disc |
| 1 | Eden-like (smooth disc) | disc | disc | disc |
| 0.3 | Eden-like, stops at r95 42 | disc, stops at 50 | disc | Eden-like (diffuse disc) |
| 0.1 | none (stops at r95 25 of 128) | disc, stops at 38 | disc | Eden-like (diffuse disc) |
| 0.06 | none (22) | disc, stops at 35 | Eden-like (diffuse disc) | Eden-like (diffuse disc) |
| 0.04 | none (20) | none (28) | Eden-like (diffuse disc) | Eden-like (diffuse disc) |

- **Box dimension** 1.57-1.94, higher the more filled.
- **Roughness** 1.00-1.17 x a circle's for the compact colonies. The motile ones at low peptone reach 1.4-5.3, from a
  diffuse rim, not from branches.
- **Arms:** one run across every circle at 0.7 r95 in all 28 (no arms).
- **Rings:** none by the profile test. Stop-go CV 0.00-0.15 where defined, so the front advances steadily.
- **Time to reach half the half-width** (r95 64 patches, 2.8 mm): 6.6 days on hard agar (1-10 g/l), 4.0 days at 1e-4,
  1.4 days at 1e-3, 0.5 days at 1e-2.

**Checks with slower nutrient spreading.** Only settings that differ from compact disc, Eden-like or none are listed.

| grid | setting | class by measure | by eye | fill | box dim | runs at 0.7 r95 | share in outer fifth |
|---|---|---|---|---|---|---|---|
| D_n 1e-7 | 0.06 g/l, hard | dense branching | round, radial streaks | 0.45 | 1.72 | 40 | 0.47 |
| D_n 1e-7 | 0.06 g/l, D_b 1e-4 | dense branching | round, radial streaks, emptied centre | 0.45 | 1.67 | 38 | 0.40 |
| D_n 1e-7 | 1 g/l, D_b 1e-4 | disc | disc with one bright ring at half radius | 1.00 | 1.91 | 1 | 0.30 |
| D_n 1e-9 | 0.06 g/l, hard | hollow front | active band over an emptied interior | 0.19 | 1.54 | 0 | 0.81 |
| D_n 1e-9 | 0.1 g/l, hard | hollow front | the same, interior less empty | 0.56 | 1.77 | 105 | 0.69 |
| D_n 1e-9 | 0.06 g/l, D_b 1e-4 | dense branching | sparse disc, faint streaks | 0.76 | 1.86 | 10 | 0.48 |
| D_n 5e-12 | 0.06 / 0.1 g/l, hard | hollow front | as at 1e-9 | 0.42 / 0.78 | 1.69 / 1.83 | 86 / 1 | 0.74 / 0.62 |

- **The 1e-9 and 5e-12 runs grow to the plate's edge,** even at 0.06-0.3 g/l, where the main runs stop at 1 mm.
  - With slow spreading, the front feeds on fresh agar while the interior starves on its own.
  - With fast spreading, the interior's upkeep draws on the whole plate.
- **6 layers a place:** compact everywhere and smaller than the monolayer: Eden-like to r95 34-54 at 1-3 g/l, and none
  at 0.3 g/l or less on hard agar.

**Figures:**
- `28_phase_main.png`, `28_phase_golding.png`, `28_phase_slow9.png`, `28_phase_pageD.png`: every run of a grid as a
  picture at its largest, bordered by its class.
- `28_examples.png`: eight runs at full resolution.

**Against Matsushita's diagram.** Sources: Fujikawa and Matsushita; Ohgiwari, Matsushita and Matsuyama 1992; Matsushita
et al. 1998; summarised by Golding et al. 1998.

| region | in the experiments | here |
|---|---|---|
| A: DLA-like | hard agar, below about 1 g/l peptone, grows in about a month | absent |
| B: Eden-like | hard agar, high peptone | compact on hard agar, but the edge is smooth, not rough |
| C: concentric rings | about 0.75% agar, high peptone | absent; one single ring at D_n 1e-7 |
| D: homogeneous disc | soft agar, high peptone | present wherever cells move |
| E: dense branching | soft agar (below 0.5%), low peptone | absent at the realistic D_n; borderline radial streaks at 1e-7 |
| (none) | | small starving colonies at 0.1 g/l and below on hard agar |
| (hollow front) | not in the diagram | at D_n 1e-9 or slower, low peptone, hard agar |

### 2.5 Reading (proposal)
- **The page's per-cell rules alone do not make Matsushita's branched regions at a realistic diffusion length.** In the
  experiments, DLA and dense branching are taken to come from growth limited by nutrient diffusion (Fujikawa and
  Matsushita; Golding et al.). Here the nutrient is never more limiting at the tips than elsewhere, for two reasons:
  - the colony is a monolayer of cells that each consume little, on an 11 mm plate;
  - the page's upkeep then empties the plate evenly.
- **What made the page itself branch (step 1) works at the scale of single cells.** Single cells sit at the tips. They
  glide only when coated. Their births are paid from a store fed by a reaction that is richer on fresh agar. A patch of
  1,024 cells averages all of that away, and this model's single nutrient has neither reaction nor coat.
- **Possible next steps (proposals; each changes the scope, so each is Justin's call):**
  1. Give the population model the page's second income as patch fields: the molecules' reaction with product
     inhibition, and the coat it makes. That is the ingredient step 1 showed sets the page's growth. Then rerun the
     diagram.
  2. Use a plate of the experiments' size (8.8 cm) with coarser patches. That tests whether the starvation of the whole
     plate is an effect of size.
  3. Lower the upkeep of still cells, or let them leak nothing. A still cell now pays 0.1 of the upkeep and still leaks.
     This bears on the page too, not only on the model.
- **None of these would be fitted to a shape.** The opening into single cells waits, as the brief says, until the shapes
  are right.

### Files (step 2)
- **Model:** `D:\labyrinth\automata\jgol_2026-11-13\popdish\pop28_pop.py` (new). Grid runner:
  `popdish\task28_step2_grid.py`.
- **Analysis and phase figures:** `popdish\task28_step2_analyze.py`. Example pictures: `popdish\task28_step2_examples.py`.
- **Queue scripts:** `popdish\task28_s2_main.cmd`, `_golding`, `_slow9`, `_pageD`, `_layers`, `_redo`.
- **Results:** `D:\labyrinth\automata\jgol_2026-11-13\results\2026-11-16\task28\step2\`
  - per grid, one JSON (units, a record every 10 ticks) and one `.npz` (peak, end and radius snapshots) per run;
  - `analysis\`: `task28_step2_measures_<grid>.json`, `<grid>.txt`, and the phase figures.
- **Figures in this folder:** `28_phase_main.png`, `28_phase_golding.png`, `28_phase_slow9.png`, `28_phase_pageD.png`,
  `28_examples.png`.

## Sources (abstracts, open copies and data pages only)
- **Golding I, Kozlovsky Y, Cohen I, Ben-Jacob E (1998),** Physica A; open copy arXiv cond-mat/9807088.
  - Units appendix: 1 g/l is 0.3 mg/cm²; about 3e-12 g of nutrient per cell per generation; an assumed D_n of
    1e-7 cm²/s.
  - Its summary of the *B. subtilis* diagram and of the growth times.
- **Matsushita M, Fujikawa H (1990),** Physica A: DLA, box dimension 1.73 ± 0.02. **Fujikawa H, Matsushita M (1991),**
  J Phys Soc Jpn 60:88. Abstracts.
- **Ohgiwari M, Matsushita M, Matsuyama T (1992),** J Phys Soc Jpn 61:816: five types. Abstract, via search.
- **Matsushita M et al. (1998),** Physica A 249:517: regions B and D. Abstract.
- **Wakita J et al. (2001),** J Phys Soc Jpn 70:911: concentric rings by migration and consolidation. Abstract, via
  search.
- **Hannoun BJM (1985),** Caltech thesis: sucrose in 2% agar, 6.7e-6 cm²/s. Taken from a search snippet of its table; I
  did not open the thesis.
- **Weart RB et al. (2007),** via BioNumbers 100213: *B. subtilis* 2.3 µm long in minimal sorbitol. **PMC106920,**
  table 2: widths 0.81-0.86 µm, generation times 30-73 min.

## Waits on Justin
1. **The population model's next ingredient** (section 2.5). Should it carry the page's molecule reaction and coat as a
   second income, keep one nutrient as the experiments do, or go another way?
2. **The realistic diffusion length gives compact colonies under the page's rules.** Should the model's scale be
   revisited: plate size, colony thickness, the upkeep of still cells?
3. **Step 1's two findings bear on any coarse model of the page:**
   - the page's income is set by the reaction's product inhibition in the square, not by the molecules' energy;
   - the page's payChem refuses 60-90% of chosen births.

   Both would need measuring again on the stage-1 page (8 reactions), which task 29 is re-baselining.
4. Nothing on the page was changed, and nothing on it was found broken in this task.
