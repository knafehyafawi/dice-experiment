# Fairness of a 30-Sided Dice
Adnan Awad

---

## Preamble

Paraphrasing from Reddit user u/jansenart on r/DnD: A 30-sided dice is not perfectly symmetrical. While they do have 30 equally-sized faces, each vertex has either 5 or 3 connecting faces. This means that if you were to superimpose one face for another, a 6-sided die would fit exactly, but a 30-sided die would only match about half the time. OP then asked, “My question is, does anyone have an actual, trial-based distribution for 30-sided die throws? I'm very interested in seeing exactly how fair one is.” That’s what this experiment attempts to answer.

## Method

It would be very easy to build a program to test a hypothetical thirty sided dice. This is faulty. It bakes in the presumption of the null hypothesis (expanded upon later) into the method of testing, which recursively returns the desired output of fairness. It asserts uniformity when the actual dice is not uniform. The idealistic theoretical assumptions abstracted from the geometry of such a dice are baked into the simulation by definition.
Thus we’ll be 3D modeling in some way. See below.

### The Toolchain

- Geometry — build the rhombic triacontahedron mesh. Use trimesh. You hand it the 32 vertices, it computes the convex hull (a watertight mesh) and — crucially — the volume, center of mass, and inertia tensor assuming uniform density.
- Physics — drop it and let it settle. Use PyBullet (pip install pybullet; C++ under the hood, Python bindings, fast enough for millions of rolls). MuJoCo (pip install mujoco) is the alternative — better physics, steeper learning curve. For a portfolio project PyBullet is the pragmatic pick.
- Stats/viz — your chi-square machinery from before, now consuming emergent frequencies instead of stipulated ones.

#### The Data-Structure Model

A die in a physics sim is four pieces of data:
1. Vertex list — an array of 3D points. The RT has 32.
2. Face/triangle list — indices into the vertex list. Physics engines want triangles, so each of the 30 rhombic faces gets split into 2 triangles → 60 triangles. But here's the key move: you keep a separate table mapping each triangle back to its die-face id (1–30). The engine sees triangle soup; you see 30 labeled faces. That mapping table is the heart of "reading the result."
3. Face normals — one outward-pointing unit vector per die-face (1–30), precomputed. At rest, you rotate all 30 normals by the die's final orientation and find the one most aligned with up (+z) — that's the top face, your roll result. It's an argmax over 30 dot products.
4. Orientation — a quaternion (the physics state). Don't use Euler angles; they'll bite you.

So conceptually: collision uses the triangle mesh; reading the result uses the 30 normals plus the orientation quaternion.

## Hypothesis

NULL HYPOTHESIS: 30 SIDED DICE IS FAIR, AND P(EACH FACE) = 1/30
