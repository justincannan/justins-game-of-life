# 07: the population dish at 1,000 × 1,000 with two resources: report

From: gpu session (scheduled check), 14 November 2026. This answers `comms/to_gpu/2026-11-14_07_popdish-fine-two-resources.md`.

- **Measurements are measurements.** The model's form, its one calibrated constant and the readings are proposals.
- **The page compared against:** report 03's page runs (`day9_repo/validate_page`, page sugar 1, 3, 10, gliding 0.1,
  3 seeds) and 03a's shape table. The page was not changed.

## In short

1. **No branching appears**, at any sugar level or diffusion rate tried. At one place per pixel the model grows as a
   compact, ragged disc (an Eden-like blob with a fringe of active cells). The page's dendrites at sugar 3 and its thin
   arms at sugar 1 do not appear.
2. **Slowing the sugar's diffusion changes almost nothing.** Over a 30-fold range (D 0.025 down to 0.0008) the
   pictures look the same, and the box dimension of the live places stays at 1.7–1.9 (the page: 1.2–1.5 at sugar 1
   and 3).
3. **The reason (proposal):** births paid by chemistry. With the fitted rates, chemistry pays for births wherever
   there are molecules, and the molecules are everywhere and do not diffuse. So growth is not limited by a diffusing
   resource, and a diffusion-limited instability has nothing to act on.
4. **A check without chemistry-paid births** (gc = 0, page-size plate): sugar 1 at the slowest diffusion comes close
   to the page in numbers (600 live cells, 314 active, box dimension 1.13 at tick 2,000; the page has 567, 364 and 1.17).
   But the picture is a sparse scatter, not branches.
5. **The model's counts do not match the page:** it overgrows at sugar 1 and 3 by 3–20 times. On the 1,000 × 1,000
   plate there is no crash at sugar 10 either, since the plate holds about 15 times the page's sugar.

## 1. The model (proposal)

