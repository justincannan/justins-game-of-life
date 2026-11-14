# Addendum to the day queue, 13 November, about 11:45 (from the cloud session)

Thank you for the status note. Change of plan for task 2, in this order.

## 1. Stop sweep C
It uses the same fitted constants as A and B, which stall where the page itself grows. More settings of that model
will not tell us much. Keep what B has finished.

## 2. Validate before sweeping (new priority 1)
A fitted population model is only worth sweeping if it reproduces the page at matched settings.
- **Settings:** the page's own dish at page sugar 1, 3 and 10, gliding 0.1, Game of Life rule off, 3 seeds each.
  Use the default inoculum and plate size, or the smallest plate that gives the same colony.
- **The model's runs:** the fitted population model at the same sugar, converted with your own scale (state which
  conversion you use), on a plate of the same physical size: one square per 10 × 10 block of page places.
- **Compare over time:** cell count (active, inactive), colony radius, and coverage.
- **Report:** whether the fitted model grows where the page grows. We already know the page grows at sugar 3 to 5,
  so if the model stalls there, it does not summarise the page.

## 3. If it fails, add the missing state (proposal, Claude's)
Your measurements suggest why: in the page, going still follows a cell's stored energy, not the square's sugar.
- Give each square a mean stored energy:
  - it rises with sugar taken in;
  - it falls with upkeep and with the cost of each division.
- Make going still depend on that energy, with the form fitted from your task 1 data (e.g. rate rising as energy
  falls below a threshold).
- Re-run the validation. The test is simple: does the summary now reproduce the detail?

This matters for Justin's model: a fold is allowed only where "a level whose detail no longer changes anything
above it". If the summary fails without energy, the energy is detail that still changes things above, and a fold
must keep it.

## 4. Spreading by birth (proposal, from your note)
Your finding that the page's cells spread mainly by birth into the next block, not by gliding, is consistent with
non-motile bacteria on hard agar. In the population model, try spreading as a share of births placed in a
neighbouring square (your 15%), instead of a movement term. Validate it the same way.

## 5. Only then, the sweep
With whichever version passes validation, at the page's own sugar range (your C range).

## Unchanged
Do not change the page or its defaults; no pushing or deleting. Write the results as before.
