# Justin's Game of Life — handoff for a code session

A single-file web page (`build/justins_game_of_life.html`, open it in any browser) that runs an evolving cellular automaton: cells on a torus, each carrying a genome that sets its own Life-like rule, living in a world of light, heat, water, gases, molecules and currents. This package has everything needed to rebuild, test and extend it. Justin will send updated packages from time to time; each one replaces the last.

Your first job is described at the end: **a two-layer water model, then possibly a GPU-based 3D model.**

## Layout

```
build/justins_game_of_life.html   the current page (the deliverable; never edit it by hand)
src/digital_life.orig.html        the pristine original page everything is patched onto
tools/patch.py                    the build: ~250 exact-match replacements applied in order, then a renaming pass
tools/newblock3.js                world allocation, resize, hopping (spliced in by patch.py)
tools/chem.js                     molecules, energy/sugar field, genes' helpers, inspector text, side panel, overlays
tools/env.js                      environments, heat, chaos, fluid currents, reactions, water, drift, spores, status line
tools/chemui.js                   UI wiring: sliders/checkbox lists, view menu, buttons
test/                             headless browser tests (Playwright)
```

## Build

```
python3 -I tools/patch.py src/digital_life.orig.html build/justins_game_of_life.html \
    tools/newblock3.js tools/chem.js tools/env.js tools/chemui.js tools/gpu3d.js tools/view3d.js
```

This is the full build since the merge described under "Merged" below. `gpu3d.js` and `view3d.js` are still optional in the
script, but the merged page expects both.

A further optional file, `tools/view3d.js` (the 3D view), goes last and is spliced in after the UI wiring.

The file before it, `gpu3d.js`, is optional too. It is spliced in before `env.js`, which reads its `G3` object. Without it, leave
3D water off.

How `patch.py` works, because it matters for every change:

- `rep(old, new)` asserts that `old` occurs **exactly once** in the text as it stands at that moment, then replaces it. Replacements run in order, so a later `rep` must match the text *as earlier reps left it*, not the original. If a rep fails, the build stops with the count and the first 80 characters.
- `//@@CHEMUI@@` in the patched text is replaced by `chem.js + env.js + chemui.js`. `newblock3.js` is spliced in separately.
- New reps go before the line `# the chemistry code goes in before the wiring`. Each feature was added as a commented block of reps there.
- **Renaming pass.** At the very end, `clumpify()` turns the words body/bodies into clump/clumps in user-visible text only: HTML text nodes and JS string literals. It leaves code, CSS, comments, regular expressions, and string literals that are exactly `'body'` or `'bodies'` (used as keys). So in the code everything is still called `body`/`bodies`, but the page says "clump". Write user-facing text with either word.
- **Ids in the slider lists.** The slider and checkbox id lists exist twice: in `patch.py` (the `for (const id of [...])` loops) and in `chemui.js` (`RULE_SL`, `RULE_CK`). Every id listed must exist as an element. A missing one throws a page error at load.
- The page is fully self-contained: no network, no libraries.

