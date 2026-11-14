# Handoff: the user's model of automata and systems (11 November 2026)

This hands over the user's general idea of self-reproducing systems to another session, as it stands after the
"automata miniature" work of 9 to 11 November 2026. It is self-contained.

The full working note, with every dated decision and Claude's longer proposals, is
`D:\labyrinth\research\notes\AUTOMATA_MINIATURE.md` on the user's computer. Section numbers below (§) refer to it.

## 1. Context

**The project.** The user designs Orbis Tertius Theatrum, a realistic historical simulation that writes chronicles.
Claude builds it.

**Its long-term goal:** a general model of self-reproducing automata that replaces the sim's separate procedural
systems.

**Sources of the goal:**

- von Neumann, above all;
- to a lesser extent Spinoza: the power to reproduce against the power to act.

**Two tests for every rework:**

1. Can categories become general formulas?
2. Can procedures become emergent systems?

**The miniature.** A small, separate model, built to explore the idea before it is integrated into the sim. The
findings are meant to turn upward, into the sim's persons, households, codes and polities, later.

## 2. The model: what the user has decided

### Systems and their relations

- **Three relations.** Every system has:
  - supersystems, which contain it;
  - cosystems, the other members of the same supersystem;
  - subsystems, its own members.
- **The relations are positions, not kinds.** A system is the supersystem of its subsystems and a subsystem of its
  supersystems (§12).
- **The individual is only an intersection, and this holds for every system, not only the subject.** This is the
  user's point "against Guattari": Guattari says it of the subject alone.
- **At least two of each is a rule** (§13). Every system that has been worked out has at least two subsystems and at
  least two supersystems.
  - Fold enforces the lower bound: a one-member system cannot be told apart from its member.
  - The intersection principle enforces the upper bound.
  - At the current floor and ceiling, the second of each is still potential.

### What a system is

- **The definition.** A system is a set that reproduces its subsets.
- **Recursion, not self-membership.** Subsets are defined by recursion. Self-containing sets are not needed:
  production may cycle, but membership stays well-founded.
- **Membership is a directed acyclic graph,** not a tree: no overall hierarchy (§9).
- **The floor and the ceiling.**
  - The floor is nutrients or resources in the broad sense: whatever a system takes in and does not make.
  - The ceiling is procedural: the largest self-maintaining closure the world supports. It can be computed, as in
    Kauffman's and Hordijk and Steel's autocatalytic sets (RAF theory).
- **Closure to efficient causation** (Rosen). The user agrees with it. It grounds their disagreement with biological
  and evolutionary determinists: if the makers are made inside the system, its causes are not handed down from one
  level, such as the genes.

### An indefinite model (§10, §11)

The model is indefinite in Kant's sense (*in indefinitum*), not infinite. It is finite at any moment, between a floor
and a ceiling that move at tension points by three operations:

- **Open (downward).** When a system's own activity changes the supply of one of its inputs, that input is no longer
  food. It is opened into the system that makes it.
- **Lift (upward).** When the top-level systems maintain one another, a new closure forms over them, and the ceiling
  rises.
- **Fold.** A level whose detail no longer changes anything above it collapses into a single process. The user chose
  the term "fold". Fold summarises; it does not forget: reopening resumes the folded state.

### Action and motive (§12)

- **Every action reproduces some system.**
- **Need, desire and obligation** sort actions by which system they reproduce:
  - **need:** its subsystems;
  - **desire:** its cosystems, read as surplus beyond its own maintenance;
  - **obligation:** its supersystems, read as what the supersystem's closure needs.
- **Deferred:** the full subject mapping and Luhmann (communications as processes, probably).
- **Spinoza** was inspiration only.

### Codes (§8, §9)

- **The code is a-signifying.** The user's choice of term: a description copied and interpreted by building, not
  read for meaning.
- **Transduction** is the name of the constructor's act: building what a description specifies.
- **Codes are required for reproduction** in the sense the model is after. The first miniature already had them.
- **Descriptions are ordered sequences** (form of expression). **Closure compositions are products of primes** (form
  of content).
- **Overcoding is probably kept for the human stratum.** In the lower levels, a supersystem's regulation of its
  members' codes is only the "second articulation".

### Viruses (§16a)

