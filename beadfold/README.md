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

Reports: `comms/from_gpu/2026-11-14_15_design-approved-prototype_report.md` (steps 1-2),
`comms/from_gpu/2026-11-14_15_step3_tertiary-fold_report.md` (step 3).