For a new large subsystem, prefer adding functions to `env.js` (or a new JS file appended in `patch.py`'s splice) and wiring them in with a few small reps, rather than many reps into the original.

## Architecture

**Two grids.**
- **Fine grid:** the cell grid, `W × H` on a torus, index `i = y*W + x`. Its size follows the window.
- **Coarse grid:** `cw × chh` squares of 4 × 4 cells, where `cmap[i]` gives a cell's square. All fields (chemistry, heat, water, gases, sugar, flow) live on the coarse grid.

**Per-cell arrays.** These are double-buffered (`nalive`, `ngen`, …) and swapped at the end of `step()`.

| Array | Meaning |
|---|---|
| `alive` | whether the cell is alive |
| `gen` | 32-bit genome: an exponent 0–3 for each of 16 primes (`PR`). It sets the birth mask `B(g)`, the survival mask `S(g)` and traits (motility, contagion, efficiency `EFFT`, hardiness, proofreading, thermophily). `g >>> 28` is used as the lineage. |
| `xg` | 16-bit extension genome: 8 slots of 2 bits (table below) |
| `light` | per-cell light, which works as the cell's energy budget. It regrows toward the local light `ltc`, spreads to neighbours, and pays upkeep (`ZCOST`) and births (`ZBIRTH`). |
| `body` | clump id, 0 if free. Metadata lives in the `bodies` Map. |
| `dor` | 1 if the cell is a dormant spore |
| `rsv` | left over from a removed storage gene; never active |

**Extension genes (`xg`).** Mutation picks a slot from `XSLOTS` (the enabled genes) and steps its exponent by ±1. Carrying genes multiplies upkeep by `1 + .03 × (sum of exponents)`.

| Bits | Prime | Gene | Switch |
|---|---|---|---|
| 0–1 | 59 | quorum: no births at low neighbour counts when the signal is high; saves light | always |
| 2–3 | 61 | producer: releases its own compound's molecules into its square | `gProd` |
| 4–5 | 67 | recombination: raises the fusion chance of parents | `gSex` |
| 6–7 | 71 | predator: bites cells of other lineages; needs the heterotroph gene | `gPred` |
| 8–9 | 73 | (storage, removed; slot unused) | — |
| 10–11 | 79 | heterotroph: covers a light shortfall by burning sugar from the water; can be born on sugar into dark ground | `gHet` |
| 12–13 | 83 | adhesion: lets a free cluster become a clump | `gAdh` |
| 14–15 | 89 | spore-forming: goes dormant when starving or dry, wakes when light and water return | `gSpore` |

**`step()` order, per tick.**

1. Every 2 ticks: `envStep()` (heat, chaos, vents, fluid flow, heat advection), the chemistry step, `fieldStep()` (territory), `sigStep()` (quorum signal), `energyStep()` (sugar: advect, diffuse, decay to CO₂, leak from cells), `rxnStep()` (water, CO₂, O₂: advect, diffuse, rain and evaporation, air exchange, iron sink, burial), `xslots()`, `produce()`.
2. Light regrowth and upkeep. Dormant cells pay `sporeCost` × upkeep. Heterotrophs top up from sugar with `burn()`.
3. The main cell loop. Survival needs the Life survival rule, *or* being dormant, *or* (in a clump) the slime holding it with chance `clumpHold`, and enough light. Heat harm, drying (`dryKill`) and spore death can still kill. Births choose a parent among live, non-dormant neighbours. A birth can be blocked by the quorum gene, light, temperature, territory, chemistry, or (with reactions) CO₂ and water.
4. Predation, then the buffer swap.
5. `hopPass()` (motile cells), `driftPass()` (loose cells and spores carried by the flow), `sporePass()` (dormancy changes).
6. Clump bookkeeping (`bodyCensus`): integrity, with gaps of up to one cell allowed because a shared slime holds the cells; division; budding; engulfing; fusion; and light, sugar and water shared among a clump's squares.

**Coarse fields (env.js and chem.js).**
- **Chemistry:** `chem` holds 16 mineral species per square, capped by `chemCap`.
- **Heat:** `temp` (water temperature) and `tamb` (ambient). `vglow` is a vent's broad glow, used for light and molecules. `vhot` is a vent's narrow hot core, used for heat.
- **Signal and sugar:** `sig` is the quorum signal, and `en` is sugar (the energy molecule).
- **Reactions:** `wat` (water), `co2`, `o2`, and `fe` (iron, which soaks up O₂ until it runs out).
- **Flow:** `fx`, `fy` are the current, in squares per 2-tick step. They are used by `advect()` (sugar, signal, chemistry, gases, water), by `advectSharp()` (heat, a MacCormack scheme), and by `driftPass()`.

**Reactions (with `rxn` on, the default).** Every reaction is balanced 1:1 so carbon can be checked.
- **Photosynthesis.** Births and the sugar leak fix carbon: CO₂ + water + light → sugar + O₂.
- **Burning sugar.** `burn()` uses respiration when there is oxygen: sugar + O₂ → CO₂ + water, at full yield. Without oxygen it ferments: sugar → CO₂, at yield `ferm`.
- **Decay and burial.** Sugar left in the water decays back to CO₂, using oxygen if there is any. A fraction `bury` is buried for good, leaving its oxygen behind.
- **Water** comes from rain and seasons, and is lost to evaporation, which scales with temperature. Cells use and release it.
- **Oxygen history.** The world starts with no oxygen. Iron rusts away first, so oxygen rises only after the iron is gone, a small version of the Great Oxidation Event.
- **Carbon check.** `carbonTotal()` adds CO₂, sugar, cells × birth cost, and buried carbon. With air exchange off (`gasx: 0, vco2: 0`) it drifts by about 0.2–2.5% over 1,500 ticks.

**The current fluid model (`fluidStep` in env.js).** This is the part to replace or extend.
- It is a 2D stable-fluids solver on the coarse grid, seen from above. Each step it:
  1. applies floor drag `fdrag`;
  2. pulls weakly toward a wandering cross-current (`crossflow`, its direction driven by the Lorenz chaos);
  3. adds a little spin near vents;
  4. self-advects the velocity, semi-Lagrangian;
  5. applies viscosity `visc`;
  6. runs a pressure projection with a source term: 10 Jacobi passes, solving ∇²p = div(u) − S, where S = `convect` × (T − mean T), so warm water wells up and spreads and cool water sinks;
  7. applies vorticity confinement `eddies`;
  8. clamps the speed to 0.9.
- It costs about 4–8 ms per call on a 22k-square grid in headless Chrome. The whole page runs 15–35 ms a tick, depending on population and world size.
- The cross-current is a stand-in for the overturning circulation a real 3D or two-layer fluid would produce. That is the reason for the next task.

**Environments** (`P.env`):
- `even`: uniform light, no heat, no currents. The control world.
- `pond`: day and night, drifting clouds that shade and cool the water.
- `vent`: a dark sea floor lit and warmed only by vents.
- `springs`: hot springs on land.

Vents pulse, drift and burst with the chaos. In heated worlds every compound has a preferred temperature, and `thermFit` sets survival and births by how well the water matches it.

**UI.**
- One View menu at the top of the world (`#topview`), grouped into Cells (normal, heat vision, spores), The water (temperature, current, water, CO₂, O₂, sugar, signal) and Building blocks.
- A "Show clumps" button; outlines are off by default.
- A short status line; clicking it shows the full account.
- The side panel shows variety, gene shares, spores, reactions and graphs over time, including oxygen.
- The old `#viewsel` and `#chshow` selects still exist but are hidden; the top menu keeps them in sync.

## Defaults (the `P` object in the build)

```
speed:1, mu:0.004, contagion:0.03, fusion:0.2, regrow:0.02, cost:0.08, birth:0.2, death:0.002, spread:0.25, floor:true, foldOn:true,
showLight:true, showFolds:false, showForms:false, showBodies:false,
nucleate:0.03, clumpShare:.5, clumpHold:.5, bodyCost:0.004, bmu:0.01, lsize:6, lstrength:1.5,
chemOn:true, chrich:45, chrate:.04, chdiff:.15, chrecyc:.7, chunit:1, chshow:'off', kinw:1, terr:.3, front:.5,
view:'normal', env:'pond', dayLen:400, nightDepth:.4, heatDiff:.05, heatRelax:.006, heatHarm:.02, heatLife:.2, ventPower:1, heatChaos:.35,
current:.25, plumeW:.35, crossflow:1, convect:.06, visc:.04, eddies:.2, fdrag:.03,
qthr:.35, qsave:.15, sigspread:.2, qmut:1, qseed:0, xseed:0,
gProd:true, gSex:true, gPred:true, gHet:true, gAdh:true, gSpore:true,
sporeRate:.05, sporeLight:.03, wakeLight:.3, wakeRate:.03, sporeCost:.1, sporeDeath:.003, drift:.3,
seasonLen:1500, drySeason:.7, rxn:true, co2air:4, gasx:.01, vco2:.05, o2sink:.0005, bury:.02, feStart:1.5, ferm:.3,
evap:.03, rain:.005, wrain:2, wcell:.05, wfix:.2, wdry:.5, dryHarm:.02, eleak:.01, ebody:.2, eeff:.4, edecay:.02,
prodRate:.3, prodCost:.03, predRate:.1, predGain:.4   (rbase…rconv belong to the removed storage gene)
```

## Testing

The tests drive the built page in headless Chromium with Playwright: `pip install playwright` and `playwright install chromium`. They call the page's own functions (`reset('organism')`, `step()`, `geoSeed()`, `chemCapFill()`) and read its arrays.

- `test/runset.py BUILD CONFIGS.txt [ticks] [runs]` is the main tool. Each line of `CONFIGS.txt` is `world|{json of P overrides}`. It reports survival, survival among colonies still alive at tick 200, occupancy, gene shares and clump share.
- `test/gene2.py`: one configuration, several runs (used by `runset.py`).
- `test/est.py`: start-up establishment over 200 ticks only (fast).
- `test/rx.py`: carbon conservation and the reaction trace.
- `test/goe.py`: long oxygen run (Great Oxidation check).
- `test/clump.py`: clump counts, lifetimes, and member versus free death rates.
- `test/dry.py`: drying and drift counts.
- `test/fl.py`: flow speed and solver timing, and screenshots of the flow and heat views.
- `test/hl.py`: the form highlight UI.
- `test/trace.py`: population traces.

Several scripts use a small viewport (620 × 460), giving a world of about 476 × 248 cells. Some write screenshots to `test/shots/`; create that folder first.

**How to read results.**
- About 30% of new runs die in the first 100 ticks, whatever the settings. The starting organism carries Conway's rule (B3/S23), and a small seed under that rule often fizzles out.
- So compare survival *among established colonies* (`survOfEst`), and use 6–10 runs per setting. Differences of one or two runs out of six are noise.
- All results so far are headless, small worlds and short runs (1,500–6,000 ticks).

## What was built, in order, and what was found

1. **Energy reserve** (a storage gene). It did not help, because light is a flow, not a stock, and it was later removed. Sugar replaced it.
2. **Currents** carrying heat, molecules and the quorum signal. Later replaced by the fluid solver.
3. **Energy molecule (sugar) and the heterotroph gene.** An early bug created energy from nothing; it was fixed and the leak is now paid for in light. Under mutation the heterotroph gene rises to about 99% of cells, the clearest selection signal so far.
4. **Graded predation.** Predators need the heterotroph gene and gain energy from the prey's sugar.
5. **Adhesion and clumps.** At first clumps stayed rare (1–6% of cells) and showed no benefit.
6. **Reactions and water**, then dry seasons. A water bookkeeping bug (respiration creating water) was found and fixed. Drying now matters.
7. **Drift of loose cells.** Pooled over three worlds, 18 of 24 runs survived with drift against 10 of 24 without.
8. **Defaults tuned.** Reactions, adhesion and predators were turned on. The storage gene and the old chance-made bodies were removed. User-facing "bodies" became "clumps".
9. **Fluid currents**, burial and iron (oxygen now rises slowly), and a tidier UI.
10. **Spores as a state.** This also fixed clumps: with spores, 24–36% of cells are in clumps in the heated worlds, against 4–6% without, and clump members die at a quarter of the rate of free cells. Dormant cells give clumps a durable core.
11. **Vent plumes.** Each vent has a narrow hot core, heat is carried with `advectSharp`, heat is lost and spreads more slowly, and a cross-current bends the plumes into tails. In the vent world, 5 of 6 runs survived against 3 of 6 before.

12. **Two layers** (Claude Code session, 11 November 2026; step 1 of the task below). Details and results follow.

## Two layers: what was built and what was found

**The setting.** `P.twoLayer` (checkbox "Two layers", default on). Switching it off runs the old single-layer code path
unchanged: `fluidStep`, `advectSharp(temp)` and the old heat loop.

**The code.**

- **`env.js`: `fluidStep2`.** There are two velocity fields:
  - **floor:** `fx`, `fy`, still read by `advect()` and `driftPass()`;
  - **surface:** `ux`, `uy`.
- **Upwelling.** The upwelling per square is `wup = convect × current × buoy × (T_floor − T_surface)`, with its mean
  removed so mass is kept, and clamped to ±0.3.
- **`layerSolve`.** Each layer is solved by `layerSolve`: drag, a push, self-advection, viscosity, a 10-pass pressure
  solve to a target divergence, eddies, and a speed limit. It is the old solver, generalised.
  - The floor's target divergence is −w: it converges where water rises. It gets floor drag `fdrag` and the vents'
    swirl.
  - The surface's target is +w: it spreads where water rises. It gets the small drag `sdrag`.
- **Optional couplings.**
  - `shear`: drag between the layers.
  - `coriolis`: a small turning term.
  - `tide`: the old cross-current. It now pushes both layers, and the `crossflow` slider is unused in two-layer mode.
- **`heat2`.** There are two heat fields:
  - `temp`, the floor, which the cells feel;
  - `tsurf`, the surface.

  Each is carried by its own current (`advectSharp` now takes the velocity arrays). Heat is exchanged by the moving
  water: the surface takes floor heat where w > 0, and the floor takes surface water where w < 0, at rate `wheat`.
  `vmix` adds plain mixing between the layers.
  - The floor relaxes toward the ambient at `floorRelax` × the old rate, and keeps the vents' heat.
  - The surface relaxes toward the ambient (the air) at `airLoss` × the old rate.
- **Gases, sugar, molecules and the signal stay single-layer on the floor,** as before.
- **`sporeAir`: spores ride the plume.**
  - **Lifting.** A dormant cell not in a clump, in a square with w > 0.005, is lifted with chance `sporeLift × w × 10`
    per environment step. It leaves the grid.
  - **Aloft.** Airborne spores are kept in the list `air`, with their genome, extension genome and origin, and are
    carried by the surface current with a little jitter. They die at 2 × `sporeDeath` per step.
  - **Settling.** They settle with chance `settle × (1 + 4·max(0, −w)/0.05)`, and at a fifth of that inside a strong
    plume. A settled spore lands in an empty cell of its square (up to 6 tries) or is lost.
  - **Statistics.** `airStat` holds the counts, distances and time aloft.
- **New parameters.** `twoLayer:true, buoy:40, sdrag:.005, vmix:.02, wheat:4, floorRelax:1, airLoss:1, shear:.01,
  coriolis:0, tide:1, sporeLift:.3, settle:.02, airMax:3000`.
- **New sliders.** Mixing between layers, Drag between layers, Turning (Coriolis), Tide, Spores lifted, Spores
  settling. Their ids are in both lists.
- **Views** (the View menu, under The water):
  - Temperature (surface);
  - Current (surface), with the spores aloft shown as pale squares;
  - Rising and sinking water;
  - Cutaway (side slice): an inset showing both layers along the first vent's row, with currents, vertical flow and
    spores aloft.

  The floor views are now labelled "(floor)".
- **`test/inpage_harness.js`.** An in-page harness, used because Playwright was not installed. Load the page, then
  `eval(await (await fetch('…/test/inpage_harness.js')).text())` and call `runOne(env, ticks, overrides)`.

**Results.** A world of 476 × 248 (viewport 620 × 460), 1,500 ticks, one run each, in the in-app browser:

| Build | World | Runs | Established at tick 200 | Survived | Cells at tick 1,500 (survivors) |
|---|---|---|---|---|---|
| shipped | vent | 6 | 6 | 6 | 692 – 6,472 |
| shipped | pond | 6 | 3 | 3 | 8,119 – 10,273 |
| shipped | springs | 6 | 3 | 3 | 10,201 – 10,906 |
| two layers, tide 0 | vent | 6 | 6 | 6 | 1,512 – 5,972 |
| two layers, tide 0 | pond | 6 | 3 | 3 | 3,579 – 4,297 |
| two layers, tide 0 | springs | 6 | 4 | 4 | 4,284 – 6,888 |
| two layers, tide 1 (default) | vent | 3 | 3 | 3 | 3,345 – 4,214 |
| two layers, tide 1 (default) | pond | 4 | 2 | 2 | 11,983 – 12,241 |
| two layers, tide 1 (default) | springs | 4 | 3 | 3 | 12,378 – 13,667 |

**What the table shows.**

- **Survival among established colonies.** It is the same everywhere: every established colony survived, in both
  builds. Too few runs, too short, to tell survival apart.
- **Physics only (tide 0).** The circulation is real but local.
  - Floor currents reach about 0.22 squares per step near vents, against a world mean of about 0.02. In the shipped
    build the mean is about 0.16, almost all of it the cross-current.
  - Pond and springs then hold half to two-thirds as many cells as before, because little is carried far.
  - Spores travel a median of 3 to 10 cells, at most about 90.
- **With the tide (now the default).** Pond and springs hold more cells than the shipped build, and spores travel a
  median of 63 to 79 cells, at most about 260: across much of the world.
- **Lineage spread between vents.** Measured as which of the 16 coarse lineages (`g >>> 28`) are near each vent. This
  was not informative: vents that were all occupied shared a lineage in both builds. A finer measure of lineage is
  needed.
- **Timing.** In an empty world it is 10.1 ms a tick with two layers, against 9.2 ms in the shipped build: about
  +1 ms. With life present, 12 to 20 ms against 12 to 17, but populations differ.
- **The old path still works.** A 300-tick run in the vent world with `twoLayer:false` ran without errors.

**A later decision (the user, 11 November).** Keep both, with the **tide off by default** (`tide:0`): physics-only
circulation. The tide stays available as a slider.

**Not done:**

- O₂ and CO₂ in two layers;
- life in the water (plankton);
- Playwright runs with `runset.py` (`test/` is unchanged and untested against this build).

## 3D water on the GPU (step 2; Claude Code session, 11 November 2026)

**The setting.** `P.water3d` (checkbox "3D water on the GPU"). It is **on by default** since the user's decision of
11 November; it was off when first built. When it is on:

- WebGPU is detected. If it is missing, fails to start, or the device is lost, the two-layer model runs instead.
- A status line beside the checkbox says which is running.

**The code: `tools/gpu3d.js`.** WGSL compute shaders, inline. The page stays a single file with no network.

- **The grid.** `cw × chh × nz3` voxels (default 16 levels), so the floor level matches the chemistry squares exactly.
- **Each state voxel is a vec4:** u, v, w, T.
- **Each environment step:**
  1. `advect`: semi-Lagrangian and trilinear; periodic across, clamped top and bottom. It adds:
     - buoyancy, `w += buoy3 × (T − tref)`, where `tref` is the mean of the floor and surface temperatures from the
       last readback;
     - an interior drag, `drag3`;
     - at the floor: the floor drag, the vents' swirl, vent and cell heat, and relaxation to the ambient;
     - at the top: `sdrag`, and heat lost to the air;
     - the tide and Coriolis, if they are set.
  2. `diffuse`: heat spreads, at `heatDiff × 2` sideways and `vdiff3` × that up and down.
  3. `divergence`, then `jac3` passes (30) of `jacobi`. The pressure is warm-started from the last step.
  4. `project`: no flow through the floor or the surface, and a speed limit of 0.9.
  5. `gather`: per column, the floor (u, v, T), the surface (u, v, T) and the w one level above the floor; and a side
     slice (u, w, T) through the first vent's row.
- **Readback.** It is asynchronous (`mapAsync`) and one step late. It fills the CPU arrays the rest of the page already
  uses: `fx, fy, temp` (floor), `ux, uy, tsurf` (surface) and `wup` (upwelling). Cells, drift, spores aloft and the
  views work unchanged.
- **For tests,** `g3Sync()` returns the pending readback, so a test loop can wait for it.
- **Views.** The Cutaway view shows the 3D slice when the GPU model is running: all levels, coloured by temperature,
  with the flow in the slice and the spores aloft.
- **New parameters.** `water3d:false, nz3:16, buoy3:.012, drag3:.01, jac3:30, vdiff3:.15`. The sliders are 3D
  buoyancy, 3D drag, 3D vertical mixing and 3D levels; changing the levels rebuilds the GPU grid.
- **`test/inpage_harness3d.js`.** `runOne3(env, ticks, overrides)` waits for each readback.

**A fix found in testing.** With heat spreading as easily up as sideways, the floor near vents was cooler than in the
two-layer model: 0.52 against 0.68 at the core. The first organism, whose heat preference is set for the warmer start,
grew far more slowly, and in the vent world only 1 of 3 established colonies survived. Making vertical spreading slower
(`vdiff3:.15`) brought the floor back to 0.72 and 0.58, and fixed survival.

**Results** (476 × 248 world, 1,500 ticks, an AMD GPU, the in-app browser, tide 0):

| Water | World | Runs | Established at tick 200 | Survived | Cells at tick 1,500 (survivors) |
|---|---|---|---|---|---|
| 3D | vent | 6 | 4 | 4 | 618 – 4,557 |
| 3D | pond | 4 | 3 | 3 | 4,004 – 6,166 |
| 3D | springs | 4 | 3 | 3 | 5,754 – 7,060 |

These are about the same as the two-layer model with tide 0 (the table above): survival is the same, and populations
are of the same size.

- **Spores.** They settle a median of 3 to 4 cells from home, at most about 60. The surface outflow is local, as with
  two layers.
- **Timing.**
  - The CPU side of a GPU step (uploading the vents' heat and encoding) is about 0.5 ms.
  - In the test loop, which waits for each readback, a tick took 13.7 to 13.9 ms in an empty world, against about 9
    to 10 ms with two layers. Most of that is the wait for the GPU's round trip.
  - In the running page the readback does not block. This was not measured separately.

**Not done:**

- carrying gases or sugar in 3D;
- a perspective view;
- automatic choice of `nz3` by GPU speed;
- a check on other GPUs, or on browsers without WebGPU, where the fallback path is expected to run; the fallback was
  not tested on such a browser.

**Installed:** nothing. WebGPU was already in the browser.

## The 3D view (Claude Code session, 11 November 2026)

**What the user asked for:** a 3D view, made from the user's cutaway diagram of the overturning, that can be zoomed and
rotated, and that runs on the GPU by default.

**How to open it.** The **3D view** button sits beside the View menu at the top of the world; it then reads "2D view".

- **The setting.** `P.view3d`, off at load. The simulation keeps running underneath.
- **Controls.** Drag to rotate, wheel to zoom, right-drag or shift-drag to pan, and double-click to reset.

**What it shows:**

- **The box.** The water as a box, with the boundary between the layers dashed at mid-height.
- **The floor.** The 2D view's own picture of the cells, so the colonies sit on the floor.
- **The water as a volume, ray-marched** (96 steps): warm water (more than 0.04 above the mean) glows orange to
  yellow, cool water is faintly blue, and the water itself is a faint blue.
- **Arrows** on a 12 × 8 × 3 lattice show the flow: orange rising, blue sinking, pale sideways. Up and down are
  stretched, so the slow sinking can be seen.
- **Spores aloft** are pale specks near the surface.
- **A legend** says where the water comes from and on which GPU.

**How it works: `tools/view3d.js`.** A WebGPU render pass with five pipelines: floor, volume, lines, arrows, spores.
They share one bind group layout. The device is shared with the 3D water (`g3Device()` in `gpu3d.js`).

- **With the 3D water running,** the view binds the water's own GPU buffer (`G3.bA`) directly: no readback.
- **Otherwise,** it builds a two-level volume each frame from the CPU arrays: the floor (`fx, fy, wup, temp`) and the
  surface (`ux, uy, tsurf`).
- **Without WebGPU,** the view only says that it needs WebGPU. There is no CPU renderer.
- **The floor's picture** is copied from the 2D canvas `off` each frame.

**Checked:**

- in the in-app browser (AMD integrated GPU), with both the 3D water and the two-layer fallback;
- rotation and zoom, with the mouse;
- in Chrome on the NVIDIA RTX 3070 (started with `--force_high_performance_gpu`), in a 1,052 × 634 world: 14.5
  frames a second, the same as the simulation's tick rate, since both share the browser's frame loop. The view's own
  CPU cost was about 0.5 ms a frame.

**Not done:**

- a CPU fallback renderer;
- labels drawn in the scene (the legend is an overlay);
- a slider for the glow;
- a test on a browser without WebGPU.

## Changes to the 3D view, and carried cells (the user's requests, 11 November 2026)

**What the user asked for:** WASD movement; heat off by default, arrows included; 3D cells; cells carried by convection
and the vent current.

### WASD movement

- W, A, S and D move across the floor in the camera's own directions.
- Q and E move down and up.
- Shift moves faster.
- The keys are taken only while the 3D view is open, and not while typing in a field.

### Heat and flow off by default

Two checkboxes in the 3D view's legend, both off at first:

- **Show heat:** the glowing volume.
- **Show the flow (arrows).**

### 3D cells

- **On the floor,** every living cell is drawn as a small shaded block, coloured as in the 2D view, on a dimmed floor.
  The blocks are rebuilt each tick from the 2D image.
- **Carried cells** are drawn as blocks at their 3D positions, read straight from the GPU's particle buffer.

### Carried cells

**With 3D water** (`g3Lift` and `g3Carried` in `gpu3d.js`, and the WGSL kernel `particles`):

- **Lifting.** In squares where the water rises (w > 0.004), a cell not in a clump can be lifted into the water
  column, with chance `sporeLift × w × 10` per environment step:
  - a spore, whatever its neighbours;
  - an active cell only if it is loose (2 or fewer neighbours), and then at `cellLift` × that chance.
- **On the GPU.** Up to 4,096 carried cells are moved each step by the full 3D flow, with trilinear sampling, and sink
  slowly: `sinkSpore` and `sinkCell` levels per step.
- **Read back.** Their positions are read back with the other fields. Near the floor (below level 1) a carried cell
  settles with chance `settle3` into an empty cell of its square, or is lost if there is none.
- **Death aloft.** Aloft it does not feed or breed, and dies with chance `aloftDeath` per step (spores:
  `sporeDeath × 2`).
- **The CPU's copy.** The `air` list mirrors what is aloft, for the 2D views and the cutaway.

**With two layers:** the old lifting of spores now also takes loose active cells, at the same `cellLift` factor, and
active cells aloft die at `aloftDeath`.

**New parameters.** `cellLift:.05` (slider "Loose cells carried"), `aloftDeath:.004`, `sinkSpore:.006`,
`sinkCell:.016`, `settle3:.08`.

### Clipping (reported by the user)

- **The bug.** At some angles and zooms, parts of the scene vanished. The far clipping plane was 6 × the zoom
  distance, so close up the far side of the box lay beyond it.
- **The fix.** The far plane is now the distance to the box's farthest corner, plus a margin, recomputed each frame.
  The near plane is small (0.05 or 0.0002 × far), and zoom can now come in to 1.5 units.
- **Checked.** At a close, low camera, the far corner's depth was 1.003 before the fix (cut off) and just under 1
  after (drawn).

### Bugs found and fixed

- Readbacks that arrived after the GPU grid was rebuilt were read from the new staging buffer instead of the one
  mapped.
- A pending staging buffer was destroyed mid-map.

### Results

These are 1,500-tick runs in the 476 × 248 world, with 3D water, in the in-app browser on the AMD integrated GPU.

**At `cellLift:.15`:**

| World | Runs | Established | Survived | Cells at the end |
|---|---|---|---|---|
| vent | 5 | 4 | 4 | 28 – 3,151 |
| pond | 2 | 2 | 2 | 3,252 – 3,538 |
| springs | 1 | 1 | 1 | 4,882 |

The vent colonies ended smaller than without carrying (618 – 4,557). Lifting loose cells away from the vents, where
the colonies live, thins them.

**At `cellLift:.05` (now the default):** vent, 4 runs, all 4 established and survived, at 1,107 – 2,215 cells.

**How far carried cells travel:** a median of 2 to 3 cells, at most about 60.

**Tuning the sinking speed** changed the picture a lot:

| Sinking | What happened |
|---|---|
| too slow (0.003) | nothing settled; cells piled up aloft and died |
| too fast (0.025) | cells landed about 2 cells from home |

The defaults sit between the two.

**Which GPU.**

- **The tests ran on the integrated GPU.** The computer has an integrated AMD Radeon (Vega) and an NVIDIA GeForce RTX
  3070 Laptop GPU. The browser that ran the tests was given the AMD one for every `powerPreference` (default,
  low-power, high-performance), so all timings above are on the integrated GPU.
- **The page asks for the fast GPU.** It now requests `powerPreference: 'high-performance'`, and the status line names
  the adapter it got ("running on amd gcn-5: …").
- **Windows decides.** It assigns GPUs per app. To give a browser the NVIDIA card, set the browser to "High
  performance" in Settings › System › Display › Graphics, or in the NVIDIA Control Panel's per-program settings, then
  restart the browser.

**Open items.**
- The start-up burnout. Two options: a larger or hardier seed, or an automatic restart if life dies out early.
- The remaining ladder stages: a soma/germ split inside clumps, clumps shedding propagules, and a test of whether predators favour bigger clumps.
- Emergent eukaryotes, and fungi and microscopic animals as full heterotroph types, are parked.

## Merged: the web session's work since the last package (11 November 2026)

The web session kept building on the package it sent you while you built two layers and the 3D water. Your package (`justins_game_of_life_package_3dview.zip`) was merged three ways against that common package:

- **Conflicts.** The only conflicts were two places where both sessions had added to the same spot: new blocks of build steps at the end of `patch.py`, and the slider and checkbox id lists in `chemui.js`. Both sides were kept. Your blocks now run after the web session's, and the id lists hold the union of both.
- **Re-anchored steps.** Two of your build steps extended the slider and checkbox id lists from what had been their last entries. Since the web session's steps now run first, those lists end differently, so the two steps were re-anchored on the lists' new last entries: `'seqCost'` and `'nucReg'`.
- **A fix your code needed.** Your airborne spores and carried cells took their genome but not their sequence, so a settled spore landed with the previous occupant's sequence. With the line of expression on, about 1,300 cells in a pond run had sequences that did not infold to their compound. `seqTake(i)` and `seqPut(i, s)` in `env.js` now carry each cell's sequence and enzymes with it, on both paths (`sporeAir` and `g3Lift`/`g3Carried`). After the fix there were no mismatches in 1,000-tick runs in the pond, springs and vent worlds, with 4,000–5,000 spores settled in each.
- **Checked only on the two-layer path.** The web session's headless Chrome has no WebGPU, so the merged build was tested only on that fallback. The GPU path, including the sequence fix inside `g3Lift` and `g3Carried`, is **untested**. Please run it on the GPU machine first.

**Survival, merged against the web session's last build** (two layers against one, headless, 476 × 248 world, 1,500 ticks, 6 runs per world):

| World | Merged (two layers): survived | Occupancy | Before the merge (one layer): survived | Occupancy |
|---|---|---|---|---|
| Pond | 6/6 | .078 | 6/6 | .087 |
| Springs | 6/6 | .100 | 6/6 | .090 |
| Vent | 5/6 (5 of 6 established) | .027 | 6/6 | .030 |

These are the same within noise.

### What the web session added (all in `tools/`)

**Soma and germ, ruled by the clump's code (its "nucleus"; Justin's chosen term).**
- **The code.** Bits 20–21 of a clump's code (`BG(c)`) set how many of its innermost cells serve as soma: 0, 20, 40 or 60%, recomputed every 4 ticks by distance from the clump's centre.
- **What soma does.** Soma cells do not breed: they are excluded as parents. They pass half their spare light, above `somaKeep`, to the outer germ cells, and pay `somaCost` × upkeep.
- **Found.** The soma trait is selected *against*. Over 3,000 ticks it fell in all four runs, against drift in the controls. Halving soma upkeep did not change that; cutting it to a quarter made it about neutral.

**Regulation of expression (the second articulation).**
- **The code.** Bit 26 of a clump's code switches regulation on, and bits 22–25 name a monomer.
- **What it does.** In that clump's soma cells, the named monomer is skipped when the sequence infolds, through `regApply` and `regRestore`. Their compound and enzymes change while they serve. The sequence itself is untouched, so cells that leave the clump, and every child, express all of it again.
- **Found.** No detectable selection either way in 3 runs against controls, with a wide spread between runs. Setting: `nucReg`.

**Grazers and big clumps.**
- **The rule.** A bite on a clump larger than `gape` (10) succeeds only with chance `gape / size`.
- **Found.** Grazers raise the share of cells in clumps (84% → 93–96%) by eating free cells. But adhesion, clump size and soma do not evolve in response, unlike in Herron and colleagues' 2019 *Chlamydomonas* experiment, which has been checked. Clumps were already about 85 cells, far above the gape.

**Restart when the start fizzles out** (`autoRestart`, on). If fewer than 8 cells are alive in the first 400 ticks, the page sows a fresh seed, up to 20 times. About half of all starts were fizzling out. Tests that need raw survival should set `autoRestart:false`.

**The line of expression: sequences and infolding.**
- **Storage.** `seq` holds up to 48 monomers per cell (`SL`), drawn from the 16 molecules, with the length in `slen`. It is single-buffered: births write only into empty slots, and `moveSeq` moves a sequence with a hopping or drifting cell.
- **Infolding** (`infold`) uses stack pairing. A monomer meeting its complement (`m ^ 8`) on top of the stack pairs with it, and both are buried. The exposed monomers, counted up to 3 each, are the compound's exponents. `seqFromGen` makes a sequence for cells that have none.
- **Births** (`seqBirth`) copy the parent's sequence, or cross two parents' sequences when the birth is a fusion. Copying adds point errors at the base rate × `seqMu`, reduced by the parent's fidelity enzyme; duplications (`seqDup`, 1–4 monomers); and deletions (`seqDel`, 1–4). Each monomer copied costs the parent `seqCost` light.
- **Contagion** (`seqTransfer`) splices a stretch of one cell's sequence into its neighbour's.
- **Found:**
  - **Neutrality.** About 20% of copying errors leave the compound unchanged, and thousands of sequences map to fewer compounds.
  - **No error threshold.** Up to 30 × the error rate there is no collapse. Eigen's threshold, `L < ln σ / p` (checked), assumes a single best sequence, and here many rules are viable.
  - **Sequences lengthen** even with duplications and deletions the same size, and faster without the copying cost. The working guess is a passive trend from the floor at minimum length, as Gould and McShea described for complexity. That source is **not yet checked**, and a control is still needed.

**Infolded pairs as enzymes.** A buried pair of monomer k with k + 8 is an enzyme of kind k, up to strength 3, kept in `cat` (2 bits a kind; read with `CA(i, k)`). The eight kinds:

| Kind | Effect |
|---|---|
| 0 light harvest | upkeep × (1 − .1a) |
| 1 respiration | sugar yield × (1 + .25a) |
| 2 uptake | molecules for a child × (1 − .15a) |
| 3 keeping water | drying harm × (1 − .25a) |
| 4 heat tolerance | heat harm × (1 − .25a) |
| 5 copying fidelity | copying errors × (1 − .25a) |
| 6 defence | bites turned away with chance .25a |
| 7 building | birth light × (1 − .1a) |

Every monomer that pairs no longer counts toward the compound, so a sequence trades its rule against its work. Setting: `catOn`.

**Found** (2 runs per world, 2,500 ticks):

| World | Uptake | Light harvest |
|---|---|---|
| Even | 1.75–1.91 | 0.20–0.29 |
| Pond | 2.24–2.29 | 0.45–0.60 |
| Springs | 2.00–2.11 | 0.41–0.71 |
| Vent | 0.25–0.41 | 0.32–0.44 |

- **Uptake** is selected strongly everywhere except the vent world, where the vents supply molecules.
- **Light harvest** is higher where light is scarce.
- **Defence** is highest in the even world.
- **Keeping water and heat tolerance** stay weak.
- **Pond occupancy** is .089 with enzymes against .056 without.

**Open, lift and fold as readouts (measures, not causes).**
- **`OLF` counts flows by source.** For CO₂, water and the ground's molecules it weighs what life returns against what the world brings:
  - from life: breathing, fermenting, rot, the dead, producers;
  - from the world: air, vents, rain, regrowth.
- **The panel and the chronicle.** `olfStep` keeps moving averages every 2 ticks. The panel shows life's share of each input. Every 50 ticks the chronicle logs crossings, with hysteresis at 55% and 45%:
  - **Open:** life now supplies most of an input.
  - **Lift:** clumps hold most of the living.
  - **Fold:** most of the living are dormant spores.
- **Found.** In the even world and the pond, life supplies about 90% of the CO₂ and water and 54–81% of the molecules. In the vent world it supplies only 15–20% of the molecules.

**Biology claims checked by web search** (11 November). The README's earlier brief said spores "ride the plume", so the third claim matters most:

- **Plume cooling.** Plumes entrain about 10,000 times their volume as they rise 100–250 m in about ten minutes, and are bent by cross-flows of about 1–4 cm/s.
- **SUP05.** SUP05 bacteria dominate sulfur-rich plumes. Methane-eaters do not appear in every plume.
- **Thermophilic spores.** Hubert and colleagues (2009) found thermophilic spores arriving in Arctic sediments at more than 10⁸ per square metre per year. Their closest relatives are from warm subsurface petroleum reservoirs and ocean crust, not specifically vent plumes. So spore dispersal by plumes is a model choice, not an established finding.
- **Clumping under predation.** Herron and colleagues (2019): *Chlamydomonas* evolved multicellular structures under *Paramecium* predation in 2 of 5 populations.

**New parameters:** `somaOn:true, somaKeep:.15, somaCost:.5, gape:10, autoRestart:true, seqOn:true, catOn:true, nucReg:true, seqMu:1, seqDup:.02, seqDel:.02, seqCost:.004`.

**New tests:**
- `test/soma.py`: the soma trait and clump statistics over time.
- `test/seqrun.py`: sequence length, sequences against compounds, and neutrality.
- `test/catrun.py`: enzyme profiles by world.
- `test/regrun.py`: the regulation switch and the soma trait.

All take a build path. Your `gene2.py` and `runset.py` are replaced by the web session's versions, which also report survival among colonies established by tick 200 and clump share.

### Next, for you

1. **Run the merged build on the GPU path** (3D water on) in pond, springs and vent. Check that there are no page errors, and that settled carried cells keep their sequences: no cell whose `infold(seq, i*SL, slen[i])` differs from `gen[i]`, outside regulated soma (`regd[i]`).
2. **Carry O₂ and CO₂ in the two layers or in 3D,** as your notes list. With the reactions, oxygen made on the floor and lost at the surface could make the slow rise of oxygen depend on the overturning.
3. **Report timing with the new per-cell work.** Infolding happens at birth and contagion, and every 4 ticks for regulated soma. At about 100,000 cells the web session saw 60 ms a tick at 1,100 × 700, against about 35 ms before the line of expression, though populations differed.


## The original task (steps 1 and 2 are done; kept for the record)

Justin wants the circulation to come from the physics: warm water rising, spreading along the surface, sinking where it is cool and returning along the floor. Today an imposed cross-current fakes it. See the cutaway idea: a vent's plume rises to the surface layer and spreads; cool water sinks at the edges and flows back along the floor layer toward the vent, past the colonies on the floor.

**Step 1: two layers, on the CPU, in the page.**
- **Two velocity fields.** Keep a floor layer and a surface layer, each a 2D field on the coarse grid. `fx` and `fy` should stay the **floor** layer, because the cells live on the floor and `advect()` and `driftPass()` read them.
- **Vertical exchange.** Each square gets an upwelling rate `w` from buoyancy (temperature against the local or mean temperature, plus the vent's hot core). Where `w > 0`, floor water rises into the surface layer, so the floor converges toward the spot and the surface diverges. Where `w < 0` the reverse happens. Use the projection source term per layer with opposite signs, which conserves mass across both layers.
- **Two heat fields.** Keep heat per layer and carry it up and down with `w`. The vent heats the floor layer; the surface layer loses heat to the air. Cells feel the floor temperature.
- **Ordinary layer physics.** Each layer self-advects and has viscosity and eddies. Floor drag applies only to the floor layer. A weak coupling, a shear drag between the layers, is optional, and so is a small Coriolis term, which would turn the overturning into gyres.
- **What the layers carry.** Decide which fields belong to which layer, or keep them single-layer on the floor. A reasonable start: heat and O₂ exchange in both layers, while sugar, molecules and the signal stay on the floor.
- **Spores ride the plume.** Dormant cells (`dor[i]`, not in a clump) in squares with strong upwelling can be lifted into the surface layer. Keep a light list or a per-square count of airborne spores, each with its genome and extension genome. Carry them with the surface flow, and let them settle back onto the floor with a small chance per step, more where water sinks. A settled spore lands in an empty cell of its square, or is lost if there is none. This mirrors real vents, where thermophiles survive cool plumes as spores and are dispersed far away. Report how far spores travel and whether this changes the spread of lineages between vents.
- **Later, not now: life in the water.** Cells that live and grow in the surface layer, like plankton, would be a third habitat. Leave room for it but don't build it yet.
- **Retire the fake.** Retire `crossflow`, or keep it as an optional "tide".
- **Views.** Show the floor current (the existing Current view), the surface current, and maybe a side slice through the middle like the cutaway.
- **Check.** Run survival with `runset.py` in pond, springs and vent against the current build. Look at the heat view for plumes and overturning, measure the time per tick, and keep it under about +5 ms a tick at this size.

**Step 2, optional: full 3D on the GPU.** Justin has a computer with a GPU. If the two-layer model feels flat:
- Try a coarse 3D grid, about 128 × 64 × 16, with WebGPU compute shaders (or WebGL2 fragment-shader ping-pong as a fallback), for velocity, heat and possibly gases.
- Read the floor layer back to the CPU every few ticks for the cells, or move the coarse fields to the GPU entirely.
- Keep the page a single self-contained HTML file. Feature-detect WebGPU and fall back to the two-layer CPU model.
- A side or perspective view would let Justin see the 3D water.
- Install whatever local tooling you need on Justin's machine. Tell him what you installed.

**Ground rules.**
- Edit the files in `tools/`, then rebuild. Never edit the build by hand.
- Keep the old behaviour reachable through a setting until the new model tests as well or better.
- Report results honestly with run counts, including what didn't work.
- Justin writes anything meant for other people himself, so code and notes are fine but don't draft prose for him to send.
