# 33: the chemotroph vent founder is in the page (re-measure when convenient)

From: cloud session, 16 November 2026, about 12:20. Justin's decisions at 12:05 and 12:09 (THEORY_NOTES.md, "Decisions
(Justin, 16 November, about 12:09), report 29; built"). Commit 34eceaf.

- `chemoFounder()` gives the vent founder a chemotroph gene: report 29's proposal 1, scored by energy released times
  the founder square's supply. Cloud check, seeds 11–30, 400 ticks: 20 of 20 founded. It picked `4 4 4 4 15 0 8 7` in
  18 seeds and `2 2 2 2 13 2 10 5` in seeds 19 and 30.
- `dishSetup` puts the `15 7` pair before a trailing run of three 15s: all 12 dish founders are one gene with 0xf0.
- The coat-array fix (f3a8b1c) stays.
- Seeding: use `P.seed` (task 30). The running cost `P.domCost` is 0.001 by default; set 0 to compare with b4ceffa.

Please re-measure vent founding with your harness when the CPU queue allows, and re-run the 4 affected dish seeds
(2, 3, 4, 6) if useful. Low priority; after tasks 26–28.

**Added about 14:00:** two more page fixes in the same series. (1) One-organism runs were not repeatable: stale
division targets carried over; now cleared on reset. (2) Virus copying could drive a square's molecules negative,
which turned whole clumps' energy into NaN and killed them in one tick: the cause of the vent die-outs. Any vent
measurement long enough for viruses to copy, from before this commit, is affected. Re-measure on this page.
