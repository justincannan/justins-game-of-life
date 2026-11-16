# 30: repeatable runs (notice; affects task 29 and every seeded comparison)

From: cloud session, 16 November 2026, about 11:00.

**Problem found.** The same seed did not give the same run (81,927 against 89,309 cells at tick 1,000, even world).
Causes, all fixed in the page:
- the geography (GEO) was drawn before a harness set its seeded rng, so from Math.random;
- zone climates used Math.random (newblock3.js newClimate);
- reset did not clear the sequence buffer, the per-cell reaction words, the coat arrays, or the **free chains in the
  water** (frAmt and the rest), so chains from the previous world floated into the new one. This was a real bug for
  every user, not only for tests; it is now cleared on every reset;
- the environment's first step in reset ran at the old world's tick (tick was set to 0 later in reset);
- the environment arrays (tamb and others) carried over.

**How to seed a run now:** set `P.seed` to a positive integer before `reset(mode)`. Every new world (not an automatic
restart) then reseeds the rng, redraws the geography, zone climates and environment, and clears the leftovers. Do not
replace `rng` or call `geoSeed()` by hand any more. P.seed 0 keeps the old Math.random behaviour.

**Checked:** even, vent, pond and springs from a soup, 600 ticks, three fresh page loads (waits of 400 and 1,500 ms
before taking control): identical cell counts and identical hashes of gen and light every 100 ticks.
Script: test/rep4.py (and rep5.py, which finds the first tick and array that differ).

**For task 29:** results from before this commit are not exactly repeatable. Re-run the baselines with P.seed, or
treat earlier seed-to-seed spread as including this noise. Note also two page changes landing in the same commit:
a running cost per working domain (P.domCost, default 0.001 light a tick per reaction) and origin tags on monomers
(display only; confirmed not to change the run). Set P.domCost = 0 to compare with the stage-1 page.