`jgol_2026-11-13/popdish/pop2_gpu.py`: `popdish_gpu.py`'s rules, extended with the second field. Choices:
- **One square is one page place, holding at most one cell.** The page holds one cell per place, and task 03's fits use
  K = places per block. So pop.py's counts become 0 or 1.
  - Every birth goes to one of the 8 neighbouring places (the page's neighbourhood), chosen at random. It fails if
    that place is occupied or off the plate.
  - Active cells glide at 0.1 a tick into a random empty neighbour (the page's gliding, `glidePass`).
  - Remains keep their place.
- **Sugar and the molecules are kept per 4 × 4 coarse square,** as in the page.
  - Sugar starts at the page's level s per coarse square.
  - The molecules' stored energy (mE) starts at 89 per coarse square: the page's plate mean at its first snapshot.
  - The molecules do not diffuse or regrow.
- **Rates: task 03's two-resource fits** (`fit_two.json`), per active cell and tick. sb is block sugar (6.25 coarse
  squares to a 10 × 10 block). c is the chemistry income per active cell, from x = mE per active cell in the square.
  - c = 0.0065 · x/(x + 8.4)
  - division attempt: 6 × (0.238 · sb/(sb + 96.8) + 0.63 · c). A sugar-paid birth costs 1.49 page sugar, thinned
    where the square cannot pay.
  - going still: 0.0231 / (1 + sb/0.51 + c/0.00088)
  - waking: 0.00031 · sb/(sb + 2.4)
  - deaths: 0.0029 active, 0.0028 still. C2x's refit values, 0.00214 and 0.00229, came to light after the runs. The
    difference is small beside the mismatches below.
  - each unit of chemistry income takes 6.0 mE from the square.
- **The factor 6 on division is the one calibrated constant (proposal).**
  - Without it, the lattice grows far too slowly: 1,005 cells at sugar 10, tick 100, against the page's 2,657. Task
    03's block rates count every active cell, but on a lattice only cells with an empty neighbour can divide.
  - 6 was fitted to sugar 10 at tick 100 only (2,928 against 2,657).
  - Sugar 1 at tick 100 then agrees without further fitting (717 against 698).
- **Sugar diffusion:** n += D · lap(n) between coarse squares, with no flux through the rim.
  - D = 0.025 is the earlier folds' fitted block rate (Dn 0.016 per 10 × 10 block, about 0.4 places² a tick).
  - Slower rates used: 0.008, 0.0025, 0.0008, that is, about 1/3, 1/10 and 1/30 of it. The aim was to span the range
    where a diffusion-limited front should sharpen, while staying stable.
- **Runs:**
  - 1,000 × 1,000 (plate radius 480, about 4 times the page's), sugar 1, 3 and 10, four diffusion rates, 3 seeds,
    2,000 ticks, on the GPU queue (about 1 minute per setting).
  - The same at the page's own plate size (256 × 256, radius 121.6), for a like-for-like picture.
  - A check with gc = 0 (no chemistry-paid births) at the page's size, for D = 0.025 and 0.0008.

## 2. Pictures

One pixel per place, in 03a's colours: active green, still purple, remains grey, empty agar black. Seed 1, ticks 250,
500, 1,000 and 2,000; the page's dish is in the top row.
- `07_pagesize_sugar1.png`, `…3.png`, `…10.png`: the page's plate size, four diffusion rates.
- `07_fine_sugar1.png`, `…3.png`, `…10.png`: the centre 512 × 512 places of the 1,000 × 1,000 plate. The page's dish
  (256 × 256) is shown at the same scale.
- `07_pagesize_gc0_sugar1.png`, `…3.png`, `…10.png`: no chemistry-paid births.

**What they show (measurement):**
- **Every model run is a compact disc:** dense inside, a ragged fringe of active cells, and remains filling the
  centre. Slower diffusion makes the disc slightly smaller and sparser, not branched.
- **The page,** as in 03a, has branched arms at sugar 3 (ticks 500–1,000) and thin arms at sugar 1 (from tick 750).
- **Without chemistry-paid births,** at slow diffusion and sugar 1, the colony is a sparse cloud of cells and
  remains, about the page's size and count. But it has no arms.

## 3. Numbers, beside the page (mean of 3 seeds)

Live = active + still; active in brackets. Rough = perimeter over that of a circle of equal area. Dim = box-counting
dimension of the live places. Both are measured as in 03a.

**1,000 × 1,000 plate:**

| Sugar | Tick | Page | D 0.025 | D 0.008 | D 0.0025 | D 0.0008 |
|---|---|---|---|---|---|---|
| 1 | 500 | 387 (145), rough 15.8, dim 1.44 | 3,140 (1,901), 34.7, 1.70 | 2,770, 34.0, 1.70 | 2,603, 34.0, 1.71 | 2,325, 33.6, 1.71 |
| 1 | 2,000 | 567 (364), 20.4, 1.17 | 17,063, 90.9, 1.70 | 15,705, 89.2, 1.70 | 14,311, 87.8, 1.70 | 12,576, 83.5, 1.68 |
| 3 | 1,000 | 2,261 (1,349), 35.5, 1.43 | 14,882, 75.2, 1.80 | 14,010, 76.6, 1.79 | 12,428, 74.1, 1.81 | 11,037, 72.2, 1.79 |
| 3 | 2,000 | 1,561 (505), 36.4, 1.18 | 35,126, 123.9, 1.72 | 33,302, 125.2, 1.72 | 30,202, 122.5, 1.73 | 26,882, 118.2, 1.72 |
| 10 | 250 | 13,160 (8,167), 53.9, 1.78 | 9,719 (7,478), 41.3, 1.82 | 10,080, 44.0, 1.82 | 10,005, 45.8, 1.84 | 9,168, 44.8, 1.82 |
| 10 | 500 | 13,495 (631), 79.6, 1.78 | 28,529 (18,755), 80.6, 1.87 | 30,345, 85.9, 1.88 | 29,022, 86.4, 1.88 | 28,063, 86.3, 1.87 |
| 10 | 2,000 | 569 (45), 26.0, 0.80 | 178,509, 269.8, 1.76 | 170,222, 273.9, 1.75 | 170,245, 275.2, 1.75 | 171,590, 276.6, 1.76 |

**Page-size plate:**

| Sugar | Tick | Page | D 0.025 | D 0.0008 | gc = 0, D 0.025 | gc = 0, D 0.0008 |
|---|---|---|---|---|---|---|
| 1 | 1,000 | 418 (273), 17.0, 1.31 | 7,402, 56.7, 1.77 | 5,416, 53.1, 1.72 | 1,602 (900), 36.6, 1.54 | **324 (170), 18.6, 1.14** |
| 1 | 2,000 | 567 (364), 20.4, 1.17 | 5,638, 65.6, 1.54 | 8,163, 71.4, 1.63 | 3,247, 53.9, 1.47 | **600 (314), 25.5, 1.13** |
| 3 | 1,000 | 2,261 (1,349), 35.5, 1.43 | 14,377, 74.1, 1.80 | 11,611, 73.3, 1.78 | 5,732, 62.0, 1.69 | 2,181 (1,243), 45.1, 1.50 |
| 3 | 2,000 | 1,561 (505), 36.4, 1.18 | 2,000 (129), 46.7, 1.25 | 2,505 (204), 51.5, 1.32 | 2,036, 47.2, 1.26 | 2,088 (649), 47.4, 1.26 |
| 10 | 250 | 13,160 (8,167), 53.9, 1.78 | 9,752 (7,489), 41.1, 1.79 | 9,083, 44.5, 1.80 | — | — |
| 10 | 1,000 | 4,496 (52), 65.4, 1.53 | 7,249 (1,045), 78.9, 1.67 | 7,221 (950), 78.7, 1.67 | 5,684 (851), 73.3, 1.61 | 4,534 (598), 67.6, 1.54 |
| 10 | 2,000 | 569 (45), 26.0, 0.80 | 443 (7), 23.5, 0.72 | 438 (3), 23.3, 0.72 | 348 (7), 20.8, 0.63 | 278 (2), 18.7, 0.55 |

Full tables: `jgol_2026-11-13/results/2026-11-14/task07/figs/07_*_table.json`.

**Reading:**
- **On the page-size plate, sugar 10 has a crash, but later and shallower than the page's:** 1,045 active cells at
  tick 1,000 against 52. By tick 2,000 the two agree.
- **Without chemistry-paid births at the slowest diffusion,** sugar 1 and 3 come close to the page's counts and
  dimensions at ticks 1,000–2,000. That is a coincidence of numbers, not of shape: the pictures show no arms.
- **Roughness is higher in the model** wherever it overgrows. Roughness grows with the colony's size, so it is not
  comparable across sizes this different.

## 4. Whether branching appears

**Not at any sugar or diffusion rate tried (measurement, by eye on the pictures and by the box dimension).** A visual
likeness to Matsushita's dishes would be a proposal in any case, and there is none to claim.

**What may be missing (proposals, not tested):**
- **A growth limited by something that diffuses.** In the page, the branches eat narrow channels of sugar (03a's
  sugar maps). Here chemistry pays for most births, and the molecules do not move. Even with gc = 0, births are
  thinned per 4 × 4 square, not per place, which may blur the gradient at a branch tip.
- **Gliding and scattered births fill in the gaps between arms.** Gliding at 0.1 a tick, with random direction, moves
  a cell several places in its life. The page's cells glide only while they have coat, and dormant cells don't glide.
- **The page's branches may come from rules a population model leaves out:** coat, the store, and lineage.
- **Next step, if wanted (proposal for Justin):**
  - sugar per place rather than per coarse square;
  - gliding limited by coat;
  - chemistry income per lineage (task 06's form).

  This is not run, since task 07 asked only whether the cheaper test branches.

## Files

- **Code:** `jgol_2026-11-13/popdish/pop2_gpu.py` (the model) and `pop2_report.py` (figures and tables).
- **Results:** `jgol_2026-11-13/results/2026-11-14/task07/`, on the GPU machine:
  - `fine/`: 1,000 × 1,000;
  - `pagesize/`: the page-size plate;
  - `pagesize_gc0/`: no chemistry-paid births.
- **Figures in this folder:** `07_fine_sugar*.png`, `07_pagesize_sugar*.png`, `07_pagesize_gc0_sugar*.png`.
