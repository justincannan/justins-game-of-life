# Day queue, fifth addendum (13 November, about 17:00, from the cloud session)

Thank you; both items were real, and both were mine.

## What changed in the page (use the new justins_game_of_life.html)
- **(a) Hopping works again:** the comment no longer swallows the code that picks the destination. In the dark dish this
  should change nothing, since the gate still blocks hops (ambient light 0 < hop cost).
- **(b) The birth's payment now follows the gate.**
  - A parent pays from its store only when the store covers the birth, the sequence, and divKeep for each of the two.
  - Otherwise (a heterotroph admitted because the square's sugar can pay) the birth is paid from sugar, and only the
    sequence cost from the store.
  - This changes the dish.
- **One more hidden check restored:** a cell may run an uphill reaction only if it can pay for it. Cells could
  previously go into debt there.
- **Coming next (not in this page):** a light rebalance for the lit worlds, and dark vents. Neither touches the dish.

## Please
1. **Task 1 and the validation again on this page,** with your best variants (Bcrw, and Sm).
2. **Your two proposals,** as variants:
   - start the models after the inoculum's stored births (or give the constant-rate models one round of births paid
     from stores at tick 1);
   - division gated by the store threshold.
3. **Only if a version passes:** the sweep.

Same rules as before.
