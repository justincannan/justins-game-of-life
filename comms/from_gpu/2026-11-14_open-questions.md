# Open questions from the GPU side, 14 November, about 21:50

From: gpu session (interactive). It gathers the questions still open in the GPU reports into one place, for the cloud
session to put to Justin or to answer within decisions already made. Nothing here is new; each item points to its
report. All are proposals unless marked otherwise.

Commits read before writing: up to 821a258 (random visiting order; task 17).

## Closed since the reports
- **The scan order (report 08, section 5).** Settled by Justin's decision at about 21:23: the page now visits places
  in random order (821a258). Task 17 re-baselines the dish; the GPU scheduled check at 23:00 starts it.

## For Justin
1. **Odd complement pairs (report 15, section 1.4).** In the new contact table, complement pairs (m ^ 8) are the best or
   second-best partners for even monomers. For odd monomers they are not: large oily monomers attract each other
   most. The proposal is that large-with-small packing shows only in packed cores, so step 3 tests it again. If step 3
   also shows no preference, the page's rule "m pairs with m ^ 8" would hold for the even monomers only. Whether that
   matters is Justin's call. It changes nothing yet; it is for information until step 3's report.
2. **Report 06, proposal 2.** A store fold in which income per cell is tied to the place, not inherited, with a cost
   that rises with the income earned. This is an alternative to proposal 1. Proposal 1 (income measured per lineage in
   harness copies) is already task 13, which the next check starts alongside task 15's step 3. Should proposal 2 also
   be tried, or wait for task 13's numbers?
3. **Report 07, section 4: the next step for branching in the population models.** It would use sugar per place
   rather than per coarse square, gliding limited by coat, and chemistry income per lineage (task 06's form). Task 16
   has since shown that spreading the molecules makes no difference. Should this be run, or set aside?

## For the cloud session (optional)
4. **Lehninger chapter 2 (report 15, section 3).** Do the chapter's numbers for an H-bond and a salt bridge in water fit
   the effective contacts in report 15, section 1.2: −1.3 to −1.9 kT, and +1.1 kT for a buried salt bridge? Only the
   numbers are needed, not the text.

## Waiting, nothing to decide
- Task 10 (finer blocks) waits on a store fold that passes; none has (reports 06 and 16).
