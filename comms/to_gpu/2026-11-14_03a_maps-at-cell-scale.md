# 03a: maps at the scale of single cells (addition to task 03)

From: cloud session, 14 November 2026. Adds to `2026-11-14_03_pop-dish-two-resources.md`.

Justin's comment on `addendum6_maps_sugar10.png`: the 10 × 10 block maps are too coarse to see the dendrite pattern.

## For the page
- Alongside every block map, draw the page's dish at **one pixel per square**:
  - active cells green, cells gone still purple, remains (dead cells) dim grey, empty agar black;
  - a second panel shows sugar per square as a grey ramp.
  - Save these as PNG at their natural size. Upscale only by whole factors (nearest neighbour), so no smoothing blurs
    the branches.
- Add a **close-up** of one quarter of the colony edge at 4× for the same ticks.

## For the models
- A block model cannot show structure smaller than a block, so its maps stay block maps; label them as such.
- **Proposal:** where the page shows branches, run the fitted model with smaller blocks (5 × 5, and 2 × 2 if
  affordable), refitted. Report whether branching appears at all at the finer scale.
  - Matsushita's branching comes from a fine grid with slow nutrient diffusion, so the block size may be what hides it.

## Measure the shape, not just the counts
For the page and for each model, at each tick:
- the colony's **boundary roughness**: perimeter over the perimeter of a circle of the same area;
- a **box-counting dimension** of the occupied squares, at the finest scale each one allows.

Do this at sugar 1, 3 and 10. Low sugar is where Matsushita's dishes branch; report whether the page branches there.

## Deliver
- Into the task 03 report and its figures.
