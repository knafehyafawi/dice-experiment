# Is a 30-sided die fair? A physics-simulation study

This project asks a deceptively simple question: does a d30 land on each of its 30 faces equally often? We answer it not by asserting probabilities, but by simulating the physics of the die and letting the frequencies emerge.

## The main inspiration:

Paraphrasing from Reddit user u/jansenart on r/DnD: A 30-sided dice is not perfectly symmetrical. While they do have 30 equally-sized faces, each vertex has either 5 or 3 connecting faces. This means that if you were to superimpose one face for another, a 6-sided die would fit exactly, but a 30-sided die would only match about half the time. OP then asked, “My question is, does anyone have an actual, trial-based distribution for 30-sided die throws? I'm very interested in seeing exactly how fair one is.” That’s essentially what this experiment attempts to answer.

Link: https://www.reddit.com/r/DnD/comments/64fa53/30_sided_die_actual_distribution/

## The one-paragraph version

A 30-sided die is a *rhombic triacontahedron*. People sometimes claim it can't be fair because it isn't a Platonic solid — its corners come in two kinds. That reasoning uses the wrong criterion. A die is geometrically fair when its faces are all equivalent under the solid's symmetry (a property called face-transitivity), and the rhombic triacontahedron has that property. So an idealized d30 *should* be fair. To check it honestly we build the die in a physics engine, drop it tens of thousands of times, and run a statistical test on where it lands — first with perfect geometry (expected: fair), then with a deliberately
off-center mass that models real manufacturing (expected: biased).

## Background: the myth and the real criterion

The common objection: a d30's vertices are not all alike — five faces meet at twelve of them, three faces meet at the other twenty — so it "can't" be a fair die the way a d6 is.

This conflates two different symmetries. Fairness needs the faces to be interchangeable under the solid's symmetry group (face-transitivity / isohedrality); it does **not** require the vertices to be interchangeable. The standard d30 is a rhombic triacontahedron, which is a Catalan solid, and Catalan solids are face-transitive. So the idealized d30 is fair. The two vertex types are a red herring — and one goal of this project is to demonstrate that mechanically, not just assert it.

## Why simulate the physics instead of just calling a random-number generator?

If you "simulate" a die with `random.choice(1..30)`, the result is uniform because the assumption is baked into the code. The flat histogram is the assumption echoing back at us. It tells you nothing about a real die.

A physics simulation does not remove assumptions; it relocates them. Instead of assuming the answer (the face probabilities), we specify the inputs:
- The geometry
- Mass distribution
- Friction and bounciness of the surface
- The way the die is thrown
- Etc.

And the probabilities come out as a result. That is a far more defensible place to put our assumptions, and it lets bias arise on its own rather than being stipulated.

## Hypothesis

> **H₀ (null):** the *modeled* die is fair — P(each face) = 1/30.

Note the word *modeled*. The simulation never touches a manufactured die; it tests the die we specify. The conclusion therefore generalizes to real dice only as far as the modeled inputs (center of mass, friction, restitution, throw distribution) are realistic. Stated this way, the claim is airtight; stated as "the physical die," it would overreach.

## The two experiments

The contrast between these is the whole story:

| Experiment | Model | Expectation |
|---|---|---|
| **A — ideal die** | perfect rhombic triacontahedron, uniform density | **fail to reject** H₀ → confirms the face-transitivity argument |
| **B — real-ish die** | center of mass offset (engraved numbers remove material unevenly) | **reject** H₀ → shows where real bias actually comes from |

Experiment A is the empirical demonstration that the vertex-type objection is irrelevant. Experiment B is the demonstration that when real dice *are* biased, it's the mass distribution — not the vertices — doing it.

## Method

The pipeline is: **roll → aggregate → test → measure → visualize → conclude.**

**Tooling**
- `trimesh` — load the die mesh; compute volume, center of mass, and inertia tensor.
- **MuJoCo** — rigid-body physics. Chosen because it lets you specify mass, center
  of mass, and inertia tensor *explicitly*, so the bias knob in Experiment B is a
  clean, legible change rather than an incantation.
- `scipy` / `numpy` / `matplotlib` — statistics and plotting.

**Core data structures** (four pieces describe a die):
1. a **vertex array** (3D points),
2. a **triangle → face-id table** (the engine wants triangles; we keep a mapping
   back to the 30 logical faces),
3. a **30 × 3 array of face normals** (precomputed), and
4. an **orientation quaternion** (the evolving physics state).

**One roll**
1. Sample a **uniform random orientation** (`scipy.spatial.transform.Rotation.random()`
   — naive Euler angles are biased toward the poles and would taint the result),
   add a random spin, drop from a small height.
2. Step the simulation until the die is **at rest** (linear and angular velocity
   below threshold for several consecutive steps).
3. Rotate the 30 face normals by the final orientation, dot each with "up"
   `(0,0,1)`, and take the `argmax` — that's the top face. Map face-id → value 1–30.
4. Append to the tally.

Repeat for N rolls; feed the tally into the test below.

## Statistics

A **chi-square goodness-of-fit test** against the uniform distribution.

- For each face *i*: expected count `Eᵢ = N / 30`; statistic `χ² = Σ (Oᵢ − Eᵢ)² / Eᵢ`; degrees of freedom = 29.
- The **p-value** is the probability of seeing deviations this large *if the die were truly fair*. A small p (< 0.05) means reject H₀.
- The test wants `Eᵢ ≥ 5`, so use **N ≥ 150** at minimum — really thousands.

**The large-N caveat (important).** A physics sim can produce millions of rolls, and chi-square's power grows with N: with enough rolls the test will reject *any* bias, however microscopic. At that scale "we reject H₀" is nearly content-free. So beyond a certain N, the headline is no longer the p-value but the **effect size** — how far each face's probability actually departs from 1/30, and how large the biggest
deviation is. The real question is not "is the bias *detectable*" (at N = 10⁷, everything is) but "is the bias *big enough to matter at the table*." Reporting both is the difference between statistical and practical significance.

## Reading the results / what counts as a conclusion

- **Experiment A** that fails to reject, with tiny effect sizes → evidence that the ideal d30 is fair, confirming the geometry argument.
- **Experiment B** that rejects, with an effect size you can quote ("face X comes up ~Y% more than fair") → a concrete account of manufacturing bias.
- A flat histogram with the expected-frequency line drawn across it makes both visible at a glance.

## Limitations (stated up front, because they're the point)

- The study tests a **modeled** die, not any physical object. Its realism is exactly the realism of its inputs.
- Results depend on chosen friction, restitution, timestep, and throw distribution; these should be documented, and ideally varied to check robustness.
- "Assumption-free" is a myth — the value here is that the assumptions are inputs you can see and change, not a hidden answer.

## Project structure (planned)

```
.
├── geometry.py      # load / build the rhombic triacontahedron, recover 30 facets + normals
├── die.mjcf         # MuJoCo scene: ground plane, gravity, the die as one convex body
├── simulate.py      # the roll loop: random orientation → settle → read top face
├── analyze.py       # chi-square + effect size on the aggregated tallies
├── plot.py          # histogram with expected-frequency line
├── requirements.txt
└── README.md
```

## References / further reading

- Rhombic triacontahedron; Catalan solids (face-transitive polyhedra).
- "Isohedral" / fair dice — the geometric criterion for fairness.
- Shoemake, *Uniform Random Rotations* (correct random-orientation sampling).
- Pearson's chi-square goodness-of-fit test; statistical vs. practical significance.
