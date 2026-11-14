# fold3d: a 3D lattice folding prototype (task 02)

A standalone prototype, outside the page. Nothing here goes into the page.

## What it does
- Folds the page's sequences (monomers a–p, codes 0–15) as self-avoiding chains on a 3D cubic lattice.
- Energy, summed over lattice neighbours that are not chain neighbours (all proposals, all parameters):
  - oily–oily contact −1 (Dill's HP model, 1985);
  - complement contact (m with m ^ 8) −eP, default 1 (adds to the oily term when both apply);
  - a polar monomer with all six lattice neighbours occupied and no complement among them: +eB, default 0.5.
- Polarity rules: `odd` (oily when `m & 1`, the default) or `low` (oily when `m < 8`).
- Search: Metropolis Monte Carlo with end, corner, crankshaft and pull moves. One folding run is replica exchange
  (parallel tempering): 8 copies of the chain at temperatures 0.12 to 1.0 (geometric), swapping temperatures every
  100 steps, 2,000 sweeps; the lowest energy any copy visits is the run's fold. Plain annealing is also available
  (`fold_many(..., method='anneal')`); it found low folds less often for the same GPU time (results/search.json).
  Many chains run at once on the GPU (PyTorch, CUDA graphs).

## Files
- `lattice.py`: the engine (`Batch`, `GraphRunner`), a numpy reference energy, symmetry-canonical fold keys.
- `run_all.py`: all measurements; writes `results/*.json` and `sample_folds.json`.
- `figs.py`: the report's figures (PIL) and `results/summary.json`.
- `dump_seq.js`: page script that dumps living cells' sequences from the even and vent worlds at tick 1,000.
- `make_page_seqs.py`: merges those dumps into `data/page_seqs.json`.
- `sample_folds.json`: about 50 folds (sequence, coordinates, energy, Tm) for the viewer.

## Run
One command (from this folder; on the shared machine, through the GPU queue):

    python D:\manuscript-images\gpu_queue\gpu_run.py run fold3d --free-mb 2500 --cwd . -- python run_all.py

then `python figs.py` for the figures. `python run_all.py --quick` is a two-minute smoke test (writes to
`results_quick/`). A stage whose result file exists is skipped; `--force` reruns, `--only speed,conv,...` picks stages.

Page sequences (already in `data/page_seqs.json`): with the headless-Chrome harness in `jgol_2026-11-13/test`,

    python rates_driver.py OUTDIR --sugar 1 --glide 0 --seeds 6 --T 1000 --W 160 --par 1 --port 8812
        --script ../../justins-game-of-life/fold3d/dump_seq.js --page ../../justins-game-of-life/build/justins_game_of_life.html
    python make_page_seqs.py OUTDIR

## sample_folds.json
`folds[]`: `seq` (letters a–p), `coords` (integer lattice sites, one per monomer, in order), `energy`, `tm` (melting
temperature, energy units where an oily–oily contact is 1; null when the fold did not melt in range), `oily` per monomer,
`bracket_pairs` (the page's infold pairs, positions), `found_in_anneals` of `anneals`.

## Notes
- Occupancy grids are 32 sites a side, taken modulo 32; a move into a site whose residue is 32 sites away is refused.
  This only forbids chains more than 32 sites across.
- Pull moves are used with plain Metropolis acceptance; their proposal is close to, not exactly, symmetric.
