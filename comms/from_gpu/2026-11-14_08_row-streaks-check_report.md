# Report 08: the horizontal streaks at sugar 10 come from the update order

From: GPU session (scheduled check), 14 November 2026. Answers `comms/to_gpu/2026-11-14_08_row-streaks-check.md`.
The page was **not** changed. Everything below is a measurement unless marked as a proposal.

## Short answer
- **Yes, the streaks are an artefact of update order (measured).** The page visits places row by row, and two of its
  loops draw down the store of the shared 4 × 4 chemistry square in place as they go. So within each square the upper
  rows get first claim on its energy and molecules, and the lower rows go still more often. When the scan is transposed
  in a harness-only copy of the page, the streaks turn vertical. When the scan is randomised each tick, they go.
- **The counts do not change beyond seed-to-seed spread (measured, 3 seeds).** The sugar-10 crash, from active
  thousands at tick 250 to hundreds or fewer by tick 500, happens under every scan order.
- **The lopsided growth at tick 250 does not follow the scan order (measured).** Its direction differs between seeds
  and between scan orders.

## 1. Where the order lives
In `src/digital_life.orig.html` (the base; `tools/patch.py` keeps these loops), inside `step()`:
- **The feeding loop**, `for (let i = 0; i < N; i++) { const z = zmap[i]; amb[i] += ZRG[z] ...`. It runs in row-major
  order (row by row, left to right). This is where a heterotroph covers its shortfall from the energy molecule with
  `burn(cmap[i], ...)`, which takes from `en[cmap[i]]`, the square's shared store, at once.
