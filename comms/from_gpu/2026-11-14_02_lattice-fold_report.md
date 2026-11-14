# 02: a 3D lattice folding prototype: report

From: gpu session, 14 November 2026. Answers `to_gpu/2026-11-14_02_lattice-fold.md`.

## Summary
- **Built:** `fold3d/`, a batched GPU folder for the page's sequences on a 3D cubic lattice (PyTorch, CUDA graphs). One
  command runs every measurement. `fold3d/sample_folds.json` holds 48 folds for the viewer.
- **Speed (measurement):** with 4,096 chains at once, one fold costs 0.08 s (length 16) to 4.9 s (length 128) of GPU time.
  Page sequences at tick 1,000 are short (most under 20). So folding every newborn is not feasible inside the page.
  Caching folds by sequence would be (proposal).
- **No unique native fold (measurement):** the search finds the lowest energy in 94% of runs for page sequences. But
  10 runs give on average 8.4 different folds at that energy. The same fold recurs in only 17% of runs. The HP-style
  energy has many equally good folds. This is the main result.
- **Melting is gradual, not abrupt (measurement):** Tm = 0.43 ± 0.14 (energy units, 48 sequences). The transition is
  about as wide as Tm itself. Lehninger's abrupt, cooperative unfolding does not appear.
- **The page's brackets do show in 3D (measurement):** 76% of non-adjacent bracket pairs touch in the lattice fold,
  against 28% for any pair at the same distance along the chain. Bracket domains keep twice the share of their
  contacts inside (0.18 against 0.09). With eP = 0 this vanishes (0.33 against 0.27). So it comes from the complement
  energy, not from the oily–polar pattern.

## The model (all proposals, from the task)
- Chain: one monomer per lattice site, bonds of length 1, no two monomers on one site.
- Energy over lattice neighbours that are not chain neighbours ("contacts"):
  - oily–oily −1 (Dill 1985, HP model);
  - complement (m with m ^ 8) −eP, default 1. It adds to the oily term when both apply (proposal);
  - +eB, default 0.5, for a polar monomer whose six neighbour sites are all filled (bonded or not), with no complement
    among the six (proposal; Lehninger: an unpartnered charged group in a core destabilises).
- Polarity rules: `odd` (oily when m & 1; default) and `low` (oily when m < 8).
- Moves: end, corner, crankshaft and pull moves, Metropolis acceptance.
- Search (proposal, changed from the brief): plain annealing was too weak (next section). One "run" is now replica
  exchange: 8 copies of the chain at temperatures 0.12 to 1.0, swapping every 100 steps, 2,000 sweeps. The run's
  fold is the lowest energy any copy visited. The 10 "anneals" per sequence are 10 such runs.
- Checks (measurement): the GPU energy matched a plain reference code on every chain tested, and no chain ever
  overlapped itself or broke a bond.

## 1. Speed
Measured step times; time per fold = one run (8 copies × 2,000 sweeps). See `02_speed.png`.

| length | batch 1 | batch 256 | batch 4,096 |
|---|---|---|---|
| 16 | 119 s | 0.48 s | 0.085 s |
| 32 | 208 s | 0.97 s | 0.32 s |
| 64 | 413 s | 2.3 s | 1.2 s |
| 128 | 823 s | 6.4 s | 4.9 s |

- A single chain is limited by kernel launches (0.4 ms a step whatever the length). Batching is everything.
- Page sequences (measurement): six seeds, tick 1,000. Even world: 400–1,000 distinct sequences per run, length at most
  21, cell-weighted mean length 2–5. Vent world: died and restarted in 5 of 6 seeds; the one that lived (seed 3) had
  10,872 distinct sequences, lengths up to 36, mean 14.
- Reading (proposal): the vent world alone makes thousands of new sequences per few hundred ticks. At 0.1–0.3 s each,
  folding them live would take longer than the run. Fold each distinct sequence once, cache by sequence, and fold in
  batches between page runs or on demand for the selected cell.

## How hard the search is
`02_convergence.png` (plain annealing, T 2 → 0.1) and `results/search.json`. Measurements.

| method (24 random sequences, length 32, 8 runs each) | GPU s | runs at best-known energy | sequences where best found |
|---|---|---|---|
| annealing T 1 → 0.1, 4,000 sweeps | 63 | 8% | 50% |
| replica exchange 8 × 500 sweeps | 18 | 3% | 21% |
| replica exchange 8 × 2,000 sweeps (used) | 74 | 25% | 83% |

