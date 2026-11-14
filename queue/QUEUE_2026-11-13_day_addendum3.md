# Day queue, third addendum (13 November, about 15:30, from the cloud session)

Your probe was exactly right, and decisive. The page is fixed as you proposed, and a little further.

## What changed in the page (use the new justins_game_of_life.html)
- **Ambient light and stored energy are separate.**
  - amb holds each place's ambient light. It relaxes towards the sun's level (ltc) and spreads, so crowds still
    shade one another.
  - A cell absorbs from amb at its place (absorb 1: whatever lies above its own store), using it up.
  - A cell's store (light) never leaks into the dark and no longer spreads between places.
- **A newborn** gets half of what its parent has left after paying for the birth, and nothing from its place.
- **A moving cell** takes its store with it.
- **The dish** starts dark (amb = dishLight = 0).
- **Ground chemistry:** chains now also join, break into two, act as ligases, and copy themselves on a template
  (fragJoin, fragCopy, fragErr). This should not matter for the dish validation, but note it.

The early sugar rise you saw in ticks 1-20 is probably dead inoculum cells releasing their bodies' sugar (ebody). The
inoculum's bodies were never paid for; they are laid in at the start. Worth confirming.

## Please, in order
1. **Stop the old-page sweep** (day3_sweep_validated) if it is still running, and mark it superseded.
2. **Task 1 again on this page,** at the same settings.
3. **The validation again,** with the variants refitted: Bc, Bm (Matsushita's form), Be or S (stores). The store
   variant S should now be closest to the page, since the page's stores are now paid for. Report page sugar 1
   separately.
4. **Only if a version passes:** the sweep at the page's sugar range.

Same rules: do not change the page or its defaults; nothing pushed or deleted; results to results/2026-11-13/.
