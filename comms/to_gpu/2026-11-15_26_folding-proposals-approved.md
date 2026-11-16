# 26: task 23's proposals approved (1, 2, 3, then 5; 4 after if needed)

From: cloud session, 15 November 2026, about 21:35. Justin's decision: THEORY_NOTES.md, "Decisions (Justin, 15 November,
about 21:26)". Answers report 23, section 5.

1. **Charge clusters: do both of your options, as the literature advises.**
   - **Self term:** a Born-like desolvation cost for each buried charge, using a low dielectric (ε_core about 4–6).
   - **Charge–charge interactions:** a high effective dielectric of about 20.
   - Sources (abstracts; check the papers before fixing numbers):
     - Schutz and Warshel 2001, *Proteins* 44: 400: the optimal dielectric constant for self-energies is not the
       optimal one for charge–charge interactions.
     - Sham, Muegge and Warshel 1998, *Biophys. J.* 74: 1744: use a large ε for charge–charge interactions and a
       small one for charge–dipole and self terms.
     - Staphylococcal nuclease pair energies from pKa shifts (PMC2373567): continuum calculations matched experiment
       with an interior ε of 20.
   - Recheck task 20's benchmarks (partner relief; a buried pair 0–6 kT worse than its oily isostere), and report the
     median Coulomb energy of random 32-mers before and after.
2. **Helices: the cooperative term,** with nucleation and propagation in the tertiary energy (Zimm–Bragg-like).
   Recalibrate isolated-helix content against step 2.
3. **The design test: relaxed target and relaxed decoys** (a few hundred gradient steps, side chains free), keep the
   relaxed competitors, more rounds, gaps evaluated on relaxed energies. This is also the tool for developed starting
   proteins, so report its cost per designed sequence.
4. **Sheets:** only if they still lag after 1–3 and 5.
5. **Repeat** the design test on the same five targets, then step 3's sets.

Report after each step, as task 15 asks. Copying errors: Justin keeps the page's rate for now; nothing to do.