- **The definition.** A virus is a code with a closure of reproduction (a lineage) but no closure of production of its
  own. It is copied inside other systems' closures, by their makers, at their cost.
- **Origin.** Viruses arise from fragments of host codes, by escape.
- **Entry.** A virus enters a host only through a receptor that the host makes.
- **Burst or integration.** Both exist, and the choice is carried by the virus and free to evolve.
- **The user's view:** a general virus model had to come before any real chemistry.

### Direction

- **No organic chemistry** (§22, §23).
  - Real chemistry and biology already supply the rules at that level, and real data would not make the miniature
    model real organisms accurately.
  - Real data's only use here would be as a test of generality.
- **Instead, digital life.** Something like digital life, unbounded by real biology, in the vein of Conway's Game of
  Life (§23 to §26).
- **Later:** turn upward, into the sim.

## 3. Proposals made but not settled

1. **Ecology and lineage as the two minimal supersystems** (§13).
   - **The closure of production (the ecology):** what makes and maintains a system's parts now. This is the side of
     content: D&G's epistrata.
   - **The closure of reproduction (the lineage):** what its code is copied from and into. This is the side of
     expression: the parastrata.
   - The user asked for this to be elaborated, and it was used in the miniature, but they never confirmed it.
2. **Joining, by dominance or equality** (§19). The user asked the question; this answer is a proposal.
   - **Dominance** is engulfment and endosymbiosis: the guest keeps its code and is copied by the host.
   - **Equality** is fusion and sex: the codes are mixed, and the lineage gets two parents.
   - **One operation.** Both, with the virus, would be one operation, entry, by size. Which happens would emerge from
     who copies whom.
3. **The semiotic carry-over** (§8). It adapts the sim's Hjelmslev net (EF, ES, CF, CS) to an a-signifying code:
   - **Strata.** The physico-chemical stratum (closures without codes), the organic stratum (linear codes, by
     transduction), and the alloplastic stratum (regimes of signs; the sim as it is).
   - **What carries over:** all four cells, real distinction and reciprocal presupposition, and the
     molecular/molar distinction.
   - **What does not:** regimes of signs, interpretation, and overcoding.
   - **Guattari's a-signifying rupture.** It reads as catalysis: something repeated and copied that maintains a
     closure without being read.
4. **A resource managed by a ceiling system** (§25). The user wants this "eventually".
   - Cells pay a share of what they gather to a supersystem that holds the commons, and it redistributes by its own
     code.
   - It persists only while what it returns keeps enough cells alive to keep paying.
   - This is obligation made concrete, and a first step toward the sim's politics.
5. **Making clumps (bodies) into organisms** (§26):
   - the body's code regulates its cells' rules;
   - engulfed guests work for the host.

## 4. What has been built (on the user's computer, `D:\labyrinth\automata\`)

### The miniature: `miniature.py` and `build_viz.py`

Pure Python, five versions. The page each version produces shows charts over time, a site map, a chronicle, and any
cell's two supersystem chains.

1. **Version 1.**
   - A binary-polymer chemistry: Hordijk and Steel's model.
   - Cells whose code is transduced into reactions, and who live while their reactions close (a RAF set).
   - Lift by synergy: a joint closure that exceeds the union of the members' closures. The same test is used at
     every level.
   - Fold by stable organisation, while the cells are replaced.
   - Open and fold of food stocks.
2. **Version 2: the loop closed.** A code is expressed only where its closure makes a "constructor" molecule. It is
   copied faithfully only where a "copier" molecule is made; otherwise copying is error-ridden.
   - Autonomy (making both makers) evolved to about 50% of cells.
3. **Version 3:** overlapping consortia (maximal cliques at the first lift), and a variable ecology (light that
   drifts and has seasons, disturbances, foods that appear and vanish).
4. **Version 4: irreducible closures.** Hordijk and Steel's reduction: minimal closures, which overlap wherever they
   share a member.
   - What had looked like one world-spanning ecology turned out to be five or six overlapping minimal closures.
5. **Version 5: viruses,** made from fragments of dying cells' codes.
   - Without limits, they drove most worlds extinct. With tuning (which the sources do not support), they became
     endemic, and life persisted in 5 of 6 worlds.
   - Integration and "domestication" of viruses happened.

### The toy: "codes as rules" (`toy/digital_life.html`)

A browser page.

