# beadfold: the ground-up folding prototype (task 15)

A standalone prototype, outside the page; nothing here goes into the page until Justin approves. Built in the order
of report 12, section 11 (design approved by Justin, 14 November). Everything in the model is a proposal.

- `beads.py` (step 1): Martini-style beads for the 16 monomers, and the 16 x 16 contact table e_ab(T, I, pH) and
  burial terms h_a(T) computed from them.
- `secondary.py` (step 2): the helix-coil (Zimm-Bragg) rule with charge corrections, and strand/coil shares.
- `checks.py`: computes the tables over 280-340 K and 5 mM-1 M, fits them, runs steps 1 and 2's checks; writes
  `results/steps12.json` and the figures `comms/from_gpu/15_step*.png`.
  Run: `python checks.py` (needs numpy and matplotlib; about 10 s on one CPU thread).

Report: `comms/from_gpu/2026-11-14_15_design-approved-prototype_report.md`.
