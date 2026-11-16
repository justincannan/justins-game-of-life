# beadfold: the ground-up folding prototype (task 15)

A standalone prototype, outside the page; nothing here goes into the page until Justin approves. Built in the order
of report 12, section 11 (design approved by Justin, 14 November). Everything in the model is a proposal.

- `beads.py` (step 1): Martini-style beads for the 16 monomers, and the 16 x 16 contact table e_ab(T, I, pH) and
  burial terms h_a(T) computed from them.
- `secondary.py` (step 2): the helix-coil (Zimm-Bragg) rule with charge corrections, and strand/coil shares.
- `checks.py`: computes the tables over 280-340 K and 5 mM-1 M, fits them, runs steps 1 and 2's checks; writes
  `results/steps12.json` and the figures `comms/from_gpu/15_step*.png`.
  Run: `python checks.py` (needs numpy and matplotlib; about 10 s on one CPU thread). Step 3 needs numpy, torch
  (CUDA) and PIL only.

- `tertiary.py` (step 3): the off-lattice folder. One bead per monomer, the step-1 table and burial, step 2's
  secondary probabilities as local biases, backbone H-bonds, and the cooperative (many-body desolvation) term
  (mode `coop`; mode `additive` is the control without it). Replica-exchange Langevin dynamics on the GPU (PyTorch,
  CUDA graphs), WHAM, Kaya-Chan kappa2.
- `run_step3.py`: GPU stages (`pilot`, `scan`, `conv`, `go`, `page`, `random`, `additive`); writes `.npz` batches to
  `D:/labyrinth/automata/jgol_2026-11-13/results/2026-11-14/task15_step3/` (too large for the repository).
  Run through the shared GPU queue, e.g. `python run_step3.py page --nrun 10 --nsteps 60000`.
- `analyse_step3.py PREFIX`: per-sequence uniqueness, melting (f, Q, C, kappa2), native core and charges (CPU).
- `summary_step3.py`: `results/step3_summary.json` and the figures `comms/from_gpu/15s3_*.png` (PIL).
- `saltbridge_step3.py`: task 20's benchmarks in the model's own energy; `results/step3_saltbridge.json`.

Task 23 (two beads per monomer, Justin's decision of 15 November; the one-bead files above are unchanged and still
work):
- `twobead.py`: the two-bead model (backbone + side-chain bead): step 2's local bias, backbone H-bonds (helix i -> i+4
  and strand pairing), a packing (van der Waals) term by bead size, a burial-dependent dielectric for side-chain
  charges, burial with the cooperative term (modes `coop` / `additive`); `REMD2` reuses tertiary.py's integrator.
- `run_tb.py`: GPU stages (`probe` = the two hand designs, `go` = Go instrument check from a natives file, `fold`
  = sequences from a JSON file, `page`, `random`, `additive`); `.npz` batches to
  `D:/labyrinth/automata/jgol_2026-11-13/results/2026-11-15/task23/`.
- `analyse_tb.py PREFIX [--target-file results/tb_targets.json] [--native-file ...]`: step 3's readouts for two beads.
- `saltbridge_tb.py`: stage 1's term checks (salt-bridge benchmarks, eps_core scan, packing) -> `results/tb_stage1_terms.json`.
- `targets_tb.py`: the five design targets -> `results/tb_targets.json`; `--go OUT` writes Go natives.
- `design_tb.py`: sequence design by Monte Carlo on the energy gap, with folding rounds -> `results/tb_designs.json`.
- `relax_targets_tb.py`: each design's target relaxed with its sequence, against its blind fold -> `results/tb_target_relax.json`.
- `stage4_tb.py walk|neutral`: mutational distance of page sequences to foldable ones; single mutants of a design.
- `summary_tb.py`: `results/tb_summary.json` and the figures `comms/from_gpu/23_*.png`.

Reports: `comms/from_gpu/2026-11-14_15_design-approved-prototype_report.md` (steps 1-2),
`comms/from_gpu/2026-11-14_15_step3_tertiary-fold_report.md` (step 3),
`comms/from_gpu/2026-11-15_23_two-beads_report.md` (task 23, two beads).

Task 26 and task 27 (Justin's decisions of 15 November, about 21:26, and 16 November, about 00:19; the task-23 modes
`elec='v23'` and `helix='v23'` are the defaults and unchanged):
- `twobead.py`: `elec='split'` (pairs at eps_pair 20, Born self term at eps_self 4-6), `elec='cd'` (split plus the
  charge-dipole payback by polar neighbours, MU_CD; task 27), `h_charge='iso'`; `helix='coop'` and `helix='coop2'`
  (Zimm-Bragg nucleation on the helix H-bonds; step 2, did not meet its check).
- `charges26.py`, `charges27.py`, `charges27_refold.py`: charge benchmarks and random 32-mers -> `results/t26_step1_charges.json`,
  `results/t27_charge_dipole.json`.
- `helix26.py`, `helix26_fig.py`: isolated-helix content against step 2's Zimm-Bragg -> `results/t26_step2_helix.json`,
  `comms/from_gpu/26_helix.png`.
- `design26.py`, `design26_summary.py`: the design loop with relaxed targets and relaxed decoys (step 3) ->
  `results/t26_designs.json`, `results/t26_design_summary.json`, `comms/from_gpu/26_design.png`.
- `summary26.py`: step 5's summary (not run: step 2 did not meet its check).
- `run_tb.py` takes `--model '{"elec": "cd", "h_charge": "iso"}'` (Model2 options) for every stage.
Report: `comms/from_gpu/2026-11-15_26_folding-proposals-approved_report.md`.