- **The rule.** Each cell's 32-bit code is its own Life-like rule: when it survives, when it gives birth, how hard it
  writes itself into its neighbours.
- **The floor: light.** Light spreads, living uses it, and each birth costs its parent light.
- **Lift:** recurring shapes are recognised and named as forms.
- **Zoom:** from named forms out to each cell's rule in.
- **Bodies, a second layer.** A body has its own code. Bodies form, divide, bud, engulf (dominance) and fuse
  (equality).

### The user's own extension: "Justin's Game of Life" (`jgol/`)

The user and a web session extended the toy a long way: heat, water, gases, sugar, clumps, spores and fluid currents.
On 11 November a code session added a two-layer water model (floor and surface, with upwelling from buoyancy, and
spores riding the plume). Its README records the results.

## 5. Biology: a standing caveat (§18a)

- **The user is not a biologist** and asks not to be treated as an authority on biology. Their agreement on a
  biological point is a decision about the model, not a confirmation of the biology.
- **Biological claims should be checked against sources** before they carry weight.
- **Checked by web search (§20):**
  - Iranzo and colleagues (2016) argue that genetic parasites are virtually inevitable in cellular life, and Koonin,
    Wolf and Katsnelson (2017) that parasite-free states are unstable. The user found this interesting.
  - Koonin, Senkevich and Dolja (2006) propose an "ancient virus world" before cells.
  - In models of early replicators, spatial structure and compartments resist parasites.
  - Later defences grew largely out of viruses themselves: Villarreal (2011), and Koonin (2017).
- **Not checked:** Spiegelman's shortening replicators, Eigen's error threshold, Margulis on endosymbiosis, and
  Maynard Smith and Szathmáry's major transitions.

## 6. Sources the model draws on

- **Deleuze and Guattari.**
  - *A Thousand Plateaus*, plateau 3: strata, double articulation, DNA as a nonsignifying code, epistrata and
    parastrata, the margin of decoding.
  - Plateau 5: regimes of signs.
  - Plateau 10: becoming by alliance and contagion against filiation.
  - *The Fold*.
- **Guattari, *The Three Ecologies*:** the individual as a terminal, and the a-signifying rupture.
- **Monod, *Chance and Necessity*:** invariance and teleonomy.
- **von Neumann, *Theory of Self-Reproducing Automata*:** constructor, copier, controller, description.
- **Autopoiesis.** Maturana and Varela: organisation against structure.
- **Rosen's (M,R) systems,** with Mossio, Longo and Stewart's computable version.
- **Kauffman; Hordijk and Steel:** RAF sets, maxRAF, irreducible RAFs.
- **Luhmann:** deferred.
- **Precedents for an indefinite model:**
  - Aristotle's potential infinite;
  - Kant's *in indefinitum*;
  - corecursion and lazy evaluation;
  - effective field theory and renormalisation;
  - adaptive mesh refinement;
  - Koestler's holons;
  - Simon's near-decomposability.

## 7. Standing preferences for working with the user

- **Terminology.** Use terms consistent with Deleuze and Guattari. Decided terms in the sim's glossary include:
  - the net (Hjelmslev's four cells);
  - isotopy;
  - code;
  - regime of signs;
  - specialist and generalist expertise.
- **Readouts, not causes.** Aggregates are measures. In the sim, persons decide.
- **Emergence, not scripts.** Chains and structures should arise from interacting systems.
- **Bidirectional causality.** Most causality runs both ways; distrust one-way claims.
- **The user's role.** The user designs; Claude builds and proposes, and records the user's decisions as decisions and
  its own ideas as proposals.
- **Quotations.** Quote sources only briefly.
- **The user writes anything meant for other people themself.**

## 8. Open questions

1. **Ecology and lineage:** are they the two minimal supersystems (§3.1)?
2. **Joining:** should it be the general operation of entry, with dominance and equality emerging from who copies
   whom (§3.2)?
3. **The ceiling-managed resource:** what is its code, and how is it chosen (§3.4)?
4. **Bodies:** should the body's code regulate its cells? If so, what should that be called, given that "overcoding"
   was kept for the human stratum?
5. **Turning upward:** how do open, lift and fold, codes, and need, desire and obligation map onto the sim's persons,
   households, faiths and polities? This is the eventual purpose of the work.
