Status: RECORD

# Klee, [USER]'s second act-1 run (2026-09-08): the rule change read as intended, the Spark-centric defence was fun and inconsistent, the tips are too long

Written 2026-09-08 from [USER]'s own notes, on `0.2.3069+proto` (main
`e7600df2` after #461), the build carrying R265 pick 1 (every Hexerei card
gives a Spark, `EB-642`) and round 24's uniform mark (`EB-663`). This is the
play the rule change was owed under the stage norm ([USER] plays when a rule
changes); it discharges `EB-642`, which leaves HEAD with this record. No
pick. Two defaults applied (§4). The run went through act 1 and died in mid
act 2 to the Entomancer, on a run [USER] describes
as not played with perfect precision, and "I don't think my early death is
unreasonable, either."

## 1. What [USER] said, verbatim where it matters

1. "Overall - good concept, and like Ironclad, we've preserved the central
   challenge of 'attack spam go!' vs 'How do I block?'"
2. "I tried to use Hexerei cards to pay for a Spark-centric defense (build
   up big bombs and eat them as needed) that did not quite have the
   consistency I needed, but the loop was fun, and I'm not sure this was
   design error as opposed to user error."
3. "We have a lot of unnecessary tooltip text that could be trimmed down,
   e.g. the Bomb tip does NOT need to explicitly say 'your deck opens with
   a placer.'"

## 2. What each note is, read against the record

**Note 1 is the brief's tension, confirmed by the owner.** The Klee brief
(draft 2, R213 course-correction) set the kit's question as
cash-or-cook against the every-turn Block problem; the round-10 to
round-24 seats named it the same way, and [USER]'s first run
(`review/ruled/klee-user-run-1-2026-09-07.md`) named "the early fragility
and the every-turn Block puzzle" as the brief's tension. Nothing to build.

**Note 2 is the Spark-economy question, read from its third edge.** Round
23 read the Spark loop from two edges: never scarce on the natural lane,
deadlocked on a deck of Spark cards. Round 24 answered readability and
not economy, and the R267 fact-check kept the question open on purpose.
[USER]'s run is the third edge: a deliberate Hexerei-paid, Spark-priced
defence (Dodoco Cover, Careful Now, Barbara's Front Row Seat are the
pool's three conditional Block rows, and the Hexerei coven is the pool's
Spark income) that was fun and not consistent enough to carry act 2. That
is the reading the brief predicts for a defence bought with a resource the
deck has to earn, and whether the inconsistency is the deck's (user error)
or the pool's (too few sinks, income too lumpy, or the Block rows too
conditional) is exactly what a seat round can separate and a single run
cannot. It goes into round 25 as an assembled lane (§5), not into a card.

**Note 3 is hygiene, applied.** The Bomb tip carried "Your deck opens with
a placer," the Spark tip "Pounding Surprise grants more," and the Mine tip
a clause about the hit landing in full: tutorial sentences and deck facts
inside rules text. The text conventions (`docs/current/text-conventions.md`)
already say a tip states the rule; these three are trimmed to the rule in
the game and in the seat glossary in one commit (§4). Set off, Hexerei, the
coven Spark, Grounded and Oz keep their text: every sentence in them is a
rule a seat has needed.

## 3. What the run did not test

An act-2 clear, so the brief's act-2 wall is still read only by seats.
Whether the deck held an Energy-priced detonator (Countdown, Sizzle or Long
Fuse, round 25's drafted hypothesis) is not recorded.
No fun verdict beyond "the loop was fun" is recorded, per Guardrail 7 a
single run does not grade fun.

## 4. Defaults applied (E), disclosed

- The three tips are trimmed as in §2 note 3, mirrored in
  `understudy/blindplay_notes.py`, under the tip ceiling.
- `EB-642` is retired with this record as its acceptance.

## 5. Round 25, redrafted: two lanes

The comparison pass (`review/records/klee-pool-comparison-pass-2026-09-06.md`
§4) drafted round 25 as a natural lane holding one Energy-priced detonator
beside the Spark-priced ones. [USER]'s note 2 adds the second lane:

1. **Natural lane, the Energy-priced detonator** (as drafted): a lane
   that holds one of Countdown, Sizzle or Long Fuse beside its Spark-priced
   detonators reaches a turn where the Spark price binds without
   deadlocking, and the seat can say which price it paid and why.
2. **Assembled lane, the Spark defence**: the coven (four Hexerei
   Personals) with Dodoco Cover, Careful Now and Front Row Seat granted,
   Jumpy Dumpty and Ka-pow! as the starter has them. The hypothesis: "a
   seat that builds the Bomb every turn and eats it for Block when the
   intent says so reaches the act-1 boss with the Spark bank never at zero
   on a Block turn; where it fails, the record names whether the Spark was
   missing, the Bomb was missing, or the Block row's condition was false."
   That sentence is what separates design error from user error.

Both lanes run on the next `+proto` build, which also carries the tip
trims and the R267/R268 Kokomi changes.