- Length 16: annealing reaches the best energy in 90% of runs at 4,000 sweeps, 100% at 16,000.
- Length 32 and 48: under a quarter of runs reach the best known energy even at 16,000 sweeps.
- So results below are firm for page sequences (lengths 12–26) and only indicative for random length-32 sequences.

## 2. Reproducibility
200 sequences × 10 runs: 120 page sequences (length 12–26, mean 15; 91 vent, 29 even) and 80 random of length 32.
`02_reproducibility.png`. Measurements.

| | page (120) | random 32 (80) |
|---|---|---|
| runs reaching the lowest energy found | 94% | 25% |
| distinct folds at that energy, in 10 runs | 8.4 | 2.5 |
| runs giving the most common lowest fold | 17% | 10% |
| sequences whose lowest fold recurs in ≥ 8 of 10 runs | 1 of 120 | 0 |
| sequences whose lowest fold appears only once | 55% | 100% |
| native contacts shared by a run's fold and the native | 59% | 48% |

- Folds are compared up to rotation and reflection (48 symmetries), chain direction kept.
- Reading: for page sequences the search works; the energy is the problem. Many folds tie for the lowest energy, so
  "the native fold" is not defined. This is a known property of two-letter HP models: many sequences have degenerate
  ground states.
- A "native" in the rest of this report = the most common of the lowest-energy folds (proposal).

## 3. Melting
48 page sequences (the longest of the 120 with at least 3 contacts; lengths 16–26). Each starts from its native and runs
at 14 temperatures, 4 copies, 1,000 sweeps to settle and 3,000 measured. Q = fraction of native contacts present.
`02_melting.png`. Measurements.

| measure | value |
|---|---|
| Q at T = 0.1 | 0.88 (not 1: the chain moves among tied folds) |
| Q at T = 2 | 0.14 (chance contacts) |
| Tm (Q at half its low-T value), mean ± sd | 0.43 ± 0.14; range 0.18–0.91 |
| Tm with Q rescaled between its low-T and high-T values | 0.38 ± 0.11; range 0.16–0.63 |
| transition width (Q from 80% to 20% of the way), median | 0.40, about 1.0 × Tm |
| sequences with width under 0.3 × Tm ("abrupt") | 0 of 48 |
| bimodality of Q at Tm (over 0.555 suggests two states) | 0.51 |
| heat capacity (mean over sequences) | a broad hump from T 0.4 to 0.7 |
| Tm against length / against lowest energy (correlation) | −0.29 / 0.06 |

- Reading: unfolding is gradual. A few sequences lose most native contacts between two neighbouring temperatures
  (e.g. Q 1.0 → 0.44 between 0.3 and 0.4), but none is two-state on the measures above. Lehninger describes heat
  unfolding as abrupt over a narrow range. Plain contact models of short chains are known not to do this.
- Proposal: if the page wants cooperative melting, add a cooperative term, e.g. a bonus that grows faster than the
  number of native-like contacts, or a core term (oily monomer fully buried). Tm itself does spread across sequences
  (0.18–0.91), which is what heat tolerance needs.

## 4. Sequence to fold
Measurements.
- Distinct folds: all 120 page sequences have different native folds (no two share one, up to symmetry). With 8 or so
  tied folds each, "distinct" says little.
- One mutation: 40 page sequences × 5 random single mutations, 5 runs each.

| | all (200) | polarity unchanged (92) | polarity changed (108) |
|---|---|---|---|
| wild-type native still a lowest-energy fold for the mutant | 56% | 71% | 43% |
| mutant's native identical to wild type's | 5% | 10% | 1% |
| wild-type native contacts kept in the mutant's native | 49% | | |

- The "identical" row is not meaningful: even unmutated sequences repeat their own native only 17% of the time.
- The first row is the useful one. About half of single mutations make the old fold no longer optimal. A change of
  polarity (oily ↔ polar) does so more often (57% against 29%).

## 5. Against the page
Brackets as in `infold` (tools/env.js): a monomer pairs with the nearest open complement (m ^ 8) on the stack; a pair
with everything inside it is a domain.
- Page bracket structure (measurement): most pairs are neighbours on the chain (e.g. `hp`, `np`). Of all cells, only
  0.2% (even) and 2.3% (vent) carry a pair that is not adjacent. 225 distinct sequences have one; 120 of them were
  folded (5 runs each), giving 135 non-adjacent pairs and 121 domains of 4 or more monomers.
- Overlap (measurement; `02_page_brackets.png`):

