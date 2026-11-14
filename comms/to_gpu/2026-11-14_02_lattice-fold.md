# 02: a 3D lattice folding prototype (standalone, outside the page)

From: cloud session, 14 November 2026. Answers nothing; new task.

## Background
Justin decided (THEORY_NOTES, 14 November): folds should be only marginally stable, with heat lowering stability, and
monomers should carry polarity (oily or polar). He approved two levels: a 3D view of the current bracket fold (the cloud
session builds this in the page), and a real 3D folding model (this task, a prototype only). Nothing here goes into the
page yet.

## The model (Claude's proposal; every choice below is a parameter, report how results depend on it)
- **Chain:** a cell's sequence (16 monomers, a–p, codes 0–15, length up to 128) as a self-avoiding walk on a 3D cubic
  lattice.
- **Polarity:** monomer m is oily when `(m & 1) == 1`, polar otherwise. This keeps a monomer and its complement
  (m ^ 8) in the same class. Also try `m < 8` oily (then every complement pair is oily–polar) and report the difference.
- **Energy** (lower is better), summed over lattice neighbours that are not chain neighbours:
  - oily–oily contact: −1 (Dill's HP model, 1985);
  - complement contact (m with m ^ 8): −eP, default 1, so the page's pairing rule still means something in 3D;
  - an oily monomer with no polar or water neighbour is fine; a polar monomer buried with six non-water neighbours and
    no complement among them: +eB, default 0.5 (Lehninger: unpartnered polar groups in a core destabilise).
- **Search:** Metropolis Monte Carlo with pull moves (or crankshaft + end + corner moves), at temperature T; anneal from
  high T for the native fold. Use the GPU (CuPy, Numba CUDA or PyTorch, your choice) to fold many chains in parallel.

## Measure
1. **Speed:** time per fold against length (16, 32, 64, 128), batch sizes 1, 256, 4096. Is folding every newborn's
   sequence feasible, or must folds be cached by sequence?
2. **Reproducibility:** for 200 sequences, 10 independent anneals each: how often the same lowest-energy fold (up to
   rotation and reflection) is found. A "native" fold should be found reliably.
3. **Melting:** fraction of native contacts against T for 20 sequences. Is the loss abrupt (cooperative), as Lehninger
   describes, or gradual? Report a melting temperature Tm per sequence and its spread.
4. **Sequence to fold:** how many distinct folds among the sequences; how often one mutation changes the fold.
5. **Against the page:** take real sequences from page runs (dump `seq`/`slen` of living cells from the even world and
   the vent world at tick 1,000; the page is `build/justins_game_of_life.html`). Do the page's bracket domains (pairs
   nested as in `infold`, tools/env.js) correspond to compact regions of the lattice fold? Report the overlap.

## Deliver
- Code in `fold3d/` (new folder), runnable with one command; README there.
- `comms/from_gpu/2026-11-14_02_lattice-fold_report.md`, with figures as PNGs.
- `fold3d/sample_folds.json`: about 50 folds (sequence, coordinates, energy, Tm) for the cloud session's viewer.
- Mark proposals as proposals; measurements as measurements.
