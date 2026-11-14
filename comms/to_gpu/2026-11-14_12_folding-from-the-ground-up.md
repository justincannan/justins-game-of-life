# 12: folding and interactions from the ground up (replaces further work on task 02's prototype)

From: cloud session, 14 November 2026, about 17:20. Justin's decisions are at the end of THEORY_NOTES.md ("Folding rebuilt
from the ground up; ions; division of labour").

Justin's decisions:
- Task 02's problems need a rebuild, not patches.
- Model secondary and tertiary structure separately, and allow for quaternary later.
- Ions will probably be needed as well as molecules, and will be needed for ion pumps later.
- The GPU side builds from the ground up where needed.

## Step 1: a design report (no long runs yet)
Write `comms/from_gpu/2026-11-14_12_design_report.md`, proposing:

1. **The interactions.** What a monomer carries:
   - polarity;
   - charge, and whether charge depends on the surroundings (pH-like);
   - size, if useful.
   How attraction is computed from these:
   - charge–charge, screened by water and by ions;
   - hydrogen-bond-like polar contacts;
   - the hydrophobic effect as burial from water;
   - a 16 × 16 contact table derived from these properties, not set by hand.
   Keep broad accuracy, not real chemistry. Check claims against sources and cite them briefly.
2. **Ions.** As a species: a few kinds, charged, not folding, screening interactions, and crossing membranes only by
   channels or pumps later. What the page would have to track: per square, and per cell inside a membrane.
3. **Secondary structure.** A local rule from neighbouring monomers, giving helix-like, strand-like and turn
   segments. Say whether the page's nested brackets survive as part of it, or are replaced.
4. **Tertiary structure.** Packing of the secondary elements in 3D, with:
   - the contact table;
   - a cooperative (many-body) term, so melting can be abrupt (Kaya and Chan);
   - stability scored against heat.
   Say how a domain's job (its reaction, and the pocket that sets its specificity) comes from the folded shape.
5. **Quaternary, later.** Say what the design must leave room for: chains associating, and binding that changes fit.
6. **Selection.** Foldability must be evolvable, not given; most random sequences should fold poorly. Say how fold
   quality enters fitness: a domain works only if its fold is stable enough at the cell's temperature.
7. **Cost.** Fold offline and cache by sequence, or something cheaper. Estimate per distinct sequence, and how many
   distinct sequences a page run makes.

## Step 2: wait
Mark the task "waiting on Justin" in STATUS.md after the design report. Justin approves the design before any
prototype is built.
