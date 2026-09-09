Status: RECORD (was OPEN, no pick; the defaults it names were applied; moved 2026-09-08 under R267)

# Klee round twenty-two: three natural lanes, one blocker, and the starter's detonator read a third time

Written 2026-09-06, under the Prototype loop. Three blind Opus seats on
`0.2.2817+proto` (round-22 branch with fixers Q and R in: the Spark-sink
offer rule `EB-577`, the Bomb tips and riders `EB-573`-`EB-575`, Kaeya's
face `EB-576`). Records: `review/qa/klee-round-22-2026-09-06/opus-natural-a-act1.md`
(lane 1, void), `opus-natural-b-act1.md` (lane 2, Ascension 1),
`opus-natural-a2-act1.md` (lane 1 re-run, Ascension 0). Two natural
lanes on purpose: the question is the starter, and an assembled grant
hides it. Prototype stage, Guardrail-7. [USER]'s act-1 run on R261 is
still due.

## 1. The hypothesis

"With the first two rewards each carrying a Spark-priced row, a natural
seat spends Sparks by fight two; the starter's single detonator is named
as the wait a second time, or not; a hallway random Set off with the tips
reworded reads as intended."

**Lane 1, first run** (seed `UAMJY5M912MU`): two acts, zero fights. Neow's
Hefty Tablet offered its three rares, the seat took one, and the Neow
screen returned with no options and no verb. The game log has it: a
CanonicalModelException thrown from Hefty Tablet's history entry on a
prototype row, because `EB-577`'s reward postfix handed the game a
canonical model. A hard blocker, `EB-594`, fixed the same night by fixer
S (the postfix now instantiates through the run's card scope and fires
only on post-fight rewards); the pilot's reward cycle in the build's soak
was the same fault seen from the other side (`EB-593`). The run is void.
**Lane 2** (seed `LMXPZWC8ZPKL`): 114 of 120, four of four including the
Terror Eel elite (140 HP), 62 of 62 at the stop. **Lane 1, re-run** (seed
`U7JJA9R7HNYG`, Hefty Tablet excluded by the coordinator and disclosed;
it was not offered): 120 of 120, six of six, 16 of 62.

## 2. What the round found

**The Spark-priced offer, first clause: the roll works and the economy
does not bind.** Spark-priced rows appeared at four of six rewards on the
re-run and at every logged reward on lane 2; both seats drafted them. Lane
2 ended fights at 4, 2, 5, 3 Sparks and spent three all act; the re-run
ended at 2, 1, 3, 4, 2, 3 and spent only on Bang Bang! and Quick Fuse.
Lane 2: "the Spark economy never binds, so a Spark price reads as free;
1-Spark cards are auto-picks and 2-Spark cards feel mispriced upward."
The re-run, the other edge of the same fact: "the Spark loop is circular.
Sparks come from detonations, so a Spark-priced detonator is dead in hand
until you have already detonated": fight 4 turn 2 printed "CANNOT BE
PLAYED: you have 1 Spark, and this costs 2" with a Bomb 12 on the board.
The rule is printed everywhere and its consequence is invisible until it
bites. Seven rounds now read the Spark bank as either inert or circular;
the offer rule reached the sinks and did not change the reading.

**The starter's detonator, third natural reading.** Lane 2: three turns
with a Bomb up and no Set off in hand; "one turn I held Ka-pow! and
deliberately banked." The re-run: "five turns across six fights had a
live Bomb on the board and nothing in hand that could set it off; those
turns are 100% filler. The draft can fix it, I took three detonators by
floor 5 and the rate fell, but the starting deck cannot." Turn one: "Jumpy
Dumpty is Innate, costs 1, and is the only card that starts the engine, so
it plays itself"; "five of six fights opened identically"; the kit's first
real decision arrived on turn two of fight one on both lanes, and turn one
was live only "when the enemy supplies armour or my HP supplies pressure,
never off its own opening hand." That is round 21's reading a second and
third time, from the lanes that could see it. The starter is R242's and
R261's, and its next move is [USER]'s: the pick is raised on its own
after this round lands, with a marked default, so this round's packet
carries none (§4).

**The random Set off with the tips reworded.** Lane 2 on Tinder Toss:
"'twice' repeats the whole clause, and against one enemy the second Set
off catches Mines the first one just created; I only learned this from
arithmetic" (`EB-595`). The Bomb readout it praised as "the single best
piece of text in the kit": "Bomb 40, Bomb sizes here: 22 / 18, growing
each turn, and dropping Mine 3 on ALL enemies when they go off. None goes
off by itself" (`EB-573` built, read once). The re-run met the same line
printing two numbers for one Bomb, "Bomb 6 ... Bomb sizes here: 4", the
Vaporize forecast beside the size with nothing saying so (`EB-605`).

**The decision, both lanes, the same as every round.** "Banking a Bomb to
40 for a Vulnerable-boosted 78-damage turn"; "choosing Chain Fuse as the
one legal Skill under Smoggy so Big Badda Boom did 84 instead of 60";
"spend a Bomb 12 now or let it reach 16"; "detonate to pay for a second
detonation". Against Plating: "a 32-point bomb is a 24-point bomb, and
the fix (spend Strikes first) makes the Bomb deck play like a Strike deck
for a turn", legible and beaten. Fireworks Show at 2 Sparks "strictly
dominated against one enemy" and never played in four fights on lane 2.

**Legibility.** Hexerei unreadable from its tip after four readings, a
draft declined on it (`EB-596`). The soft rider and the hard refusal on
the same bare board ("No Bomb on the field" on Ka-pow!, "CANNOT BE
PLAYED: no enemy is holding a Bomb" on Fireworks Show), correct and
asymmetric, recorded. The Mine's timing "invites the hopeful reading"
(chip damage on the enemy's turn, not mitigation), recorded. Reactions
invisible on the re-run, detectable only from the Spark ledger (`EB-410`,
cited). Ornamental Fan at five Attacks paying once (the game's,
recorded). Praised: faces reprinting under Weak; the refusal lines
"saved me at least two wasted actions"; the reward screens "consistently
well judged".

## 3. What the round did not test

The act-1 boss on any lane. Hefty Tablet on the fixed build. Nothing here
is a strength reading.

## 4. The smallest interventions, ranked

1. **`EB-594` and `EB-593`:** built by fixer S the same night; the next
   Klee soak must reach three fights before a seat embarks.
2. **The starter's detonator and the Spark loop:** three natural readings
   agree, and the move is the starter's, so it is [USER]'s. Raised as its
   own numbered pick after this round lands; nothing here proposes it.
3. **`EB-595`, `EB-596`, `EB-605`:** the "twice", the Hexerei tip, the
   two-number Bomb line.

## 5. Defaults applied (D and E), disclosed

- **`EB-593` to `EB-596`, `EB-605` minted; `EB-410`, `EB-573`, `EB-577`
  cited.**
- **Lane 1's first run is void** (the blocker); the re-run's Hefty Tablet
  exclusion was disclosed and never bound.
- **The two completed records are the round's evidence.**
