# Day queue, second addendum (13 November, about 12:30, from the cloud session)

Thank you for the validation; it was decisive. Your energy fit pointed to a flaw in the page, now fixed. So the page
has changed, and your measurements need repeating.

## What changed in the page since your measurements
Use the new `justins_game_of_life.html` in this bundle.
1. **Heterotrophs store energy from sugar.** An eating cell now also tops up its store towards hetStore (0.4), at most
   hetFill (0.02) × gene strength a tick, within its uptake limit. Dormant cells do this at a quarter of the rate.
   Before, an eating cell only covered each tick's shortfall, so stores ran down like a clock. Your finding.
2. **The chemistry audit.** Matter and energy are now conserved:
   - production is built from sugar;
   - deaths return everything;
   - no lonely-birth fee with the Life rule off;
   - contagion pays for what it rewrites;
   - coat is matter;
   - the reserve no longer multiplies energy;
   - uphill reactions cost more than they store;
   - moving cells take their energy with them;
   - reactions follow Michaelis-Menten kinetics (rxKm 1).
3. **Vent strength (ventPower)** now defaults to 2.
4. **Fragments in the ground** (fragOn): dying cells release short chains, which break down, may catalyse, and may
   be taken up.
5. **The population dish's folded record** (not needed for your runs).

## Please, in order
1. Let the running sweep (day3_sweep_validated) finish, but mark its results provisional: they summarise the old
   page.
2. Repeat task 1's measurements on the new page, at the same settings. Report what changed, especially:
   - going still against the square's sugar and against the cells' stores;
   - whether any inactive cell wakes;
   - births per unit of sugar (u).
3. Repeat the validation with Bc59, refitted from the new measurements. If going still now depends on sugar, try
   Matsushita's form a0/(1 + n/n1), fitted, in place of the constant (a proposal). Report page sugar 1 separately.
4. Only if a version passes: the sweep, as before.

Same rules as before: do not change the page or its defaults; nothing pushed or deleted; results to
`results/2026-11-13/`.
