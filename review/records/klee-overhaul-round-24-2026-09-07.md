Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Klee round 24: the coven lane; both seats state the Hexerei rule and get it right, and the one card that breaks it is Klee's own

Written 2026-09-08, small hours. Two blind Opus seats on `0.2.3022+proto`
(main `8ce6931f`), the first round after `EB-642` (every Hexerei card gives
Klee a Spark, R265 pick 1) and `EB-596` (the tip rewritten to say who pays
and what "up to 3" caps). Records:
`review/qa/klee-round-24-2026-09-07/opus-lane1-coven.md` (lane 1, six
Hexerei cards granted: Coven Errand, Witches' Circle, Alice's Introduction
Magic, Fischl's Oz, Sucrose's Gust, Mona's Stellaris Phantasm) and
`opus-lane2-natural.md` (lane 2, natural). Prototype stage, Guardrail 7. The
starter's detonator is R262's hold and is not re-asked.

## 1. The hypothesis

"With every Hexerei card granting a Spark and the tip stating who pays and
what 'up to 3' caps, a seat given a coven deck states Hexerei's rule in its
own words and gets it right, names a turn where the Spark from a Companion
play bought a Set off, and passes on no card over the word; the natural
seat meets the word on a reward and reads it first time."

**Coven** (lane 1): 120 of 120 acts, floor 14, seven fights, five won, the
first elite (Byrdonis, 83 HP) killed in one card, the second (Bygone
Effigy) cut off by the cap at 121 of 127; 24 of 62 HP. **Natural** (lane 2):
120 of 120, floor 11, six fights, five won including the Terror Eel elite,
the sixth live at the cap; 15 of 62. Neither lane stalled or hit a refusal
streak.

## 2. The reads

**1. The rule, in the seat's words.** Both right, and the same. Lane 1:
"Klee gains 1 Spark; +1 more if that play triggered an Elemental Reaction,
and +1 more if the card is upgraded, to a maximum of 3 Sparks from any one
play. Nobody pays anything for it: it is a grant, not a cost, and the cap
caps the Sparks minted by a single play, not the Sparks you can hold." Lane
2: the same three parts, "the cap of 3 caps a single play's payout, not the
pool." That is `KleeCompanionSpark.cs` exactly (Base 1, ReactionBonus 1,
UpgradedBonus 1, MaxPerPlay 3). Both read it from the battle screen's
glossary line plus the "Sparks from your Companion" rider on the Companion's
own face, on the first battle screen of fight 1 (lane 1) and the fight-1
reward glossary at floor 2 (lane 2). Round 23's three questions are closed
by this: what "up to 3" caps, who pays, and whether "and Klee herself" means
anything (it is gone, and neither seat asked).

**2. The turn a Companion's Spark changed something.** Lane 1, fight 4 turn
1: Fischl played first so Coven Errand's "if you played a Hexerei card this
turn" rider read true and put a Bomb 5 on both bodies, "a whole extra charge
bought purely by ordering." That is the condition half of the word, not the
Spark half. Lane 2, fight 4 turn 2, is the Spark half: knowing Razor "pays me
rather than costing me" is what made the seat willing to spend a Strike
ahead of it. Neither seat names a Set off that the Companion's Spark alone
made affordable.

**3. Scarcity.** Neither record names a turn where the Spark price bound.
Lane 1 (c) 4: "the 'up to 3 a play' cap never bit; every Hexerei play I made
granted exactly +1," and a third of the keyword's text (the upgraded bonus)
was unreachable without an upgraded Companion. Round 23's deadlock did not
recur in either lane.

**4. Cards passed over the word.** None in either record. Lane 2 notes the
opposite gap: "not every Companion is Hexerei," Freminet, Amber and Lisa
print no word, and the word itself does not say so.

**5. The natural lane.** First Hexerei card offered: Razor's Claw and
Thunder, taken, the tip read first time from the reward glossary under
Witches' Circle. Lane 2 predicted two damage totals (42 and 30) from the
faces and hit both.

**6. Block that reads the Bomb.** Lane 1 took zero damage in two of its
first three fights and names Careful Now beside its Bombs; it does not
repeat round 23's "no unconditional Block" finding for the coven deck.

## 3. What this says

The rewritten tip did its job: two seats, one reading, matching the code.
The word's remaining faults are on the edges of the rule, not in it: a card
that counts as Hexerei but is not a Companion pays nothing (`EB-663`), a
stack preview that says "for N Sparks" reads as a price (`EB-666`), and the
tip does not say that some Companions are not Hexerei.

## 4. Where the screen and the outcome disagreed

- **Alice's Introduction Magic** (lane 1, fight 4 turn 2): played, then
  Coven Errand and Careful Now; the Errand's rider fired on both bodies,
  so the game agreed the cards counted as Hexerei, and the Spark counter
  sat at 2 through all three plays. Both engines pay the Spark only for a
  Companion card (`effects.klee_companion_spark`, `PaysKleesSpark`), so a
  Klee card marked or hand-marked prints the promise and breaks it.
- **Flame Dance** skipped an enemy carrying no aura and a 22 stack. The
  face says "whose aura is not Pyro"; both engines read "has an aura other
  than Pyro." The face is wrong, the rule is the intended one.
- **Mona's reaction preview** says Electro-Charged, the body shows Poison:
  it is PoisonPower at the preview's number, ticked once by the time the
  seat looked. Name, not number.
- **"Mine 14, in 2 hits for 2 Sparks"** (lane 2, unresolved; lane 1 read
  the same clause): each explosion makes a Spark; "for" reads as a price.
- Not ours: Corpse Slug's Ravenous feeding two slugs off one corpse, Fat
  Gremlin's stolen gold arriving as a reward line, and Rapid Fire refusing
  a target are the base game and the bridge's grammar, each answered
  correctly on screen.

## 5. Rows and defaults

Minted: `EB-663` (one rule: any card that counts as Hexerei pays the Spark;
both engines drop the Companion gate, the tip's first sentence follows),
`EB-664` (Flame Dance's face), `EB-665` (the Electro-Charged preview names
Poison), `EB-666` (the stack clause says "making N Sparks"), `EB-667` (the
Smith screen's missing basics and Alice's two upgrade lines).

Defaults applied (E): `EB-663` takes the uniform rule rather than removing
the mark from Klee's own cards, because R265 pick 1 said every Hexerei card
and the seats read the word as one promise; the "not every Companion is
Hexerei" line goes into the tip with `EB-663`. No further coven lanes are
scheduled; the next Klee read is [USER]'s act-1 run on the R261 build,
still due, and after it a natural lane on whatever it changes.