| setting | bracket pairs in contact | any pair, same separation | domain: share of contacts inside | any window, same length |
|---|---|---|---|---|
| eP 0 | 0.33 | 0.27 | 0.10 | 0.09 |
| eP 1 (default) | 0.76 | 0.28 | 0.18 | 0.09 |
| eP 2 | 0.81 | 0.29 | 0.19 | 0.09 |
| rule m < 8, eP 1 | 0.64 | 0.28 | 0.15 | 0.09 |

- Reading: with the complement energy, the page's bracket pairs mostly become real 3D contacts, and bracket domains are
  about twice as self-contained as random stretches. Without it, oily–polar folding alone ignores the brackets. With
  rule m < 8 every complement pair is oily–polar, so the oily term competes with pairing and fewer pairs form.
- Proposal: if 3D folds are adopted, keep eP ≥ 1 so the page's pairing rule and the 3D fold agree.

## How results depend on the parameters
First 60 page sequences, 10 runs each; melting on 16 of them, 12 temperatures, 2 copies. `02_parameters.png`.
Measurements.

| setting | lowest energy (mean) | same lowest fold | tied folds in 10 runs | Tm (mean ± sd) | Q at T 0.1 |
|---|---|---|---|---|---|
| default (odd, eP 1, eB 0.5) | −12.1 | 16% | 8.9 | 0.37 ± 0.07 | 0.93 |
| eP 0 | −7.8 | 13% | 9.5 | 0.49 ± 0.30 | 0.64 |
| eP 2 | −16.3 | 16% | 8.8 | 0.61 ± 0.22 | 0.89 |
| eB 0 | −12.1 | 16% | 8.9 | 0.43 ± 0.11 | 0.87 |
| eB 1 | −12.1 | 17% | 8.9 | 0.44 ± 0.12 | 0.86 |
| rule m < 8 | −7.7 | 18% | 8.7 | 0.36 ± 0.19 | 0.84 |

- eB has no effect on the lowest energies: in chains of 12–26 almost no polar monomer is fully enclosed. It matters
  only for longer chains (not tested here).
- eP raises stability and Tm, and helps the brackets show in 3D. It does not remove the tied folds.
- eP 0 leaves the native poorly held even when cold (Q 0.64 at T 0.1): pure oily–oily folds are the most degenerate.
- The polarity rule changes energies (m < 8 gives fewer oily monomers in page sequences) but not reproducibility.
- Tm differences between settings in this smaller run are within about one standard deviation, except eP 2.

## What failed or was cut
- "A native fold found reliably": not met, because of tied folds, not search failure (page sequences).
- Random length-32 chains: the search is not converged; their numbers are lower bounds.
- Parameter runs used 60 sequences (not 200), melting runs for parameters 16 sequences and 2 copies.
- The page stage folded 120 of 225 eligible sequences, 5 runs each; mutants 5 runs each.
- No lengths above 36 were folded for measurements (page sequences don't reach them at tick 1,000); 64 and 128 were
  timed only.
- Vent world: 5 of 6 seeds died and restarted before tick 1,000, so vent sequences come from one seed (seed 3).
- Pull moves use plain Metropolis acceptance; their proposal is close to, not exactly, symmetric.
- GPU time used: about 75 minutes for the measurements, plus about 15 minutes of tests.

## Proposals (for Justin's decision)
1. Do not fold inside the page in real time. Fold distinct sequences offline in batches and cache by sequence.
2. Before any page use, reduce tied folds: more than two monomer classes in the energy (e.g. a 16 × 16 contact table),
   or rank tied folds by a second criterion. Otherwise "the fold" of a sequence is a set, not one shape.
3. For heat: Tm already varies across sequences, so heat tolerance could be read from it. For abrupt melting, add a
   cooperative term.
4. Keep the complement energy (eP ≥ 1) so the page's brackets and the 3D fold agree.

## Files
- Code: `fold3d/lattice.py`, `fold3d/run_all.py`, `fold3d/figs.py`, `fold3d/make_page_seqs.py`, `fold3d/dump_seq.js`,
  `fold3d/README.md`.
- Data: `fold3d/data/page_seqs.json` (page dumps), `fold3d/results/*.json`, `fold3d/sample_folds.json` (48 folds).
- Figures: `02_speed.png`, `02_convergence.png`, `02_reproducibility.png`, `02_melting.png`, `02_parameters.png`,
  `02_page_brackets.png`, `02_example_folds.png`.
