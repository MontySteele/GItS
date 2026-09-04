Status: OPEN (no pick; the defaults in §4 are applied)

# Klee round twelve: ordering as the puzzle, and the rules a seat had to run experiments to learn

Written 2026-09-04. Two blind Opus seats played the Bomb kit on
`0.2.2501+proto`, the build with round 11's fixes live: the Mine badge names
a Mine (`EB-417`), the Little Hexenzirkul Spark rider prints on the
Companion's face (`EB-418`), the harness's seed read-back fixed (`EB-435`).
Countdown is in the pool and, for a fourth and fifth run, was not drawn.
Records: `review/qa/klee-round-12-2026-09-04/opus-act1.md` (run 1) and
`opus-run2-act1.md` (run 2). Prototype stage, Guardrail-7. No pick.

## 1. The runs in one paragraph

Run 1 (seed `JNPWLQR7U532`, Ascension 0, 120 of 120 actions): five fights
won including the floor-6 elite, floor 10 at 39 of 62, one refusal (an
unplayable quest card). Run 2 (seed `Y2NRXL11P8LT`, Ascension 1, 120 of
120): four fights won, the Phantasmal Gardener elite left mid-fight at 9
of 62 with one Gardener on 8, nine Sparks unspent with two 1-Spark sinks
in the deck. Neither reached the boss.

## 2. What the round found

**Card ordering is a real puzzle every turn, because Set off is not
optional.** Mine Toss before a detonator is caught in the blast; after, it
stays armed; run 1 made that call six times and both ways. The peak was an
elite turn where one 0-cost Ka-pow! resolved a chain, a kill, a summon, a
"kills move it on" transfer onto an enemy that had not existed a moment
earlier, and a Mine-on-ALL rider, "five printed rules in the right order,
all checkable on the next screen." Vaporize paid exactly 1.5x and the
glossary predicted it. Both seats called the rules coherent.

**The Mine tip reads as mitigation and is not.** "A Mine goes off when its
enemy attacks you, before the hit lands" led run 1 to end an elite turn
with three Mines armed, expecting the hits blunted; five Mines went off,
every host survived, every hit landed, 36 to 18 HP on a turn planned as
free (`EB-436`). The line is true and says nothing about the hit.

**Two rules were learned by experiment.** Run 2 detonated two 11-point
Bombs into Skittish and found Skittish does not tax a Bomb (it is not an
Attack) and then inferred a Bomb ignores Block; the tip's negative, "only
their Vulnerable and a cap move it", leaves Block and when-hit triggers to
inference, and the brief's rule is that Block absorbs the hit (`EB-443`).
The same seat found Fischl was Hexerei by counting Bombs on a badge, and
met a third set, "Klee's own Companions", on Noelle; no Companion face says
its set, and Witches' Circle was dead for four fights (`EB-392`, widened).

**The bottom of the pool and the surplus.** Strike and Defend were a third
of both decks and interact with nothing; run 1's first turn of fight one
was Strike, three Defends and Ka-pow! against a debuff intent, and
presented no decision. Big Badda Boom was a flat 2-cost 12 twice with no
placer in hand and 34 two turns later. Sparks: nine unspent at the stop
with two 1-Spark sinks in the deck. Countdown, the pool pass's first row,
has now gone undrawn in five runs from a 34-row pool; the Spark sink the
audit withdrew (Explosive Spark, C3) is the shape the surplus keeps asking
for, and the next pool-pass row keys a sink to a Bomb decision rather than
to the bank (a number the sim decides, D). Not a pick.

**The rider printed, and paid.** Run 1 read Diona's Spark rider on the face
and budgeted a Spark-priced detonator off it; the round-11 finding closed
on the first read.

## 3. What the round did not test

Countdown; the boss; act 2. Two runs, both budget-out. Nothing here is a
strength reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-436`, `EB-443` minted; `EB-392` widened** (a duplicate, `EB-444`,
  was minted and retired the same hour). All three are on an Opus fix
  branch beneath this packet.
- **The pool pass's second row** (a Spark sink keyed to a Bomb decision) is
  written next and read by GPT before any tester, the same door as
  Countdown.