- **The birth scan**, `for (let y = 0; y < H; y++) { ... for (let x = 0; x < W; x++) {`. Also row-major. Going still
  (`dor[i] = 1` when a dish cell's `light[i] < 0`), death, remains (`husk[i] = 1`) and birth are decided here. A
  birth pays from the square's stores in place (`payChem(cmap[i] << 4, ...)`, `burn(sq, ...)`, `co2[sq] -= ...`), and
  the parent's own `light[pj]` is halved in place.
- New states are written to a second buffer (`nalive`, `ngen`, `ndor`, ...). So the *states* do not depend on scan
  order, but the *shared stores* do: a place visited earlier in a tick sees a fuller square.
- `divPick()` (`tools/env.js`, the division target with no Life rule) is also row-major, but it draws only random
  numbers and no stores, so its order does not bias anything.
- A chemistry square is 4 × 4 places (`CSH = 2`), so the bias repeats every 4 rows.

## 2. Measuring the streaks on the page's own runs
Source: 03a's snapshot runs (`jgol_2026-11-13/results/2026-11-13/day9_repo/validate_page`), sugar 1, 3 and 10,
3 seeds, glide 0.1, W 256. Script: `jgol_2026-11-13/popdish/streaks.py`, output
`jgol_2026-11-13/results/2026-11-14/task08/page_streaks.json`.

**The gone-still fraction among live places, by the place's row within its square (y mod 4).** If scan order matters,
this should rise from row 0 to row 3.

| sugar | tick | y mod 4 = 0, 1, 2, 3 (seeds 1 / 2 / 3) | x mod 4 = 0, 1, 2, 3 (seed 1) |
|---|---|---|---|
| 10 | 250 | .25 .42 .50 .52 / .19 .33 .38 .43 / .20 .39 .44 .45 | .36 .42 .45 .48 |
| 10 | 500 | .90 .98 .99 .99 / .85 .90 .93 .94 / .98 1.0 1.0 1.0 | .94 .97 .97 .98 |
| 3 | 250 | .41 .61 .62 .76 / .50 .62 .65 .74 / .41 .59 .66 .71 | .54 .59 .64 .65 |
| 3 | 1000 | .29 .42 .45 .51 / .19 .34 .38 .42 / .29 .42 .50 .52 | .35 .40 .45 .46 |
| 1 | 250 | .45 .75 .72 .80 / .48 .68 .81 .87 / .34 .69 .71 .81 | .57 .67 .75 .75 |
| 1 | 1000 | .30 .46 .53 .57 / .20 .34 .32 .35 / .17 .32 .32 .39 | .34 .43 .55 .53 |

- At every sugar level, in every seed, the first row of each square goes still least. The rise along x mod 4 is
  smaller: within a row, places are also visited in order, but a square's four rows are visited one after another, so
  the first row as a whole comes first.
- **It is not only sugar 10.** The bias is present at sugar 1 and 3 too. It shows as streaks at sugar 10 because there
  the colony fills the plate and almost all of it goes still at about the same time (tick 250–500), so the
  row-by-row difference is drawn across the whole dish.
- The along-rows autocorrelation of the still map exceeds the along-columns one at sugar 10, ticks 250–500 (mean
  difference over lags 1–4: +0.05 to +0.22). The row-mean profile has a peak at period 4 (power 4–71 × its
  neighbours). By tick 1,000 at sugar 10 nearly everything is still or remains, and the measure has nothing left to see.

## 3. Rerunning with the scan order changed (harness only)
`jgol_2026-11-13/test/scan_variants.py` writes copies of the repository's page to
`jgol_2026-11-13/results/2026-11-14/task08/pages/`, with the two loops above visiting places in another order. The
repository's page is untouched. The modes are:
- row: the page's own order, a control;
- reverse;
- transpose: column by column;
- random: a fresh permutation every tick, from `Math.random`, so the page's seeded random numbers are not consumed.

Sugar 10, glide 0.1, W 256, to tick 1,000. Run through the CPU queue (`test/task08_scan.cmd`, port 8812).

- **Control:** the row copy gives the page's run bit for bit (seed 1, ticks 250, 500, 1,000: identical states). So the
  rewrite changed only the order.
- **Within-square profile at tick 250, seed 1** (gone-still fraction, y mod 4 / x mod 4):

| scan | y mod 4 = 0..3 | x mod 4 = 0..3 | row − column autocorrelation, ticks 250 / 500 |
|---|---|---|---|
| row (page) | .25 .42 .50 .52 | .36 .42 .45 .48 | +0.11 / +0.22 |
| reverse | .52 .49 .39 .19 | .44 .42 .39 .35 | +0.12 / +0.17 |
| transpose | .27 .29 .31 .31 | .18 .28 .35 .38 | −0.08 / −0.24 |
| random (seeds 1, 2, 3) | .42 .40 .39 .38 · .29 .32 .31 .31 · .34 .35 .37 .38 | .39 .39 .40 .41 · ... | +0.02 −0.01 −0.01 / +0.02 +0.06 −0.05 |

  Reversing the scan reverses the profile: the last row, now visited first, goes still least. Transposing moves the
  bias to columns and turns the streaks vertical. Random order flattens both profiles, and the anisotropy falls to
  seed noise.
- **Picture:** `08_scan_modes_sugar10.png` shows seed 1 at ticks 250 and 500 under each order. The streaks are
  horizontal under row and reverse, vertical under transpose, and absent under random.
- **Counts (active / gone still / remains, sugar 10, seeds 1, 2, 3):**

| scan | tick 250 active | tick 500 active | tick 1,000 active | tick 1,000 still | tick 1,000 remains |
|---|---|---|---|---|---|
| row (page) | 7,904 · 5,826 · 10,771 | 497 · 1,321 · 75 | 14 · 120 · 23 | 4,296 · 4,453 · 4,581 | 8,808 · 9,368 · 9,091 |
| random | 6,705 · 9,679 · 6,588 | 337 · 15 · 881 | 1 · 4 · 125 | 3,991 · 4,432 · 4,149 | 8,739 · 9,608 · 8,676 |
| reverse (seed 1) | 10,954 | 101 | 0 | 4,526 | 9,571 |
| transpose (seed 1) | 9,038 | 286 | 0 | 4,558 | 9,725 |

  The two sets overlap seed for seed. The crash is the same event under every order. Random order may leave slightly
  fewer still places at tick 1,000 (about 4,190 against 4,440 on average), but three seeds cannot separate that from
  noise.

## 4. Lopsided growth
The colony's centre at tick 250, sugar 10, measured from the plate's centre in places (x, y):
- page seeds 1, 2, 3: (−17, −17), (0, +17), (+4, −16);
- seed 1 under reverse, transpose and random: visibly lopsided in other directions (figure, top row).

So the lopsidedness is real but does not follow the scan order. In the page's own runs its direction changes with the
seed. **Proposal (not tested):** it comes from which early branches happen to reach fresh agar first, and then win the
race outward; the measure would be its spread over more seeds. At sugar 1 and 3 the offsets are 2 places or less at
tick 250.

## 5. What this means (proposals, for Justin)
- The streaks are a model artefact. The counts and the crash are not. Earlier dish counts stand.
- **Proposal:** if Justin wants the artefact gone, visit places in a random order each tick in those two loops (or
  draw the square's store as a share split among its claimants, which is order-free). This changes the model, so it is
  Justin's decision, as task 08 says. The random-order copy used here is a harness tool, not a proposed patch; a real
  change would go through `tools/` with the page's seeded rng.
- The same first-come bias exists wherever a square's store is drawn in place during a row-major scan. It is weak where
  stores are ample and strong where they run out, which is the dish's late phase.

## Files
- `08_scan_modes_sugar10.png` (this folder).
- Code and data, outside the repository (`D:\labyrinth\automata\jgol_2026-11-13\`): `popdish/streaks.py`,
  `popdish/streaks_fig.py`, `test/scan_variants.py`, `test/task08_scan.cmd`; results in `results/2026-11-14/task08/`
  (`page_streaks.json`, `scan_streaks.json`, `08_scan_modes_sugar10_counts.json`, the page copies, the run records).
