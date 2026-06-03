# Fairness of a 30-Sided Dice
Adnan Awad

---

## Preamble

Paraphrasing from Reddit user u/jansenart on r/DnD: A 30-sided dice is not perfectly symmetrical. While they do have 30 equally-sized faces, each vertex has either 5 or 3 connecting faces. This means that if you were to superimpose one face for another, a 6-sided die would fit exactly, but a 30-sided die would only match about half the time. OP then asked, “My question is, does anyone have an actual, trial-based distribution for 30-sided die throws? I'm very interested in seeing exactly how fair one is.” That’s what this experiment attempts to answer.

## Method

It would be very easy to build a program to test a hypothetical thirty sided dice. This is faulty. It bakes in the presumption of the null hypothesis (expanded upon later) into the method of testing, which recursively returns the desired output of fairness. It asserts uniformity when the actual dice is not uniform. The idealistic theoretical assumptions abstracted from the geometry of such a dice are baked into the simulation by definition.

## Hypothesis

NULL HYPOTHESIS: 30 SIDED DICE IS FAIR, AND P(EACH FACE) = 1/30
