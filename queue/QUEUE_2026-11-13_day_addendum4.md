# Day queue, fourth addendum (13 November, about 16:30, from the cloud session)

Your probes found both leaks, and the page's own hopping mutants found the first one. Both are fixed as you proposed.

## What changed in the page (use the new justins_game_of_life.html)
- **Hopping:** a hopping cell takes its store with it (light[best] = light[i] - hc; light[i] = 0), and its gate and
  preference read amb.
- **Absorption** takes only positive ambient light, never more than is there:
  ab = absorb × max(0, min(amb, amb − max(0, light))).
- **A birth needs the whole cost,** sequence included, plus divKeep for each of the two cells.
- **The dish's empty places** start with light 0.
- **The reset line** swallowed by a comment is fixed (husk is cleared).
- **Two new defaults from a health check:**
  - seqCost 0.0004 (was 0.004);
  - divKeep 0.1: a parent divides only when its store covers the birth and leaves 0.1 for each of the two.

## Please, in order
1. **Task 1 again,** hopping on and off, at the same settings. Report the sugar budget (u), going still against store
   and sugar, and waking.
2. **The validation again.** Charge S the measured birth cost (your proposal), and add waking on returned sugar if the
   page now shows it. Report page sugar 1 separately.
3. **Only if a version passes:** the sweep at the page's sugar range.

Same rules: do not change the page or its defaults; nothing pushed or deleted; results to results/2026-11-13/.
